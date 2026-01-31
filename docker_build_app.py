#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker环境应用打包脚本 (Docker App Build Script)
================================================
在Docker环境中打包video-app并自动配置API接口

功能:
- 自动检测并安装Docker
- 自动配置API接口地址
- 自动修改前端配置文件
- 支持Web/Android/iOS多平台打包
- 支持调试版和发布版构建

使用方法:
    python3 docker_build_app.py                      # 构建Web版本
    python3 docker_build_app.py --platform android   # 构建Android APK
    python3 docker_build_app.py --platform ios       # 构建iOS项目
    python3 docker_build_app.py --release            # 构建发布版
    python3 docker_build_app.py --api-url http://your-api:5000  # 自定义API地址
    python3 docker_build_app.py --check              # 仅检查依赖
    python3 docker_build_app.py --clean              # 清理构建产物

作者: Auto-generated
日期: 2026-01-31
"""

import os
import sys
import subprocess
import argparse
import shutil
import json
import re
import time
from typing import Tuple, Optional
from urllib.parse import urlparse
from pathlib import Path


class Colors:
    """终端颜色常量 (Terminal color constants)"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str) -> None:
    """打印标题 (Print header)"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}{Colors.RESET}\n")


def print_step(text: str) -> None:
    """打印步骤 (Print step)"""
    print(f"{Colors.BLUE}[*]{Colors.RESET} {text}")


def print_success(text: str) -> None:
    """打印成功信息 (Print success message)"""
    print(f"{Colors.GREEN}[✓]{Colors.RESET} {text}")


def print_warning(text: str) -> None:
    """打印警告信息 (Print warning message)"""
    print(f"{Colors.YELLOW}[!]{Colors.RESET} {text}")


def print_error(text: str) -> None:
    """打印错误信息 (Print error message)"""
    print(f"{Colors.RED}[✗]{Colors.RESET} {text}")


def run_command(
    cmd: str,
    check: bool = True,
    capture: bool = False,
    shell: bool = True,
    cwd: Optional[str] = None
) -> Tuple[int, str, str]:
    """
    执行系统命令 (Execute system command)

    Args:
        cmd: 要执行的命令 (Command to execute)
        check: 是否检查返回码 (Whether to check return code)
        capture: 是否捕获输出 (Whether to capture output)
        shell: 是否使用shell执行 (Whether to use shell)
        cwd: 工作目录 (Working directory)

    Returns:
        (返回码, 标准输出, 标准错误)
        (return code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=capture,
            text=True,
            check=check,
            cwd=cwd
        )
        return (result.returncode,
                result.stdout if capture else '',
                result.stderr if capture else '')
    except subprocess.CalledProcessError as e:
        return (e.returncode,
                e.stdout if capture else '',
                e.stderr if capture else '')
    except Exception as e:
        return (1, '', str(e))


def is_docker_installed() -> bool:
    """检查Docker是否已安装 (Check if Docker is installed)"""
    code, _, _ = run_command("docker --version", capture=True, check=False)
    return code == 0


def is_docker_running() -> bool:
    """检查Docker服务是否运行 (Check if Docker service is running)"""
    code, _, _ = run_command("docker info", capture=True, check=False)
    return code == 0


def check_docker() -> bool:
    """
    检查Docker环境 (Check Docker environment)

    Returns:
        是否就绪 (Whether ready)
    """
    print_step("检查Docker安装状态...")
    if not is_docker_installed():
        print_error("Docker未安装。请先安装Docker:")
        print("  Ubuntu: sudo apt-get install docker.io docker-compose")
        print("  macOS: 安装 Docker Desktop")
        print("  或运行: sudo python3 deploy.py 自动安装")
        return False

    print_success("Docker已安装")

    print_step("检查Docker服务状态...")
    if not is_docker_running():
        print_error("Docker服务未运行。请启动Docker:")
        print("  Linux: sudo systemctl start docker")
        print("  macOS: 启动 Docker Desktop")
        return False

    print_success("Docker服务运行中")
    return True


class APIConfigManager:
    """API配置管理器 (API Configuration Manager)"""

    def __init__(self, base_dir: str, api_url: str):
        """
        初始化配置管理器 (Initialize configuration manager)

        Args:
            base_dir: 项目根目录 (Project root directory)
            api_url: API服务器地址 (API server URL)
        """
        self.base_dir = Path(base_dir)
        self.video_app_dir = self.base_dir / "video-app"
        self.api_url = api_url.rstrip('/')

    def update_env_file(self) -> bool:
        """
        更新.env.local文件 (Update .env.local file)

        Returns:
            是否成功 (Whether successful)
        """
        print_step(f"配置API地址: {self.api_url}")

        env_file = self.video_app_dir / ".env.local"
        env_content = f"""# API Configuration
# Generated by docker_build_app.py

# The base URL of your API server (without /api suffix)
VITE_API_BASE_URL={self.api_url}
"""
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            print_success(f"已创建 .env.local: {env_file}")
            return True
        except Exception as e:
            print_error(f"创建 .env.local 失败: {e}")
            return False

    def update_config_js(self) -> bool:
        """
        更新config/index.js中的API配置 (Update API config in config/index.js)

        Returns:
            是否成功 (Whether successful)
        """
        config_file = self.video_app_dir / "config" / "index.js"

        if not config_file.exists():
            print_warning(f"配置文件不存在: {config_file}")
            return True  # 不是致命错误

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 替换DEFAULT_API_BASE_URL
            pattern = r"const DEFAULT_API_BASE_URL = '[^']*'"
            replacement = f"const DEFAULT_API_BASE_URL = '{self.api_url}'"

            if re.search(pattern, content):
                new_content = re.sub(pattern, replacement, content)
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print_success("已更新 config/index.js 中的API地址")
            else:
                print_warning("config/index.js 中未找到 DEFAULT_API_BASE_URL")

            return True
        except Exception as e:
            print_error(f"更新 config/index.js 失败: {e}")
            return False

    def update_capacitor_config(self) -> bool:
        """
        更新Capacitor配置 (Update Capacitor configuration)

        Returns:
            是否成功 (Whether successful)
        """
        config_file = self.video_app_dir / "capacitor.config.json"

        if not config_file.exists():
            print_warning(f"Capacitor配置文件不存在: {config_file}")
            return True

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 确保server配置存在
            if 'server' not in config:
                config['server'] = {}

            # 使用urlparse提取主机名 (Use urlparse to extract hostname)
            parsed_url = urlparse(self.api_url)
            hostname = parsed_url.hostname or parsed_url.netloc.split(':')[0]

            # 设置允许的URL (用于开发调试)
            config['server']['allowNavigation'] = [
                hostname + "*"
            ]

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            print_success("已更新 capacitor.config.json")
            return True
        except Exception as e:
            print_error(f"更新 capacitor.config.json 失败: {e}")
            return False

    def update_nginx_config(self) -> bool:
        """
        更新Nginx配置中的API代理 (Update API proxy in Nginx config)

        Returns:
            是否成功 (Whether successful)
        """
        nginx_file = self.video_app_dir / "nginx.conf"

        if not nginx_file.exists():
            print_warning(f"Nginx配置文件不存在: {nginx_file}")
            return True

        try:
            with open(nginx_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 替换proxy_pass配置
            # 查找 proxy_pass http://api:5000; 或类似模式
            pattern = r"proxy_pass http://[^;]+;"
            # 对于Docker内部，使用服务名api
            replacement = "proxy_pass http://api:5000;"

            if re.search(pattern, content):
                new_content = re.sub(pattern, replacement, content)
                with open(nginx_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print_success("已更新 nginx.conf 中的API代理配置")

            return True
        except Exception as e:
            print_error(f"更新 nginx.conf 失败: {e}")
            return False

    def configure_all(self) -> bool:
        """
        配置所有API相关设置 (Configure all API related settings)

        Returns:
            是否全部成功 (Whether all successful)
        """
        print_header("配置API接口")

        results = [
            self.update_env_file(),
            self.update_config_js(),
            self.update_capacitor_config(),
            self.update_nginx_config()
        ]

        if all(results):
            print_success("API配置完成!")
            return True
        else:
            print_warning("部分API配置失败，但可能不影响构建")
            return True  # 继续构建


class DockerBuilder:
    """Docker构建器 (Docker Builder)"""

    # 构建用Dockerfile模板
    BUILD_DOCKERFILE = '''# Multi-platform build environment
FROM node:20-alpine AS builder

# Install required packages
RUN apk add --no-cache bash git python3 make g++

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY patches ./patches
COPY scripts ./scripts

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build argument for API URL
ARG API_BASE_URL=http://103.74.193.179:5000
ENV VITE_API_BASE_URL=$API_BASE_URL

# Build the application
RUN npm run build

# Output stage - copy built files
FROM alpine:latest AS output
COPY --from=builder /app/dist /output/dist
'''

    ANDROID_DOCKERFILE = '''# Android build environment
FROM node:20-bookworm

# Install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \\
    bash \\
    git \\
    python3 \\
    make \\
    g++ \\
    wget \\
    unzip \\
    ca-certificates \\
    && rm -rf /var/lib/apt/lists/*

# Install OpenJDK 21 from Adoptium (Eclipse Temurin) with checksum verification
RUN mkdir -p /opt/java && \\
    wget -q https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.5%2B11/OpenJDK21U-jdk_x64_linux_hotspot_21.0.5_11.tar.gz -O /tmp/openjdk21.tar.gz && \\
    echo "5f6edef70086604dfa43ce83c78123e2ec065690731b77a1e126c1dbeba57020  /tmp/openjdk21.tar.gz" | sha256sum -c - && \\
    tar -xzf /tmp/openjdk21.tar.gz -C /opt/java && \\
    rm /tmp/openjdk21.tar.gz

# Set Java environment
ENV JAVA_HOME=/opt/java/jdk-21.0.5+11
ENV PATH=$JAVA_HOME/bin:$PATH

# Install Android SDK
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH

RUN mkdir -p $ANDROID_HOME/cmdline-tools && \\
    cd $ANDROID_HOME/cmdline-tools && \\
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O cmdline-tools.zip && \\
    unzip -q cmdline-tools.zip && \\
    mv cmdline-tools latest && \\
    rm cmdline-tools.zip

# Accept licenses and install required SDK components
RUN yes | sdkmanager --licenses && \\
    sdkmanager "platforms;android-34" "build-tools;34.0.0" "platform-tools"

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY patches ./patches
COPY scripts ./scripts

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build argument for API URL
ARG API_BASE_URL=http://103.74.193.179:5000
ENV VITE_API_BASE_URL=$API_BASE_URL

# Build web assets
RUN npm run build

# Add Android platform and sync
RUN npx cap add android || true
RUN npx cap sync android

# Build APK
ARG BUILD_TYPE=debug
WORKDIR /app/android
RUN if [ "$BUILD_TYPE" = "release" ]; then \\
        ./gradlew assembleRelease --no-daemon; \\
    else \\
        ./gradlew assembleDebug --no-daemon; \\
    fi

# Output stage
FROM alpine:latest AS output
ARG BUILD_TYPE=debug
COPY --from=0 /app/android/app/build/outputs/apk/$BUILD_TYPE/*.apk /output/
'''

    def __init__(self, base_dir: str, output_dir: str, platform: str = 'web',
                 release: bool = False, api_url: str = 'http://103.74.193.179:5000',
                 no_cache: bool = False):
        """
        初始化构建器 (Initialize builder)

        Args:
            base_dir: 项目根目录 (Project root directory)
            output_dir: 输出目录 (Output directory)
            platform: 目标平台 (Target platform): web, android, ios
            release: 是否构建发布版 (Whether to build release version)
            api_url: API服务器地址 (API server URL)
            no_cache: 是否禁用缓存 (Whether to disable cache)
        """
        self.base_dir = Path(base_dir)
        self.output_dir = Path(output_dir)
        self.video_app_dir = self.base_dir / "video-app"
        self.platform = platform
        self.release = release
        self.api_url = api_url
        self.no_cache = no_cache
        self.image_name = f"video-app-builder-{platform}"

    def prepare_output_dir(self) -> bool:
        """
        准备输出目录 (Prepare output directory)

        Returns:
            是否成功 (Whether successful)
        """
        print_step(f"准备输出目录: {self.output_dir}")
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            print_success("输出目录已就绪")
            return True
        except Exception as e:
            print_error(f"创建输出目录失败: {e}")
            return False

    def create_dockerfile(self) -> Tuple[bool, str]:
        """
        创建构建用Dockerfile (Create build Dockerfile)

        Returns:
            (是否成功, Dockerfile路径)
            (Whether successful, Dockerfile path)
        """
        dockerfile_path = self.video_app_dir / "Dockerfile.build"

        try:
            if self.platform == 'android':
                content = self.ANDROID_DOCKERFILE
            else:
                content = self.BUILD_DOCKERFILE

            with open(dockerfile_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print_success(f"已创建构建Dockerfile: {dockerfile_path}")
            return True, str(dockerfile_path)
        except Exception as e:
            print_error(f"创建Dockerfile失败: {e}")
            return False, ""

    def build_image(self, dockerfile_path: str) -> bool:
        """
        构建Docker镜像 (Build Docker image)

        Args:
            dockerfile_path: Dockerfile路径 (Dockerfile path)

        Returns:
            是否成功 (Whether successful)
        """
        print_header(f"构建Docker镜像 ({self.platform})")

        build_type = "release" if self.release else "debug"
        cache_flag = "--no-cache" if self.no_cache else ""

        cmd = (
            f"docker build "
            f"{cache_flag} "
            f"--build-arg API_BASE_URL={self.api_url} "
            f"--build-arg BUILD_TYPE={build_type} "
            f"-f {dockerfile_path} "
            f"-t {self.image_name} "
            f"."
        )

        print_step("执行构建命令...")
        print(f"  {cmd}")

        code, _, _ = run_command(cmd, cwd=str(self.video_app_dir), check=False)

        if code != 0:
            print_error("Docker镜像构建失败")
            return False

        print_success("Docker镜像构建成功!")
        return True

    def extract_artifacts(self) -> bool:
        """
        从容器中提取构建产物 (Extract build artifacts from container)

        Returns:
            是否成功 (Whether successful)
        """
        print_header("提取构建产物")

        container_name = f"video-app-extract-{int(time.time())}"

        try:
            # 创建临时容器
            print_step("创建临时容器...")
            code, _, _ = run_command(
                f"docker create --name {container_name} {self.image_name}",
                capture=True,
                check=False
            )

            if code != 0:
                print_error("创建临时容器失败")
                return False

            # 复制构建产物
            if self.platform == 'web':
                output_subdir = self.output_dir / "web"
                output_subdir.mkdir(parents=True, exist_ok=True)

                print_step("复制Web构建产物...")
                code, _, _ = run_command(
                    f"docker cp {container_name}:/output/dist/. {output_subdir}/",
                    check=False
                )
            elif self.platform == 'android':
                output_subdir = self.output_dir / "android"
                output_subdir.mkdir(parents=True, exist_ok=True)

                print_step("复制Android APK...")
                code, _, _ = run_command(
                    f"docker cp {container_name}:/output/. {output_subdir}/",
                    check=False
                )

            if code != 0:
                print_error("复制构建产物失败")
                return False

            print_success(f"构建产物已保存到: {output_subdir}")
            return True

        finally:
            # 清理临时容器
            run_command(f"docker rm -f {container_name}", check=False, capture=True)

    def cleanup_dockerfile(self, dockerfile_path: str) -> None:
        """
        清理构建用Dockerfile (Cleanup build Dockerfile)

        Args:
            dockerfile_path: Dockerfile路径 (Dockerfile path)
        """
        try:
            if os.path.exists(dockerfile_path):
                os.remove(dockerfile_path)
                print_step("已清理临时Dockerfile")
        except Exception:
            pass  # 忽略清理错误

    def build(self) -> bool:
        """
        执行完整构建流程 (Execute complete build process)

        Returns:
            是否成功 (Whether successful)
        """
        print_header(f"开始构建 video-app ({self.platform})")

        # 准备输出目录
        if not self.prepare_output_dir():
            return False

        # 创建Dockerfile
        success, dockerfile_path = self.create_dockerfile()
        if not success:
            return False

        try:
            # 构建镜像
            if not self.build_image(dockerfile_path):
                return False

            # 提取产物
            if not self.extract_artifacts():
                return False

            print_success("构建完成!")
            return True

        finally:
            # 清理临时文件
            self.cleanup_dockerfile(dockerfile_path)


def clean_build_artifacts(base_dir: str, output_dir: str) -> bool:
    """
    清理构建产物和Docker镜像 (Clean build artifacts and Docker images)

    Args:
        base_dir: 项目根目录 (Project root directory)
        output_dir: 输出目录 (Output directory)

    Returns:
        是否成功 (Whether successful)
    """
    print_header("清理构建产物")

    # 清理输出目录
    if os.path.exists(output_dir):
        print_step(f"清理输出目录: {output_dir}")
        try:
            shutil.rmtree(output_dir)
            print_success("输出目录已清理")
        except Exception as e:
            print_warning(f"清理输出目录失败: {e}")

    # 清理临时Dockerfile
    video_app_dir = os.path.join(base_dir, "video-app")
    dockerfile_build = os.path.join(video_app_dir, "Dockerfile.build")
    if os.path.exists(dockerfile_build):
        os.remove(dockerfile_build)
        print_success("临时Dockerfile已清理")

    # 清理Docker镜像
    print_step("清理Docker镜像...")
    for platform in ['web', 'android', 'ios']:
        image_name = f"video-app-builder-{platform}"
        run_command(f"docker rmi -f {image_name}", check=False, capture=True)

    print_success("构建产物清理完成!")
    return True


def show_build_summary(output_dir: str, platform: str, api_url: str) -> None:
    """
    显示构建摘要 (Show build summary)

    Args:
        output_dir: 输出目录 (Output directory)
        platform: 目标平台 (Target platform)
        api_url: API服务器地址 (API server URL)
    """
    print_header("构建摘要")

    print(f"  平台: {platform}")
    print(f"  API地址: {api_url}")
    print(f"  输出目录: {output_dir}")
    print()

    output_path = Path(output_dir)
    if output_path.exists():
        print("  构建产物:")
        for item in output_path.rglob('*'):
            if item.is_file():
                size = item.stat().st_size
                size_str = f"{size / 1024 / 1024:.2f} MB" if size > 1024 * 1024 else f"{size / 1024:.2f} KB"
                print(f"    - {item.relative_to(output_path)} ({size_str})")


def main() -> None:
    """主函数 (Main function)"""
    parser = argparse.ArgumentParser(
        description='Docker环境应用打包脚本 (Docker App Build Script)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例 (Examples):
  python3 docker_build_app.py                              # 构建Web版本
  python3 docker_build_app.py --platform android           # 构建Android APK
  python3 docker_build_app.py --platform android --release # 构建发布版APK
  python3 docker_build_app.py --api-url http://myserver:5000  # 自定义API地址
  python3 docker_build_app.py --check                      # 仅检查依赖
  python3 docker_build_app.py --clean                      # 清理构建产物
        '''
    )

    parser.add_argument('--platform', type=str, default='web',
                        choices=['web', 'android', 'ios'],
                        help='目标平台 (Target platform): web, android, ios (默认: web)')
    parser.add_argument('--release', action='store_true',
                        help='构建发布版而非调试版 (Build release instead of debug)')
    parser.add_argument('--api-url', type=str, default='http://103.74.193.179:5000',
                        help='API服务器地址 (API server URL)')
    parser.add_argument('--check', action='store_true',
                        help='仅检查依赖，不构建 (Check dependencies only)')
    parser.add_argument('--clean', action='store_true',
                        help='清理构建产物和Docker镜像 (Clean build artifacts)')
    parser.add_argument('--no-cache', action='store_true',
                        help='禁用Docker缓存，强制完整重建 (Disable Docker cache)')
    parser.add_argument('--dir', type=str, default=None,
                        help='项目目录 (Project directory, 默认: 脚本所在目录)')
    parser.add_argument('--output', type=str, default=None,
                        help='输出目录 (Output directory, 默认: build-output)')
    parser.add_argument('--skip-api-config', action='store_true',
                        help='跳过API配置步骤 (Skip API configuration)')

    args = parser.parse_args()

    # 获取项目目录
    if args.dir:
        base_dir = os.path.abspath(args.dir)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # 获取输出目录
    if args.output:
        output_dir = os.path.abspath(args.output)
    else:
        output_dir = os.path.join(base_dir, "build-output")

    print_header("Video-App Docker 构建工具")
    print(f"项目目录: {base_dir}")
    print(f"输出目录: {output_dir}")
    print(f"目标平台: {args.platform}")
    print(f"API地址: {args.api_url}")

    # 清理模式
    if args.clean:
        if clean_build_artifacts(base_dir, output_dir):
            sys.exit(0)
        sys.exit(1)

    # 检查Docker环境
    if not check_docker():
        sys.exit(1)

    # 仅检查模式
    if args.check:
        print_success("依赖检查完成!")
        sys.exit(0)

    # 配置API (除非跳过)
    if not args.skip_api_config:
        api_manager = APIConfigManager(base_dir, args.api_url)
        if not api_manager.configure_all():
            print_warning("API配置部分失败，继续构建...")

    # iOS平台提示
    if args.platform == 'ios':
        print_warning("iOS构建需要macOS环境和Xcode")
        print("请在macOS上运行以下命令:")
        print("  cd video-app")
        print("  npm run build")
        print("  npx cap add ios")
        print("  npx cap sync ios")
        print("  npx cap open ios")
        sys.exit(0)

    # 执行构建
    builder = DockerBuilder(
        base_dir=base_dir,
        output_dir=output_dir,
        platform=args.platform,
        release=args.release,
        api_url=args.api_url,
        no_cache=args.no_cache
    )

    if builder.build():
        show_build_summary(output_dir, args.platform, args.api_url)
        print_header("构建成功! 🎉")
        sys.exit(0)
    else:
        print_error("构建失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
