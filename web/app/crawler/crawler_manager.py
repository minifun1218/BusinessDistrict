#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫管理器 - 统一管理和调度各个爬虫
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

from app.extensions import db
from app.models.business_area import BusinessArea, Store
from app.models.city import City
from .data_sources.baidu_crawler import BaiduMapCrawler
from .data_sources.amap_crawler import AmapCrawler
from .data_sources.dianping_crawler import DianpingCrawler

logger = logging.getLogger(__name__)

class CrawlerManager:
    """爬虫管理器"""
    
    def __init__(self, baidu_api_key: str = None, amap_api_key: str = None):
        self.baidu_api_key = baidu_api_key
        self.amap_api_key = amap_api_key
        self.crawlers = {}
        self.stats = {
            'total_areas_crawled': 0,
            'total_stores_crawled': 0,
            'last_crawl_time': None,
            'errors': []
        }
        
        # 初始化爬虫实例
        self._init_crawlers()
    
    def _init_crawlers(self):
        """初始化爬虫实例"""
        try:
            if self.baidu_api_key:
                self.crawlers['baidu'] = BaiduMapCrawler(self.baidu_api_key)
                logger.info("百度地图爬虫初始化成功")
            
            if self.amap_api_key:
                self.crawlers['amap'] = AmapCrawler(self.amap_api_key)
                logger.info("高德地图爬虫初始化成功")
            
            # 大众点评爬虫（演示版本）
            self.crawlers['dianping'] = DianpingCrawler()
            logger.info("大众点评爬虫初始化成功")
            
            logger.info(f"爬虫管理器初始化完成，共加载 {len(self.crawlers)} 个爬虫")
            
        except Exception as e:
            logger.error(f"爬虫初始化失败: {str(e)}")
            raise
    
    def crawl_city_data(self, city_id: str, city_name: str, 
                       crawlers: List[str] = None, 
                       update_existing: bool = False) -> Dict[str, Any]:
        """
        爬取指定城市的数据
        
        Args:
            city_id: 城市ID
            city_name: 城市名称
            crawlers: 指定使用的爬虫列表，None表示使用所有可用爬虫
            update_existing: 是否更新已存在的数据
        
        Returns:
            爬取结果统计
        """
        try:
            logger.info(f"开始爬取城市 {city_name}({city_id}) 的数据")
            
            # 确定要使用的爬虫
            active_crawlers = crawlers or list(self.crawlers.keys())
            active_crawlers = [name for name in active_crawlers if name in self.crawlers]
            
            if not active_crawlers:
                logger.error("没有可用的爬虫")
                return {'success': False, 'error': '没有可用的爬虫'}
            
            # 并行爬取商圈数据
            all_areas = []
            with ThreadPoolExecutor(max_workers=len(active_crawlers)) as executor:
                future_to_crawler = {
                    executor.submit(
                        self.crawlers[crawler_name].get_business_areas,
                        city_id, city_name
                    ): crawler_name
                    for crawler_name in active_crawlers
                }
                
                for future in as_completed(future_to_crawler):
                    crawler_name = future_to_crawler[future]
                    try:
                        areas = future.result()
                        logger.info(f"{crawler_name} 爬虫获取到 {len(areas)} 个商圈")
                        all_areas.extend(areas)
                    except Exception as e:
                        logger.error(f"{crawler_name} 爬虫执行失败: {str(e)}")
                        self.stats['errors'].append({
                            'crawler': crawler_name,
                            'error': str(e),
                            'time': datetime.now().isoformat()
                        })
            
            # 数据去重和合并
            unique_areas = self._merge_area_data(all_areas)
            logger.info(f"去重后得到 {len(unique_areas)} 个唯一商圈")
            
            # 保存商圈数据
            saved_areas = self._save_business_areas(unique_areas, update_existing)
            
            # 爬取店铺数据
            total_stores = 0
            for area in saved_areas:
                stores_count = self._crawl_area_stores(
                    area['id'], area['name'], 
                    area['latitude'], area['longitude'],
                    active_crawlers, update_existing
                )
                total_stores += stores_count
            
            # 更新统计信息
            self.stats['total_areas_crawled'] += len(saved_areas)
            self.stats['total_stores_crawled'] += total_stores
            self.stats['last_crawl_time'] = datetime.now().isoformat()
            
            result = {
                'success': True,
                'city_id': city_id,
                'city_name': city_name,
                'areas_count': len(saved_areas),
                'stores_count': total_stores,
                'crawlers_used': active_crawlers,
                'crawl_time': datetime.now().isoformat()
            }
            
            logger.info(f"城市 {city_name} 数据爬取完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"爬取城市 {city_name} 数据失败: {str(e)}")
            return {
                'success': False,
                'city_id': city_id,
                'city_name': city_name,
                'error': str(e)
            }
    
    def _crawl_area_stores(self, area_id: str, area_name: str, 
                          area_lat: float, area_lng: float,
                          crawler_names: List[str], 
                          update_existing: bool = False) -> int:
        """爬取指定商圈的店铺数据"""
        try:
            all_stores = []
            
            # 并行爬取店铺数据
            with ThreadPoolExecutor(max_workers=len(crawler_names)) as executor:
                future_to_crawler = {
                    executor.submit(
                        self.crawlers[crawler_name].get_stores,
                        area_id, area_name, area_lat, area_lng
                    ): crawler_name
                    for crawler_name in crawler_names
                    if hasattr(self.crawlers[crawler_name], 'get_stores')
                }
                
                for future in as_completed(future_to_crawler):
                    crawler_name = future_to_crawler[future]
                    try:
                        stores = future.result()
                        logger.info(f"{crawler_name} 爬虫为商圈 {area_name} 获取到 {len(stores)} 个店铺")
                        all_stores.extend(stores)
                    except Exception as e:
                        logger.error(f"{crawler_name} 爬虫获取商圈 {area_name} 店铺失败: {str(e)}")
            
            # 数据去重和合并
            unique_stores = self._merge_store_data(all_stores)
            
            # 保存店铺数据
            saved_stores = self._save_stores(unique_stores, update_existing)
            
            # 更新商圈的店铺数量
            self._update_area_store_count(area_id, len(saved_stores))
            
            return len(saved_stores)
            
        except Exception as e:
            logger.error(f"爬取商圈 {area_name} 店铺数据失败: {str(e)}")
            return 0
    
    def _merge_area_data(self, areas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """合并多个数据源的商圈数据"""
        merged_areas = {}
        
        for area in areas:
            # 使用名称和大致坐标作为合并键
            lat_rounded = round(area['latitude'], 3)
            lng_rounded = round(area['longitude'], 3)
            key = f"{area['name']}_{lat_rounded}_{lng_rounded}"
            
            if key not in merged_areas:
                merged_areas[key] = area.copy()
            else:
                # 合并数据，优先保留更完整的信息
                existing = merged_areas[key]
                
                # 合并数值字段（取平均值或最大值）
                if area.get('hot_value', 0) > existing.get('hot_value', 0):
                    existing['hot_value'] = area['hot_value']
                
                if area.get('rating', 0) > existing.get('rating', 0):
                    existing['rating'] = area['rating']
                
                # 合并列表字段
                existing['facilities'] = list(set(
                    existing.get('facilities', []) + area.get('facilities', [])
                ))
                existing['tags'] = list(set(
                    existing.get('tags', []) + area.get('tags', [])
                ))
                
                # 合并描述信息
                if area.get('description') and len(area['description']) > len(existing.get('description', '')):
                    existing['description'] = area['description']
        
        return list(merged_areas.values())
    
    def _merge_store_data(self, stores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """合并多个数据源的店铺数据"""
        merged_stores = {}
        
        for store in stores:
            # 使用名称和大致坐标作为合并键
            lat_rounded = round(store['latitude'], 3)
            lng_rounded = round(store['longitude'], 3)
            key = f"{store['name']}_{lat_rounded}_{lng_rounded}"
            
            if key not in merged_stores:
                merged_stores[key] = store.copy()
            else:
                # 合并数据
                existing = merged_stores[key]
                
                # 取更高的评分和更多的评论数
                if store.get('rating', 0) > existing.get('rating', 0):
                    existing['rating'] = store['rating']
                
                if store.get('review_count', 0) > existing.get('review_count', 0):
                    existing['review_count'] = store['review_count']
                
                # 合并标签和设施
                existing['tags'] = list(set(
                    existing.get('tags', []) + store.get('tags', [])
                ))
                existing['facilities'] = list(set(
                    existing.get('facilities', []) + store.get('facilities', [])
                ))
        
        return list(merged_stores.values())
    
    def _save_business_areas(self, areas: List[Dict[str, Any]], 
                            update_existing: bool = False) -> List[Dict[str, Any]]:
        """保存商圈数据到数据库"""
        saved_areas = []
        
        try:
            for area_data in areas:
                try:
                    # 检查是否已存在
                    existing_area = BusinessArea.query.get(area_data['id'])
                    
                    if existing_area and not update_existing:
                        logger.debug(f"商圈 {area_data['name']} 已存在，跳过")
                        saved_areas.append(area_data)
                        continue
                    
                    if existing_area and update_existing:
                        # 更新现有记录
                        for key, value in area_data.items():
                            if hasattr(existing_area, key) and key != 'id':
                                setattr(existing_area, key, value)
                        existing_area.updated_at = datetime.utcnow()
                        logger.info(f"更新商圈: {area_data['name']}")
                    else:
                        # 创建新记录
                        area = BusinessArea(**area_data)
                        db.session.add(area)
                        logger.info(f"新增商圈: {area_data['name']}")
                    
                    saved_areas.append(area_data)
                    
                except Exception as e:
                    logger.error(f"保存商圈 {area_data.get('name', 'Unknown')} 失败: {str(e)}")
                    continue
            
            db.session.commit()
            logger.info(f"成功保存 {len(saved_areas)} 个商圈")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"保存商圈数据失败: {str(e)}")
            raise
        
        return saved_areas
    
    def _save_stores(self, stores: List[Dict[str, Any]], 
                    update_existing: bool = False) -> List[Dict[str, Any]]:
        """保存店铺数据到数据库"""
        saved_stores = []
        
        try:
            for store_data in stores:
                try:
                    # 检查是否已存在
                    existing_store = Store.query.get(store_data['id'])
                    
                    if existing_store and not update_existing:
                        saved_stores.append(store_data)
                        continue
                    
                    if existing_store and update_existing:
                        # 更新现有记录
                        for key, value in store_data.items():
                            if hasattr(existing_store, key) and key != 'id':
                                setattr(existing_store, key, value)
                        existing_store.updated_at = datetime.utcnow()
                    else:
                        # 创建新记录
                        store = Store(**store_data)
                        db.session.add(store)
                    
                    saved_stores.append(store_data)
                    
                except Exception as e:
                    logger.error(f"保存店铺 {store_data.get('name', 'Unknown')} 失败: {str(e)}")
                    continue
            
            db.session.commit()
            logger.info(f"成功保存 {len(saved_stores)} 个店铺")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"保存店铺数据失败: {str(e)}")
            raise
        
        return saved_stores
    
    def _update_area_store_count(self, area_id: str, store_count: int):
        """更新商圈的店铺数量"""
        try:
            area = BusinessArea.query.get(area_id)
            if area:
                area.store_count = store_count
                db.session.commit()
        except Exception as e:
            logger.error(f"更新商圈店铺数量失败: {str(e)}")
    
    def get_crawler_stats(self) -> Dict[str, Any]:
        """获取爬虫统计信息"""
        return {
            'available_crawlers': list(self.crawlers.keys()),
            'stats': self.stats.copy()
        }
    
    def test_crawlers(self) -> Dict[str, Any]:
        """测试所有爬虫的连通性"""
        results = {}
        
        for name, crawler in self.crawlers.items():
            try:
                # 简单的连通性测试
                if name == 'baidu' and hasattr(crawler, '_get_city_center'):
                    result = crawler._get_city_center('北京')
                    results[name] = {'status': 'ok' if result else 'failed', 'details': result}
                elif name == 'amap' and hasattr(crawler, '_search_places'):
                    result = crawler._search_places('商圈', '北京')
                    results[name] = {'status': 'ok' if result else 'failed', 'count': len(result)}
                else:
                    results[name] = {'status': 'ok', 'details': 'Mock crawler'}
                    
            except Exception as e:
                results[name] = {'status': 'error', 'error': str(e)}
        
        return results
    
    def close(self):
        """关闭所有爬虫连接"""
        for crawler in self.crawlers.values():
            if hasattr(crawler, 'close'):
                crawler.close()
        
        logger.info("爬虫管理器已关闭")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
