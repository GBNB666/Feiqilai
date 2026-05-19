# Paper-Formatter 项目复盘总结

## 一、项目是什么

一个**论文AI格式排版网站**，用户上传docx/pdf论文 → AI分析结构 → 自动按学术规范排版 → 下载修正后的文件。

- **目标用户**：大学生（主要是护理学等非CS专业，对论文格式要求不熟悉）
- **商业定位**：个人全栈作品，简历项目，顺便赚点生活费
- **开发周期**：2026年5月11日MVP完成，5月12日暂停，5月19日尝试修Bug后决定重来

---

## 二、技术栈 & 项目结构

### 后端 `C:\Users\博博\paper-formatter\backend\`

```
技术：Python + FastAPI + SQLAlchemy + SQLite + python-docx + DeepSeek-V4 API
```

| 文件 | 作用 |
|------|------|
| `app/main.py` | FastAPI入口，CORS只允许localhost:5173，注册路由 |
| `app/config.py` | 环境配置（DeepSeek API key、数据库路径等），从.env读取 |
| `app/database.py` | SQLAlchemy引擎和Session |
| `app/models/job.py` | FormatJob数据模型（上传→分析→排版→完成的状态机） |
| `app/routers/upload.py` | POST /api/upload — 文件上传 |
| `app/routers/format.py` | /api/format/* — 分析、标注、自定义设置、执行排版、状态查询 |
| `app/routers/download.py` | GET /api/download/{job_id} — 下载排版结果 |
| `app/routers/preview.py` | /api/preview/* — 前端预览 |
| `app/services/ai_analyzer.py` | 调用DeepSeek-V4分析论文结构（SYSTEM_PROMPT定义输出格式） |
| `app/services/formatter.py` | 排版编排器，调用AI分析 + docx_processor |
| `app/services/docx_processor.py` | **核心排版引擎**：匹配段落、应用标题/正文/题注格式 |
| `app/services/format_standards.py` | 格式标准定义（一级标题16pt黑体居中、正文12pt宋体两端对齐等） |
| `app/services/pdf_processor.py` | PDF处理（stub，未完整实现） |
| `uploads/` | 用户上传的原始文件 |
| `outputs/` | 排版后的输出文件 |

### 前端 `C:\Users\博博\paper-formatter\frontend\`

```
技术：React 19 + TypeScript + Vite 8 + Tailwind CSS 4 + shadcn/ui + React Router 7
```

| 文件 | 作用 |
|------|------|
| `vite.config.ts` | **关键**：代理/api到后端端口，配置@别名 |
| `src/main.tsx` | 入口 |
| `src/App.tsx` | 路由定义（/ → HomePage, /process/:id → ProcessPage） |
| `src/pages/HomePage.tsx` | 首页，文件上传 + 历史记录 |
| `src/pages/ProcessPage.tsx` | 6步流程页（模式选择→分析→格式设置→排版→结果→下载） |
| `src/components/upload/FileUploader.tsx` | 拖拽上传组件，accept=.pdf/.docx |
| `src/hooks/useFileUpload.ts` | 上传状态管理hook |
| `src/services/api.ts` | 所有API调用（upload、analyze、execute、download等） |
| `src/types/index.ts` | TypeScript类型定义 |

### 启动方式

```bash
# 后端（终端1）
cd C:\Users\博博\paper-formatter\backend
/c/Users/博博/python.exe -m uvicorn app.main:app --port 8000 --reload

# 前端（终端2）
cd C:\Users\博博\paper-formatter\frontend
npx vite --port 5173
```

访问：http://localhost:5173

### 启动前检查清单

- [ ] 后端端口8000没有被占用
- [ ] 前端vite.config.ts中代理target端口和实际后端端口一致（都是8000）
- [ ] `.env`文件在backend目录下，DeepSeek API key有效
- [ ] `npm install`已执行过（node_modules存在）
- [ ] Python依赖已安装（requirements.txt中的包）

---

## 三、已知Bug & 修复状态

### 严重Bug（3个）

| # | Bug | 状态 | 根因 |
|---|-----|------|------|
| 1 | **正文粗体传播** — 正文变粗体大号字，标题反而不粗 | **已修复** | AI返回的start_marker是正文文字不是标题文字，匹配逻辑把正文段当成了标题 |
| 2 | **字体变蓝** — 部分文字颜色异常 | **未复现** | 需要更多测试样本 |
| 3 | **表格图片占位丢失** | **未验证** | 测试文件无表格图片 |

### 中等Bug（3个）

| # | Bug | 状态 |
|---|-----|------|
| 4 | 摘要格式丢失 | 未修 |
| 5 | 参考文献标题化 | 未修 |
| 6 | 目录静态页码 | 未修 |

### 交互缺漏（3个）

| # | 问题 | 状态 |
|---|------|------|
| 7 | 前进后退导航 | 未做 |
| 8 | 口令修改框 | 未做 |
| 9 | 悬停浮窗 | 未做 |

### 已修复的Bug详情

**Bug 1 修复过程（粗体传播）**：
- 根因：AI的SYSTEM_PROMPT要求start_marker存"该节开头的标志性文本"，AI理解为正文前20字。docx_processor用这个marker去匹配段落，正文段包含marker文本 → 被当成标题 → 加粗变大。
- 修了3个文件：
  1. `docx_processor.py`：新增`_text_matches_title()`函数，匹配策略改为**标题文字优先**（用section的title字段精确匹配），start_marker降级为兜底。每个section只匹配一次防止重复传播。
  2. `ai_analyzer.py`：修改SYSTEM_PROMPT，明确start_marker放标题文字本身。
  3. `vite.config.ts`：修复代理端口8001→8000（阻止前端上传的附加Bug）。

### 本次会话新发现的Bug

**Bug: Vite代理端口配错**
- 现象：拖动文件或点击上传无任何反应
- 根因：`vite.config.ts`中proxy target写了`8001`，后端跑在`8000`
- 修复：改回`8000`

---

## 四、为什么会出这么多Bug

### 根本原因

1. **需求表达不清晰**：用户是大二非CS学生，对论文格式深层规则不熟悉，发现Bug时只能说"这里不对"，无法描述预期行为。AI只按指令执行，缺乏主动验证。

2. **缺乏对照测试机制**：开发过程中没有用"标准格式文件"做对比验证，Bug积累到后期才发现。

3. **AI分析的输出与排版引擎的输入不匹配**：AI返回的start_marker语义（"段落起始标记"）和代码实际使用方式（"标题定位标记"）存在理解偏差。

4. **一次开发了太多功能**：6步流程、支付、模板、历史记录等全做了，但核心的格式匹配逻辑都没跑通。

### 经验教训

1. **先做最小可用版本**：只做"上传→排版→下载"三步，确认格式正确后再加高级功能。
2. **必须有对照测试**：准备一篇格式正确的标准论文，每次改代码后跑一遍对比。
3. **AI分析输出要精确验证**：检查AI返回的start_marker是不是真的指向标题段落。
4. **配置检查清单**：端口、环境变量这些应该在启动时就检查好。

---

## 五、下次重新开始时的建议流程

### 第0步：打开Skills（开始前必做）

```
1. 先开 brainstorming skill — 理清方向
2. 然后开 update-config skill — 检查settings.json
3. 按任务需要开其他 skills
```

### 第1步：环境确认

```
□ 后端端口 ./backend/.env 中的设置
□ 前端 vite.config.ts 的 proxy target 端口一致
□ DeepSeek API key 有效
□ Python依赖完整
□ npm依赖完整
```

### 第2步：准备测试素材

```
□ 准备1篇格式完全正确的论文（标准文件）
□ 基于标准文件制作1个格式打乱的版本（测试输入）
□ 跑一遍标准文件→了解正确的格式规范
```

### 第3步：核心流程开发（只做三步）

```
1. 上传docx → 2. AI分析结构 → 3. 排版输出
```
确认格式正确之前，不要加模式选择、模板、支付、历史记录等功能。

### 第4步：对照测试

```
每次改代码后：
1. 上传打乱文件
2. 运行排版
3. 下载结果
4. 用compare脚本对比标准文件
5. 逐个修差异
```

### 第5步：交互功能

核心排版100%正确后再加：
- 格式设置面板
- 模板管理
- 历史记录
- 支付

---

## 六、关键代码位置速查

```
后端核心：
  backend/app/services/docx_processor.py  ← 排版引擎，匹配逻辑在 _text_matches_title() 和 apply_formatting()
  backend/app/services/ai_analyzer.py     ← AI提示词在 SYSTEM_PROMPT
  backend/app/services/format_standards.py ← 格式标准（标题/正文/题注的字体字号对齐）
  backend/app/routers/format.py           ← API路由
  backend/app/main.py                     ← CORS配置

前端核心：
  frontend/vite.config.ts                 ← 代理端口配置（必须和后端一致！）
  frontend/src/components/upload/FileUploader.tsx ← 文件上传组件
  frontend/src/services/api.ts            ← API调用
  frontend/src/pages/HomePage.tsx         ← 首页

工具脚本：
  paper-formatter/compare_format.py       ← 三向格式对比脚本
  paper-formatter/debug_match.py          ← 段落匹配调试脚本
```

---

## 七、提醒自己的话

1. **不要一口气做全部功能**。把核心排版做对，验证通过，再做别的。
2. **每改一处代码就跑一遍测试**。用标准文件对比，确认没有倒退。
3. **描述Bug时给三样东西**：复现步骤 + 预期效果 + 实际效果。不说"这里坏了"。
4. **配置问题优先排查**：端口、环境变量、代理、CORS。这些跟业务逻辑无关但最容易炸。
5. **AI不是万能的**。它给的start_marker可能是错的，要在代码里加兜底逻辑。
6. **先把产品跑通，再谈赚钱**。支付、模板这些MVP之后再说。

---

生成日期：2026-05-19
项目路径：C:\Users\博博\paper-formatter\
