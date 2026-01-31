#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker环境APK打包脚本 (Docker APK Build Script)
=================================================

功能 (Features):
- 自动检测并验证Docker环境
- 自动检测并安装必要依赖
- 在Docker容器中构建Android APK
- 完善的错误检测和处理机制
- 确保一次打包成功

使用方法 (Usage):
    python3 docker_build_apk.py                # 完整构建APK
    python3 docker_build_apk.py --check        # 仅检查依赖
    python3 docker_build_apk.py --clean        # 清理构建产物
    python3 docker_build_apk.py --release      # 构建Release版本
    python3 docker_build_apk.py --no-cache     # 不使用Docker缓存

作者: Auto-generated
日期: 2026-01-31
"""

import os
import sys
import subprocess
import shutil
import argparse
import time
import platform
import json
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Any
from dataclasses import dataclass, field


# ============================================================================
# 版本配置 (Version Configuration)
# ============================================================================
@dataclass
class BuildConfig:
    """构建配置"""
    android_sdk_version: str = "11076708"
    android_platform_version: str = "34"
    android_build_tools_version: str = "34.0.0"
    node_version: str = "20"
    java_version: str = "17"
    docker_image_name: str = "video-app-apk-builder"
    apk_output_name: str = "video-app"


# ============================================================================
# 颜色输出 (Color Output)
# ============================================================================
class Colors:
    """终端颜色常量"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class Logger:
    """日志输出类"""
    
    @staticmethod
    def header(text: str) -> None:
        """打印标题"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}")
        print(f"  {text}")
        print(f"{'=' * 70}{Colors.RESET}\n")
    
    @staticmethod
    def step(text: str) -> None:
        """打印步骤"""
        print(f"{Colors.BLUE}[*]{Colors.RESET} {text}")
    
    @staticmethod
    def success(text: str) -> None:
        """打印成功信息"""
        print(f"{Colors.GREEN}[✓]{Colors.RESET} {text}")
    
    @staticmethod
    def warning(text: str) -> None:
        """打印警告信息"""
        print(f"{Colors.YELLOW}[!]{Colors.RESET} {text}")
    
    @staticmethod
    def error(text: str) -> None:
        """打印错误信息"""
        print(f"{Colors.RED}[✗]{Colors.RESET} {text}")
    
    @staticmethod
    def info(text: str) -> None:
        """打印信息"""
        print(f"{Colors.CYAN}[i]{Colors.RESET} {text}")
    
    @staticmethod
    def debug(text: str) -> None:
        """打印调试信息"""
        print(f"{Colors.MAGENTA}[D]{Colors.RESET} {text}")


log = Logger()


# ============================================================================
# 系统命令执行 (System Command Execution)
# ============================================================================
class CommandRunner:
    """命令执行器"""
    
    @staticmethod
    def run(
        cmd: str,
        capture: bool = False,
        check: bool = True,
        shell: bool = True,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Tuple[int, str, str]:
        """
        执行系统命令
        
        Args:
            cmd: 要执行的命令
            capture: 是否捕获输出
            check: 是否检查返回码
            shell: 是否使用shell执行
            cwd: 工作目录
            env: 环境变量
            timeout: 超时时间(秒)
            
        Returns:
            (返回码, 标准输出, 标准错误)
        """
        try:
            # 合并环境变量
            run_env = os.environ.copy()
            if env:
                run_env.update(env)
            
            result = subprocess.run(
                cmd,
                shell=shell,
                capture_output=capture,
                text=True,
                check=False,  # We handle manually
                cwd=cwd,
                env=run_env,
                timeout=timeout
            )
            
            if check and result.returncode != 0:
                log.error(f"命令执行失败: {cmd}")
                if capture and result.stderr:
                    log.error(f"错误信息: {result.stderr}")
            
            return (
                result.returncode,
                result.stdout if capture else '',
                result.stderr if capture else ''
            )
        except subprocess.TimeoutExpired:
            log.error(f"命令执行超时: {cmd}")
            return (1, '', 'Command timed out')
        except Exception as e:
            log.error(f"命令执行异常: {e}")
            return (1, '', str(e))
    
    @staticmethod
    def run_with_output(
        cmd: str,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> int:
        """
        执行命令并实时输出
        
        Args:
            cmd: 要执行的命令
            cwd: 工作目录
            env: 环境变量
            
        Returns:
            返回码
        """
        try:
            run_env = os.environ.copy()
            if env:
                run_env.update(env)
            
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=cwd,
                env=run_env,
                bufsize=1
            )
            
            # 实时输出
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    print(f"    {line.rstrip()}")
            
            return process.returncode
        except Exception as e:
            log.error(f"命令执行异常: {e}")
            return 1


runner = CommandRunner()


# ============================================================================
# 系统检测 (System Detection)
# ============================================================================
class SystemDetector:
    """系统检测器"""
    
    @staticmethod
    def detect_os() -> str:
        """检测操作系统类型"""
        system = platform.system().lower()
        if system == 'linux':
            # 检测Linux发行版
            if shutil.which('apt-get'):
                return 'ubuntu'
            elif shutil.which('yum'):
                return 'centos'
            elif shutil.which('dnf'):
                return 'fedora'
            return 'linux'
        elif system == 'darwin':
            return 'macos'
        elif system == 'windows':
            return 'windows'
        return 'unknown'
    
    @staticmethod
    def is_root() -> bool:
        """检查是否为root用户"""
        try:
            return os.geteuid() == 0
        except AttributeError:
            # Windows
            return False
    
    @staticmethod
    def command_exists(cmd: str) -> bool:
        """检查命令是否存在"""
        return shutil.which(cmd) is not None
    
    @staticmethod
    def get_command_version(cmd: str, version_arg: str = '--version') -> Optional[str]:
        """获取命令版本"""
        code, stdout, stderr = runner.run(
            f"{cmd} {version_arg}",
            capture=True,
            check=False
        )
        if code == 0:
            return stdout.strip() or stderr.strip()
        return None


detector = SystemDetector()


# ============================================================================
# 依赖检测器 (Dependency Checker)
# ============================================================================
@dataclass
class DependencyStatus:
    """依赖状态"""
    name: str
    installed: bool
    version: Optional[str] = None
    required: bool = True
    message: str = ""


class DependencyChecker:
    """依赖检测器"""
    
    def __init__(self, config: BuildConfig):
        self.config = config
    
    def check_docker(self) -> DependencyStatus:
        """检查Docker"""
        log.step("检查 Docker 安装状态...")
        
        if not detector.command_exists('docker'):
            return DependencyStatus(
                name="Docker",
                installed=False,
                message="Docker 未安装，请先安装 Docker"
            )
        
        version = detector.get_command_version('docker')
        
        # 检查Docker服务是否运行
        code, _, _ = runner.run("docker info", capture=True, check=False)
        if code != 0:
            return DependencyStatus(
                name="Docker",
                installed=True,
                version=version,
                message="Docker 服务未运行，请启动 Docker 服务"
            )
        
        log.success(f"Docker 已安装且运行中 ({version})")
        return DependencyStatus(
            name="Docker",
            installed=True,
            version=version
        )
    
    def check_docker_compose(self) -> DependencyStatus:
        """检查Docker Compose"""
        log.step("检查 Docker Compose 安装状态...")
        
        # 检查 docker compose (V2)
        code, stdout, _ = runner.run(
            "docker compose version",
            capture=True,
            check=False
        )
        if code == 0:
            log.success(f"Docker Compose 已安装 ({stdout.strip()})")
            return DependencyStatus(
                name="Docker Compose",
                installed=True,
                version=stdout.strip()
            )
        
        # 检查 docker-compose (V1)
        if detector.command_exists('docker-compose'):
            version = detector.get_command_version('docker-compose')
            log.success(f"Docker Compose 已安装 ({version})")
            return DependencyStatus(
                name="Docker Compose",
                installed=True,
                version=version
            )
        
        return DependencyStatus(
            name="Docker Compose",
            installed=False,
            required=False,
            message="Docker Compose 未安装 (可选)"
        )
    
    def check_project_files(self, project_dir: Path) -> DependencyStatus:
        """检查项目文件完整性"""
        log.step("检查项目文件完整性...")
        
        required_files = [
            'video-app/package.json',
            'video-app/capacitor.config.json',
            'video-app/vite.config.js',
            'video-app/index.html',
        ]
        
        required_dirs = [
            'video-app/src',
            'video-app/patches',
            'video-app/scripts',
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (project_dir / file_path).exists():
                missing_files.append(file_path)
        
        for dir_path in required_dirs:
            if not (project_dir / dir_path).is_dir():
                missing_files.append(dir_path)
        
        if missing_files:
            log.error(f"缺少必要文件: {', '.join(missing_files)}")
            return DependencyStatus(
                name="项目文件",
                installed=False,
                message=f"缺少必要文件: {', '.join(missing_files)}"
            )
        
        log.success("项目文件完整")
        return DependencyStatus(
            name="项目文件",
            installed=True
        )
    
    def check_all(self, project_dir: Path) -> Tuple[bool, List[DependencyStatus]]:
        """检查所有依赖"""
        log.header("检查系统依赖")
        
        statuses = []
        all_ok = True
        
        # 检测操作系统
        os_type = detector.detect_os()
        log.info(f"操作系统: {os_type}")
        
        # 检查Docker (必需)
        docker_status = self.check_docker()
        statuses.append(docker_status)
        if not docker_status.installed or docker_status.message:
            all_ok = False
        
        # 检查Docker Compose (可选)
        compose_status = self.check_docker_compose()
        statuses.append(compose_status)
        
        # 检查项目文件
        files_status = self.check_project_files(project_dir)
        statuses.append(files_status)
        if not files_status.installed:
            all_ok = False
        
        return all_ok, statuses


# ============================================================================
# Docker构建器 (Docker Builder)
# ============================================================================
class DockerAPKBuilder:
    """Docker APK构建器"""
    
    def __init__(self, config: BuildConfig, project_dir: Path, output_dir: Path):
        self.config = config
        self.project_dir = project_dir
        self.output_dir = output_dir
        self.docker_build_dir = project_dir / '.docker-apk-build'
    
    def _create_dockerfile(self, release: bool = False) -> Path:
        """创建Dockerfile"""
        log.step("生成 Dockerfile...")
        
        self.docker_build_dir.mkdir(parents=True, exist_ok=True)
        dockerfile_path = self.docker_build_dir / 'Dockerfile'
        
        build_type = "Release" if release else "Debug"
        gradle_task = "assembleRelease" if release else "assembleDebug"
        apk_subdir = "release" if release else "debug"
        apk_name = f"app-{apk_subdir}.apk"
        
        dockerfile_content = f'''# ============================================================================
# Docker APK Build Image
# Auto-generated on {time.strftime("%Y-%m-%d %H:%M:%S")}
# ============================================================================

FROM node:{self.config.node_version}-bookworm

# 设置环境变量，避免交互式安装
ENV DEBIAN_FRONTEND=noninteractive

# 安装必要的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \\
    openjdk-{self.config.java_version}-jdk \\
    wget \\
    unzip \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# 设置 Java 环境变量
ENV JAVA_HOME=/usr/lib/jvm/java-{self.config.java_version}-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# 设置 Android SDK 环境变量
ENV ANDROID_HOME=/opt/android-sdk
ENV ANDROID_SDK_ROOT=$ANDROID_HOME
ENV PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

# Install Android SDK
RUN mkdir -p $ANDROID_HOME/cmdline-tools && \\
    echo ">>> Downloading Android command-line tools..." && \\
    wget https://dl.google.com/android/repository/commandlinetools-linux-{self.config.android_sdk_version}_latest.zip -O /tmp/cmdline-tools.zip && \\
    echo ">>> Extracting Android command-line tools..." && \\
    unzip -q /tmp/cmdline-tools.zip -d $ANDROID_HOME/cmdline-tools && \\
    mv $ANDROID_HOME/cmdline-tools/cmdline-tools $ANDROID_HOME/cmdline-tools/latest && \\
    rm /tmp/cmdline-tools.zip && \\
    echo ">>> Accepting Android SDK licenses..." && \\
    (yes | sdkmanager --licenses > /dev/null 2>&1; exit_code=$?; if [ $exit_code -ne 0 ] && [ $exit_code -ne 141 ]; then echo "Warning: License acceptance returned $exit_code"; fi) && \\
    echo ">>> Installing Android SDK components..." && \\
    sdkmanager "platform-tools" "platforms;android-{self.config.android_platform_version}" "build-tools;{self.config.android_build_tools_version}" && \\
    echo ">>> Android SDK installation complete"

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json (利用Docker缓存)
COPY video-app/package*.json ./video-app/

# 复制 patches 目录 (patch-package postinstall 脚本需要)
COPY video-app/patches ./video-app/patches

# 复制 scripts 目录 (postinstall 脚本需要)
COPY video-app/scripts ./video-app/scripts

# 安装 npm 依赖 (postinstall 会运行 patch-package)
RUN echo ">>> 安装 npm 依赖..." && \\
    cd video-app && npm ci && \\
    echo ">>> npm 依赖安装完成"

# 复制剩余的前端源代码
COPY video-app/src ./video-app/src
COPY video-app/index.html ./video-app/
COPY video-app/vite.config.js ./video-app/
COPY video-app/capacitor.config.json ./video-app/

# 构建 Web 应用
RUN echo ">>> 构建 Web 应用..." && \\
    cd video-app && npm run build && \\
    echo ">>> Web 应用构建完成"

# 添加 Android 平台并构建 APK
RUN echo ">>> 添加 Android 平台..." && \\
    cd video-app && \\
    npx cap add android && \\
    echo ">>> 同步 Web 资源到 Android..." && \\
    npx cap sync android && \\
    echo ">>> 配置 Gradle 设置..." && \\
    mkdir -p android/.gradle && \\
    echo "# Memory settings - optimized for Docker builds" > android/gradle.properties && \\
    echo "org.gradle.jvmargs=-Xmx2048m -XX:MaxMetaspaceSize=512m -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8" >> android/gradle.properties && \\
    echo "# Limit workers to prevent memory issues" >> android/gradle.properties && \\
    echo "org.gradle.workers.max=2" >> android/gradle.properties && \\
    echo "# Disable parallel and caching for more stable Docker builds" >> android/gradle.properties && \\
    echo "org.gradle.parallel=false" >> android/gradle.properties && \\
    echo "org.gradle.caching=false" >> android/gradle.properties && \\
    echo "# Disable file locking for containerized environments" >> android/gradle.properties && \\
    echo "org.gradle.daemon=false" >> android/gradle.properties && \\
    echo "org.gradle.vfs.watch=false" >> android/gradle.properties && \\
    echo "# Enable AndroidX compatibility" >> android/gradle.properties && \\
    echo "android.useAndroidX=true" >> android/gradle.properties && \\
    echo "# Network timeout settings for Docker builds" >> android/gradle.properties && \\
    echo "systemProp.org.gradle.internal.http.connectionTimeout=120000" >> android/gradle.properties && \\
    echo "systemProp.org.gradle.internal.http.socketTimeout=120000" >> android/gradle.properties && \\
    echo ">>> 使用 Gradle 构建 {build_type} APK..." && \\
    cd android && \\
    ./gradlew {gradle_task} --no-daemon --stacktrace --max-workers=2 --no-watch-fs --warning-mode=all && \\
    echo ">>> APK 构建完成"

# 创建输出目录并复制APK
RUN mkdir -p /output && \\
    cp video-app/android/app/build/outputs/apk/{apk_subdir}/{apk_name} /output/{self.config.apk_output_name}-{apk_subdir}.apk && \\
    echo ">>> APK 已复制到输出目录"

# 验证APK文件
RUN echo ">>> 验证 APK 文件..." && \\
    ls -la /output/ && \\
    file /output/{self.config.apk_output_name}-{apk_subdir}.apk && \\
    echo ">>> APK 文件验证完成"
'''
        
        dockerfile_path.write_text(dockerfile_content)
        log.success(f"Dockerfile 已生成: {dockerfile_path}")
        
        return dockerfile_path
    
    def _create_dockerignore(self) -> Path:
        """创建.dockerignore文件"""
        dockerignore_path = self.project_dir / '.dockerignore.apk'
        
        dockerignore_content = '''# APK 构建时忽略的文件
.git
.gitignore
*.md
*.log
*.db

# 已有的构建产物
build-output/
.docker-build/
.docker-apk-build/

# 移动平台目录 (会在Docker中生成)
video-app/android/
video-app/ios/
video-app/dist/

# node_modules (会在Docker中安装)
video-app/node_modules/

# 其他不需要的文件
api/
*.pyc
__pycache__/
venv/
.env
.env.local
'''
        
        dockerignore_path.write_text(dockerignore_content)
        return dockerignore_path
    
    def build(self, release: bool = False, no_cache: bool = False) -> bool:
        """
        执行Docker构建
        
        Args:
            release: 是否构建Release版本
            no_cache: 是否禁用Docker缓存
            
        Returns:
            构建是否成功
        """
        log.header("开始构建 Android APK")
        
        build_type = "Release" if release else "Debug"
        apk_subdir = "release" if release else "debug"
        
        log.info(f"构建类型: {build_type}")
        log.info(f"项目目录: {self.project_dir}")
        log.info(f"输出目录: {self.output_dir}")
        
        # 显示版本配置
        log.info("版本配置:")
        log.info(f"  - Node.js: {self.config.node_version}")
        log.info(f"  - Java: {self.config.java_version}")
        log.info(f"  - Android SDK: {self.config.android_sdk_version}")
        log.info(f"  - Android 平台: {self.config.android_platform_version}")
        log.info(f"  - 构建工具: {self.config.android_build_tools_version}")
        
        # 创建Dockerfile
        dockerfile_path = self._create_dockerfile(release)
        
        # 创建.dockerignore
        dockerignore_path = self._create_dockerignore()
        
        try:
            # 构建Docker镜像
            log.step("构建 Docker 镜像 (这可能需要几分钟)...")
            
            cache_option = "--no-cache" if no_cache else ""
            build_cmd = (
                f"docker build "
                f"-f {dockerfile_path} "
                f"--progress=plain "
                f"{cache_option} "
                f"-t {self.config.docker_image_name}:{apk_subdir} "
                f"."
            )
            
            return_code = runner.run_with_output(build_cmd, cwd=str(self.project_dir))
            
            if return_code != 0:
                log.error("Docker 镜像构建失败")
                return False
            
            log.success("Docker 镜像构建成功")
            
            # 从容器中提取APK
            log.step("从容器中提取 APK 文件...")
            
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # 删除已存在的临时容器 (ignore errors if container doesn't exist)
            runner.run(
                "docker rm -f apk-temp-container",
                capture=True,
                check=False
            )
            
            # 创建临时容器
            code, _, _ = runner.run(
                f"docker create --name apk-temp-container "
                f"{self.config.docker_image_name}:{apk_subdir}",
                capture=True
            )
            
            if code != 0:
                log.error("创建临时容器失败")
                return False
            
            # 复制APK文件
            apk_filename = f"{self.config.apk_output_name}-{apk_subdir}.apk"
            code, _, _ = runner.run(
                f"docker cp apk-temp-container:/output/{apk_filename} "
                f"{self.output_dir}/{apk_filename}"
            )
            
            # 清理临时容器
            runner.run("docker rm apk-temp-container", check=False)
            
            if code != 0:
                log.error("提取 APK 文件失败")
                return False
            
            # 验证APK文件
            apk_path = self.output_dir / apk_filename
            if not apk_path.exists():
                log.error(f"APK 文件不存在: {apk_path}")
                return False
            
            apk_size = apk_path.stat().st_size
            apk_size_mb = apk_size / (1024 * 1024)
            
            log.success(f"APK 构建成功!")
            log.success(f"文件路径: {apk_path}")
            log.success(f"文件大小: {apk_size_mb:.2f} MB")
            
            return True
            
        except Exception as e:
            log.error(f"构建过程发生异常: {e}")
            return False
        
        finally:
            # 清理临时文件
            if dockerignore_path.exists():
                dockerignore_path.unlink()
    
    def _create_project_only_dockerfile(self) -> Path:
        """创建仅导出 Android 项目的 Dockerfile (不执行 Gradle 构建)"""
        log.step("生成 Android 项目导出 Dockerfile...")
        
        self.docker_build_dir.mkdir(parents=True, exist_ok=True)
        dockerfile_path = self.docker_build_dir / 'Dockerfile.project-only'
        
        dockerfile_content = f'''# ============================================================================
# Docker Android 项目导出镜像 (不执行 Gradle 构建)
# Docker Android Project Export Image (No Gradle Build)
# 自动生成于 {time.strftime("%Y-%m-%d %H:%M:%S")}
# ============================================================================
# 此镜像仅导出 Android 项目，不执行 Gradle 构建
# 可以使用 Android Studio 或 GitHub Actions 构建 APK

FROM node:{self.config.node_version}-bookworm

# 设置环境变量，避免交互式安装
ENV DEBIAN_FRONTEND=noninteractive

# 安装必要的系统依赖 (不需要完整的 Android SDK)
RUN apt-get update && apt-get install -y --no-install-recommends \\
    openjdk-{self.config.java_version}-jdk \\
    wget \\
    unzip \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# 设置 Java 环境变量
ENV JAVA_HOME=/usr/lib/jvm/java-{self.config.java_version}-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json (利用Docker缓存)
COPY video-app/package*.json ./video-app/

# 复制 patches 目录 (patch-package postinstall 脚本需要)
COPY video-app/patches ./video-app/patches

# 复制 scripts 目录 (postinstall 脚本需要)
COPY video-app/scripts ./video-app/scripts

# 安装 npm 依赖 (postinstall 会运行 patch-package)
RUN echo ">>> 安装 npm 依赖..." && \\
    cd video-app && npm ci && \\
    echo ">>> npm 依赖安装完成"

# 复制剩余的前端源代码
COPY video-app/src ./video-app/src
COPY video-app/index.html ./video-app/
COPY video-app/vite.config.js ./video-app/
COPY video-app/capacitor.config.json ./video-app/

# 构建 Web 应用
RUN echo ">>> 构建 Web 应用..." && \\
    cd video-app && npm run build && \\
    echo ">>> Web 应用构建完成"

# 添加 Android 平台 (不执行 Gradle 构建)
RUN echo ">>> 添加 Android 平台..." && \\
    cd video-app && \\
    npx cap add android && \\
    echo ">>> 同步 Web 资源到 Android..." && \\
    npx cap sync android && \\
    echo ">>> Android 项目已准备就绪 (未执行 Gradle 构建)"

# 创建输出目录并复制 Android 项目
RUN mkdir -p /output && \\
    cp -r video-app/android /output/android-project && \\
    echo ">>> Android 项目已复制到输出目录"

# 添加使用说明
RUN echo "================================================" > /output/README.txt && \\
    echo "Android 项目导出成功!" >> /output/README.txt && \\
    echo "================================================" >> /output/README.txt && \\
    echo "" >> /output/README.txt && \\
    echo "构建 APK 的方法:" >> /output/README.txt && \\
    echo "" >> /output/README.txt && \\
    echo "方法 1: 使用 Android Studio" >> /output/README.txt && \\
    echo "  1. 用 Android Studio 打开 android-project 目录" >> /output/README.txt && \\
    echo "  2. 等待 Gradle 同步完成" >> /output/README.txt && \\
    echo "  3. 点击 Build > Build Bundle(s) / APK(s) > Build APK(s)" >> /output/README.txt && \\
    echo "" >> /output/README.txt && \\
    echo "方法 2: 使用 GitHub Actions" >> /output/README.txt && \\
    echo "  1. 将代码推送到 GitHub" >> /output/README.txt && \\
    echo "  2. 在 Actions 页面触发 Build Android APK 工作流程" >> /output/README.txt && \\
    echo "  3. 下载构建完成的 APK" >> /output/README.txt && \\
    echo "" >> /output/README.txt && \\
    echo "方法 3: 命令行构建" >> /output/README.txt && \\
    echo "  cd android-project" >> /output/README.txt && \\
    echo "  ./gradlew assembleDebug" >> /output/README.txt && \\
    echo "" >> /output/README.txt
'''
        
        dockerfile_path.write_text(dockerfile_content)
        log.success(f"Dockerfile 已生成: {dockerfile_path}")
        
        return dockerfile_path
    
    def export_project_only(self, no_cache: bool = False) -> bool:
        """
        仅导出 Android 项目，不执行 Gradle 构建
        
        Args:
            no_cache: 是否禁用 Docker 缓存
            
        Returns:
            导出是否成功
        """
        log.header("导出 Android 项目 (不执行 Gradle 构建)")
        
        log.info(f"项目目录: {self.project_dir}")
        log.info(f"输出目录: {self.output_dir}")
        log.info("此模式仅导出 Android 项目，您可以使用以下方式构建 APK:")
        log.info("  1. Android Studio")
        log.info("  2. GitHub Actions")
        log.info("  3. 本地 Gradle 命令行")
        
        # 创建 Dockerfile
        dockerfile_path = self._create_project_only_dockerfile()
        
        # 创建 .dockerignore
        dockerignore_path = self._create_dockerignore()
        
        try:
            # 构建 Docker 镜像
            log.step("构建 Docker 镜像 (仅准备 Android 项目)...")
            
            cache_option = "--no-cache" if no_cache else ""
            build_cmd = (
                f"docker build "
                f"-f {dockerfile_path} "
                f"--progress=plain "
                f"{cache_option} "
                f"-t {self.config.docker_image_name}:project-only "
                f"."
            )
            
            return_code = runner.run_with_output(build_cmd, cwd=str(self.project_dir))
            
            if return_code != 0:
                log.error("Docker 镜像构建失败")
                return False
            
            log.success("Docker 镜像构建成功")
            
            # 从容器中提取 Android 项目
            log.step("从容器中提取 Android 项目...")
            
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # 删除已存在的临时容器 (ignore errors if container doesn't exist)
            runner.run(
                "docker rm -f project-temp-container",
                capture=True,
                check=False
            )
            
            # 创建临时容器
            code, _, _ = runner.run(
                f"docker create --name project-temp-container "
                f"{self.config.docker_image_name}:project-only",
                capture=True
            )
            
            if code != 0:
                log.error("创建临时容器失败")
                return False
            
            # 复制 Android 项目
            project_output_dir = self.output_dir / 'android-project'
            if project_output_dir.exists():
                shutil.rmtree(project_output_dir)
            
            code, _, _ = runner.run(
                f"docker cp project-temp-container:/output/android-project "
                f"{self.output_dir}/"
            )
            
            # 复制说明文件
            runner.run(
                f"docker cp project-temp-container:/output/README.txt "
                f"{self.output_dir}/",
                check=False
            )
            
            # 清理临时容器
            runner.run("docker rm project-temp-container", check=False)
            
            if code != 0:
                log.error("提取 Android 项目失败")
                return False
            
            # 验证项目目录
            if not project_output_dir.exists():
                log.error(f"Android 项目目录不存在: {project_output_dir}")
                return False
            
            log.success(f"Android 项目导出成功!")
            log.success(f"项目路径: {project_output_dir}")
            log.info("")
            log.info("下一步操作:")
            log.info("  1. 使用 Android Studio 打开项目并构建 APK")
            log.info("  2. 或使用 GitHub Actions 自动构建 (推荐)")
            log.info("     运行: python3 docker_build_apk.py --use-actions 查看详情")
            
            return True
            
        except Exception as e:
            log.error(f"导出过程发生异常: {e}")
            return False
        
        finally:
            # 清理临时文件
            if dockerignore_path.exists():
                dockerignore_path.unlink()
    
    def clean(self) -> bool:
        """清理构建产物"""
        log.header("清理构建产物")
        
        cleaned = False
        
        # 清理Docker构建目录
        if self.docker_build_dir.exists():
            log.step(f"删除 Docker 构建目录: {self.docker_build_dir}")
            shutil.rmtree(self.docker_build_dir)
            log.success("Docker 构建目录已清理")
            cleaned = True
        
        # 清理输出目录
        if self.output_dir.exists():
            log.step(f"删除输出目录: {self.output_dir}")
            shutil.rmtree(self.output_dir)
            log.success("输出目录已清理")
            cleaned = True
        
        # 清理Docker镜像 (Clean Docker images)
        for build_type in ['debug', 'release', 'project-only']:
            image_name = f"{self.config.docker_image_name}:{build_type}"
            # Check if image exists before attempting removal
            check_code, stdout, _ = runner.run(
                f"docker images -q {image_name}",
                capture=True,
                check=False
            )
            if check_code == 0 and stdout.strip():
                code, _, _ = runner.run(
                    f"docker rmi {image_name}",
                    capture=True,
                    check=False
                )
                if code == 0:
                    log.success(f"Docker 镜像已删除: {image_name}")
                    cleaned = True
                else:
                    log.warning(f"无法删除 Docker 镜像: {image_name}")
        
        if cleaned:
            log.success("清理完成!")
        else:
            log.info("没有需要清理的内容")
        
        return True


# ============================================================================
# 主程序 (Main Program)
# ============================================================================
def show_banner():
    """显示程序横幅"""
    banner = f'''
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║             Docker APK 打包脚本 (Docker APK Build Script)            ║
║                                                                      ║
║                  确保一次打包成功 - Ensure One-time Success          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.RESET}'''
    print(banner)


def show_github_actions_instructions():
    """显示 GitHub Actions 使用说明"""
    instructions = f'''
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════╗
║           使用 GitHub Actions 构建 APK (推荐替代方案)                ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.RESET}

{Colors.GREEN}优势 (Advantages):{Colors.RESET}
  • 更稳定的构建环境，无需担心 Docker 内存限制
  • GitHub 提供的专用 Android 构建环境
  • 自动 Gradle 缓存，加速后续构建
  • 构建产物自动保存，可随时下载

{Colors.CYAN}使用步骤 (Usage Steps):{Colors.RESET}

  {Colors.BOLD}1. 自动触发构建:{Colors.RESET}
     将代码推送到 main 分支，或创建 Pull Request
     GitHub Actions 会自动触发构建

  {Colors.BOLD}2. 手动触发构建:{Colors.RESET}
     a. 访问仓库的 Actions 页面
     b. 选择 "Build Android APK" 工作流程
     c. 点击 "Run workflow" 按钮
     d. 选择构建类型 (debug/release)
     e. 点击绿色的 "Run workflow" 按钮

  {Colors.BOLD}3. 下载 APK:{Colors.RESET}
     a. 等待构建完成 (约 5-10 分钟)
     b. 点击完成的工作流程运行
     c. 在 "Artifacts" 部分下载 APK 文件

{Colors.YELLOW}工作流程文件位置:{Colors.RESET}
  .github/workflows/build-apk.yml

{Colors.CYAN}本地替代方案:{Colors.RESET}
  如果需要在本地构建，可以使用以下命令导出 Android 项目:
  
  python3 docker_build_apk.py --project-only
  
  然后使用 Android Studio 打开项目并构建 APK。
'''
    print(instructions)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Docker环境APK打包脚本 - 确保一次打包成功',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python3 docker_build_apk.py                # 构建 Debug APK
  python3 docker_build_apk.py --release      # 构建 Release APK
  python3 docker_build_apk.py --check        # 仅检查依赖
  python3 docker_build_apk.py --clean        # 清理构建产物
  python3 docker_build_apk.py --no-cache     # 不使用Docker缓存重新构建
  python3 docker_build_apk.py --project-only # 仅导出 Android 项目
  python3 docker_build_apk.py --use-actions  # 查看 GitHub Actions 构建说明

输出:
  APK文件将保存在 build-output/android/ 目录下
        '''
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='仅检查依赖，不执行构建'
    )
    parser.add_argument(
        '--release',
        action='store_true',
        help='构建 Release 版本 (默认构建 Debug 版本)'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='清理构建产物和Docker镜像'
    )
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='不使用Docker缓存，完全重新构建'
    )
    parser.add_argument(
        '--dir',
        type=str,
        default=None,
        help='项目目录 (默认: 脚本所在目录)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='输出目录 (默认: build-output/android)'
    )
    parser.add_argument(
        '--project-only',
        action='store_true',
        help='仅导出 Android 项目，不构建 APK (可在 Android Studio 中打开)'
    )
    parser.add_argument(
        '--use-actions',
        action='store_true',
        help='显示如何使用 GitHub Actions 构建 APK 的说明'
    )
    
    args = parser.parse_args()
    
    # 显示横幅
    show_banner()
    
    # 获取项目目录
    if args.dir:
        project_dir = Path(args.dir).resolve()
    else:
        project_dir = Path(__file__).parent.resolve()
    
    # 获取输出目录
    if args.output:
        output_dir = Path(args.output).resolve()
    else:
        output_dir = project_dir / 'build-output' / 'android'
    
    log.info(f"项目目录: {project_dir}")
    log.info(f"输出目录: {output_dir}")
    log.info(f"系统: {detector.detect_os()}")
    
    # 处理 GitHub Actions 说明
    if args.use_actions:
        show_github_actions_instructions()
        sys.exit(0)
    
    # 初始化配置
    config = BuildConfig()
    
    # 初始化构建器
    builder = DockerAPKBuilder(config, project_dir, output_dir)
    
    # 处理清理操作
    if args.clean:
        if builder.clean():
            sys.exit(0)
        sys.exit(1)
    
    # 初始化依赖检测器
    checker = DependencyChecker(config)
    
    # 检查依赖
    all_ok, statuses = checker.check_all(project_dir)
    
    if not all_ok:
        log.error("依赖检查失败，请解决上述问题后重试")
        for status in statuses:
            if not status.installed and status.required:
                log.error(f"  - {status.name}: {status.message}")
        sys.exit(1)
    
    # 仅检查模式
    if args.check:
        log.header("依赖检查完成")
        log.success("所有依赖检查通过，可以开始构建!")
        sys.exit(0)
    
    # 执行构建
    start_time = time.time()
    
    # 仅导出项目模式
    if args.project_only:
        success = builder.export_project_only(no_cache=args.no_cache)
    else:
        success = builder.build(
            release=args.release,
            no_cache=args.no_cache
        )
    
    elapsed_time = time.time() - start_time
    elapsed_minutes = int(elapsed_time // 60)
    elapsed_seconds = int(elapsed_time % 60)
    
    if success:
        log.header("构建完成! 🎉")
        log.success(f"耗时: {elapsed_minutes}分{elapsed_seconds}秒")
        log.info(f"APK 文件位于: {output_dir}")
        
        # 列出生成的文件
        if output_dir.exists():
            for apk_file in output_dir.glob("*.apk"):
                size_mb = apk_file.stat().st_size / (1024 * 1024)
                log.info(f"  - {apk_file.name} ({size_mb:.2f} MB)")
        
        sys.exit(0)
    else:
        log.header("构建失败 ❌")
        log.error(f"耗时: {elapsed_minutes}分{elapsed_seconds}秒")
        log.error("请检查上述错误信息并修复问题后重试")
        sys.exit(1)


if __name__ == '__main__':
    main()
