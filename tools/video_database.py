#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频数据库模块 (Video Database Module)
======================================
基于MySQL的视频信息存储系统

数据表结构:
- video_id: 视频ID (主键)
- video_url: 视频链接
- video_image: 视频图片/封面
- video_title: 视频标题
- video_category: 视频分类
- play_count: 播放数
- upload_time: 上传时间
- video_duration: 视频时长
- video_coins: 视频金币

MySQL连接配置通过环境变量设置:
- MYSQL_HOST: 数据库主机
- MYSQL_PORT: 数据库端口
- MYSQL_DATABASE: 数据库名
- MYSQL_USER: 用户名
- MYSQL_PASSWORD: 密码

SQLite配置:
- SQLITE_DB_PATH: SQLite数据库文件路径 (默认: /app/data/videos.db)

使用方法:
    from video_database import VideoDatabase

    db = VideoDatabase()
    db.insert_video({
        'video_id': 1,
        'video_url': 'https://example.com/video.mp4',
        'video_image': 'https://example.com/cover.jpg',
        'video_title': '示例视频',
        'video_category': '电影',
        'play_count': 1000,
        'upload_time': '2026-01-30 10:00:00',
        'video_duration': '01:30:00',
        'video_coins': 0
    })

作者: Auto-generated
日期: 2026-01-30
"""

import os
import re
import json
import logging
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any

# 配置日志
logger = logging.getLogger(__name__)

# MySQL连接配置 - 从环境变量获取
MYSQL_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'port': int(os.environ.get('MYSQL_PORT', '3306')),
    'database': os.environ.get('MYSQL_DATABASE', 'videos'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'charset': 'utf8mb4'
}

# 尝试导入MySQL连接器
try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    logger.warning("pymysql 未安装，将使用SQLite作为备用数据库")


class VideoDatabase:
    """
    视频数据库管理类

    支持MySQL和SQLite两种数据库后端。
    注意：建议使用上下文管理器 (with语句) 来确保数据库连接正确关闭，
    或手动调用 close() 方法。
    """

    @staticmethod
    def _get_default_db_path():
        """
        获取默认数据库路径

        优先级:
        1. SQLITE_DB_PATH 环境变量 (如果设置且非空)
        2. /app/data/videos.db (Docker环境，当目录存在时)
        3. data/videos.db (本地开发)
        """
        env_path = os.environ.get('SQLITE_DB_PATH', '').strip()
        if env_path:
            return env_path
        # Docker环境优先使用绝对路径
        if os.path.isdir('/app/data'):
            return '/app/data/videos.db'
        # 本地开发使用相对路径
        return 'data/videos.db'

    def __init__(self, use_mysql: bool = True, db_path: Optional[str] = None,
                 mysql_config: Optional[Dict[str, Any]] = None, verbose: bool = True):
        """
        初始化数据库连接

        Args:
            use_mysql: 是否使用MySQL，默认True。如果pymysql未安装，自动降级到SQLite
            db_path: SQLite数据库文件路径。默认路径取决于环境:
                     - SQLITE_DB_PATH环境变量 (如果设置)
                     - Docker环境: /app/data/videos.db
                     - 本地开发: data/videos.db
            mysql_config: MySQL连接配置，默认使用全局配置
            verbose: 是否输出日志信息，默认True
        """
        self.db_path = db_path or self._get_default_db_path()
        self.verbose = verbose
        self.connection = None
        self.use_mysql = use_mysql and MYSQL_AVAILABLE
        self.mysql_config = mysql_config or MYSQL_CONFIG
        self._init_database()

    def _init_database(self) -> None:
        """初始化数据库，创建表结构"""
        if self.use_mysql:
            self._init_mysql()
        else:
            self._init_sqlite()

    def _init_mysql(self) -> None:
        """初始化MySQL数据库"""
        try:
            self.connection = pymysql.connect(
                host=self.mysql_config['host'],
                port=self.mysql_config['port'],
                user=self.mysql_config['user'],
                password=self.mysql_config['password'],
                database=self.mysql_config['database'],
                charset=self.mysql_config.get('charset', 'utf8mb4'),
                cursorclass=pymysql.cursors.DictCursor
            )

            cursor = self.connection.cursor()

            # 创建视频表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    video_id INT PRIMARY KEY,
                    video_url TEXT NOT NULL,
                    video_image TEXT,
                    video_title VARCHAR(500) NOT NULL,
                    video_category VARCHAR(100),
                    play_count INT DEFAULT 0,
                    upload_time VARCHAR(50),
                    video_duration VARCHAR(50),
                    video_coins INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            ''')

            # 创建索引以提高查询效率
            try:
                cursor.execute('CREATE INDEX idx_video_category ON videos(video_category)')
            except pymysql.err.OperationalError:
                pass  # 索引已存在

            try:
                cursor.execute('CREATE INDEX idx_video_upload_time ON videos(upload_time)')
            except pymysql.err.OperationalError:
                pass

            try:
                cursor.execute('CREATE INDEX idx_video_play_count ON videos(play_count)')
            except pymysql.err.OperationalError:
                pass

            self.connection.commit()
            self._log(f"✅ MySQL数据库初始化完成: {self.mysql_config['database']}")
        except Exception as e:
            logger.error(f"MySQL连接失败: {e}")
            self._log(f"⚠️ MySQL连接失败，降级到SQLite: {e}")
            self.use_mysql = False
            self._init_sqlite()

    def _init_sqlite(self) -> None:
        """初始化SQLite数据库"""
        # 确保父目录存在
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            self._log(f"📂 创建数据库目录: {db_dir}")

        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

        cursor = self.connection.cursor()

        # 创建视频表 (使用video_coins代替video_price)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                video_id INTEGER PRIMARY KEY,
                video_url TEXT NOT NULL,
                video_image TEXT,
                video_title TEXT NOT NULL,
                video_category TEXT,
                play_count INTEGER DEFAULT 0,
                upload_time TEXT,
                video_duration TEXT,
                video_coins INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建索引以提高查询效率
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_video_category
            ON videos(video_category)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_video_upload_time
            ON videos(upload_time)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_video_play_count
            ON videos(play_count)
        ''')

        # 创建导航分类配置表 (Create nav_categories table for global admin settings)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nav_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_key TEXT UNIQUE NOT NULL,
                label TEXT NOT NULL,
                subcategories TEXT,
                sort_order INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.connection.commit()
        self._log(f"✅ 数据库初始化完成: {self.db_path}")

    def _log(self, message: str) -> None:
        """输出日志信息"""
        if self.verbose:
            print(message)
        logger.info(message)

    def insert_video(self, video_data: Dict[str, Any]) -> bool:
        """
        插入单个视频记录

        Args:
            video_data: 视频数据字典，包含以下字段:
                - video_id: 视频ID (必需)
                - video_url: 视频链接 (必需)
                - video_image: 视频图片
                - video_title: 视频标题 (必需)
                - video_category: 视频分类
                - play_count: 播放数
                - upload_time: 上传时间
                - video_duration: 视频时长
                - video_coins: 视频金币

        Returns:
            插入成功返回True，失败返回False
        """
        required_fields = ['video_id', 'video_url', 'video_title']
        for field in required_fields:
            if field not in video_data or video_data[field] is None:
                self._log(f"❌ 缺少必需字段: {field}")
                return False

        try:
            cursor = self.connection.cursor()

            if self.use_mysql:
                # MySQL使用 REPLACE INTO
                cursor.execute('''
                    REPLACE INTO videos
                    (video_id, video_url, video_image, video_title, video_category,
                     play_count, upload_time, video_duration, video_coins)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    video_data.get('video_id'),
                    video_data.get('video_url'),
                    video_data.get('video_image', ''),
                    video_data.get('video_title'),
                    video_data.get('video_category', ''),
                    video_data.get('play_count', 0),
                    video_data.get('upload_time', ''),
                    video_data.get('video_duration', ''),
                    video_data.get('video_coins', 0)
                ))
            else:
                # SQLite使用 INSERT OR REPLACE
                cursor.execute('''
                    INSERT OR REPLACE INTO videos
                    (video_id, video_url, video_image, video_title, video_category,
                     play_count, upload_time, video_duration, video_coins, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    video_data.get('video_id'),
                    video_data.get('video_url'),
                    video_data.get('video_image', ''),
                    video_data.get('video_title'),
                    video_data.get('video_category', ''),
                    video_data.get('play_count', 0),
                    video_data.get('upload_time', ''),
                    video_data.get('video_duration', ''),
                    video_data.get('video_coins', 0),
                    datetime.now().isoformat()
                ))

            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"插入视频失败: {e}")
            self._log(f"❌ 插入视频失败: {e}")
            return False

    def insert_videos(self, videos: List[Dict[str, Any]]) -> int:
        """
        批量插入视频记录

        Args:
            videos: 视频数据列表

        Returns:
            成功插入的视频数量
        """
        success_count = 0
        for video in videos:
            if self.insert_video(video):
                success_count += 1

        self._log(f"✅ 批量插入完成: 成功 {success_count}/{len(videos)} 个")
        return success_count

    def get_video(self, video_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取视频信息

        Args:
            video_id: 视频ID

        Returns:
            视频数据字典，如果不存在返回None
        """
        cursor = self.connection.cursor()
        placeholder = '%s' if self.use_mysql else '?'
        cursor.execute(f'SELECT * FROM videos WHERE video_id = {placeholder}', (video_id,))
        row = cursor.fetchone()

        if row:
            return dict(row) if isinstance(row, dict) else dict(row)
        return None

    def get_all_videos(self, limit: Optional[int] = None,
                       offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取所有视频

        Args:
            limit: 限制返回数量
            offset: 偏移量

        Returns:
            视频列表
        """
        cursor = self.connection.cursor()
        placeholder = '%s' if self.use_mysql else '?'

        if limit:
            cursor.execute(
                f'SELECT * FROM videos ORDER BY upload_time DESC LIMIT {placeholder} OFFSET {placeholder}',
                (limit, offset)
            )
        else:
            cursor.execute('SELECT * FROM videos ORDER BY upload_time DESC')

        rows = cursor.fetchall()
        return [dict(row) if isinstance(row, dict) else dict(row) for row in rows]

    def get_videos_by_category(self, category: str,
                               limit: Optional[int] = None,
                               offset: int = 0) -> List[Dict[str, Any]]:
        """
        按分类获取视频

        Args:
            category: 视频分类
            limit: 限制返回数量
            offset: 偏移量

        Returns:
            视频列表
        """
        cursor = self.connection.cursor()
        placeholder = '%s' if self.use_mysql else '?'

        if limit:
            cursor.execute(
                f'SELECT * FROM videos WHERE video_category = {placeholder} ORDER BY upload_time DESC LIMIT {placeholder} OFFSET {placeholder}',
                (category, limit, offset)
            )
        else:
            cursor.execute(
                f'SELECT * FROM videos WHERE video_category = {placeholder} ORDER BY upload_time DESC',
                (category,)
            )

        rows = cursor.fetchall()
        return [dict(row) if isinstance(row, dict) else dict(row) for row in rows]

    def search_videos(self, keyword: str,
                      limit: Optional[int] = None,
                      offset: int = 0) -> List[Dict[str, Any]]:
        """
        搜索视频标题

        Args:
            keyword: 搜索关键词
            limit: 限制返回数量
            offset: 偏移量

        Returns:
            匹配的视频列表
        """
        cursor = self.connection.cursor()
        search_pattern = f"%{keyword}%"
        placeholder = '%s' if self.use_mysql else '?'

        if limit:
            cursor.execute(
                f'SELECT * FROM videos WHERE video_title LIKE {placeholder} ORDER BY play_count DESC LIMIT {placeholder} OFFSET {placeholder}',
                (search_pattern, limit, offset)
            )
        else:
            cursor.execute(
                f'SELECT * FROM videos WHERE video_title LIKE {placeholder} ORDER BY play_count DESC',
                (search_pattern,)
            )

        rows = cursor.fetchall()
        return [dict(row) if isinstance(row, dict) else dict(row) for row in rows]

    def get_top_videos(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取播放量最高的视频

        Args:
            limit: 返回数量

        Returns:
            视频列表
        """
        cursor = self.connection.cursor()
        placeholder = '%s' if self.use_mysql else '?'
        cursor.execute(
            f'SELECT * FROM videos ORDER BY play_count DESC LIMIT {placeholder}',
            (limit,)
        )
        rows = cursor.fetchall()
        return [dict(row) if isinstance(row, dict) else dict(row) for row in rows]

    def update_video(self, video_id: int,
                     updates: Dict[str, Any]) -> bool:
        """
        更新视频信息

        Args:
            video_id: 视频ID
            updates: 要更新的字段和值

        Returns:
            更新成功返回True，失败返回False
        """
        if not updates:
            return False

        # 构建更新SQL
        # 注意：字段名来自 allowed_fields 白名单，防止SQL注入
        allowed_fields = [
            'video_url', 'video_image', 'video_title', 'video_category',
            'play_count', 'upload_time', 'video_duration', 'video_coins'
        ]

        placeholder = '%s' if self.use_mysql else '?'
        set_clauses = []
        values = []

        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = {placeholder}")
                values.append(value)

        if not set_clauses:
            return False

        if not self.use_mysql:
            set_clauses.append(f"updated_at = {placeholder}")
            values.append(datetime.now().isoformat())

        values.append(video_id)

        try:
            cursor = self.connection.cursor()
            sql = f"UPDATE videos SET {', '.join(set_clauses)} WHERE video_id = {placeholder}"
            cursor.execute(sql, values)
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"更新视频失败: {e}")
            self._log(f"❌ 更新视频失败: {e}")
            return False

    def update_play_count(self, video_id: int,
                          increment: int = 1) -> bool:
        """
        增加视频播放数

        Args:
            video_id: 视频ID
            increment: 增加的数量，默认为1

        Returns:
            更新成功返回True
        """
        try:
            cursor = self.connection.cursor()
            placeholder = '%s' if self.use_mysql else '?'

            if self.use_mysql:
                cursor.execute(
                    f'UPDATE videos SET play_count = play_count + {placeholder} WHERE video_id = {placeholder}',
                    (increment, video_id)
                )
            else:
                cursor.execute(
                    f'UPDATE videos SET play_count = play_count + {placeholder}, updated_at = {placeholder} WHERE video_id = {placeholder}',
                    (increment, datetime.now().isoformat(), video_id)
                )
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"更新播放数失败: {e}")
            self._log(f"❌ 更新播放数失败: {e}")
            return False

    def delete_video(self, video_id: int) -> bool:
        """
        删除视频

        Args:
            video_id: 视频ID

        Returns:
            删除成功返回True
        """
        try:
            cursor = self.connection.cursor()
            placeholder = '%s' if self.use_mysql else '?'
            cursor.execute(f'DELETE FROM videos WHERE video_id = {placeholder}', (video_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"删除视频失败: {e}")
            self._log(f"❌ 删除视频失败: {e}")
            return False

    def get_categories(self) -> List[Dict[str, Any]]:
        """
        获取所有分类及其视频数量

        Returns:
            分类列表，包含分类名和视频数量
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT video_category, COUNT(*) as video_count
            FROM videos
            GROUP BY video_category
            ORDER BY video_count DESC
        ''')
        rows = cursor.fetchall()
        return [dict(row) if isinstance(row, dict) else dict(row) for row in rows]

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取数据库统计信息

        Returns:
            统计信息字典
        """
        cursor = self.connection.cursor()

        # 总视频数
        cursor.execute('SELECT COUNT(*) as cnt FROM videos')
        row = cursor.fetchone()
        total_videos = row['cnt'] if isinstance(row, dict) else row[0]

        # 总播放数
        cursor.execute('SELECT COALESCE(SUM(play_count), 0) as total FROM videos')
        row = cursor.fetchone()
        total_plays = row['total'] if isinstance(row, dict) else row[0]

        # 分类数
        cursor.execute('SELECT COUNT(DISTINCT video_category) as cnt FROM videos')
        row = cursor.fetchone()
        category_count = row['cnt'] if isinstance(row, dict) else row[0]

        # 平均播放数
        avg_plays = total_plays / total_videos if total_videos > 0 else 0

        return {
            'total_videos': total_videos,
            'total_plays': total_plays,
            'category_count': category_count,
            'total_categories': category_count,  # Alias for frontend compatibility
            'average_plays': round(avg_plays, 2)
        }

    # ==================== 导航分类管理 (Navigation Categories Management) ====================

    def get_nav_categories(self) -> List[Dict[str, Any]]:
        """
        获取所有导航分类配置 (Get all navigation categories)

        Returns:
            导航分类列表
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT category_key, label, subcategories, sort_order
            FROM nav_categories
            ORDER BY sort_order ASC, id ASC
        ''')
        rows = cursor.fetchall()

        result = []
        for row in rows:
            row_dict = dict(row)
            # Parse subcategories from JSON string
            subcategories_str = row_dict.get('subcategories', '[]')
            try:
                subcategories = json.loads(subcategories_str) if subcategories_str else []
            except (json.JSONDecodeError, TypeError):
                subcategories = []

            result.append({
                'key': row_dict['category_key'],
                'label': row_dict['label'],
                'subcategories': subcategories
            })

        return result

    def save_nav_categories(self, categories: List[Dict[str, Any]]) -> bool:
        """
        保存导航分类配置 (Save navigation categories - replaces all)

        Args:
            categories: 导航分类列表 [{ key, label, subcategories }]

        Returns:
            成功返回True，失败返回False
        """
        try:
            cursor = self.connection.cursor()

            # 删除所有现有分类 (Delete all existing categories)
            cursor.execute('DELETE FROM nav_categories')

            # 插入新的分类 (Insert new categories)
            for i, cat in enumerate(categories):
                subcategories_json = json.dumps(cat.get('subcategories', []), ensure_ascii=False)
                cursor.execute('''
                    INSERT INTO nav_categories (category_key, label, subcategories, sort_order)
                    VALUES (?, ?, ?, ?)
                ''', (cat['key'], cat['label'], subcategories_json, i))

            self.connection.commit()
            self._log(f"✅ 保存了 {len(categories)} 个导航分类")
            return True
        except Exception as e:
            logger.error(f"保存导航分类失败: {e}")
            return False

    # ==================== 视频管理功能 (Video Management Features) ====================

    def get_category_stats(self) -> List[Dict[str, Any]]:
        """
        获取各分类视频统计 (Get video count statistics by category)

        Returns:
            分类统计列表，包含分类名和视频数量
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT video_category, COUNT(*) as video_count
            FROM videos
            WHERE video_category IS NOT NULL AND video_category != ''
            GROUP BY video_category
            ORDER BY video_count DESC
        ''')
        rows = cursor.fetchall()
        return [dict(row) if isinstance(row, dict) else dict(row) for row in rows]

    # SQL expression for normalizing video titles (removing spaces and common separators)
    # Used in find_duplicates to identify similar titles like "海绵宝宝" and "海绵宝 宝"
    TITLE_NORMALIZE_SQL = "REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(video_title, ' ', ''), '　', ''), '-', ''), '_', ''), '.', '')"

    def find_duplicates(self, check_type: str = 'title') -> List[Dict[str, Any]]:
        """
        查找重复视频 (Find duplicate videos by title or image)
        
        对于标题查重，会移除空格和特殊字符进行比较，
        例如 "海绵宝宝" 和 "海绵宝 宝" 会被识别为重复。

        Args:
            check_type: 'title' 按标题查找 (忽略空格), 'image' 按图片URL查找

        Returns:
            重复视频列表，每组包含重复的视频信息
        """
        cursor = self.connection.cursor()

        if check_type == 'title':
            # 查找标题重复的视频 (忽略空格和常见分隔符)
            # 使用 TITLE_NORMALIZE_SQL 移除空格、全角空格、以及常见的分隔符后进行比较
            # 这样 "海绵宝宝" 和 "海绵宝 宝" 会被识别为相同标题
            cursor.execute(f'''
                SELECT 
                    {self.TITLE_NORMALIZE_SQL} as normalized_title,
                    COUNT(*) as duplicate_count
                FROM videos
                WHERE video_title IS NOT NULL AND video_title != ''
                GROUP BY normalized_title
                HAVING COUNT(*) > 1
                ORDER BY duplicate_count DESC
                LIMIT 100
            ''')
            duplicate_groups = cursor.fetchall()

            result = []
            placeholder = '%s' if self.use_mysql else '?'
            
            for group in duplicate_groups:
                group_dict = dict(group) if isinstance(group, dict) else dict(group)
                normalized_title = group_dict['normalized_title']

                # 使用相同的规范化方式查找所有匹配的视频
                cursor.execute(
                    f'''SELECT video_id, video_title, video_image, video_category, upload_time 
                        FROM videos 
                        WHERE {self.TITLE_NORMALIZE_SQL} = {placeholder}''',
                    (normalized_title,)
                )
                videos = cursor.fetchall()
                
                # 使用第一个视频的原始标题作为显示值
                video_list = [dict(v) if isinstance(v, dict) else dict(v) for v in videos]
                display_title = video_list[0]['video_title'] if video_list else normalized_title
                
                result.append({
                    'duplicate_value': display_title,
                    'duplicate_type': 'title',
                    'count': group_dict['duplicate_count'],
                    'videos': video_list
                })

            return result

        else:  # check_type == 'image'
            # 查找图片URL重复的视频
            cursor.execute('''
                SELECT video_image, COUNT(*) as duplicate_count
                FROM videos
                WHERE video_image IS NOT NULL AND video_image != ''
                GROUP BY video_image
                HAVING COUNT(*) > 1
                ORDER BY duplicate_count DESC
                LIMIT 100
            ''')
            duplicate_groups = cursor.fetchall()

            result = []
            for group in duplicate_groups:
                group_dict = dict(group) if isinstance(group, dict) else dict(group)
                image = group_dict['video_image']
                placeholder = '%s' if self.use_mysql else '?'

                cursor.execute(
                    f'SELECT video_id, video_title, video_image, video_category, upload_time FROM videos WHERE video_image = {placeholder}',
                    (image,)
                )
                videos = cursor.fetchall()
                result.append({
                    'duplicate_value': image,
                    'duplicate_type': 'image',
                    'count': group_dict['duplicate_count'],
                    'videos': [dict(v) if isinstance(v, dict) else dict(v) for v in videos]
                })

            return result

    def get_next_video_id(self) -> int:
        """
        获取下一个可用的视频ID (Get next available video ID)
        
        使用时间戳和随机数组合生成唯一ID，避免并发竞争条件

        Returns:
            下一个视频ID (基于时间戳)
        """
        import random
        from datetime import datetime
        
        # 使用时间戳 + 随机数生成唯一ID
        # 格式: YYMMDDHHMM + 4位随机数 = 14位数字
        timestamp = datetime.now().strftime('%y%m%d%H%M')
        random_suffix = random.randint(1000, 9999)
        video_id = int(f"{timestamp}{random_suffix}")
        
        return video_id

    def get_collection_status(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取采集状态统计 (Get collection status statistics)

        Args:
            hours: 统计多少小时内的采集数据

        Returns:
            采集状态统计信息
        """
        cursor = self.connection.cursor()

        # 总视频数
        cursor.execute('SELECT COUNT(*) as cnt FROM videos')
        row = cursor.fetchone()
        total_videos = row['cnt'] if isinstance(row, dict) else row[0]

        # 分类统计
        cursor.execute('''
            SELECT COUNT(DISTINCT video_category) as cnt FROM videos
            WHERE video_category IS NOT NULL AND video_category != ''
        ''')
        row = cursor.fetchone()
        total_categories = row['cnt'] if isinstance(row, dict) else row[0]

        # 最新采集时间 (基于created_at或upload_time)
        cursor.execute('''
            SELECT MAX(created_at) as latest FROM videos
        ''')
        row = cursor.fetchone()
        latest_collection = row['latest'] if isinstance(row, dict) else row[0]

        # 按分类统计视频数量
        category_stats = self.get_category_stats()

        return {
            'total_videos': total_videos,
            'total_categories': total_categories,
            'latest_collection_time': latest_collection,
            'category_breakdown': category_stats[:10],  # Top 10 categories
            'hours_checked': hours
        }

    def close(self) -> None:
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self._log("📁 数据库连接已关闭")

    def __del__(self):
        """析构函数，确保连接被关闭"""
        self.close()

    def __enter__(self):
        """支持with语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时自动关闭连接"""
        self.close()


def import_from_collector(collector_data: List[Dict[str, Any]],
                          db: VideoDatabase) -> int:
    """
    从采集器数据导入到数据库

    Args:
        collector_data: 采集器收集的视频数据列表
        db: 数据库实例

    Returns:
        成功导入的数量
    """
    videos_to_insert = []
    skipped_count = 0

    for video in collector_data:
        # 验证必需字段
        vod_id = video.get('vod_id')
        vod_name = video.get('vod_name', '')
        vod_play_url = video.get('vod_play_url', '')

        if not vod_id or not vod_name:
            skipped_count += 1
            logger.warning(f"跳过无效视频记录: 缺少必需字段 (vod_id={vod_id}, vod_name={vod_name})")
            continue

        # 映射采集器字段到数据库字段
        db_video = {
            'video_id': vod_id,
            'video_url': vod_play_url,
            'video_image': video.get('vod_pic', ''),
            'video_title': vod_name,
            'video_category': video.get('type_name', ''),
            'play_count': video.get('vod_hits', 0),
            'upload_time': video.get('vod_time', ''),
            'video_duration': video.get('vod_duration', video.get('vod_remarks', '')),
            'video_coins': 0  # 默认金币为0
        }
        videos_to_insert.append(db_video)

    if skipped_count > 0:
        logger.info(f"跳过 {skipped_count} 个无效视频记录")

    return db.insert_videos(videos_to_insert)


def parse_spjs_file(file_path: str) -> List[Dict[str, Any]]:
    """
    解析sp.js文件，提取视频数据

    sp.js文件格式通常为JavaScript变量赋值，包含视频数组
    例如: var videoList = [{...}, {...}];

    Args:
        file_path: sp.js文件路径

    Returns:
        视频数据列表
    """
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        print(f"❌ 文件不存在: {file_path}")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 尝试提取JSON数组
        # 方法1: 查找 var xxx = [...] 或 let xxx = [...] 或 const xxx = [...]
        array_match = re.search(r'(?:var|let|const)\s+\w+\s*=\s*(\[[\s\S]*?\]);?\s*$', content, re.MULTILINE)
        if array_match:
            json_str = array_match.group(1)
            # 清理JavaScript特有的语法
            json_str = re.sub(r',\s*([}\]])', r'\1', json_str)  # 移除尾随逗号
            videos = json.loads(json_str)
            print(f"✅ 从sp.js解析到 {len(videos)} 个视频 (变量赋值格式)")
            return videos

        # 方法2: 直接尝试作为JSON解析
        try:
            videos = json.loads(content)
            if isinstance(videos, list):
                print(f"✅ 从sp.js解析到 {len(videos)} 个视频 (JSON数组格式)")
                return videos
            elif isinstance(videos, dict) and 'data' in videos:
                videos = videos['data']
                print(f"✅ 从sp.js解析到 {len(videos)} 个视频 (JSON对象格式)")
                return videos if isinstance(videos, list) else []
        except json.JSONDecodeError:
            pass

        # 方法3: 查找JSON数组部分
        bracket_match = re.search(r'\[[\s\S]*\]', content)
        if bracket_match:
            json_str = bracket_match.group(0)
            json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
            videos = json.loads(json_str)
            print(f"✅ 从sp.js解析到 {len(videos)} 个视频 (提取JSON数组)")
            return videos

        print("❌ 无法解析sp.js文件格式")
        return []

    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        print(f"❌ JSON解析失败: {e}")
        return []
    except Exception as e:
        logger.error(f"读取文件失败: {e}")
        print(f"❌ 读取文件失败: {e}")
        return []


def import_from_spjs(file_path: str, db: VideoDatabase) -> int:
    """
    从sp.js文件导入视频数据到数据库

    Args:
        file_path: sp.js文件路径
        db: 数据库实例

    Returns:
        成功导入的数量
    """
    videos = parse_spjs_file(file_path)

    if not videos:
        print("⚠️ 没有找到可导入的视频数据")
        return 0

    videos_to_insert = []
    skipped_count = 0

    def get_first_value(*keys, default=None, source=None):
        """从字典中获取第一个存在的键值"""
        for key in keys:
            val = source.get(key)
            if val is not None:
                return val
        return default

    for video in videos:
        # 尝试多种字段名映射
        video_id = get_first_value('video_id', 'vod_id', 'id', source=video)
        video_title = get_first_value('video_title', 'vod_name', 'title', 'name', source=video)
        video_url = get_first_value('video_url', 'vod_play_url', 'url', 'play_url', default='', source=video)

        if not video_id or not video_title:
            skipped_count += 1
            continue

        db_video = {
            'video_id': video_id,
            'video_url': video_url,
            'video_image': get_first_value('video_image', 'vod_pic', 'pic', 'thumb', default='', source=video),
            'video_title': video_title,
            'video_category': get_first_value('video_category', 'type_name', 'category', default='', source=video),
            'play_count': get_first_value('play_count', 'vod_hits', 'hits', default=0, source=video),
            'upload_time': get_first_value('upload_time', 'vod_time', 'time', default='', source=video),
            'video_duration': get_first_value('video_duration', 'vod_duration', 'duration', 'vod_remarks', default='', source=video),
            'video_coins': get_first_value('video_coins', 'coins', 'gold', default=0, source=video)
        }
        videos_to_insert.append(db_video)

    if skipped_count > 0:
        print(f"⏭️ 跳过 {skipped_count} 个无效视频记录")

    return db.insert_videos(videos_to_insert)


# 命令行测试
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='视频数据库管理工具 - 支持MySQL和SQLite')
    parser.add_argument('--mysql', action='store_true', default=True,
                        help='使用MySQL数据库 (默认)')
    parser.add_argument('--sqlite', action='store_true',
                        help='使用SQLite数据库')
    parser.add_argument('--db', type=str, default='videos.db',
                        help='SQLite数据库文件路径')
    parser.add_argument('--import-spjs', type=str, default=None, metavar='FILE',
                        help='从sp.js文件导入视频数据')
    parser.add_argument('--stats', action='store_true',
                        help='显示统计信息')
    parser.add_argument('--categories', action='store_true',
                        help='显示所有分类')
    parser.add_argument('--list', type=int, default=None,
                        help='列出指定数量的视频')
    parser.add_argument('--search', type=str, default=None,
                        help='搜索视频标题')
    parser.add_argument('--top', type=int, default=None,
                        help='显示播放量最高的N个视频')

    args = parser.parse_args()

    # 确定使用MySQL还是SQLite
    use_mysql = not args.sqlite

    print("\n" + "=" * 60)
    print("🎬 视频数据库管理工具 v2.0")
    print("=" * 60)

    if use_mysql and MYSQL_AVAILABLE:
        print("📡 数据库类型: MySQL")
        print(f"   主机: {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}")
        print(f"   数据库: {MYSQL_CONFIG['database']}")
    else:
        print(f"📡 数据库类型: SQLite ({args.db})")

    with VideoDatabase(use_mysql=use_mysql, db_path=args.db) as db:
        # 导入sp.js文件
        if args.import_spjs:
            print(f"\n📥 正在从 {args.import_spjs} 导入视频数据...")
            count = import_from_spjs(args.import_spjs, db)
            print(f"✅ 成功导入 {count} 个视频到数据库")

        if args.stats:
            stats = db.get_statistics()
            print("\n📊 数据库统计信息:")
            print(f"  总视频数: {stats['total_videos']}")
            print(f"  总播放数: {stats['total_plays']}")
            print(f"  分类数量: {stats['category_count']}")
            print(f"  平均播放: {stats['average_plays']}")

        if args.categories:
            categories = db.get_categories()
            print("\n📂 视频分类:")
            for cat in categories:
                print(f"  - {cat['video_category']}: {cat['video_count']} 个视频")

        if args.list:
            videos = db.get_all_videos(limit=args.list)
            print(f"\n📺 视频列表 (共 {len(videos)} 个):")
            for v in videos:
                print(f"  [{v['video_id']}] {v['video_title']} - {v['video_category']}")

        if args.search:
            results = db.search_videos(args.search)
            print(f"\n🔍 搜索 '{args.search}' 结果 (共 {len(results)} 个):")
            for v in results:
                print(f"  [{v['video_id']}] {v['video_title']}")

        if args.top:
            top_videos = db.get_top_videos(limit=args.top)
            print(f"\n🔥 播放量TOP{args.top}:")
            for i, v in enumerate(top_videos, 1):
                print(f"  {i}. [{v['play_count']}播放] {v['video_title']}")
