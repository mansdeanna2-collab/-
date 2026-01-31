# HBuilderX 打包 APK 指南

本文档介绍如何使用 HBuilderX 打包 Android APK。

## 📋 前提条件

1. 下载并安装 [HBuilderX](https://www.dcloud.io/hbuilderx.html)
2. 在 HBuilderX 中登录 DCloud 账号
3. 确保已安装 App 开发相关插件

## 🚀 快速开始

### 1. 导入项目

1. 打开 HBuilderX
2. 选择 **文件** → **导入** → **从本地目录导入**
3. 选择 `video-app` 目录
4. 项目将以 uni-app 模式打开

### 2. 配置项目

#### 2.1 修改 AppID

1. 在 HBuilderX 中打开 `manifest.json`
2. 点击左侧 **基础配置**
3. 点击 **重新获取** 按钮获取 DCloud AppID
4. 或手动填写您已注册的 AppID

#### 2.2 配置 API 地址

在 `api/index.js` 中修改 API 基础地址：

```javascript
// App 环境需要完整 URL (生产环境建议使用 https)
baseUrl = 'https://your-server-domain.com/api'
// 或开发环境
baseUrl = 'http://your-server-ip:5000/api'
```

#### 2.3 配置应用图标

1. 在 `manifest.json` 中选择 **App 图标配置**
2. 上传不同尺寸的应用图标
3. 或将图标放入 `static/icons/` 目录

#### 2.4 配置启动页

1. 在 `manifest.json` 中选择 **App 启动界面配置**
2. 配置启动页样式或上传自定义启动图
3. 或将启动图放入 `static/launch/` 目录

### 3. 运行和调试

#### 3.1 运行到浏览器

- 点击工具栏 **运行** → **运行到浏览器** → 选择浏览器

#### 3.2 运行到 Android 模拟器/手机

1. 连接 Android 手机（开启 USB 调试）或启动模拟器
2. 点击 **运行** → **运行到手机或模拟器** → **运行到 Android App 基座**

### 4. 打包 APK

#### 4.1 云端打包（推荐）

1. 点击 **发行** → **原生 App-云打包**
2. 填写打包配置：
   - **Android 包名**: `com.videoapp.player`（或自定义）
   - **版本号**: 按需修改
   - **证书**: 使用 DCloud 公共证书或上传自有证书
3. 选择 **打正式包** 或 **打测试包**
4. 点击 **打包** 开始云端打包
5. 等待打包完成，下载 APK 文件

#### 4.2 本地打包

如需本地打包，请参考 DCloud 官方文档：
https://nativesupport.dcloud.net.cn/AppDocs/usesdk/android

## 📁 项目结构（HBuilderX 模式）

```
video-app/
├── manifest.json          # 应用配置文件（核心）
├── pages.json             # 页面路由配置
├── main.hbuilder.js       # uni-app 入口文件
├── App.hbuilder.vue       # 根组件
├── pages/                 # 页面目录
│   ├── index/
│   │   └── index.vue      # 首页
│   ├── player/
│   │   └── player.vue     # 播放页
│   ├── category/
│   │   └── category.vue   # 分类页
│   └── search/
│       └── search.vue     # 搜索页
├── api/                   # API 接口（uni.request）
│   └── index.js
├── static/                # 静态资源
│   ├── icons/             # 应用图标
│   ├── launch/            # 启动图
│   └── tabbar/            # 底部栏图标
└── src/                   # 原有 Vite/Vue 源码
```

## ⚙️ 文件说明

| 文件 | 说明 |
|------|------|
| `manifest.json` | HBuilderX 项目核心配置，包含 AppID、图标、权限等 |
| `pages.json` | 页面路由和全局样式配置 |
| `main.hbuilder.js` | uni-app 应用入口 |
| `App.hbuilder.vue` | uni-app 根组件 |
| `api/index.js` | uni.request 封装的 API 模块 |

## 🔧 常见问题

### Q: HBuilderX 无法识别项目？

确保项目根目录有 `manifest.json` 和 `pages.json` 文件。

### Q: 运行报错找不到页面？

检查 `pages.json` 中的页面路径是否正确，确保 `pages/` 目录下有对应的 `.vue` 文件。

### Q: API 请求失败？

1. 确保后端 API 服务已启动
2. 在 App 端需要配置完整的 API 地址（包含 http:// 和端口）
3. 确保服务器允许跨域请求

### Q: 打包失败？

1. 检查 DCloud 账号是否已登录
2. 确保 AppID 配置正确
3. 查看打包日志定位具体错误

## 📱 Android 权限说明

项目已配置以下权限（在 `manifest.json` 中）：

- `INTERNET` - 网络访问
- `ACCESS_NETWORK_STATE` - 获取网络状态
- `ACCESS_WIFI_STATE` - 获取 WiFi 状态
- `READ_EXTERNAL_STORAGE` - 读取存储
- `WRITE_EXTERNAL_STORAGE` - 写入存储

如需更多权限，请在 `manifest.json` 的 Android 配置中添加。

## 🔗 相关链接

- [DCloud 开发者中心](https://dev.dcloud.net.cn/)
- [uni-app 官方文档](https://uniapp.dcloud.io/)
- [HBuilderX 下载](https://www.dcloud.io/hbuilderx.html)
- [云打包说明](https://ask.dcloud.net.cn/article/37979)

## 📝 两种模式切换

本项目同时支持两种开发模式：

### Vite/Vue 模式（原有模式）
```bash
cd video-app
npm install
npm run dev
```
使用 `src/` 目录下的源码，适合 H5 和 Capacitor 打包。

### HBuilderX/uni-app 模式
用 HBuilderX 打开项目，使用 `pages/` 目录下的页面，适合多端打包。

两种模式的核心逻辑相同，UI 和 API 调用方式略有差异以适配不同平台。
