#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频采集脚本 (Video Collection Script)
=====================================
基于CMS资源站API的视频采集工具

API URL配置:
- 列表URL: https://api.sq03.shop/api.php/provide/vod/?ac=detail
- 详情URL: https://api.sq03.shop/api.php/provide/vod/?ac=detail

使用方法:
    python video_collector.py                    # 采集全部视频
    python video_collector.py --page 1           # 采集指定页
    python video_collector.py --type 1           # 采集指定分类
    python video_collector.py --keyword "电影"   # 搜索关键词
    python video_collector.py --hours 24         # 采集24小时内更新的

作者: Auto-generated
日期: 2026-01-29
"""

import requests
import json
import time
import argparse
import csv
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

# 默认配置
DEFAULT_API_URL = "https://api.sq03.shop/api.php/provide/vod/"
DEFAULT_TIMEOUT = 30
DEFAULT_DELAY = 1.0


class VideoCollector:
    """视频采集器类"""
    
    def __init__(self, base_url: str = DEFAULT_API_URL, timeout: int = DEFAULT_TIMEOUT):
        """
        初始化采集器
        
        Args:
            base_url: API基础URL
            timeout: 请求超时时间(秒)
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.collected_data: List[Dict] = []
        self.collection_params: Dict[str, Any] = {}  # 记录采集参数
        
    def get_categories(self) -> List[Dict]:
        """
        获取分类列表
        
        Returns:
            分类列表
        """
        try:
            params = {'ac': 'list'}
            response = self.session.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            categories = data.get('class', [])
            print(f"📂 获取到 {len(categories)} 个分类:")
            for cat in categories:
                print(f"   - ID: {cat.get('type_id')}, 名称: {cat.get('type_name')}")
            
            return categories
        except Exception as e:
            print(f"❌ 获取分类失败: {e}")
            return []
    
    def get_video_list(self, page: int = 1, type_id: Optional[int] = None, 
                       keyword: Optional[str] = None, hours: Optional[int] = None) -> Dict:
        """
        获取视频列表
        
        Args:
            page: 页码
            type_id: 分类ID
            keyword: 搜索关键词
            hours: 获取多少小时内更新的视频
            
        Returns:
            包含视频列表和分页信息的字典
        """
        params = {
            'ac': 'detail',  # 获取详细信息
            'pg': page
        }
        
        if type_id:
            params['t'] = type_id
        if keyword:
            params['wd'] = keyword
        if hours:
            params['h'] = hours
            
        try:
            print(f"📡 正在请求第 {page} 页数据...")
            response = self.session.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            total = data.get('total', 0)
            page_count = data.get('pagecount', 1)
            video_list = data.get('list', [])
            
            print(f"✅ 第 {page}/{page_count} 页，获取到 {len(video_list)} 个视频 (总计: {total})")
            
            return {
                'total': total,
                'page': page,
                'page_count': page_count,
                'list': video_list
            }
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return {'total': 0, 'page': page, 'page_count': 0, 'list': []}
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            if 'response' in dir():
                print(f"   响应内容: {response.text[:200]}...")
            return {'total': 0, 'page': page, 'page_count': 0, 'list': []}
    
    def get_video_detail(self, vod_id: int) -> Optional[Dict]:
        """
        获取单个视频的详细信息
        
        Args:
            vod_id: 视频ID
            
        Returns:
            视频详情字典
        """
        params = {
            'ac': 'detail',
            'ids': vod_id
        }
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            video_list = data.get('list', [])
            if video_list:
                return video_list[0]
            return None
        except Exception as e:
            print(f"❌ 获取视频详情失败 (ID: {vod_id}): {e}")
            return None
    
    def collect_all(self, type_id: Optional[int] = None, keyword: Optional[str] = None,
                    hours: Optional[int] = None, max_pages: Optional[int] = None,
                    start_page: int = 1, delay: float = DEFAULT_DELAY) -> List[Dict]:
        """
        采集全部视频
        
        Args:
            type_id: 分类ID筛选
            keyword: 搜索关键词
            hours: 获取多少小时内更新的
            max_pages: 最大采集页数
            start_page: 起始页码
            delay: 请求间隔(秒), 必须为正数
            
        Returns:
            采集到的视频列表
        """
        # 验证delay参数
        if delay <= 0:
            print(f"⚠️ delay必须为正数，使用默认值 {DEFAULT_DELAY} 秒")
            delay = DEFAULT_DELAY
        
        # 记录采集参数
        self.collection_params = {
            'type_id': type_id,
            'keyword': keyword,
            'hours': hours
        }
        print("\n" + "="*60)
        print("🚀 开始视频采集任务")
        print("="*60)
        
        if type_id:
            print(f"📌 分类筛选: ID={type_id}")
        if keyword:
            print(f"🔍 关键词搜索: {keyword}")
        if hours:
            print(f"⏰ 时间范围: {hours}小时内更新")
        
        self.collected_data = []
        current_page = start_page
        
        # 首次请求获取总页数
        first_result = self.get_video_list(
            page=current_page, 
            type_id=type_id, 
            keyword=keyword, 
            hours=hours
        )
        
        if not first_result['list']:
            print("⚠️ 未获取到任何数据")
            return []
        
        self.collected_data.extend(first_result['list'])
        total_pages = first_result['page_count']
        
        if max_pages:
            total_pages = min(total_pages, start_page + max_pages - 1)
        
        print(f"\n📊 总页数: {first_result['page_count']}, 计划采集: {total_pages - start_page + 1} 页")
        
        # 采集剩余页面
        for page in range(start_page + 1, total_pages + 1):
            time.sleep(delay)  # 请求间隔，避免被封
            
            result = self.get_video_list(
                page=page, 
                type_id=type_id, 
                keyword=keyword, 
                hours=hours
            )
            
            if result['list']:
                self.collected_data.extend(result['list'])
            else:
                print(f"⚠️ 第 {page} 页无数据，停止采集")
                break
        
        print(f"\n✅ 采集完成! 共获取 {len(self.collected_data)} 个视频")
        return self.collected_data
    
    def save_to_json(self, filename: Optional[str] = None, indent: int = 2) -> str:
        """
        保存采集数据到JSON文件
        
        Args:
            filename: 文件名(不含扩展名)
            indent: JSON缩进
            
        Returns:
            保存的文件路径
        """
        if not self.collected_data:
            print("⚠️ 没有数据可保存")
            return ""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 包含采集参数信息
            params_str = ""
            if self.collection_params.get('type_id'):
                params_str += f"_t{self.collection_params['type_id']}"
            if self.collection_params.get('keyword'):
                params_str += f"_{self.collection_params['keyword'][:10]}"
            filename = f"videos{params_str}_{timestamp}"
        
        filepath = f"{filename}.json"
        
        # 检查文件是否存在
        if os.path.exists(filepath):
            print(f"⚠️ 文件 {filepath} 已存在，将被覆盖")
        
        output = {
            'collected_at': datetime.now().isoformat(),
            'total_count': len(self.collected_data),
            'source_url': self.base_url,
            'collection_params': self.collection_params,
            'data': self.collected_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=indent)
        
        print(f"💾 数据已保存到: {filepath}")
        return filepath
    
    def save_to_csv(self, filename: Optional[str] = None) -> str:
        """
        保存采集数据到CSV文件
        
        Args:
            filename: 文件名(不含扩展名)
            
        Returns:
            保存的文件路径
        """
        if not self.collected_data:
            print("⚠️ 没有数据可保存")
            return ""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 包含采集参数信息
            params_str = ""
            if self.collection_params.get('type_id'):
                params_str += f"_t{self.collection_params['type_id']}"
            if self.collection_params.get('keyword'):
                params_str += f"_{self.collection_params['keyword'][:10]}"
            filename = f"videos{params_str}_{timestamp}"
        
        filepath = f"{filename}.csv"
        
        # 检查文件是否存在
        if os.path.exists(filepath):
            print(f"⚠️ 文件 {filepath} 已存在，将被覆盖")
        
        # CSV字段
        fieldnames = ['vod_id', 'vod_name', 'type_name', 'vod_time', 'vod_remarks', 'vod_play_url']
        
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for video in self.collected_data:
                row = {
                    'vod_id': video.get('vod_id', ''),
                    'vod_name': video.get('vod_name', ''),
                    'type_name': video.get('type_name', ''),
                    'vod_time': video.get('vod_time', ''),
                    'vod_remarks': video.get('vod_remarks', ''),
                    'vod_play_url': video.get('vod_play_url', '')  # 完整保存播放链接
                }
                writer.writerow(row)
        
        print(f"💾 数据已保存到: {filepath}")
        return filepath
    
    def print_summary(self) -> None:
        """打印采集数据摘要"""
        if not self.collected_data:
            print("⚠️ 没有采集到数据")
            return
        
        print("\n" + "="*60)
        print("📊 采集数据摘要")
        print("="*60)
        print(f"总数量: {len(self.collected_data)}")
        
        # 统计分类
        categories = {}
        for video in self.collected_data:
            type_name = video.get('type_name', '未知')
            categories[type_name] = categories.get(type_name, 0) + 1
        
        print("\n分类统计:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {cat}: {count} 个")
        
        # 显示最新的5个视频
        print("\n最新视频 (前5个):")
        for video in self.collected_data[:5]:
            print(f"  📺 {video.get('vod_name', '未知')} - {video.get('vod_remarks', '')} ({video.get('vod_time', '')})")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='视频采集脚本 - 基于CMS资源站API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python video_collector.py                      # 采集全部视频(仅第1页)
  python video_collector.py --all                # 采集全部页面
  python video_collector.py --page 1 --max 5     # 从第1页开始,最多采集5页
  python video_collector.py --type 1             # 采集分类ID为1的视频
  python video_collector.py --keyword "电影"     # 搜索包含"电影"的视频
  python video_collector.py --hours 24           # 采集24小时内更新的
  python video_collector.py --categories         # 查看所有分类
        '''
    )
    
    parser.add_argument('--url', type=str, 
                        default='https://api.sq03.shop/api.php/provide/vod/',
                        help='API基础URL')
    parser.add_argument('--page', type=int, default=1,
                        help='起始页码 (默认: 1)')
    parser.add_argument('--max', type=int, default=None,
                        help='最大采集页数')
    parser.add_argument('--all', action='store_true',
                        help='采集全部页面')
    parser.add_argument('--type', type=int, default=None,
                        help='分类ID筛选')
    parser.add_argument('--keyword', type=str, default=None,
                        help='搜索关键词')
    parser.add_argument('--hours', type=int, default=None,
                        help='获取多少小时内更新的视频')
    parser.add_argument('--delay', type=float, default=1.0,
                        help='请求间隔(秒), 默认1秒')
    parser.add_argument('--output', type=str, default=None,
                        help='输出文件名(不含扩展名)')
    parser.add_argument('--format', type=str, choices=['json', 'csv', 'both'],
                        default='json', help='输出格式 (默认: json)')
    parser.add_argument('--categories', action='store_true',
                        help='仅显示分类列表')
    
    args = parser.parse_args()
    
    # 创建采集器
    collector = VideoCollector(base_url=args.url)
    
    print("\n" + "="*60)
    print("🎬 视频采集脚本 v1.0")
    print("="*60)
    print(f"📡 API地址: {args.url}")
    
    # 仅显示分类
    if args.categories:
        collector.get_categories()
        return
    
    # 确定最大页数
    max_pages = args.max
    if not args.all and max_pages is None:
        max_pages = 1  # 默认只采集1页
    
    # 开始采集
    collector.collect_all(
        type_id=args.type,
        keyword=args.keyword,
        hours=args.hours,
        max_pages=max_pages,
        start_page=args.page,
        delay=args.delay
    )
    
    # 打印摘要
    collector.print_summary()
    
    # 保存数据
    if collector.collected_data:
        if args.format in ['json', 'both']:
            collector.save_to_json(args.output)
        if args.format in ['csv', 'both']:
            collector.save_to_csv(args.output)


if __name__ == '__main__':
    main()
