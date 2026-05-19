# 论文排版网站 第二轮功能实施计划

**6 个新功能：** 格式自定义面板 | 口令修改 | 全局导航 | 保存/加载模板 | 历史记录 | 错误格式警告

---

## Phase 1: 后端扩展

### 1.1 格式自定义 API
- `POST /api/format/customize` — 接收自定义 FormatSettings
- `GET /api/format/defaults` — 返回默认格式规范值

### 1.2 口令修改 API
- `POST /api/format/modify-section/{job_id}` — 修改指定节的正文

### 1.3 模板 API
- `POST /api/templates/save` — 保存模板到 DB
- `GET /api/templates/` — 列出所有模板
- `GET /api/templates/{id}` — 加载模板
- `DELETE /api/templates/{id}` — 删除模板

### 1.4 格式验证
- 在 analyze 后自动检测：缺失结构、图表缺标注、格式冲突
- 以 warnings 数组返回

---

## Phase 2: 前端组件

### 2.1 FormatSettingsPanel — 左侧格式可编辑面板
### 2.2 CommandInput — 预览页口令修改框
### 2.3 StepNavigation — 全局前进/后退
### 2.4 TemplateManager — 保存/加载模板
### 2.5 HistoryPanel — localStorage 历史记录
### 2.6 WarningBanner — 格式警告条

## Phase 3: 构建验证
