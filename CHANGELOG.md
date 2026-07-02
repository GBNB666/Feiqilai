# Changelog

## v3.0.0 (2026-07-01)

### 新增
- **exe 打包发布** — PyInstaller 打包为单个 .exe，双击运行
- **三线表格式化** — 自动转换表格边框为学术三线表
- **公式编号** — 按章节自动编号 + 居中 + 右对齐
- **图表题注重排** — 图1.1 / 表1.1 按章独立编号
- **参考文献重排** — 连续 [1], [2], [3]... 编号 + 悬挂缩进
- **页眉增强** — 校名/标题 + 当前章节
- **前端生产构建** — FastAPI 直接 serve 构建产物
- **Error Boundary** — 前端异常边界
- **速率限制** — AI 分析每 IP 每分钟限 5 次

### 修复
- 图片居中 OOXML 层直接写入 w:jc
- 论文标题加入目录首条
- 参考文献 apply_reference_format 补充西文字体调用
- 默认参考规则增加悬挂缩进 0.74cm
- TOC 重跑不重复插入
- 题注重编号保留 run 格式
- AnnotationPanel 受控组件修复
- 文件上传前检查 Content-Length
- 状态机添加合法转换守卫
- AppError 全局异常处理器统一响应格式
- useEffect cleanup 防止组件卸载后 setState
- 上传中禁用文件选择器点击
- 默认模板改为有意义的学术论文设置

### 变更
- 配置系统重构：支持 exe (%APPDATA%) 和开发双模式
- CORS 收紧为具体 methods/headers
- httpx 客户端由 FastAPI lifespan 管理生命周期
