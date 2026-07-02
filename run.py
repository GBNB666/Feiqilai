#!/usr/bin/env python3
"""智排AI 启动入口 — 双击运行或 PyInstaller 打包后自动启动。

- 启动 uvicorn 服务器
- 自动打开默认浏览器
- 优雅退出（Ctrl+C 关闭）
"""
import os
import sys
import time
import webbrowser
import threading


def get_app_dir() -> str:
    """获取应用数据目录（exe 旁或 %APPDATA%）。

    PyInstaller 打包后 sys.frozen=True，exe 所在目录用于静态文件；
    用户数据（数据库、上传、输出）放在 %APPDATA%/智排AI/。
    """
    if getattr(sys, "frozen", False):
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(appdata, "智排AI")
    return os.path.dirname(os.path.abspath(__file__))


def main():
    app_dir = get_app_dir()
    os.makedirs(app_dir, exist_ok=True)
    os.chdir(app_dir)

    # Set data dir env for the config system
    os.environ.setdefault("DATA_DIR", app_dir)
    os.environ.setdefault("SERVE_STATIC", "true")

    print(f"数据目录: {app_dir}")
    print("正在启动智排AI服务器...")

    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"

    # 延迟打开浏览器（等服务器就绪）
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()

    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        log_level="info",
        reload=False,
    )


if __name__ == "__main__":
    main()
