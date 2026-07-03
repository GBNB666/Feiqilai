# AI智排 — 论文排版助手

一键上传，AI 自动排版，三线表 / 参考文献重排 / 目录生成全搞定。

## 功能

- **AI 智能分析** — DeepSeek 自动识别论文标题、章节、参考文献结构
- **全自动排版** — 标题/正文/引用一键格式化
- **三线表转换** — 普通表格自动转为学术三线表
- **图表题注编号** — 图1.1 / 表1.1 按章独立编号
- **参考文献重排** — 连续编号 + 悬挂缩进
- **目录自动生成** — 勾选开关即可插入
- **学校模板** — 内置多校论文格式，一键应用
- **图片调整** — 批量设置宽度比例、对齐方式
- **格式设置面板** — 字体/字号/间距逐项微调
- **实时预览** — 排版后 HTML 预览，满意再下载
- **Word + PDF 双格式下载**

## 快速开始

### 开发模式

```bash
# 后端
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# 前端（另一个终端）
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173

### 打包为 exe

```bash
pip install pyinstaller
python build_exe.py
```

输出: `dist/AI智排.exe` — 双击运行，浏览器自动打开。

## 技术栈

- **后端**: FastAPI + SQLAlchemy + python-docx
- **前端**: React + TypeScript + Tailwind CSS
- **AI**: DeepSeek API
- **打包**: PyInstaller

## 项目结构

```
paper-formatter/
├── backend/
│   ├── app/
│   │   ├── modules/
│   │   │   ├── ai_analyzer/      # AI 分析
│   │   │   ├── file_handler/     # 文件上传/下载/转换
│   │   │   ├── format_engine/    # 排版引擎
│   │   │   ├── image_formatter/  # 图片格式化
│   │   │   ├── job_manager/      # 任务管理
│   │   │   ├── preview/          # HTML 预览
│   │   │   ├── school_template/  # 学校模板
│   │   │   └── template_manager/ # 用户模板
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   └── data/school_templates/    # 学校模板 JSON
├── frontend/
│   └── src/
│       ├── pages/                # 页面
│       ├── modules/              # 功能模块
│       ├── components/           # 通用组件
│       └── services/             # API 调用
├── run.py                        # exe 启动入口
├── build_exe.py                  # 一键构建脚本
└── paper-formatter.spec          # PyInstaller 配置
```

## License

MIT
