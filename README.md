# 视频播放器应用 (Video Player App)

一个现代化的视频播放器应用，支持 Docker 一键部署和 Android APK 打包。

## 项目结构

```
├── video-app/          # 前端 Vue.js 应用
│   ├── src/            # Vite/Vue 源码
│   │   ├── api/        # API 接口封装 (axios)
│   │   ├── components/ # Vue 组件
│   │   ├── views/      # 页面视图
│   │   ├── router/     # 路由配置
│   │   └── assets/     # 静态资源
│   ├── package.json    # 依赖配置
│   └── Dockerfile      # 前端容器配置
├── api/                # 后端 API 服务
│   ├── api_server.py   # Flask API 服务器
│   ├── Dockerfile      # API容器配置
│   └── requirements.txt
├── tools/              # 工具脚本
│   ├── video_database.py   # 数据库模块 (MySQL/SQLite)
│   └── video_collector.py  # 视频采集脚本
├── deploy.py           # Docker自动部署脚本
├── docker_build_app.py # 应用打包脚本 (Web/Android)
└── docker-compose.yml  # Docker Compose配置
```

## 功能特性

- ✅ Vue 3 + Vite 现代化前端架构
- ✅ 支持 H5 网页访问
- ✅ 支持 Android WebView APK 打包
- ✅ 视频分类和搜索
- ✅ 视频播放器支持多集
- ✅ 响应式设计，适配手机和平板
- ✅ REST API 接口
- ✅ 支持 MySQL 和 SQLite 数据库
- ✅ Docker 一键自动部署 (Ubuntu 22)
- ✅ TypeScript 支持 (TypeScript support)
- ✅ ESLint 代码质量检查 (ESLint code quality checking)

## 🔧 代码质量工具 (Code Quality Tools)

### 前端代码检查 (Frontend Linting)

项目使用 ESLint 和 TypeScript 来保证代码质量。

```bash
cd video-app

# 运行代码检查 (Run linting)
npm run lint

# 自动修复可修复的问题 (Auto-fix fixable issues)
npm run lint:fix

# 运行 TypeScript 类型检查 (Run TypeScript type checking)
npm run type-check
```

### 后端代码检查 (Backend Linting)

项目配置了 flake8 和 mypy 用于 Python 代码质量检查。

```bash
# 安装检查工具 (Install linting tools)
pip install flake8 mypy

# 运行 flake8 检查 (Run flake8 check)
flake8 api/ tools/ deploy.py

# 运行类型检查 (Run type check)
mypy api/ tools/ --ignore-missing-imports
```


## 🚀 Docker 一键部署 (推荐)

适用于 **Ubuntu 22.04 LTS**，自动检测并安装所有依赖。

### 一键部署

```bash
# 克隆项目
git clone https://github.com/mansdeanna2-collab/wuka.git
cd wuka

# 运行自动部署脚本 (需要sudo权限)
sudo python3 deploy.py
```

部署脚本会自动:
- 检测并安装 Docker (如未安装)
- 检测并安装 Docker Compose (如未安装)
- 构建前端和后端镜像
- 启动所有服务

### 部署命令

```bash
sudo python3 deploy.py              # 完整部署
sudo python3 deploy.py --check      # 仅检查依赖
sudo python3 deploy.py --no-build   # 不重新构建镜像
sudo python3 deploy.py --stop       # 停止应用
sudo python3 deploy.py --restart    # 重启应用
sudo python3 deploy.py --logs       # 查看日志
sudo python3 deploy.py --clean      # 清理所有容器和镜像
```

### 访问应用

部署完成后:
- 前端: http://localhost:8080
- API: http://103.74.193.179:5000/api

## 手动安装

### 1. 安装前端依赖

```bash
cd video-app
npm install
```

### 2. 安装后端依赖

```bash
cd api
pip install -r requirements.txt
```

### 3. 启动开发服务器

启动后端 API 服务器:
```bash
cd api
python api_server.py --sqlite  # 使用 SQLite
# 或
python api_server.py           # 使用 MySQL
```

启动前端开发服务器:
```bash
cd video-app
npm run dev
```

访问 http://localhost:3000 查看应用。

## Docker 手动部署

如果不使用自动部署脚本，可以手动使用 Docker Compose:

```bash
# 构建并启动
docker compose up -d --build

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止
docker compose down
```

## 📱 Android APK 打包

使用 `docker_build_app.py` 脚本可以构建 Android WebView APK，该 APK 包装了 deploy.py 部署的 Web 应用。

### 使用方法

```bash
# 构建 Web 版本
python3 docker_build_app.py

# 构建 Android WebView APK (使用默认地址 http://localhost:8080)
python3 docker_build_app.py --platform android

# 构建 Android APK 并指定 Web 应用地址
python3 docker_build_app.py --platform android --web-url http://your-server:8080

# 构建发布版 APK
python3 docker_build_app.py --platform android --release --web-url http://your-server:8080

# 检查依赖
python3 docker_build_app.py --check

# 清理构建产物
python3 docker_build_app.py --clean
```

### 构建流程

1. 首先使用 `deploy.py` 部署 Web 应用到服务器
2. 然后使用 `docker_build_app.py --platform android --web-url http://your-server:8080` 构建 APK
3. APK 会在 `build-output/android/` 目录生成

### GitHub Actions 构建

也可以使用 GitHub Actions 自动构建:

1. 访问仓库的 Actions 页面
2. 选择 "Build Android WebView APK" 工作流程
3. 点击 "Run workflow" 按钮
4. 输入 Web 应用地址和构建类型
5. 下载构建完成的 APK

## API 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/videos | 获取视频列表 |
| GET | /api/videos/:id | 获取单个视频 |
| GET | /api/videos/search | 搜索视频 |
| GET | /api/videos/category | 按分类获取 |
| GET | /api/videos/top | 热门视频 |
| POST | /api/videos/:id/play | 更新播放次数 |
| GET | /api/categories | 获取分类列表 |
| GET | /api/statistics | 数据库统计 |

## 数据库配置

默认使用 MySQL，通过环境变量配置:

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_DATABASE=psspsj
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
```

如果 MySQL 不可用，自动降级到 SQLite。

## API 服务器配置

前端应用需要连接后端 API 服务器。默认配置连接到 `http://103.74.193.179:5000`。

### 配置自定义 API 地址

1. 复制环境变量示例文件:
   ```bash
   cd video-app
   cp .env.example .env.local
   ```

2. 编辑 `.env.local` 文件，设置您的 API 服务器地址:
   ```bash
   VITE_API_BASE_URL=http://your-api-server:5000
   ```

3. 重启开发服务器:
   ```bash
   npm run dev
   ```

### 本地 API 服务器

如果要使用本地 API 服务器:

1. 启动后端 API 服务器:
   ```bash
   cd api
   python api_server.py --sqlite
   ```

2. 设置环境变量指向本地服务器:
   ```bash
   # .env.local
   VITE_API_BASE_URL=http://103.74.193.179:5000
   ```

### 故障排除

如果看到黑屏且没有 API 流量:
1. 检查 API 服务器是否正在运行
2. 检查 `.env.local` 中的 `VITE_API_BASE_URL` 是否正确
3. 打开浏览器开发者工具 (F12) 查看网络请求和控制台错误

## 导入视频数据

从采集器导入:
```bash
python tools/video_collector.py --all --format json
python tools/video_database.py --import-spjs videos_*.json
```

## 技术栈

- **前端**: Vue 3, Vite, Vue Router, Axios
- **后端**: Flask, Flask-CORS
- **数据库**: MySQL / SQLite
- **部署**: Docker, Docker Compose, Nginx

## 许可证

ISC
