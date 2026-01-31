# 修复历史记录 (Fix History)

此文件记录了项目构建过程中遇到的问题及其解决方案，供后续维护参考。

---

## 2026-01-31: 修复 Gradle 弃用警告 (Fix Gradle Deprecation Warnings)

### 问题描述 (Issue Description)

Android APK 构建时出现 Gradle 弃用警告：

```
Deprecated Gradle features were used in this build, making it incompatible with Gradle 9.0.

You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.
```

构建可能会失败，显示 `SessionFailureReportingActionExecutor` 相关的堆栈跟踪。

### 根本原因 (Root Cause)

Capacitor 生成的 Android 项目模板使用了两个在 Gradle 8.x 中已弃用的功能：

1. **`lintOptions`** - 在 `capacitor-cordova-android-plugins/build.gradle` 和 `@capacitor/android` 模块中使用，应改为 `lint`
2. **`rootProject.buildDir`** - 在 `build.gradle` 中使用，应改为 `layout.buildDirectory`

### 解决方案 (Solution)

1. 更新 `@capacitor/android` 的 patch-package 补丁，将 `lintOptions` 改为 `lint`
2. 扩展 `postinstall.sh` 脚本，在安装时修复两个 Capacitor CLI 模板：
   - `capacitor-cordova-android-plugins.tar.gz`: 修复 `lintOptions` → `lint`
   - `android-template.tar.gz`: 修复 `rootProject.buildDir` → `layout.buildDirectory`

### 实施的更改 (Changes Made)

**文件: `video-app/patches/@capacitor+android+7.4.5.patch`**
- 添加 `lintOptions` → `lint` 的修复

**文件: `video-app/scripts/postinstall.sh`**
- 添加 `lintOptions` → `lint` 修复到 `capacitor-cordova-android-plugins.tar.gz` 模板
- 添加 `rootProject.buildDir` → `layout.buildDirectory` 修复到 `android-template.tar.gz` 模板
- 重构脚本，使用通用的 `sed_inplace` 辅助函数

---

## 2026-01-31: 添加替代 APK 打包方案 (Alternative APK Packaging Solutions)

### 问题描述 (Issue Description)

在 Docker 容器中使用 Gradle 构建 Android APK 时持续失败，即使添加了内存优化配置也无法解决。错误信息：

```
BUILD FAILED in 1m 43s
42 actionable tasks: 42 executed
```

Docker 环境的内存和资源限制导致 Gradle 构建不稳定。

### 解决方案 (Solution)

提供三种替代方案来构建 APK：

#### 方案 1: GitHub Actions (推荐)

添加 `.github/workflows/build-apk.yml` 工作流程：
- 利用 GitHub 提供的专用 Android 构建环境
- 更多内存和资源，构建更稳定
- 自动 Gradle 缓存，加速后续构建
- 构建产物自动保存，可随时下载

使用方法：
```bash
# 查看 GitHub Actions 使用说明
python3 docker_build_apk.py --use-actions
```

#### 方案 2: 仅导出 Android 项目

添加 `--project-only` 选项：
- 在 Docker 中完成 Web 应用构建和 Capacitor 同步
- 导出 Android 项目，但不执行 Gradle 构建
- 可以使用 Android Studio 或本地 Gradle 构建 APK

使用方法：
```bash
# 仅导出 Android 项目
python3 docker_build_apk.py --project-only
```

#### 方案 3: 原有 Docker 构建 (可能失败)

保留原有的完整 Docker 构建功能，但可能因资源限制而失败。

### 实施的更改 (Changes Made)

**新增文件:**
- `.github/workflows/build-apk.yml` - GitHub Actions APK 构建工作流程

**修改文件: `docker_build_apk.py`**
- 添加 `--project-only` 选项：仅导出 Android 项目
- 添加 `--use-actions` 选项：显示 GitHub Actions 使用说明
- 添加 `show_github_actions_instructions()` 函数
- 添加 `export_project_only()` 方法
- 添加 `_create_project_only_dockerfile()` 方法

---

## 2026-01-31: Gradle 执行任务失败 (Gradle Execution Task Failure)

### 问题描述 (Issue Description)

在 Docker 容器中构建 Android APK 时，Gradle 构建失败，错误信息：

```
BUILD FAILED in 1m 29s
42 actionable tasks: 42 executed
```

堆栈跟踪显示 `LocalTaskNodeExecutor.execute` 和 `DefaultPlanExecutor$ExecutorWorker` 相关错误。

### 根本原因 (Root Cause)

1. **内存限制**: Docker 容器中 Gradle 构建内存不足，导致任务执行失败
2. **Gradle Worker 进程问题**: 默认的并行 worker 数量在容器环境中可能过高
3. **JVM 配置不当**: 未正确配置 Gradle 和 JVM 内存参数

### 解决方案 (Solution)

1. 在 Docker 构建过程中创建 `gradle.properties` 文件，配置 JVM 内存参数
2. 限制 Gradle 的 max workers 数量为 2
3. 禁用 Gradle 并行构建和缓存以减少内存使用
4. 为 Gradle 命令添加 `--max-workers=2` 参数

### 实施的更改 (Changes Made)

**文件: `docker_build_apk.py`**
- 在 Gradle 构建前创建 `gradle.properties` 文件
- 添加配置:
  - `org.gradle.jvmargs=-Xmx2048m -XX:MaxMetaspaceSize=512m -XX:+HeapDumpOnOutOfMemoryError`
  - `org.gradle.workers.max=2`
  - `org.gradle.parallel=false`
  - `org.gradle.caching=false`
- Gradle 命令添加 `--max-workers=2` 参数

**文件: `docker_build_app.sh`**
- 同样添加 Gradle 内存配置
- 添加 `--no-daemon --max-workers=2` 参数

---

## 模板: 添加新的修复记录

## YYYY-MM-DD: 问题标题

### 问题描述
[描述遇到的问题]

### 根本原因
[分析问题的根本原因]

### 解决方案
[描述解决方案]

### 实施的更改
[列出具体的文件和代码更改]
