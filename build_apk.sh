#!/bin/bash
# -*- coding: utf-8 -*-
# ============================================================================
# APK 构建脚本 (APK Build Script)
# ============================================================================
#
# 用于导出 Android 项目后完成 APK 构建
# Used to complete APK build after exporting Android project
#
# 使用方法 (Usage):
#   chmod +x build_apk.sh
#   ./build_apk.sh           # 构建 Debug APK
#   ./build_apk.sh --release # 构建 Release APK
#   ./build_apk.sh --help    # 显示帮助信息
#
# ============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# 默认选项
BUILD_TYPE="debug"
GRADLE_TASK="assembleDebug"

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

# 显示帮助信息
show_help() {
    cat << EOF
${BOLD}APK 构建脚本${NC}

${CYAN}使用方法:${NC}
  $0 [选项]

${CYAN}选项:${NC}
  --debug         构建调试版 APK (默认)
  --release       构建发布版 APK
  --help, -h      显示此帮助信息

${CYAN}示例:${NC}
  $0              # 构建 Debug APK
  $0 --release    # 构建 Release APK

${CYAN}前提条件:${NC}
  - Java JDK 17+ 已安装
  - ANDROID_HOME 或 ANDROID_SDK_ROOT 环境变量已设置
  - 在 android-project 目录或包含 gradlew 的目录中运行

${CYAN}导出项目后使用:${NC}
  1. 运行: python3 docker_build_apk.py --project-only
  2. 进入: cd build-output/android/android-project
  3. 构建: ./build_apk.sh

EOF
}

# 检查 Java
check_java() {
    print_step "检查 Java 环境..."
    
    if command -v java &> /dev/null; then
        local java_version_output java_major_version
        java_version_output=$(java -version 2>&1 | head -n 1)
        
        # 提取主版本号
        java_major_version=$(echo "$java_version_output" | sed -E 's/.*version "([0-9]+).*/\1/')
        
        if [[ "$java_major_version" =~ ^[0-9]+$ ]] && [[ "$java_major_version" -ge 17 ]]; then
            print_success "Java 已安装 (版本: $java_version_output)"
            return 0
        else
            print_warning "Java 版本过低: $java_version_output"
            print_error "需要 JDK 17 或更高版本"
            print_info "Ubuntu: sudo apt-get install openjdk-17-jdk"
            print_info "macOS: brew install openjdk@17"
            return 1
        fi
    else
        print_error "Java 未安装，请安装 JDK 17+"
        print_info "Ubuntu: sudo apt-get install openjdk-17-jdk"
        print_info "macOS: brew install openjdk@17"
        return 1
    fi
}

# 检查 Android SDK
check_android_sdk() {
    print_step "检查 Android SDK..."
    
    if [[ -n "$ANDROID_HOME" ]] && [[ -d "$ANDROID_HOME" ]]; then
        print_success "Android SDK 已配置 (路径: $ANDROID_HOME)"
        return 0
    elif [[ -n "$ANDROID_SDK_ROOT" ]] && [[ -d "$ANDROID_SDK_ROOT" ]]; then
        export ANDROID_HOME="$ANDROID_SDK_ROOT"
        print_success "Android SDK 已配置 (路径: $ANDROID_SDK_ROOT)"
        return 0
    else
        # 检查常见路径
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
        
        print_error "Android SDK 未找到"
        print_info "请设置 ANDROID_HOME 或 ANDROID_SDK_ROOT 环境变量"
        return 1
    fi
}

# 检查 gradlew
check_gradlew() {
    print_step "检查 Gradle 包装器..."
    
    if [[ -f "gradlew" ]]; then
        print_success "gradlew 已找到"
        chmod +x gradlew
        return 0
    else
        print_error "gradlew 未找到，请确保在正确的目录中运行此脚本"
        print_info "应该在 android-project 目录或 video-app/android 目录中运行"
        return 1
    fi
}

# 配置 Gradle
configure_gradle() {
    print_step "配置 Gradle..."
    
    if [[ ! -f "gradle.properties" ]]; then
        cat > gradle.properties << EOF
# Gradle 配置 (Gradle Configuration)
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8
org.gradle.parallel=true
org.gradle.caching=true
android.useAndroidX=true
android.enableJetifier=true
EOF
        print_success "gradle.properties 已创建"
    else
        print_info "gradle.properties 已存在"
    fi
}

# 构建 APK
build_apk() {
    print_step "开始构建 $BUILD_TYPE APK..."
    
    ./gradlew "$GRADLE_TASK" --no-daemon --stacktrace
    
    # 检查输出文件
    local apk_path="app/build/outputs/apk/$BUILD_TYPE/app-$BUILD_TYPE.apk"
    
    if [[ -f "$apk_path" ]]; then
        print_success "APK 构建成功!"
        print_info "APK 文件: $(pwd)/$apk_path"
        
        # 显示文件大小
        local file_size
        file_size=$(du -h "$apk_path" | cut -f1)
        print_info "文件大小: $file_size"
    else
        print_error "APK 文件未找到: $apk_path"
        return 1
    fi
}

# ============================================================================
# 主函数
# ============================================================================

main() {
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --debug)
                BUILD_TYPE="debug"
                GRADLE_TASK="assembleDebug"
                shift
                ;;
            --release)
                BUILD_TYPE="release"
                GRADLE_TASK="assembleRelease"
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
    
    print_header "APK 构建脚本"
    print_info "构建类型: $BUILD_TYPE"
    print_info "当前目录: $(pwd)"
    
    # 检查环境
    check_java || exit 1
    check_android_sdk || exit 1
    check_gradlew || exit 1
    
    # 配置和构建
    configure_gradle
    build_apk
    
    # 完成
    print_header "构建完成! 🎉"
}

# 运行主函数
main "$@"
