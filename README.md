# 智排AI — 智能论文排版助手

一键排版你的学术论文。上传 `.docx` 文件 → AI 分析结构 → 自动排版 → 下载 Word/PDF。

## 功能特性

- **AI 结构分析** — DeepSeek 自动识别论文的标题、章节、图表、参考文献
- **自动排版** — 字体、字号、行距、缩进一键标准化
- **学校模板** — 内置多个高校论文格式模板，一键套用
- **三线表** — 自动转换表格为标准三线表
- **目录生成** — 自动生成带页码的目录，Word 打开自动更新
- **公式编号** — 按章节自动编号 (1-1), (1-2)...
- **图表题注重排** — 图1.1 / 表1.1 按章内独立编号
- **参考文献重排** — [1], [2], [3]... 连续编号 + 悬挂缩进
- **图片调整** — 可视化调整图片尺寸和对齐
- **预览系统** — 排版后按章节预览效果

## 快速开始

### 下载运行（无需 Python）

从 [Releases](https://github.com/your-username/paper-formatter/releases) 下载 `智排AI.exe`，双击运行。

### 开发模式

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 前端
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173`。

### 构建 exe

```bash
pip install pyinstaller
python build_exe.py
```

产出 `dist/智排AI.exe`。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 19 + TypeScript + Tailwind CSS 4 + Vite |
| 后端 | FastAPI + SQLAlchemy + python-docx |
| AI | DeepSeek Chat API |
| 打包 | PyInstaller |

## 项目结构

```
paper-formatter/
  backend/          # FastAPI 后端
    app/
      modules/      # 功能模块 (file_handler, ai_analyzer, format_engine, ...)
      shared/       # 共享 schemas + 错误处理
      data/         # 学校模板 JSON
  frontend/         # React 前端
    src/
      pages/        # 页面组件
      modules/      # 功能面板
      components/   # 通用组件
  run.py            # exe 启动入口
  build_exe.py      # 构建脚本
  paper-formatter.spec  # PyInstaller 配置
```

## 环境变量

在 `backend/.env` 中配置（开发模式）：

```
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

## License

MIT
