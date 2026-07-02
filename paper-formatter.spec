# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for 智排AI"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = os.path.dirname(os.path.abspath(SPECPATH))
BACKEND = os.path.join(ROOT, "backend")

# 收集 sqlalchemy, docx, uvicorn 的隐藏导入
hiddenimports = [
    "uvicorn.logging", "uvicorn.loops", "uvicorn.loops.auto",
    "uvicorn.protocols", "uvicorn.protocols.http", "uvicorn.protocols.http.auto",
    "uvicorn.lifespan", "uvicorn.lifespan.on",
    "sqlalchemy", "sqlalchemy.ext.declarative",
    "docx", "docx.opc", "docx.oxml",
    "pydantic_settings",
    "fastapi",
    "starlette",
]

# 收集数据文件
datas = []

# 学校模板
templates_dir = os.path.join(BACKEND, "data", "school_templates")
if os.path.isdir(templates_dir):
    datas.append((templates_dir, "data/school_templates"))

# 前端静态文件
static_dir = os.path.join(BACKEND, "static")
if os.path.isdir(static_dir):
    datas.append((static_dir, "static"))

a = Analysis(
    [os.path.join(ROOT, "run.py")],
    pathex=[BACKEND, ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter", "matplotlib", "numpy", "scipy",
        "pandas", "PIL", "cv2", "tensorflow", "torch",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="智排AI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # GUI 模式，不弹黑框
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # 后续可添加 .ico 图标
)
