# Paper-Formatter V2 实施进程

## 整体进度可视化

```
第1步  第2步  第3步  第4步  第5步  第6步  第7步  第8步  第9步
 板块9  板块4  板块1  板块6  板块2  板块3  板块5  板块7  板块8
 基础   格式   文件   任务   AI    排版   预览   模板   前端
 设施   标准   处理   管理   分析   引擎   服务   管理    UI
 ───   ───   ───   ───   ───   ───   ───   ───   ───
 [ ]   [ ]   [ ]   [ ]   [ ]   [ ]   [ ]   [ ]   [ ]
```

**状态标记**：`[ ]` 待开始 `[~]` 进行中 `[✓]` 已完成 `[!]` 阻塞

---

## 各板块完成标准

### 板块9：基础设施
```
[ ] 9.1 config.py — pydantic-settings加载，api_key为空时打印警告
[ ] 9.2 database.py — SQLAlchemy engine/session/Base/get_db，datetime用UTC
[ ] 9.3 main.py — create_app()工厂函数，CORS配置，init_app()注册路由+建表+seed模板
[ ] 9.4 shared/errors.py — AppError基类 + FileValidationError/AIError/FormatError/NotFoundError
[ ] 9.5 shared/schemas.py — 所有Pydantic模型从旧文件迁移
[ ] 9.6 requirements.txt — 删除aiofiles，补充lxml
```
**完成标准**：`uvicorn app.main:app` 启动成功，`/api/health` 返回 `{"status": "ok"}`

### 板块4：格式标准
```
[ ] 4.1 defaults.py — 完整格式常量（页面/标题4级/特殊标题/正文/题注/参考文献/页眉页脚）
[ ] 4.2 defaults.py — 中文字号→pt映射（二号22pt/小三15pt/四号14pt/小四12pt/五号10.5pt/小五9pt）
[ ] 4.3 fonts.py — set_east_asian_font() + set_latin_font()（Times New Roman）
[ ] 4.4 custom.py — merge_settings()自定义→默认合并逻辑
```
**完成标准**：导入模块无报错，所有get_*_spec()返回正确的dict值

### 板块1：文件处理
```
[ ] 1.1 service.py — FileService类：validate/save/get_output_path
[ ] 1.2 extractors.py — DOCX文本提取（python-docx逐段） + PDF文本提取（PyPDF2逐页）
[ ] 1.3 router.py — POST /api/upload + GET /api/download/{id}
```
**完成标准**：上传docx→返回JobResponse(201)，下载返回正确MIME类型

### 板块6：任务管理
```
[ ] 6.1 models.py — FormatJob ORM（ai_analysis String(50000)，用JSON存储）
[ ] 6.2 service.py — JobService类：create/get/set_status/save_analysis/save_output/to_response
[ ] 6.3 router.py — POST /api/format/select-mode + GET /api/format/job/{id}
```
**完成标准**：创建Job→状态流转→查询状态，整条链路无报错

### 板块2：AI分析
```
[ ] 2.1 prompt.py — SYSTEM_PROMPT（四级编号体系+特殊标题识别+start_marker规则）
[ ] 2.2 service.py — AIService.analyze()（复用HTTP client，JSON修复，temperature=0.1）
[ ] 2.3 warnings.py — detect_warnings()（正则检测图表标签，特殊节名检测）
[ ] 2.4 router.py — POST /api/format/analyze
```
**完成标准**：上传论文→AI返回正确JSON结构→warnings检测运行→分析结果存入Job

### 板块3：排版引擎（核心）
```
[ ] 3.1 matcher.py — match_paragraph()三策略（标题优先/编号匹配/marker兜底+防重复+文献区检测）
[ ] 3.2 applier.py — 根据匹配类型应用对应格式（标题/特殊标题/正文/题注/参考文献/页眉页脚）
[ ] 3.3 applier.py — 英文数字设Times New Roman，标题固定行距20磅
[ ] 3.4 toc.py — 检测旧目录→移除→在正文前插入新目录
[ ] 3.5 service.py — FormatEngine.execute()编排整体流程
[ ] 3.6 router.py — POST /api/format/execute + /api/format/customize + /api/format/annotate + /api/format/modify-section
```
**完成标准**：上传打乱文件→排版→下载，对比标准文件，格式一致（标题层级/字体/字号/行距/缩进/对齐）

### 板块5：预览服务
```
[ ] 5.1 service.py — PreviewService.extract()（复用matcher，段落聚合，图表标记，目录区检测）
[ ] 5.2 router.py — GET /api/preview/{job_id}
```
**完成标准**：排版后预览API返回正确章节结构和占位标记

### 板块7：模板管理
```
[ ] 7.1 models.py — FormatTemplate ORM
[ ] 7.2 service.py — TemplateService类：create_or_update/list_all/get/delete/seed_default
[ ] 7.3 router.py — POST/GET/DELETE /api/templates/*
```
**完成标准**：保存模板→列表显示→加载→删除，全链路正常

### 板块8：前端UI
```
[ ] 8.1 修复 useFileUpload — XMLHttpRequest真实进度
[ ] 8.2 修复 useFormatting — JSON.parse解析ai_analysis
[ ] 8.3 修复 useTemplate — 同名模板替换逻辑
[ ] 8.4 修复 CommandInput — unmount清理setTimeout
[ ] 8.5 修复 FormatTooltip — scroll事件监听重新定位
[ ] 8.6 修复 上传进度显示
[ ] 8.7 清理未使用依赖（class-variance-authority, aiofiles, DownloadButton）
[ ] 8.8 格式规范更新为护理学论文标准（字号/字体/行距/缩进）
```
**完成标准**：前端全流程走通：上传→分析→预览→下载，无控制台报错

---

## 依赖关系图

```
第1步(9)基础设施
    ↓
第2步(4)格式标准 ─────────────────────┐
    ↓                                 │
第3步(1)文件处理                       │
    ↓                                 │
第4步(6)任务管理                       │
    ↓                                 │
第5步(2)AI分析 ──→ 依赖(1)提取文本     │
    ↓                                 │
第6步(3)排版引擎 ──→ 依赖(4)格式标准 ──┘
    ↓
第7步(5)预览服务 ──→ 依赖(3)matcher
    ↓
第8步(7)模板管理 ──→ 依赖(9)数据库
    ↓
第9步(8)前端UI ──→ 依赖所有后端板块
```

---

## 当前状态

**开始时间**：2026-05-19
**当前步骤**：第0步 — 规划完成，待开始实施
**阻塞项**：无

---

## 过程日志

| 时间 | 事件 | 操作 |
|------|------|------|
| 2026-05-19 | 设计文档+进程文件创建 | 规划完成 |
| | | |

---

## 下机提示

每次对话结束前，在此记录当前进度和下次启动要点：

```
下次启动提示：
- 当前在第 X 步
- 上次完成了：XXX
- 接下来要做：XXX
- 阻塞项：XXX / 无
- 启动命令：XXX
```
