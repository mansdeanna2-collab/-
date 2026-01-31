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
from functools import wraps
from contextlib import contextmanager
from typing import Any, Callable, cast, Dict, Generator, List, Optional, Tuple, TypeVar

from flask import Flask, jsonify, request, Response
from flask_cors import CORS

# 导入视频数据库模块 (在同一目录或父目录中)
try:
    from video_database import VideoDatabase
except ImportError:
    # 如果同目录找不到,尝试父目录 (本地开发环境)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    limit: int = min(int(request.args.get('limit', 20)), 100)
    offset: int = int(request.args.get('offset', 0))
    
    with get_db() as db:
        videos: List[Dict[str, Any]] = db.get_all_videos(limit=limit, offset=offset)
    
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
    
    limit: int = min(int(request.args.get('limit', 20)), 100)
    offset: int = max(int(request.args.get('offset', 0)), 0)
    
    with get_db() as db:
        videos: List[Dict[str, Any]] = db.search_videos(keyword, limit=limit, offset=offset)
    
    return api_response(data=videos)


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
    
    limit: int = min(int(request.args.get('limit', 20)), 100)
    offset: int = max(int(request.args.get('offset', 0)), 0)
    
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
    limit: int = min(int(request.args.get('limit', 10)), 50)
    
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
    
    print("\n" + "="*60)
    print("🚀 视频API服务器 (Video API Server)")
    print("="*60)
    print(f"📡 地址 (Address): http://{args.host}:{args.port}")
    print(f"🔧 模式 (Mode): {'生产 (Production)' if args.production else '开发 (Development)'}")
    print(f"📦 数据库 (Database): {'SQLite' if args.sqlite else 'MySQL'}")
    print("="*60 + "\n")
    
    app.run(
        host=args.host,
        port=args.port,
        debug=debug,
        threaded=True
    )
