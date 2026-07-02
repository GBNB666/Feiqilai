#!/usr/bin/env python3
"""智排AI 一键构建脚本

1. 构建前端 (npm run build)
2. 复制静态文件到 backend/static/
3. 调用 PyInstaller 打包为单个 .exe

用法: python build_exe.py
"""
import os
import sys
import shutil
import subprocess


ROOT = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT, "frontend")
BACKEND_DIR = os.path.join(ROOT, "backend")
STATIC_DIR = os.path.join(BACKEND_DIR, "static")
DIST_DIR = "dist"


def run(cmd, cwd=None, desc=""):
    print(f"\n{'='*60}")
    print(f"  {desc or cmd}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, cwd=cwd or ROOT)
    if result.returncode != 0:
        print(f"\n错误: {desc} 失败 (code={result.returncode})")
        sys.exit(1)


def main():
    # 1. 构建前端
    if os.path.isdir(FRONTEND_DIR):
        run("npm install", cwd=FRONTEND_DIR, desc="安装前端依赖")
        run("npm run build", cwd=FRONTEND_DIR, desc="构建前端 (Vite build)")

        # 2. 复制 dist → backend/static/
        frontend_dist = os.path.join(FRONTEND_DIR, "dist")
        if os.path.isdir(frontend_dist):
            if os.path.isdir(STATIC_DIR):
                shutil.rmtree(STATIC_DIR)
            shutil.copytree(frontend_dist, STATIC_DIR)
            print(f"  前端构建产物已复制到: {STATIC_DIR}")
    else:
        print("  跳过前端构建（frontend/ 目录不存在）")

    # 3. 安装后端依赖
    run(f"{sys.executable} -m pip install -r requirements.txt",
        cwd=BACKEND_DIR, desc="安装后端依赖")

    # 4. PyInstaller 打包
    run("pyinstaller --clean --noconfirm paper-formatter.spec",
        desc="PyInstaller 打包")

    print(f"\n{'='*60}")
    print(f"  构建完成! 输出: {os.path.join(ROOT, DIST_DIR, '智排AI.exe')}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
