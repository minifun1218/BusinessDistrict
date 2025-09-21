#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫相关的CLI命令
"""

import click
from flask import current_app
from flask.cli import with_appcontext

from app.extensions import db
from app.models.city import City
from app.models.business_area import BusinessArea
from .crawler_manager import CrawlerManager

@click.group()
def crawler():
    """爬虫相关命令"""
    pass

@crawler.command()
@click.option('--city-id', help='城市ID')
@click.option('--city-name', help='城市名称')
@click.option('--crawlers', help='指定爬虫（用逗号分隔）')
@click.option('--update', is_flag=True, help='更新已存在的数据')
@with_appcontext
def crawl_city(city_id, city_name, crawlers, update):
    """爬取指定城市的数据"""
    try:
        if not city_id and not city_name:
            click.echo("错误：必须指定城市ID或城市名称")
            return
        
        # 查找城市
        if city_id:
            city = City.query.get(city_id)
        else:
            city = City.query.filter_by(name=city_name).first()
        
        if not city:
            click.echo(f"错误：找不到城市 {city_id or city_name}")
            return
        
        # 解析爬虫列表
        crawler_list = crawlers.split(',') if crawlers else None
        
        # 初始化爬虫管理器
        baidu_key = current_app.config.get('BAIDU_MAP_AK')
        amap_key = current_app.config.get('AMAP_KEY')
        
        with CrawlerManager(baidu_key, amap_key) as crawler_manager:
            click.echo(f"开始爬取城市: {city.name}")
            
            result = crawler_manager.crawl_city_data(
                city_id=city.id,
                city_name=city.name,
                crawlers=crawler_list,
                update_existing=update
            )
            
            if result['success']:
                click.echo(f"✅ 爬取成功！")
                click.echo(f"   商圈数量: {result['areas_count']}")
                click.echo(f"   店铺数量: {result['stores_count']}")
                click.echo(f"   使用爬虫: {', '.join(result['crawlers_used'])}")
            else:
                click.echo(f"❌ 爬取失败: {result.get('error')}")
    
    except Exception as e:
        click.echo(f"❌ 执行失败: {str(e)}")

@crawler.command()
@click.option('--area-id', help='商圈ID')
@click.option('--area-name', help='商圈名称')
@click.option('--crawlers', help='指定爬虫（用逗号分隔）')
@click.option('--update', is_flag=True, help='更新已存在的数据')
@with_appcontext
def crawl_area(area_id, area_name, crawlers, update):
    """爬取指定商圈的店铺数据"""
    try:
        if not area_id and not area_name:
            click.echo("错误：必须指定商圈ID或商圈名称")
            return
        
        # 查找商圈
        if area_id:
            area = BusinessArea.query.get(area_id)
        else:
            area = BusinessArea.query.filter_by(name=area_name).first()
        
        if not area:
            click.echo(f"错误：找不到商圈 {area_id or area_name}")
            return
        
        # 解析爬虫列表
        crawler_list = crawlers.split(',') if crawlers else None
        
        # 初始化爬虫管理器
        baidu_key = current_app.config.get('BAIDU_MAP_AK')
        amap_key = current_app.config.get('AMAP_KEY')
        
        with CrawlerManager(baidu_key, amap_key) as crawler_manager:
            click.echo(f"开始爬取商圈店铺: {area.name}")
            
            stores_count = crawler_manager._crawl_area_stores(
                area_id=area.id,
                area_name=area.name,
                area_lat=area.latitude,
                area_lng=area.longitude,
                crawler_names=crawler_list or list(crawler_manager.crawlers.keys()),
                update_existing=update
            )
            
            click.echo(f"✅ 爬取成功！获得 {stores_count} 个店铺")
    
    except Exception as e:
        click.echo(f"❌ 执行失败: {str(e)}")

@crawler.command()
@click.option('--limit', default=10, help='限制城市数量')
@click.option('--crawlers', help='指定爬虫（用逗号分隔）')
@click.option('--update', is_flag=True, help='更新已存在的数据')
@with_appcontext
def crawl_hot_cities(limit, crawlers, update):
    """爬取热门城市数据"""
    try:
        # 获取热门城市
        hot_cities = City.query.filter_by(is_hot=True).limit(limit).all()
        
        if not hot_cities:
            click.echo("没有找到热门城市")
            return
        
        # 解析爬虫列表
        crawler_list = crawlers.split(',') if crawlers else None
        
        # 初始化爬虫管理器
        baidu_key = current_app.config.get('BAIDU_MAP_AK')
        amap_key = current_app.config.get('AMAP_KEY')
        
        with CrawlerManager(baidu_key, amap_key) as crawler_manager:
            click.echo(f"开始批量爬取 {len(hot_cities)} 个热门城市...")
            
            success_count = 0
            total_areas = 0
            total_stores = 0
            
            for city in hot_cities:
                click.echo(f"正在爬取: {city.name}")
                
                result = crawler_manager.crawl_city_data(
                    city_id=city.id,
                    city_name=city.name,
                    crawlers=crawler_list,
                    update_existing=update
                )
                
                if result['success']:
                    success_count += 1
                    total_areas += result['areas_count']
                    total_stores += result['stores_count']
                    click.echo(f"  ✅ 成功：{result['areas_count']} 个商圈，{result['stores_count']} 个店铺")
                else:
                    click.echo(f"  ❌ 失败：{result.get('error')}")
            
            click.echo(f"\n批量爬取完成：")
            click.echo(f"成功城市: {success_count}/{len(hot_cities)}")
            click.echo(f"总商圈数: {total_areas}")
            click.echo(f"总店铺数: {total_stores}")
    
    except Exception as e:
        click.echo(f"❌ 执行失败: {str(e)}")

@crawler.command()
@with_appcontext
def test_crawlers():
    """测试爬虫连通性"""
    try:
        baidu_key = current_app.config.get('BAIDU_MAP_AK')
        amap_key = current_app.config.get('AMAP_KEY')
        
        with CrawlerManager(baidu_key, amap_key) as crawler_manager:
            click.echo("测试爬虫连通性...")
            
            results = crawler_manager.test_crawlers()
            
            for crawler_name, result in results.items():
                status = result['status']
                if status == 'ok':
                    click.echo(f"✅ {crawler_name}: 连接正常")
                elif status == 'failed':
                    click.echo(f"⚠️  {crawler_name}: 连接失败")
                else:
                    click.echo(f"❌ {crawler_name}: 错误 - {result.get('error')}")
    
    except Exception as e:
        click.echo(f"❌ 测试失败: {str(e)}")

@crawler.command()
@with_appcontext
def show_stats():
    """显示爬虫统计信息"""
    try:
        baidu_key = current_app.config.get('BAIDU_MAP_AK')
        amap_key = current_app.config.get('AMAP_KEY')
        
        with CrawlerManager(baidu_key, amap_key) as crawler_manager:
            stats = crawler_manager.get_crawler_stats()
            
            click.echo("爬虫统计信息:")
            click.echo(f"可用爬虫: {', '.join(stats['available_crawlers'])}")
            click.echo(f"已爬取商圈: {stats['stats']['total_areas_crawled']}")
            click.echo(f"已爬取店铺: {stats['stats']['total_stores_crawled']}")
            
            last_crawl = stats['stats']['last_crawl_time']
            if last_crawl:
                click.echo(f"最后爬取: {last_crawl}")
            
            errors = stats['stats']['errors']
            if errors:
                click.echo(f"错误数量: {len(errors)}")
                for error in errors[-3:]:  # 显示最近3个错误
                    click.echo(f"  - {error['crawler']}: {error['error']}")
    
    except Exception as e:
        click.echo(f"❌ 获取统计信息失败: {str(e)}")

@crawler.command()
@with_appcontext
def check_data_quality():
    """检查数据质量"""
    try:
        from sqlalchemy import func
        
        # 统计商圈数据
        total_areas = BusinessArea.query.count()
        areas_with_coords = BusinessArea.query.filter(
            BusinessArea.longitude.isnot(None),
            BusinessArea.latitude.isnot(None)
        ).count()
        
        # 统计店铺数据
        from app.models.business_area import Store
        total_stores = Store.query.count()
        stores_with_rating = Store.query.filter(Store.rating > 0).count()
        
        click.echo("数据质量报告:")
        click.echo(f"商圈总数: {total_areas}")
        click.echo(f"有坐标的商圈: {areas_with_coords} ({areas_with_coords/total_areas*100:.1f}%)")
        click.echo(f"店铺总数: {total_stores}")
        click.echo(f"有评分的店铺: {stores_with_rating} ({stores_with_rating/total_stores*100:.1f}%)")
        
        # 按城市统计
        city_stats = db.session.query(
            City.name,
            func.count(BusinessArea.id).label('area_count')
        ).outerjoin(BusinessArea).group_by(City.id).all()
        
        click.echo("\n按城市统计:")
        for city_name, area_count in city_stats:
            if area_count > 0:
                click.echo(f"  {city_name}: {area_count} 个商圈")
    
    except Exception as e:
        click.echo(f"❌ 检查数据质量失败: {str(e)}")

def register_commands(app):
    """注册爬虫命令"""
    app.cli.add_command(crawler)
