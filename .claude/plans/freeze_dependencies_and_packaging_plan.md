# 固定依赖版本和添加打包功能

## 目标
1. 修改 requirements.txt，固定当前环境的所有依赖版本
2. 添加打包功能，支持 macOS (M芯片)、Windows、macOS (Intel芯片) 三种平台

## 当前问题

### 问题 1：依赖版本未固定
- 当前 requirements.txt 可能使用宽松的版本约束
- 缺少完整的依赖列表
- 不同环境可能安装不同版本，导致兼容性问题

### 问题 2：缺少打包功能
- 用户需要手动安装 Python 环境才能运行
- 无法直接分发给非技术用户
- 需要支持多平台打包

## 修改方案

### 修改 1：固定依赖版本

**步骤：**
1. 使用 `pip freeze` 获取当前环境所有依赖
2. 筛选本项目直接和间接依赖
3. 写入 requirements.txt，固定精确版本

**示例：**
```
customtkinter==5.2.1
lmdb==1.4.1
...
```

### 修改 2：添加打包功能

**工具选择：PyInstaller**
- 成熟稳定，支持多平台
- 可以打包为单个可执行文件
- 支持 macOS universal binary

**打包配置：**

1. **创建 .spec 文件**
   - 配置入口点：`main.py`
   - 包含数据文件
   - 设置应用图标
   - 配置隐藏导入

2. **创建打包脚本**
   - `build_macos_arm64.sh` - macOS M芯片
   - `build_macos_intel.sh` - macOS Intel
   - `build_windows.bat` - Windows
   - `build_all.sh` - 打包所有平台（需要在对应平台运行）

3. **打包输出**
   - macOS: `.app` 应用包
   - Windows: `.exe` 可执行文件

## 实施步骤

### 步骤 1：固定依赖版本
1. 运行 `pip freeze > requirements.txt`
2. 检查依赖列表
3. 测试全新环境安装

### 步骤 2：安装打包工具
```bash
pip install pyinstaller
```

### 步骤 3：创建打包配置
1. 创建 `ObjectBoxViewer.spec` 文件
2. 配置应用信息、图标、数据文件
3. 配置隐藏导入（customtkinter 等）

### 步骤 4：创建打包脚本
1. macOS ARM64 打包脚本
2. macOS Intel 打包脚本
3. Windows 打包脚本
4. 通用打包脚本

### 步骤 5：测试打包
1. 在 macOS 上测试打包
2. 验证可执行文件运行正常
3. 测试数据文件加载功能

## 打包配置细节

### .spec 文件配置
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'customtkinter',
        'lmdb',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ObjectBoxViewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI应用，不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ObjectBoxViewer',
)

app = BUNDLE(
    coll,
    name='ObjectBoxViewer.app',
    icon=None,  # 可以后续添加图标
    bundle_identifier='com.objectbox.viewer',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '1.0.0',
    },
)
```

### macOS 打包选项

**Universal Binary（通用二进制）：**
- 同时支持 Intel 和 M芯片
- 需要在两个架构上分别编译后合并
- 文件体积较大

**分离打包：**
- 分别打包 ARM64 和 x86_64
- 用户下载对应架构版本
- 文件体积较小

**推荐：分离打包**

## 影响范围
- `requirements.txt` - 依赖版本
- `ObjectBoxViewer.spec` - PyInstaller 配置（新增）
- `build_macos_arm64.sh` - macOS ARM64 打包脚本（新增）
- `build_macos_intel.sh` - macOS Intel 打包脚本（新增）
- `build_windows.bat` - Windows 打包脚本（新增）
- `build_all.sh` - 通用打包脚本（新增）
- `.gitignore` - 忽略打包输出目录

## 预期结果
1. requirements.txt 包含所有依赖的精确版本
2. 提供打包脚本，一键生成可执行文件
3. 支持 macOS M芯片、Intel、Windows 三种平台
4. 用户无需安装 Python 环境即可运行

## 打包输出
- `dist/ObjectBoxViewer.app` - macOS 应用
- `dist/ObjectBoxViewer.exe` - Windows 可执行文件
- `build/` - 临时构建文件（不提交）
