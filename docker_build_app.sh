#!/bin/bash
# -*- coding: utf-8 -*-
# ============================================================================
# Docker 环境应用打包脚本 (Docker App Build Script)
# ============================================================================
# 
# 功能 (Features):
# - 自动检测并安装 Docker
# - 自动检测并安装 Node.js 和 npm
# - 自动检测并安装 Java JDK (Android 构建需要)
# - 自动检测并安装 Android SDK 命令行工具
# - 支持在 Docker 容器中构建应用
# - 支持 H5 Web 应用打包
# - 支持 Android APK 打包
# - 支持 iOS 应用打包 (仅 macOS)
#
# 使用方法 (Usage):
#   chmod +x docker_build_app.sh
#   ./docker_build_app.sh [选项]
#
# 选项 (Options):
#   --check         仅检查依赖，不执行打包
#   --web           仅打包 H5 Web 应用
#   --android       打包 Android APK
#   --ios           打包 iOS 应用 (需要 macOS)
#   --all           打包所有平台 (Web + Android + iOS)
#   --docker        在 Docker 容器中执行打包
#   --clean         清理构建产物
#   --help          显示帮助信息
#
# 作者: Auto-generated
# 日期: 2026-01-30
# ============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
VIDEO_APP_DIR="$PROJECT_DIR/video-app"
OUTPUT_DIR="$PROJECT_DIR/build-output"

# 默认选项
BUILD_WEB=false
BUILD_ANDROID=false
BUILD_IOS=false
USE_DOCKER=false
CHECK_ONLY=false
CLEAN_BUILD=false

# ============================================================================
# 版本配置 (Version Configuration)
# 可根据需要修改以下版本号
# ============================================================================
ANDROID_SDK_VERSION="11076708"  # Android 命令行工具版本号
ANDROID_PLATFORM_VERSION="34"   # Android 平台版本
ANDROID_BUILD_TOOLS_VERSION="34.0.0"  # Android 构建工具版本
NODE_VERSION="20"  # Node.js 主版本号

# ============================================================================
# 辅助函数
# ============================================================================

print_header() {
    echo ""
    echo -e "${BOLD}${CYAN}============================================================${NC}"
    echo -e "${BOLD}${CYAN}  $1${NC}"
    echo -e "${BOLD}${CYAN}============================================================${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[i]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            echo "ubuntu"
        elif command -v yum &> /dev/null; then
            echo "centos"
        elif command -v dnf &> /dev/null; then
            echo "fedora"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# 检查命令是否存在
command_exists() {
    command -v "$1" &> /dev/null
}

# 检查是否为 root 用户
is_root() {
    [[ $EUID -eq 0 ]]
}

# 请求 sudo 权限
require_sudo() {
    if ! is_root; then
        print_warning "某些操作需要 sudo 权限"
        sudo -v || {
            print_error "无法获取 sudo 权限"
            exit 1
        }
    fi
}

# ============================================================================
# 依赖检测和安装
# ============================================================================

# 安装 Docker (Ubuntu/Debian)
install_docker_ubuntu() {
    print_step "正在安装 Docker..."
    
    sudo apt-get update -y
    sudo apt-get install -y ca-certificates curl gnupg lsb-release
    
    # 添加 Docker GPG 密钥
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    
    # 添加 Docker 软件源
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 将当前用户添加到 docker 组
    if ! is_root; then
        sudo usermod -aG docker "$USER"
        print_warning "用户已添加到 docker 组，可能需要重新登录才能生效"
    fi
    
    print_success "Docker 安装完成"
}

# 安装 Docker (macOS)
install_docker_macos() {
    print_step "正在安装 Docker Desktop..."
    
    if command_exists brew; then
        brew install --cask docker
        print_success "Docker Desktop 已安装"
        print_warning "请手动启动 Docker Desktop 应用"
    else
        print_error "请先安装 Homebrew 或手动下载 Docker Desktop"
        print_info "下载地址: https://www.docker.com/products/docker-desktop/"
        exit 1
    fi
}

# 检测并安装 Docker
check_docker() {
    print_step "检查 Docker 安装状态..."
    
    if command_exists docker; then
        local docker_version
        docker_version=$(docker --version 2>/dev/null | cut -d' ' -f3 | tr -d ',')
        print_success "Docker 已安装 (版本: $docker_version)"
        
        # 检查 Docker 服务是否运行
        if ! docker info &> /dev/null; then
            print_warning "Docker 服务未运行"
            local os_type
            os_type=$(detect_os)
            if [[ "$os_type" == "ubuntu" || "$os_type" == "centos" || "$os_type" == "fedora" ]]; then
                print_step "正在启动 Docker 服务..."
                sudo systemctl start docker
                print_success "Docker 服务已启动"
            else
                print_error "请手动启动 Docker 服务"
                return 1
            fi
        fi
        return 0
    else
        print_warning "Docker 未安装"
        local os_type
        os_type=$(detect_os)
        case "$os_type" in
            ubuntu)
                require_sudo
                install_docker_ubuntu
                ;;
            macos)
                install_docker_macos
                ;;
            *)
                print_error "不支持自动安装 Docker，请手动安装"
                print_info "下载地址: https://docs.docker.com/get-docker/"
                return 1
                ;;
        esac
    fi
}

# 安装 Node.js (Ubuntu/Debian)
install_nodejs_ubuntu() {
    print_step "正在安装 Node.js 20.x..."
    
    # 使用 NodeSource 官方源
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    
    print_success "Node.js 安装完成"
}

# 安装 Node.js (macOS)
install_nodejs_macos() {
    print_step "正在安装 Node.js..."
    
    if command_exists brew; then
        brew install node@20
        print_success "Node.js 安装完成"
    else
        print_error "请先安装 Homebrew"
        exit 1
    fi
}

# 检测并安装 Node.js
check_nodejs() {
    print_step "检查 Node.js 安装状态..."
    
    if command_exists node && command_exists npm; then
        local node_version npm_version
        node_version=$(node --version)
        npm_version=$(npm --version)
        print_success "Node.js 已安装 (版本: $node_version, npm: $npm_version)"
        return 0
    else
        print_warning "Node.js 未安装"
        local os_type
        os_type=$(detect_os)
        case "$os_type" in
            ubuntu)
                require_sudo
                install_nodejs_ubuntu
                ;;
            macos)
                install_nodejs_macos
                ;;
            *)
                print_error "不支持自动安装 Node.js，请手动安装"
                print_info "下载地址: https://nodejs.org/"
                return 1
                ;;
        esac
    fi
}

# 安装 Java JDK (Ubuntu/Debian)
install_java_ubuntu() {
    print_step "正在安装 OpenJDK 17..."
    
    sudo apt-get update -y
    sudo apt-get install -y openjdk-17-jdk
    
    # 设置 JAVA_HOME
    export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
    
    # 检查是否已存在 JAVA_HOME 配置，避免重复添加
    if ! grep -q "JAVA_HOME" ~/.bashrc 2>/dev/null; then
        echo "" >> ~/.bashrc
        echo "# Java JDK" >> ~/.bashrc
        echo "export JAVA_HOME=$JAVA_HOME" >> ~/.bashrc
    fi
    
    print_success "Java JDK 安装完成"
}

# 安装 Java JDK (macOS)
install_java_macos() {
    print_step "正在安装 OpenJDK 17..."
    
    if command_exists brew; then
        brew install openjdk@17
        # 创建符号链接
        sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk 2>/dev/null || true
        print_success "Java JDK 安装完成"
    else
        print_error "请先安装 Homebrew"
        exit 1
    fi
}

# 检测并安装 Java JDK
check_java() {
    print_step "检查 Java JDK 安装状态..."
    
    if command_exists java; then
        local java_version
        java_version=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
        print_success "Java JDK 已安装 (版本: $java_version)"
        return 0
    else
        print_warning "Java JDK 未安装 (Android 构建需要)"
        local os_type
        os_type=$(detect_os)
        case "$os_type" in
            ubuntu)
                require_sudo
                install_java_ubuntu
                ;;
            macos)
                install_java_macos
                ;;
            *)
                print_error "不支持自动安装 Java JDK，请手动安装"
                return 1
                ;;
        esac
    fi
}

# 安装 Android SDK 命令行工具
install_android_sdk() {
    print_step "正在安装 Android SDK 命令行工具..."
    
    local ANDROID_HOME="${HOME}/Android/Sdk"
    local CMDLINE_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-linux-${ANDROID_SDK_VERSION}_latest.zip"
    
    if [[ "$(detect_os)" == "macos" ]]; then
        ANDROID_HOME="${HOME}/Library/Android/sdk"
        CMDLINE_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-mac-${ANDROID_SDK_VERSION}_latest.zip"
    fi
    
    mkdir -p "$ANDROID_HOME/cmdline-tools"
    
    local temp_zip="/tmp/cmdline-tools.zip"
    print_step "下载 Android 命令行工具 (版本: $ANDROID_SDK_VERSION)..."
    curl -L "$CMDLINE_TOOLS_URL" -o "$temp_zip"
    
    print_step "解压 Android 命令行工具..."
    unzip -q -o "$temp_zip" -d "$ANDROID_HOME/cmdline-tools"
    mv "$ANDROID_HOME/cmdline-tools/cmdline-tools" "$ANDROID_HOME/cmdline-tools/latest" 2>/dev/null || true
    rm -f "$temp_zip"
    
    # 设置环境变量
    export ANDROID_HOME="$ANDROID_HOME"
    export ANDROID_SDK_ROOT="$ANDROID_HOME"
    export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools"
    
    # 写入到 shell 配置文件
    local shell_config="${HOME}/.bashrc"
    if [[ "$(detect_os)" == "macos" ]]; then
        shell_config="${HOME}/.zshrc"
    fi
    
    if ! grep -q "ANDROID_HOME" "$shell_config" 2>/dev/null; then
        echo "" >> "$shell_config"
        echo "# Android SDK" >> "$shell_config"
        echo "export ANDROID_HOME=\"$ANDROID_HOME\"" >> "$shell_config"
        echo "export ANDROID_SDK_ROOT=\"$ANDROID_HOME\"" >> "$shell_config"
        echo "export PATH=\"\$PATH:\$ANDROID_HOME/cmdline-tools/latest/bin:\$ANDROID_HOME/platform-tools\"" >> "$shell_config"
    fi
    
    # 接受许可证
    print_warning "将自动接受 Android SDK 许可证 (包括 Google Play 服务等条款)"
    print_info "许可证详情: https://developer.android.com/studio/terms"
    print_step "接受 Android SDK 许可证..."
    yes | "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" --licenses > /dev/null 2>&1 || true
    
    # 安装必要的 SDK 组件
    print_step "安装 Android SDK 组件 (platform: android-$ANDROID_PLATFORM_VERSION, build-tools: $ANDROID_BUILD_TOOLS_VERSION)..."
    "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" "platform-tools" "platforms;android-${ANDROID_PLATFORM_VERSION}" "build-tools;${ANDROID_BUILD_TOOLS_VERSION}"
    
    print_success "Android SDK 安装完成"
}

# 检测并安装 Android SDK
check_android_sdk() {
    print_step "检查 Android SDK 安装状态..."
    
    if [[ -n "$ANDROID_HOME" ]] && [[ -d "$ANDROID_HOME" ]]; then
        print_success "Android SDK 已安装 (路径: $ANDROID_HOME)"
        return 0
    fi
    
    # 检查常见安装路径
    local possible_paths=(
        "$HOME/Android/Sdk"
        "$HOME/Library/Android/sdk"
        "/opt/android-sdk"
    )
    
    for path in "${possible_paths[@]}"; do
        if [[ -d "$path" ]]; then
            export ANDROID_HOME="$path"
            export ANDROID_SDK_ROOT="$path"
            print_success "Android SDK 已找到 (路径: $path)"
            return 0
        fi
    done
    
    print_warning "Android SDK 未安装"
    
    if $BUILD_ANDROID; then
        install_android_sdk
    else
        print_info "如需构建 Android 应用，请使用 --android 选项"
    fi
}

# 检测所有依赖
check_all_dependencies() {
    print_header "检查系统依赖"
    
    local all_ok=true
    
    # 检测操作系统
    local os_type
    os_type=$(detect_os)
    print_info "检测到操作系统: $os_type"
    
    # 检查 Docker (如果使用 Docker 构建)
    if $USE_DOCKER; then
        check_docker || all_ok=false
    fi
    
    # 检查 Node.js
    check_nodejs || all_ok=false
    
    # 检查 Java (如果构建 Android)
    if $BUILD_ANDROID; then
        check_java || all_ok=false
        check_android_sdk || all_ok=false
    fi
    
    # 检查 iOS 构建依赖 (仅 macOS)
    if $BUILD_IOS; then
        if [[ "$os_type" != "macos" ]]; then
            print_error "iOS 应用只能在 macOS 上构建"
            all_ok=false
        else
            print_step "检查 Xcode 安装状态..."
            if command_exists xcodebuild; then
                local xcode_version
                xcode_version=$(xcodebuild -version | head -n 1)
                print_success "Xcode 已安装 ($xcode_version)"
            else
                print_error "Xcode 未安装，请从 App Store 安装"
                all_ok=false
            fi
            
            # 检查 CocoaPods
            print_step "检查 CocoaPods 安装状态..."
            if command_exists pod; then
                print_success "CocoaPods 已安装"
            else
                print_warning "正在安装 CocoaPods (需要 sudo 权限)..."
                print_info "CocoaPods 将被安装到系统 Ruby 环境中"
                sudo gem install cocoapods
                print_success "CocoaPods 安装完成"
            fi
        fi
    fi
    
    if $all_ok; then
        print_success "所有依赖检查通过!"
        return 0
    else
        print_error "部分依赖检查失败"
        return 1
    fi
}

# ============================================================================
# 构建功能
# ============================================================================

# 安装前端依赖
install_frontend_deps() {
    print_step "安装前端依赖..."
    
    cd "$VIDEO_APP_DIR"
    
    if [[ -f "package-lock.json" ]]; then
        npm ci
    else
        npm install
    fi
    
    print_success "前端依赖安装完成"
    cd "$PROJECT_DIR"
}

# 构建 Web 应用
build_web() {
    print_header "构建 H5 Web 应用"
    
    cd "$VIDEO_APP_DIR"
    
    print_step "运行 npm build..."
    npm run build
    
    # 创建输出目录
    mkdir -p "$OUTPUT_DIR/web"
    
    # 复制构建产物
    if [[ -d "dist" ]]; then
        cp -r dist/* "$OUTPUT_DIR/web/"
        print_success "Web 应用构建完成"
        print_info "输出目录: $OUTPUT_DIR/web"
    else
        print_error "构建输出目录不存在"
        return 1
    fi
    
    cd "$PROJECT_DIR"
}

# 初始化 Capacitor Android 平台
init_android_platform() {
    print_step "初始化 Android 平台..."
    
    cd "$VIDEO_APP_DIR"
    
    # 检查是否需要添加 Android 平台
    if [[ ! -d "android" ]]; then
        print_step "添加 Android 平台..."
        npx cap add android
    fi
    
    # 同步 Web 资源到 Android
    print_step "同步 Web 资源..."
    npx cap sync android
    
    print_success "Android 平台初始化完成"
    cd "$PROJECT_DIR"
}

# 构建 Android APK
build_android() {
    print_header "构建 Android APK"
    
    # 确保 Web 应用已构建
    if [[ ! -d "$VIDEO_APP_DIR/dist" ]]; then
        print_step "先构建 Web 应用..."
        build_web
    fi
    
    # 初始化 Android 平台
    init_android_platform
    
    cd "$VIDEO_APP_DIR/android"
    
    print_step "使用 Gradle 构建 APK..."
    
    # 设置 JAVA_HOME (如果未设置)
    if [[ -z "$JAVA_HOME" ]]; then
        if [[ -d "/usr/lib/jvm/java-17-openjdk-amd64" ]]; then
            export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
        elif [[ -d "/Library/Java/JavaVirtualMachines/openjdk-17.jdk/Contents/Home" ]]; then
            export JAVA_HOME="/Library/Java/JavaVirtualMachines/openjdk-17.jdk/Contents/Home"
        fi
    fi
    
    # 构建 Debug APK
    ./gradlew assembleDebug
    
    # 创建输出目录
    mkdir -p "$OUTPUT_DIR/android"
    
    # 复制 APK 文件
    local apk_path="app/build/outputs/apk/debug/app-debug.apk"
    if [[ -f "$apk_path" ]]; then
        cp "$apk_path" "$OUTPUT_DIR/android/video-app-debug.apk"
        print_success "Android APK 构建完成"
        print_info "APK 文件: $OUTPUT_DIR/android/video-app-debug.apk"
    else
        print_error "APK 文件未找到"
        return 1
    fi
    
    cd "$PROJECT_DIR"
}

# 初始化 Capacitor iOS 平台
init_ios_platform() {
    print_step "初始化 iOS 平台..."
    
    cd "$VIDEO_APP_DIR"
    
    # 检查是否需要添加 iOS 平台
    if [[ ! -d "ios" ]]; then
        print_step "添加 iOS 平台..."
        npx cap add ios
    fi
    
    # 同步 Web 资源到 iOS
    print_step "同步 Web 资源..."
    npx cap sync ios
    
    # 安装 CocoaPods 依赖
    print_step "安装 CocoaPods 依赖..."
    cd ios/App
    pod install
    
    print_success "iOS 平台初始化完成"
    cd "$PROJECT_DIR"
}

# 构建 iOS 应用
build_ios() {
    print_header "构建 iOS 应用"
    
    if [[ "$(detect_os)" != "macos" ]]; then
        print_error "iOS 应用只能在 macOS 上构建"
        return 1
    fi
    
    # 确保 Web 应用已构建
    if [[ ! -d "$VIDEO_APP_DIR/dist" ]]; then
        print_step "先构建 Web 应用..."
        build_web
    fi
    
    # 初始化 iOS 平台
    init_ios_platform
    
    cd "$VIDEO_APP_DIR/ios/App"
    
    print_step "使用 xcodebuild 构建 iOS 应用..."
    
    # 构建 iOS 应用 (模拟器版本)
    xcodebuild -workspace App.xcworkspace \
               -scheme App \
               -configuration Debug \
               -destination 'generic/platform=iOS Simulator' \
               -archivePath "$OUTPUT_DIR/ios/App.xcarchive" \
               clean build
    
    # 创建输出目录
    mkdir -p "$OUTPUT_DIR/ios"
    
    print_success "iOS 应用构建完成"
    print_info "使用 Xcode 打开项目进行真机构建和签名"
    print_info "项目路径: $VIDEO_APP_DIR/ios/App/App.xcworkspace"
    
    cd "$PROJECT_DIR"
}

# 在 Docker 容器中构建
build_in_docker() {
    print_header "在 Docker 容器中构建应用"
    
    # 创建 Docker 构建文件
    local dockerfile_path="$PROJECT_DIR/.docker-build/Dockerfile.builder"
    mkdir -p "$PROJECT_DIR/.docker-build"
    
    # 注意: 以下版本号来自脚本顶部的版本配置
    print_info "使用以下版本配置:"
    print_info "  - Android SDK 版本: $ANDROID_SDK_VERSION"
    print_info "  - Android 平台版本: $ANDROID_PLATFORM_VERSION"
    print_info "  - Android 构建工具版本: $ANDROID_BUILD_TOOLS_VERSION"
    print_info "  - Node.js 版本: $NODE_VERSION"
    print_warning "将自动接受 Android SDK 许可证"
    
    cat > "$dockerfile_path" << DOCKERFILE
FROM node:${NODE_VERSION}-bullseye

# 安装必要的工具
RUN apt-get update && apt-get install -y \\
    openjdk-17-jdk \\
    wget \\
    unzip \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# 设置 JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=\$PATH:\$JAVA_HOME/bin

# 安装 Android SDK
ENV ANDROID_HOME=/opt/android-sdk
ENV ANDROID_SDK_ROOT=\$ANDROID_HOME
ENV PATH=\$PATH:\$ANDROID_HOME/cmdline-tools/latest/bin:\$ANDROID_HOME/platform-tools

RUN mkdir -p \$ANDROID_HOME/cmdline-tools && \\
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-${ANDROID_SDK_VERSION}_latest.zip -O /tmp/cmdline-tools.zip && \\
    unzip -q /tmp/cmdline-tools.zip -d \$ANDROID_HOME/cmdline-tools && \\
    mv \$ANDROID_HOME/cmdline-tools/cmdline-tools \$ANDROID_HOME/cmdline-tools/latest && \\
    rm /tmp/cmdline-tools.zip && \\
    yes | sdkmanager --licenses > /dev/null 2>&1 && \\
    sdkmanager "platform-tools" "platforms;android-${ANDROID_PLATFORM_VERSION}" "build-tools;${ANDROID_BUILD_TOOLS_VERSION}"

WORKDIR /app

# 复制项目文件
COPY video-app/package*.json ./video-app/

# 安装依赖
RUN cd video-app && npm ci

# 复制其余文件
COPY video-app ./video-app

# 构建 Web 应用
RUN cd video-app && npm run build

# 添加 Android 平台并构建
RUN cd video-app && \
    npx cap add android && \
    npx cap sync android && \
    cd android && \
    ./gradlew assembleDebug

# 创建输出目录
RUN mkdir -p /output/web /output/android && \
    cp -r video-app/dist/* /output/web/ && \
    cp video-app/android/app/build/outputs/apk/debug/app-debug.apk /output/android/video-app-debug.apk
DOCKERFILE

    print_step "构建 Docker 镜像..."
    docker build -f "$dockerfile_path" -t video-app-builder .
    
    print_step "从容器中提取构建产物..."
    mkdir -p "$OUTPUT_DIR"
    
    # 删除已存在的临时容器（如果有）
    docker rm -f temp-builder 2>/dev/null || true
    
    # 创建临时容器并复制文件
    docker create --name temp-builder video-app-builder
    docker cp temp-builder:/output/web "$OUTPUT_DIR/"
    docker cp temp-builder:/output/android "$OUTPUT_DIR/"
    docker rm temp-builder
    
    print_success "Docker 容器构建完成"
    print_info "Web 应用: $OUTPUT_DIR/web"
    print_info "Android APK: $OUTPUT_DIR/android/video-app-debug.apk"
    
    # 清理
    rm -rf "$PROJECT_DIR/.docker-build"
}

# 清理构建产物
clean_build() {
    print_header "清理构建产物"
    
    # 清理输出目录
    if [[ -d "$OUTPUT_DIR" ]]; then
        print_step "清理输出目录..."
        rm -rf "$OUTPUT_DIR"
        print_success "输出目录已清理"
    fi
    
    # 清理前端构建产物
    if [[ -d "$VIDEO_APP_DIR/dist" ]]; then
        print_step "清理前端构建产物..."
        rm -rf "$VIDEO_APP_DIR/dist"
        print_success "前端构建产物已清理"
    fi
    
    # 清理 Android 构建产物
    if [[ -d "$VIDEO_APP_DIR/android" ]]; then
        print_step "清理 Android 构建产物..."
        rm -rf "$VIDEO_APP_DIR/android"
        print_success "Android 构建产物已清理"
    fi
    
    # 清理 iOS 构建产物
    if [[ -d "$VIDEO_APP_DIR/ios" ]]; then
        print_step "清理 iOS 构建产物..."
        rm -rf "$VIDEO_APP_DIR/ios"
        print_success "iOS 构建产物已清理"
    fi
    
    # 清理 Docker 构建文件
    if [[ -d "$PROJECT_DIR/.docker-build" ]]; then
        print_step "清理 Docker 构建文件..."
        rm -rf "$PROJECT_DIR/.docker-build"
        print_success "Docker 构建文件已清理"
    fi
    
    # 清理 node_modules
    if [[ -d "$VIDEO_APP_DIR/node_modules" ]]; then
        print_step "清理 node_modules..."
        rm -rf "$VIDEO_APP_DIR/node_modules"
        print_success "node_modules 已清理"
    fi
    
    print_success "清理完成!"
}

# ============================================================================
# 主函数
# ============================================================================

show_help() {
    cat << EOF
${BOLD}Docker 环境应用打包脚本${NC}

${CYAN}使用方法:${NC}
  $0 [选项]

${CYAN}选项:${NC}
  --check         仅检查依赖，不执行打包
  --web           仅打包 H5 Web 应用
  --android       打包 Android APK
  --ios           打包 iOS 应用 (需要 macOS)
  --all           打包所有平台 (Web + Android + iOS)
  --docker        在 Docker 容器中执行打包
  --clean         清理构建产物
  --help          显示此帮助信息

${CYAN}示例:${NC}
  $0 --check              # 检查所有依赖
  $0 --web                # 仅构建 Web 应用
  $0 --android            # 构建 Android APK
  $0 --ios                # 构建 iOS 应用 (仅 macOS)
  $0 --all                # 构建所有平台
  $0 --docker --web       # 在 Docker 中构建 Web 应用
  $0 --docker --android   # 在 Docker 中构建 Android APK
  $0 --clean              # 清理所有构建产物

${CYAN}输出目录:${NC}
  Web 应用: $OUTPUT_DIR/web
  Android APK: $OUTPUT_DIR/android
  iOS: $OUTPUT_DIR/ios

${CYAN}注意事项:${NC}
  - Android 构建需要 Java JDK 17+ 和 Android SDK
  - iOS 构建需要 macOS、Xcode 和 CocoaPods
  - 使用 --docker 选项可以在容器中完成构建，无需本地安装依赖

EOF
}

main() {
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --check)
                CHECK_ONLY=true
                shift
                ;;
            --web)
                BUILD_WEB=true
                shift
                ;;
            --android)
                BUILD_ANDROID=true
                shift
                ;;
            --ios)
                BUILD_IOS=true
                shift
                ;;
            --all)
                BUILD_WEB=true
                BUILD_ANDROID=true
                BUILD_IOS=true
                shift
                ;;
            --docker)
                USE_DOCKER=true
                shift
                ;;
            --clean)
                CLEAN_BUILD=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_header "Docker 环境应用打包脚本"
    print_info "项目目录: $PROJECT_DIR"
    print_info "输出目录: $OUTPUT_DIR"
    
    # 清理模式
    if $CLEAN_BUILD; then
        clean_build
        exit 0
    fi
    
    # 如果没有指定任何构建目标，默认构建 Web
    if ! $BUILD_WEB && ! $BUILD_ANDROID && ! $BUILD_IOS && ! $CHECK_ONLY; then
        BUILD_WEB=true
    fi
    
    # 检查依赖
    check_all_dependencies || {
        print_error "依赖检查失败，请解决上述问题后重试"
        exit 1
    }
    
    # 仅检查模式
    if $CHECK_ONLY; then
        print_success "依赖检查完成"
        exit 0
    fi
    
    # Docker 构建模式
    if $USE_DOCKER; then
        build_in_docker
        exit 0
    fi
    
    # 安装前端依赖
    install_frontend_deps
    
    # 构建目标
    if $BUILD_WEB; then
        build_web
    fi
    
    if $BUILD_ANDROID; then
        build_android
    fi
    
    if $BUILD_IOS; then
        build_ios
    fi
    
    # 完成信息
    print_header "构建完成! 🎉"
    print_info "构建产物位于: $OUTPUT_DIR"
    
    if [[ -d "$OUTPUT_DIR/web" ]]; then
        print_info "  - Web 应用: $OUTPUT_DIR/web"
    fi
    
    if [[ -f "$OUTPUT_DIR/android/video-app-debug.apk" ]]; then
        print_info "  - Android APK: $OUTPUT_DIR/android/video-app-debug.apk"
    fi
    
    if [[ -d "$OUTPUT_DIR/ios" ]]; then
        print_info "  - iOS: $OUTPUT_DIR/ios"
    fi
}

# 运行主函数
main "$@"
