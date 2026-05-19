# Paper-Formatter 项目复盘总结（V1 + V2）

## 一、项目是什么

一个**论文AI格式排版网站**：上传docx → AI分析结构 → 按护理学论文规范排版 → 下载。

- **目标用户**：博博自己 + 其他大学生（护理学等非CS专业）
- **商业定位**：个人全栈作品 + 简历项目 + 赚生活费
- **时间线**：
  - 2026-05-11：V1 MVP完成
  - 2026-05-12：修Bug发现太多问题，暂停
  - 2026-05-19：V2 模块化重写（9板块架构），全功能跑通但下载Bug连环炸
  - 2026-05-19 晚：用户决定删除全部代码，重新来

---

## 二、V2 做了什么不同的事

V2 吸取了 V1 的教训，做了以下改进：

1. **模块化架构**：9 个独立板块（基础设施→格式标准→文件处理→任务管理→AI分析→排版引擎→预览→模板→前端），每个板块有独立目录
2. **护理学论文格式标准**：四级标题体系（一、(一)、1.、(1)），特殊标题（摘要/Abstract/关键词/目录/参考文献/致谢/附录），黑体/宋体区分，Times New Roman for Latin
3. **段落匹配三策略**：编号+标题精确匹配 → start_marker 兜底 → 特殊关键词匹配
4. **前端重写**：React 19 + TypeScript + Vite + Tailwind + shadcn/ui，真实上传进度，章节导航，修改框

---

## 三、V2 最终状态

**全部 9 板块代码完成**，18 个 API 端点注册，TypeScript 编译通过，前端全流程可走通。

**端到端测试结果**（用测试论文 `test-paper-from-html.docx`）：
- 上传 ✓
- AI 分析（16 章节正确识别）✓
- 排版（40085 bytes 输出）✓
- 预览（16 章节，正文正确分配到各标题下）✓
- 下载（curl 测试：200 OK，正确 Content-Type 和 Content-Length）✓

**但在浏览器端用户下载失败**，暴露出以下问题。

---

## 四、BUG 编年史（按修复顺序）

### Bug 1：`'center' is not a valid WD_ALIGN_PARAGRAPH`
- **现象**：排版报错
- **根因**：前端传字符串 `"center"`，python-docx 需要枚举 `WD_ALIGN_PARAGRAPH.CENTER`
- **修复**：applier.py 加 `_normalize_alignment()` 字符串→枚举映射
- **教训**：前后端数据格式不匹配

### Bug 2：首行缩进被继承
- **现象**：标题也带缩进
- **根因**：原文档段落的首行缩进被 python-docx 保留
- **修复**：在 `_apply_spec` 中显式设置 `pf.first_line_indent`
- **教训**：python-docx 会保留原文档的段落属性，必须显式覆盖

### Bug 3：参考文献模式泄漏
- **现象**：参考文献后面的所有正文都变成参考文献格式
- **根因**：进入 `in_reference` 模式后没有退出机制
- **修复**：遇到新标题/特殊标题且不是"参考文献"时退出参考文献模式
- **教训**：状态机必须有明确的退出条件

### Bug 4：前端白屏
- **现象**：排版完成后页面闪一下然后全白
- **根因**：后端返回 `content: string[]`（数组），前端调 `s.content.split("\n")`（字符串方法）
- **修复**：types/index.ts 改成 `content: string[]`，渲染改成 `s.content.map()`
- **教训**：前后端类型必须一致，不能假设数据结构

### Bug 5：正文全部流向"致谢"章节
- **现象**：所有正文都出现在致谢里
- **根因**：`match_paragraph` 的 Strategy 0c（特殊关键词匹配）用了 `kw in clean` 子串匹配。比如正文中出现"参考文献"三个字就创建了假章节
- **修复**：改成 `clean.startswith(kw)` + 长度 ≤ 30 字符
- **教训**：宽松的子串匹配会污染整个匹配链

### Bug 6：目录条目被识别为章节
- **现象**：预览里出现 "1前言 ............ [页码]" 这样的标题
- **根因**：TOC 生成写死了 "............ [页码]" 文本，matcher 看到包含完整标题就匹配了
- **修复**：加 `_is_toc_entry()` 检测连续点号
- **教训**：生成的内容要考虑到它会被下游处理

### Bug 7：下载按钮点不了
- **现象**：fetch+Blob 方案让按钮无响应
- **根因**：JS 运行时错误导致组件崩溃
- **修复**：回退到 `<a>` 标签

### Bug 8：`<a download>` 报 `ERR_FAILED`
- **现象**：Chrome 拦截下载，显示"恢复/复制下载链接"
- **根因**：Chrome 阻止 `<a download>` 属性（安全策略）
- **修复**：去掉 `download` 属性，改用 `target="_blank"` + 服务端 `Content-Disposition: attachment`

### Bug 9：Internal Server Error（自定义异常未注册）
- **现象**：`NotFoundError` 返回 500 而不是 404
- **根因**：`AppError` 继承 `Exception` 而不是 FastAPI 的 `HTTPException`，FastAPI 不认识
- **修复**：`main.py` 加 `@app.exception_handler(AppError)`
- **教训**：自定义异常必须注册到框架

### Bug 10：`{"detail":"任务 undefined 不存在"}`
- **现象**：下载链接变成 `/api/download/undefined`
- **根因**：后端接口返回 `job_id` 字段，前端 `FormatJob` 类型用 `id` 字段。`setJob(analyzed)` 覆盖了之前的 job 对象，`job.id` 变成 `undefined`
- **修复**：4 个后端路由统一改成 `"id"`，前端用合并更新而非覆盖
- **教训**：字段命名不一致是沉默的杀手，前后端类型必须对齐

---

## 五、为什么 Bug 修不完

### 根本原因

1. **一次性做了太多东西**：V2 做了 9 个板块、18 个 API 端点、完整前端，但核心的"格式化→下载"链路都没在浏览器里实际验证过

2. **测试只在命令行做**：curl 测试全部通过，但浏览器里的真实场景（跨域、下载属性、Chrome 安全策略）完全没测

3. **没有"快乐路径"端到端测试**：每次都从上传开始，每次都要等 AI 分析。没有准备一个"已分析好"的状态快速跳到各个节点测试

4. **前后端字段名不一致**：`job_id` vs `id`，`structure` 格式反复变，改了后端漏了前端

5. **非核心功能抢了时间**：模板管理、格式设置面板、悬停浮窗花了很多时间，但核心下载都没跑通

6. **子智能体开发模式的代价**：9 个板块交给不同子智能体独立开发，每个都对自己的上下文负责，但没人对"拼起来能不能跑"负责

---

## 六、下一次的正确做法

### 用户的原话（一字不差）

> "下一次开始打开头脑风暴 skills 和 PUA skills，将我的要求一字不差的总结起来，这是以后的完成条件"

### 铁律（必须遵守）

1. **先跑通快乐路径再碰别的**：上传→分析→排版→下载，这 4 步必须在浏览器里 100% 正常，再写一行其他代码

2. **每个改动都在浏览器验证**：改完后端重启，改完前端刷新，点一遍完整流程

3. **前后端类型对齐**：所有接口返回的 JSON 必须和前端 `types/index.ts` 里的 interface 字段一一对应

4. **功能最小化**：只做 4 步流程 + 一个干净的界面。不要模板、不要设置面板、不要导航、不要修改框、不要历史记录、不要定价

5. **准备测试数据**：一个标准护理学论文 docx，放在固定路径，每次测试都用它

6. **下载功能第一时间做对**：下载是整个流程的终点，不能留到最后

### 必做 vs 不做的边界

**必做（核心流程）**：
- 上传 docx 文件
- AI 分析论文结构（标题层级、章节划分）
- 按护理学论文格式排版
- 浏览器下载排版后的文件

**不做（等核心跑通后再说）**：
- 模板管理/保存/切换
- 格式设置面板
- 手动标注模式
- 章节修改/重新排版
- 目录生成
- 页眉页脚
- 历史记录
- 定价/支付
- PDF 支持（只做 docx）

---

## 七、技术栈 & 启动命令（保留）

```
后端：Python + FastAPI + SQLAlchemy + SQLite + python-docx + DeepSeek API
前端：React 19 + TypeScript + Vite + Tailwind CSS 4 + shadcn/ui

启动：
  后端: cd backend && /c/Users/博博/python.exe -m uvicorn app.main:app --port 8000
  前端: cd frontend && npx vite --port 5173

访问：http://localhost:5173

关键配置：
  - 后端 .env 里 DeepSeek API key
  - 前端 vite.config.ts proxy target 端口必须和后端一致
```

---

## 八、复盘保存位置

- 本文档：`docs/project-retrospective.md`
- V2 设计文档：`docs/superpowers/specs/2026-05-19-paper-formatter-v2-design.md`
- V2 进程日志：`docs/superpowers/plans/2026-05-19-paper-formatter-v2-progress.md`

---

生成日期：2026-05-19（终版）
项目路径：C:\Users\博博\paper-formatter\
结果：代码已删除，docs/ 保留
