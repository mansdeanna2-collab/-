#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频API服务器 (Video API Server)
================================
基于Flask的REST API服务器，连接视频数据库

启动方式:
    python api_server.py                    # 开发模式
    python api_server.py --production       # 生产模式

API端点:
    GET  /api/videos                - 获取视频列表 (支持分页)
    GET  /api/videos/<id>           - 获取单个视频
    GET  /api/videos/search         - 搜索视频
    GET  /api/videos/category       - 按分类获取视频
    GET  /api/videos/top            - 获取热门视频
    POST /api/videos/<id>/play      - 增加播放次数
    GET  /api/categories            - 获取所有分类
    GET  /api/statistics            - 获取统计信息

作者: Auto-generated
日期: 2026-01-30
"""
from __future__ import annotations

import os
import sys
import logging
import time
from datetime import datetime
from functools import wraps
from contextlib import contextmanager
from typing import Any, Callable, cast, Dict, Generator, List, Optional, Tuple, TypeVar

import requests as http_requests
from flask import Flask, jsonify, request, Response, g
from flask_cors import CORS

# 导入视频数据库模块 (在同一目录或父目录中)
try:
    from video_database import VideoDatabase
except ImportError:
    # 如果同目录找不到,尝试父目录 (本地开发环境)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, repo_root)
    tools_path = os.path.join(repo_root, "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    try:
        from video_database import VideoDatabase
    except ImportError:
        print("错误: 无法导入 video_database 模块")
        print("请确保 video_database.py 在正确的位置")
        sys.exit(1)

# Type variable for decorated functions
F = TypeVar('F', bound=Callable[..., Any])

# 配置日志 (Configure logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger: logging.Logger = logging.getLogger(__name__)

# 创建Flask应用 (Create Flask app)
app: Flask = Flask(__name__)

# 配置CORS - 允许跨域请求
# 在部署的app或H5中，origin可能来自多种来源（Capacitor、WebView、不同域名等）
# 因此需要允许所有来源以确保图片和API请求能正常加载
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})


# 请求计时中间件 (Request timing middleware)
@app.before_request
def before_request() -> None:
    """记录请求开始时间 (Record request start time)"""
    g.start_time = time.time()


@app.after_request
def after_request(response: Response) -> Response:
    """记录请求处理时间 (Log request processing time)"""
    if hasattr(g, 'start_time'):
        elapsed = time.time() - g.start_time
        # 记录慢请求 (超过1秒) (Log slow requests over 1 second)
        if elapsed > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.path} "
                f"took {elapsed:.3f}s"
            )
    return response


@contextmanager
def get_db() -> Generator[VideoDatabase, None, None]:
    """
    获取数据库连接 (Get database connection)
    每个请求创建新连接，解决SQLite线程问题
    Creates a new connection per request to solve SQLite threading issues
    """
    use_mysql: bool = os.environ.get('USE_MYSQL', 'true').lower() == 'true'
    db: VideoDatabase = VideoDatabase(use_mysql=use_mysql, verbose=False)
    try:
        yield db
    finally:
        db.close()


def api_response(
    data: Optional[Any] = None,
    message: str = "success",
    code: int = 200
) -> Tuple[Response, int]:
    """
    统一API响应格式 (Unified API response format)

    Args:
        data: Response data
        message: Response message
        code: HTTP status code

    Returns:
        Tuple of (JSON response, status code)
    """
    response: Dict[str, Any] = {
        "code": code,
        "message": message,
        "data": data
    }
    return jsonify(response), code


def handle_errors(f: F) -> F:
    """
    错误处理装饰器 (Error handling decorator)
    Wraps route handlers to provide consistent error handling
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Tuple[Response, int]:
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"参数错误 (Parameter error): {e}")
            return api_response(message=str(e), code=400)
        except Exception as e:
            logger.error(f"服务器错误 (Server error): {e}", exc_info=True)
            return api_response(message="服务器内部错误", code=500)
    return cast(F, decorated_function)


# ==================== API路由 (API Routes) ====================

@app.route('/api/health', methods=['GET'])
def health_check() -> Tuple[Response, int]:
    """健康检查端点 (Health check endpoint)"""
    return api_response(data={"status": "healthy"})


@app.route('/api/videos', methods=['GET'])
@handle_errors
def get_videos() -> Tuple[Response, int]:
    """
    获取视频列表 (Get video list)

    Query参数 (Query parameters):
        limit: 返回数量 (默认20, 最大100) / Return count (default 20, max 100)
        offset: 偏移量 (默认0) / Offset (default 0)
    """
    limit: int = max(1, min(int(request.args.get('limit', 20)), 100))
    offset: int = max(0, int(request.args.get('offset', 0)))

    with get_db() as db:
        videos: List[Dict[str, Any]] = db.get_all_videos(limit=limit, offset=offset)

    return api_response(data=videos)


@app.route('/api/videos/search', methods=['GET'])
@handle_errors
def search_videos() -> Tuple[Response, int]:
    """
    搜索视频 (Search videos)

    Query参数 (Query parameters):
        keyword: 搜索关键词 (必需) / Search keyword (required)
        limit: 返回数量 (默认20, 最大100) / Return count (default 20, max 100)
        offset: 偏移量 (默认0) / Offset (default 0)
    """
    keyword: str = request.args.get('keyword', '').strip()
    if not keyword:
        return api_response(message="请提供搜索关键词", code=400)

    limit: int = max(1, min(int(request.args.get('limit', 20)), 100))
    offset: int = max(0, int(request.args.get('offset', 0)))

    with get_db() as db:
        videos: List[Dict[str, Any]] = db.search_videos(keyword, limit=limit, offset=offset)

    return api_response(data=videos)


@app.route('/api/videos/<int:video_id>', methods=['GET'])
@handle_errors
def get_video(video_id: int) -> Tuple[Response, int]:
    """获取单个视频详情 (Get single video details)"""
    with get_db() as db:
        video: Optional[Dict[str, Any]] = db.get_video(video_id)

    if video:
        return api_response(data=video)
    else:
        return api_response(message="视频不存在", code=404)


@app.route('/api/videos/category', methods=['GET'])
@handle_errors
def get_videos_by_category() -> Tuple[Response, int]:
    """
    按分类获取视频 (Get videos by category)

    Query参数 (Query parameters):
        category: 分类名称 (必需) / Category name (required)
        limit: 返回数量 (默认20, 最大100) / Return count (default 20, max 100)
        offset: 偏移量 (默认0) / Offset (default 0)
    """
    category: str = request.args.get('category', '').strip()
    if not category:
        return api_response(message="请提供分类名称", code=400)

    limit: int = max(1, min(int(request.args.get('limit', 20)), 100))
    offset: int = max(0, int(request.args.get('offset', 0)))

    with get_db() as db:
        videos: List[Dict[str, Any]] = db.get_videos_by_category(category, limit=limit, offset=offset)

    return api_response(data=videos)


@app.route('/api/videos/top', methods=['GET'])
@handle_errors
def get_top_videos() -> Tuple[Response, int]:
    """
    获取热门视频 (Get top videos by play count)

    Query参数 (Query parameters):
        limit: 返回数量 (默认10) / Return count (default 10)
    """
    limit: int = max(1, min(int(request.args.get('limit', 10)), 50))

    with get_db() as db:
        videos: List[Dict[str, Any]] = db.get_top_videos(limit=limit)

    return api_response(data=videos)


@app.route('/api/videos/<int:video_id>/play', methods=['POST'])
@handle_errors
def update_play_count(video_id: int) -> Tuple[Response, int]:
    """增加视频播放次数 (Increment video play count)"""
    with get_db() as db:
        success: bool = db.update_play_count(video_id)

    if success:
        return api_response(message="播放次数已更新")
    else:
        return api_response(message="视频不存在", code=404)


@app.route('/api/videos/random', methods=['GET'])
@handle_errors
def get_random_videos() -> Tuple[Response, int]:
    """
    获取随机视频推荐 (Get random video recommendations)

    Query参数 (Query parameters):
        limit: 返回数量 (默认10, 最大50) / Return count (default 10, max 50)
        category: 可选分类过滤 / Optional category filter
    """
    limit: int = max(1, min(int(request.args.get('limit', 10)), 50))
    category: str = request.args.get('category', '').strip()

    with get_db() as db:
        if category:
            videos: List[Dict[str, Any]] = db.get_videos_by_category(
                category, limit=limit * 2, offset=0
            )
        else:
            videos = db.get_all_videos(limit=limit * 2, offset=0)

    # Shuffle and return random subset
    import random
    random.shuffle(videos)
    return api_response(data=videos[:limit])


@app.route('/api/videos/related/<int:video_id>', methods=['GET'])
@handle_errors
def get_related_videos(video_id: int) -> Tuple[Response, int]:
    """
    获取相关视频 (Get related videos based on category)

    Query参数 (Query parameters):
        limit: 返回数量 (默认6, 最大20) / Return count (default 6, max 20)
    """
    limit: int = max(1, min(int(request.args.get('limit', 6)), 20))

    with get_db() as db:
        # Get the current video to find its category
        video: Optional[Dict[str, Any]] = db.get_video(video_id)
        if not video:
            return api_response(message="视频不存在", code=404)

        # Get videos from the same category
        category = video.get('video_category', '')
        if category:
            related: List[Dict[str, Any]] = db.get_videos_by_category(
                category, limit=limit + 1, offset=0
            )
            # Filter out the current video
            related = [v for v in related if v.get('video_id') != video_id][:limit]
        else:
            related = []

    return api_response(data=related)


@app.route('/api/categories', methods=['GET'])
@handle_errors
def get_categories() -> Tuple[Response, int]:
    """获取所有视频分类 (Get all video categories)"""
    with get_db() as db:
        categories: List[Dict[str, Any]] = db.get_categories()

    return api_response(data=categories)


@app.route('/api/statistics', methods=['GET'])
@handle_errors
def get_statistics() -> Tuple[Response, int]:
    """获取数据库统计信息 (Get database statistics)"""
    with get_db() as db:
        stats: Dict[str, Any] = db.get_statistics()

    return api_response(data=stats)


# ==================== 导航分类管理API (Navigation Categories API) ====================

# 默认导航分类配置 (Default navigation categories)
DEFAULT_NAV_CATEGORIES: List[Dict[str, Any]] = [
    {
        'key': 'recommend',
        'label': '推荐',
        'subcategories': ['热门推荐', '动作电影', '喜剧片', '科幻大片', '爱情电影', '恐怖惊悚', '纪录片', '动漫']
    },
    {
        'key': 'japan',
        'label': '日本',
        'subcategories': ['日本AV', '无码高清', '制服诱惑', '人妻系列', '女优精选', '素人企划', '动漫资源', '经典作品']
    },
    {
        'key': 'domestic',
        'label': '国产',
        'subcategories': ['国产自拍', '网红主播', '偷拍私拍', '情侣实录', '素人投稿', '制服诱惑', '熟女人妻', '精品短视频']
    },
    {
        'key': 'anime',
        'label': '动漫',
        'subcategories': ['里番动漫', '3D动画', '同人作品', '触手系列', 'NTR剧情', '巨乳萝莉', '校园爱情', '经典番剧']
    },
    {
        'key': 'welfare',
        'label': '福利',
        'subcategories': ['写真福利', '丝袜美腿', '性感模特', '大尺度写真', '韩国女团', '日本偶像', '网红热舞', 'ASMR']
    }
]


@app.route('/api/nav-categories', methods=['GET'])
@handle_errors
def get_nav_categories() -> Tuple[Response, int]:
    """
    获取导航分类配置 (Get navigation categories)
    如果数据库中没有配置，返回默认配置
    """
    with get_db() as db:
        categories: List[Dict[str, Any]] = db.get_nav_categories()

    # 如果没有配置，返回默认配置
    if not categories:
        categories = DEFAULT_NAV_CATEGORIES

    return api_response(data=categories)


@app.route('/api/nav-categories', methods=['POST'])
@handle_errors
def save_nav_categories() -> Tuple[Response, int]:
    """
    保存导航分类配置 (Save navigation categories)
    所有用户共享此配置
    """
    data = request.get_json()
    if not data or not isinstance(data, list):
        return api_response(message="请提供有效的分类配置列表", code=400)

    # 验证数据格式
    for cat in data:
        if not isinstance(cat, dict):
            return api_response(message="分类格式无效", code=400)
        if not cat.get('key') or not cat.get('label'):
            return api_response(message="每个分类必须包含 key 和 label", code=400)

    with get_db() as db:
        success: bool = db.save_nav_categories(data)

    if success:
        return api_response(message="导航分类配置已保存")
    else:
        return api_response(message="保存失败", code=500)


@app.route('/api/nav-categories/reset', methods=['POST'])
@handle_errors
def reset_nav_categories() -> Tuple[Response, int]:
    """
    重置导航分类为默认配置 (Reset navigation categories to default)
    """
    with get_db() as db:
        success: bool = db.save_nav_categories(DEFAULT_NAV_CATEGORIES)

    if success:
        return api_response(data=DEFAULT_NAV_CATEGORIES, message="已恢复默认配置")
    else:
        return api_response(message="重置失败", code=500)


# ==================== 视频管理API (Video Management API) ====================

@app.route('/api/admin/category-stats', methods=['GET'])
@handle_errors
def get_category_stats() -> Tuple[Response, int]:
    """
    获取各分类视频统计 (Get video count statistics by category)
    返回每个分类的视频数量
    """
    with get_db() as db:
        stats: List[Dict[str, Any]] = db.get_category_stats()

    return api_response(data=stats)


@app.route('/api/admin/category-videos', methods=['GET'])
@handle_errors
def get_category_videos_admin() -> Tuple[Response, int]:
    """
    获取指定分类的视频列表 (Get videos in a specific category for admin)
    用于后台查看分类内的视频

    Query参数:
        category: 分类名称 (必需)
        limit: 返回数量 (默认50, 最大200)
        offset: 偏移量 (默认0)
    """
    category: str = request.args.get('category', '').strip()
    if not category:
        return api_response(message="请提供分类名称", code=400)

    limit: int = max(1, min(int(request.args.get('limit', 50)), 200))
    offset: int = max(0, int(request.args.get('offset', 0)))

    with get_db() as db:
        videos: List[Dict[str, Any]] = db.get_videos_by_category(category, limit=limit, offset=offset)

    return api_response(data=videos)


@app.route('/api/admin/duplicates', methods=['GET'])
@handle_errors
def get_duplicate_videos() -> Tuple[Response, int]:
    """
    检测重复视频 (Detect duplicate videos)
    根据标题或图片URL查找重复的视频

    Query参数:
        type: 检测类型 ('title' 或 'image', 默认 'title')
    """
    check_type: str = request.args.get('type', 'title').strip().lower()
    if check_type not in ['title', 'image']:
        check_type = 'title'

    with get_db() as db:
        duplicates: List[Dict[str, Any]] = db.find_duplicates(check_type)

    return api_response(data=duplicates)


@app.route('/api/admin/videos', methods=['POST'])
@handle_errors
def add_video() -> Tuple[Response, int]:
    """
    添加新视频 (Add a new video)
    """
    data = request.get_json()
    if not data:
        return api_response(message="请提供视频数据", code=400)

    required_fields = ['video_url', 'video_title']
    for field in required_fields:
        if not data.get(field):
            return api_response(message=f"缺少必需字段: {field}", code=400)

    with get_db() as db:
        # Generate a new video_id if not provided
        if not data.get('video_id'):
            data['video_id'] = db.get_next_video_id()

        success: bool = db.insert_video(data)

    if success:
        return api_response(message="视频添加成功", data={'video_id': data['video_id']})
    else:
        return api_response(message="添加失败", code=500)


@app.route('/api/admin/videos/<int:video_id>', methods=['DELETE'])
@handle_errors
def delete_video(video_id: int) -> Tuple[Response, int]:
    """
    删除视频 (Delete a video)
    """
    with get_db() as db:
        success: bool = db.delete_video(video_id)

    if success:
        return api_response(message="视频删除成功")
    else:
        return api_response(message="视频不存在或删除失败", code=404)


@app.route('/api/admin/collection-status', methods=['GET'])
@handle_errors
def get_collection_status() -> Tuple[Response, int]:
    """
    获取采集状态 (Get collection status)
    检查是否有新视频可以采集，以及已采集的视频统计

    Query参数:
        hours: 检查多少小时内的更新 (默认24)
    """
    hours: int = max(1, min(int(request.args.get('hours', 24)), 168))  # Max 7 days

    with get_db() as db:
        status: Dict[str, Any] = db.get_collection_status(hours)

    return api_response(data=status)


@app.route('/api/admin/check-new-videos', methods=['POST'])
@handle_errors
def check_new_videos() -> Tuple[Response, int]:
    """
    检查新视频 (Check for new videos from source)
    从采集源检查是否有新的视频可以采集
    """
    # 采集API配置 - 使用环境变量或默认值
    api_url = os.environ.get('COLLECTOR_API_URL', 'https://api.sq03.shop/api.php/provide/vod/')
    hours: int = max(1, min(int(request.args.get('hours', 24)), 168))

    try:
        # 请求最近更新的视频 (使用较短超时避免阻塞)
        params = {'ac': 'detail', 'h': hours, 'pg': 1}
        response = http_requests.get(api_url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        total_available = data.get('total', 0)
        source_videos = data.get('list', [])

        # 检查哪些视频已经在数据库中
        with get_db() as db:
            existing_ids = set()
            for video in source_videos:
                vod_id = video.get('vod_id')
                if vod_id and db.get_video(vod_id):
                    existing_ids.add(vod_id)

            new_videos = [v for v in source_videos if v.get('vod_id') not in existing_ids]
            already_collected = [v for v in source_videos if v.get('vod_id') in existing_ids]

        result = {
            'total_available': total_available,
            'checked_count': len(source_videos),
            'new_count': len(new_videos),
            'already_collected_count': len(already_collected),
            'new_videos': [{
                'vod_id': v.get('vod_id'),
                'vod_name': v.get('vod_name'),
                'vod_pic': v.get('vod_pic'),
                'type_name': v.get('type_name'),
                'vod_time': v.get('vod_time')
            } for v in new_videos[:20]],  # Only return first 20
            'checked_at': datetime.now().isoformat()
        }

        return api_response(data=result)

    except http_requests.RequestException as e:
        logger.error(f"检查新视频失败: {e}")
        return api_response(message=f"检查失败: {str(e)}", code=500)
    except Exception as e:
        logger.error(f"检查新视频失败: {e}")
        return api_response(message="检查失败", code=500)


@app.route('/api/admin/collect-videos', methods=['POST'])
@handle_errors
def collect_videos() -> Tuple[Response, int]:
    """
    后台采集视频 (Background video collection)
    从采集源采集视频并保存到数据库

    Request Body:
        type_id: 分类ID筛选 (可选)
        hours: 获取多少小时内更新的视频 (可选, 默认24)
        max_pages: 最大采集页数 (可选, 默认1)
        skip_duplicates: 是否跳过已存在的视频 (可选, 默认true)
    """
    # 获取请求参数
    data = request.get_json() or {}
    type_id = data.get('type_id')
    hours: int = max(1, min(int(data.get('hours', 24)), 168))
    max_pages: int = max(1, min(int(data.get('max_pages', 1)), 50))
    skip_duplicates: bool = data.get('skip_duplicates', True)

    # 采集API配置
    api_url = os.environ.get('COLLECTOR_API_URL', 'https://api.sq03.shop/api.php/provide/vod/')

    # 域名替换配置 (与video_collector.py一致)
    domain_replacements = {
        'vip.sq03.shop': 'd34zpx35a2d8cd.cloudfront.net'
    }

    def process_play_url(play_url: str) -> str:
        """处理播放URL，替换指定域名"""
        if not play_url:
            return play_url
        for old_domain, new_domain in domain_replacements.items():
            play_url = play_url.replace(old_domain, new_domain)
        return play_url

    def is_valid_video(video: dict) -> bool:
        """检查视频是否有效（图片URL不能以.txt结尾）"""
        vod_pic = video.get('vod_pic', '')
        if vod_pic and vod_pic.lower().endswith('.txt'):
            return False
        return True

    collected_videos = []
    skipped_count = 0
    duplicate_count = 0
    pages_processed = 0

    try:
        with get_db() as db:
            # 遍历采集页面
            for page in range(1, max_pages + 1):
                params = {'ac': 'detail', 'pg': page}
                if type_id:
                    params['t'] = type_id
                if hours:
                    params['h'] = hours

                response = http_requests.get(api_url, params=params, timeout=30)
                response.raise_for_status()
                page_data = response.json()

                source_videos = page_data.get('list', [])
                if not source_videos:
                    break
                
                pages_processed += 1

                for video in source_videos:
                    # 验证视频有效性
                    if not is_valid_video(video):
                        skipped_count += 1
                        continue

                    vod_id = video.get('vod_id')
                    if not vod_id:
                        skipped_count += 1
                        continue

                    # 检查重复
                    if skip_duplicates and db.get_video(vod_id):
                        duplicate_count += 1
                        continue

                    # 处理播放URL
                    vod_play_url = process_play_url(video.get('vod_play_url', ''))

                    # 映射字段并插入数据库
                    db_video = {
                        'video_id': vod_id,
                        'video_url': vod_play_url,
                        'video_image': video.get('vod_pic', ''),
                        'video_title': video.get('vod_name', ''),
                        'video_category': video.get('type_name', ''),
                        'play_count': video.get('vod_hits', 0),
                        'upload_time': video.get('vod_time', ''),
                        'video_duration': video.get('vod_duration', video.get('vod_remarks', '')),
                        'video_coins': 0
                    }

                    if db.insert_video(db_video):
                        collected_videos.append({
                            'video_id': vod_id,
                            'video_title': video.get('vod_name', ''),
                            'video_category': video.get('type_name', '')
                        })

        result = {
            'collected_count': len(collected_videos),
            'skipped_count': skipped_count,
            'duplicate_count': duplicate_count,
            'pages_processed': pages_processed,
            'type_id': type_id,
            'hours': hours,
            'collected_at': datetime.now().isoformat(),
            'collected_videos': collected_videos[:50]  # Return first 50 for preview
        }

        if len(collected_videos) > 0:
            return api_response(data=result, message=f"成功采集 {len(collected_videos)} 个视频")
        else:
            return api_response(data=result, message="没有新视频可采集")

    except http_requests.RequestException as e:
        logger.error(f"采集视频失败: {e}")
        return api_response(message=f"采集失败: {str(e)}", code=500)
    except Exception as e:
        logger.error(f"采集视频失败: {e}")
        return api_response(message="采集失败", code=500)


@app.route('/api/admin/get-source-categories', methods=['GET'])
@handle_errors
def get_source_categories() -> Tuple[Response, int]:
    """
    获取采集源分类列表 (Get source categories)
    从采集源API获取可用的视频分类
    """
    api_url = os.environ.get('COLLECTOR_API_URL', 'https://api.sq03.shop/api.php/provide/vod/')

    try:
        params = {'ac': 'list'}
        response = http_requests.get(api_url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        categories = data.get('class', [])
        return api_response(data=categories)

    except http_requests.RequestException as e:
        logger.error(f"获取分类失败: {e}")
        return api_response(message=f"获取分类失败: {str(e)}", code=500)
    except Exception as e:
        logger.error(f"获取分类失败: {e}")
        return api_response(message="获取分类失败", code=500)


# ==================== 错误处理 (Error Handlers) ====================

@app.errorhandler(404)
def not_found(e: Exception) -> Tuple[Response, int]:
    """404 错误处理 (404 error handler)"""
    return api_response(message="接口不存在", code=404)


@app.errorhandler(405)
def method_not_allowed(e: Exception) -> Tuple[Response, int]:
    """405 错误处理 (405 error handler)"""
    return api_response(message="方法不允许", code=405)


@app.errorhandler(500)
def internal_error(e: Exception) -> Tuple[Response, int]:
    """500 错误处理 (500 error handler)"""
    return api_response(message="服务器内部错误", code=500)


# ==================== 主程序入口 (Main Entry Point) ====================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='视频API服务器 (Video API Server)')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='监听地址 / Listen address (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000,
                        help='监听端口 / Listen port (默认: 5000)')
    parser.add_argument('--production', action='store_true',
                        help='生产模式 / Production mode (关闭调试)')
    parser.add_argument('--sqlite', action='store_true',
                        help='使用SQLite而非MySQL / Use SQLite instead of MySQL')

    args = parser.parse_args()

    # 设置环境变量 (Set environment variables)
    if args.sqlite:
        os.environ['USE_MYSQL'] = 'false'

    debug: bool = not args.production

    print("\n" + "=" * 60)
    print("🚀 视频API服务器 (Video API Server)")
    print("=" * 60)
    print(f"📡 地址 (Address): http://{args.host}:{args.port}")
    print(f"🔧 模式 (Mode): {'生产 (Production)' if args.production else '开发 (Development)'}")
    print(f"📦 数据库 (Database): {'SQLite' if args.sqlite else 'MySQL'}")
    print("=" * 60 + "\n")

    app.run(
        host=args.host,
        port=args.port,
        debug=debug,
        threaded=True
    )
