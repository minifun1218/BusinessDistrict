#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源爬虫模块
"""

from .baidu_crawler import BaiduMapCrawler
from .amap_crawler import AmapCrawler
from .dianping_crawler import DianpingCrawler

__all__ = ['BaiduMapCrawler', 'AmapCrawler', 'DianpingCrawler']
