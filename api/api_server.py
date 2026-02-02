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
from functools import wraps
from contextlib import contextmanager
from typing import Any, Callable, cast, Dict, Generator, List, Optional, Tuple, TypeVar

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
