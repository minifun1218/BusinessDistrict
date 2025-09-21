#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫任务调度器 - 使用APScheduler实现定时任务
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from flask import current_app

from app.extensions import db
from app.models.city import City
from app.models.business_area import BusinessArea
from .crawler_manager import CrawlerManager

logger = logging.getLogger(__name__)

class CrawlerScheduler:
    """爬虫任务调度器"""
    
    def __init__(self, app=None):
        self.scheduler = None
        self.crawler_manager = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化调度器"""
        try:
            # 配置调度器
            jobstores = {
                'default': SQLAlchemyJobStore(url=app.config['SQLALCHEMY_DATABASE_URI'])
            }
            executors = {
                'default': ThreadPoolExecutor(20),
            }
            job_defaults = {
                'coalesce': False,
                'max_instances': 3
            }
            
            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='Asia/Shanghai'
            )
            
            # 初始化爬虫管理器
            with app.app_context():
                baidu_key = app.config.get('BAIDU_MAP_AK')
                amap_key = app.config.get('AMAP_KEY')
                self.crawler_manager = CrawlerManager(baidu_key, amap_key)
            
            # 启动调度器
            self.scheduler.start()
            logger.info("爬虫调度器启动成功")
            
            # 注册默认任务
            self._register_default_jobs()
            
        except Exception as e:
            logger.error(f"爬虫调度器初始化失败: {str(e)}")
            raise
    
    def _register_default_jobs(self):
        """注册默认的定时任务"""
        try:
            # 每日数据更新任务（凌晨2点执行）
            self.scheduler.add_job(
                func=self._daily_data_update,
                trigger='cron',
                hour=2,
                minute=0,
                id='daily_data_update',
                name='每日数据更新',
                replace_existing=True
            )
            
            # 每周全量数据同步（周日凌晨3点执行）
            self.scheduler.add_job(
                func=self._weekly_full_sync,
                trigger='cron',
                day_of_week=6,  # 周日
                hour=3,
                minute=0,
                id='weekly_full_sync',
                name='每周全量数据同步',
                replace_existing=True
            )
            
            logger.info("默认定时任务注册成功")
            
        except Exception as e:
            logger.error(f"注册默认任务失败: {str(e)}")
    
    def _daily_data_update(self):
        """每日数据更新任务"""
        try:
            logger.info("开始执行每日数据更新任务")
            
            with current_app.app_context():
                # 获取热门城市列表
                hot_cities = City.query.filter_by(is_hot=True).limit(10).all()
                
                success_count = 0
                for city in hot_cities:
                    try:
                        result = self.crawler_manager.crawl_city_data(
                            city_id=city.id,
                            city_name=city.name,
                            update_existing=True
                        )
                        
                        if result['success']:
                            success_count += 1
                            logger.info(f"城市 {city.name} 数据更新成功")
                        else:
                            logger.error(f"城市 {city.name} 数据更新失败: {result.get('error')}")
                    
                    except Exception as e:
                        logger.error(f"更新城市 {city.name} 数据时出错: {str(e)}")
                
                logger.info(f"每日数据更新任务完成，成功更新 {success_count}/{len(hot_cities)} 个城市")
        
        except Exception as e:
            logger.error(f"每日数据更新任务执行失败: {str(e)}")
    
    def _weekly_full_sync(self):
        """每周全量数据同步任务"""
        try:
            logger.info("开始执行每周全量数据同步任务")
            
            with current_app.app_context():
                # 获取所有城市
                all_cities = City.query.filter_by(level='city').all()
                
                success_count = 0
                for city in all_cities:
                    try:
                        result = self.crawler_manager.crawl_city_data(
                            city_id=city.id,
                            city_name=city.name,
                            update_existing=True
                        )
                        
                        if result['success']:
                            success_count += 1
                            logger.info(f"城市 {city.name} 全量同步成功")
                        else:
                            logger.error(f"城市 {city.name} 全量同步失败: {result.get('error')}")
                    
                    except Exception as e:
                        logger.error(f"同步城市 {city.name} 数据时出错: {str(e)}")
                
                logger.info(f"每周全量数据同步任务完成，成功同步 {success_count}/{len(all_cities)} 个城市")
        
        except Exception as e:
            logger.error(f"每周全量数据同步任务执行失败: {str(e)}")
    
    def schedule_city_crawl(self, city_id: str, city_name: str, 
                           run_date: datetime, 
                           crawlers: List[str] = None,
                           update_existing: bool = False) -> str:
        """调度城市爬取任务"""
        try:
            job_id = f"crawl_city_{city_id}_{int(run_date.timestamp())}"
            
            self.scheduler.add_job(
                func=self._crawl_single_city,
                trigger='date',
                run_date=run_date,
                args=[city_id, city_name, crawlers, update_existing],
                id=job_id,
                name=f'爬取城市数据: {city_name}',
                replace_existing=True
            )
            
            logger.info(f"城市爬取任务已调度: {city_name} at {run_date}")
            return job_id
            
        except Exception as e:
            logger.error(f"调度城市爬取任务失败: {str(e)}")
            raise
    
    def schedule_area_crawl(self, area_id: str, area_name: str,
                           run_date: datetime,
                           crawlers: List[str] = None,
                           update_existing: bool = False) -> str:
        """调度商圈爬取任务"""
        try:
            job_id = f"crawl_area_{area_id}_{int(run_date.timestamp())}"
            
            self.scheduler.add_job(
                func=self._crawl_single_area,
                trigger='date',
                run_date=run_date,
                args=[area_id, area_name, crawlers, update_existing],
                id=job_id,
                name=f'爬取商圈数据: {area_name}',
                replace_existing=True
            )
            
            logger.info(f"商圈爬取任务已调度: {area_name} at {run_date}")
            return job_id
            
        except Exception as e:
            logger.error(f"调度商圈爬取任务失败: {str(e)}")
            raise
    
    def schedule_recurring_crawl(self, target_type: str, target_ids: List[str],
                                cron_expr: Dict[str, Any],
                                crawlers: List[str] = None,
                                update_existing: bool = True) -> str:
        """调度周期性爬取任务"""
        try:
            job_id = f"recurring_{target_type}_{len(target_ids)}_{int(datetime.now().timestamp())}"
            
            if target_type == 'city':
                func = self._crawl_multiple_cities
                args = [target_ids, crawlers, update_existing]
            elif target_type == 'area':
                func = self._crawl_multiple_areas
                args = [target_ids, crawlers, update_existing]
            else:
                raise ValueError(f"不支持的目标类型: {target_type}")
            
            self.scheduler.add_job(
                func=func,
                trigger='cron',
                args=args,
                id=job_id,
                name=f'周期性爬取{target_type}数据',
                replace_existing=True,
                **cron_expr
            )
            
            logger.info(f"周期性爬取任务已调度: {target_type} - {len(target_ids)} 个目标")
            return job_id
            
        except Exception as e:
            logger.error(f"调度周期性爬取任务失败: {str(e)}")
            raise
    
    def _crawl_single_city(self, city_id: str, city_name: str, 
                          crawlers: List[str] = None, 
                          update_existing: bool = False):
        """爬取单个城市数据"""
        try:
            with current_app.app_context():
                result = self.crawler_manager.crawl_city_data(
                    city_id=city_id,
                    city_name=city_name,
                    crawlers=crawlers,
                    update_existing=update_existing
                )
                
                if result['success']:
                    logger.info(f"定时任务：城市 {city_name} 数据爬取成功")
                else:
                    logger.error(f"定时任务：城市 {city_name} 数据爬取失败: {result.get('error')}")
        
        except Exception as e:
            logger.error(f"定时任务：爬取城市 {city_name} 数据失败: {str(e)}")
    
    def _crawl_single_area(self, area_id: str, area_name: str,
                          crawlers: List[str] = None,
                          update_existing: bool = False):
        """爬取单个商圈数据"""
        try:
            with current_app.app_context():
                area = BusinessArea.query.get(area_id)
                if not area:
                    logger.error(f"商圈 {area_id} 不存在")
                    return
                
                stores_count = self.crawler_manager._crawl_area_stores(
                    area_id=area.id,
                    area_name=area.name,
                    area_lat=area.latitude,
                    area_lng=area.longitude,
                    crawler_names=crawlers or list(self.crawler_manager.crawlers.keys()),
                    update_existing=update_existing
                )
                
                logger.info(f"定时任务：商圈 {area_name} 爬取到 {stores_count} 个店铺")
        
        except Exception as e:
            logger.error(f"定时任务：爬取商圈 {area_name} 数据失败: {str(e)}")
    
    def _crawl_multiple_cities(self, city_ids: List[str], 
                              crawlers: List[str] = None,
                              update_existing: bool = True):
        """批量爬取城市数据"""
        try:
            with current_app.app_context():
                cities = City.query.filter(City.id.in_(city_ids)).all()
                
                success_count = 0
                for city in cities:
                    try:
                        result = self.crawler_manager.crawl_city_data(
                            city_id=city.id,
                            city_name=city.name,
                            crawlers=crawlers,
                            update_existing=update_existing
                        )
                        
                        if result['success']:
                            success_count += 1
                    
                    except Exception as e:
                        logger.error(f"批量爬取：城市 {city.name} 失败: {str(e)}")
                
                logger.info(f"批量爬取任务完成，成功 {success_count}/{len(cities)} 个城市")
        
        except Exception as e:
            logger.error(f"批量爬取城市数据失败: {str(e)}")
    
    def _crawl_multiple_areas(self, area_ids: List[str],
                             crawlers: List[str] = None,
                             update_existing: bool = True):
        """批量爬取商圈数据"""
        try:
            with current_app.app_context():
                areas = BusinessArea.query.filter(BusinessArea.id.in_(area_ids)).all()
                
                success_count = 0
                total_stores = 0
                
                for area in areas:
                    try:
                        stores_count = self.crawler_manager._crawl_area_stores(
                            area_id=area.id,
                            area_name=area.name,
                            area_lat=area.latitude,
                            area_lng=area.longitude,
                            crawler_names=crawlers or list(self.crawler_manager.crawlers.keys()),
                            update_existing=update_existing
                        )
                        
                        success_count += 1
                        total_stores += stores_count
                    
                    except Exception as e:
                        logger.error(f"批量爬取：商圈 {area.name} 失败: {str(e)}")
                
                logger.info(f"批量爬取商圈任务完成，成功 {success_count}/{len(areas)} 个商圈，共 {total_stores} 个店铺")
        
        except Exception as e:
            logger.error(f"批量爬取商圈数据失败: {str(e)}")
    
    def get_jobs(self) -> List[Dict[str, Any]]:
        """获取所有调度任务"""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger),
                    'func_name': job.func.__name__ if hasattr(job.func, '__name__') else str(job.func)
                })
            
            return jobs
            
        except Exception as e:
            logger.error(f"获取调度任务失败: {str(e)}")
            return []
    
    def remove_job(self, job_id: str) -> bool:
        """移除调度任务"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"任务 {job_id} 已移除")
            return True
            
        except Exception as e:
            logger.error(f"移除任务 {job_id} 失败: {str(e)}")
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """暂停调度任务"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"任务 {job_id} 已暂停")
            return True
            
        except Exception as e:
            logger.error(f"暂停任务 {job_id} 失败: {str(e)}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """恢复调度任务"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"任务 {job_id} 已恢复")
            return True
            
        except Exception as e:
            logger.error(f"恢复任务 {job_id} 失败: {str(e)}")
            return False
    
    def shutdown(self):
        """关闭调度器"""
        try:
            if self.scheduler:
                self.scheduler.shutdown()
                logger.info("爬虫调度器已关闭")
            
            if self.crawler_manager:
                self.crawler_manager.close()
        
        except Exception as e:
            logger.error(f"关闭调度器失败: {str(e)}")

# 全局调度器实例
crawler_scheduler = CrawlerScheduler()
