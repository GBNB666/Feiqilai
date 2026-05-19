import json
from httpx import Client, Timeout
from app.config import settings

SYSTEM_PROMPT = """你是一个学术论文排版专家。分析论文内容，识别并输出结构信息。

排版格式标准：
- 一级标题：黑体 16pt 加粗 居中
- 二级标题：黑体 14pt 加粗 左对齐
- 三级标题：黑体 12pt 加粗 左对齐
- 正文：宋体 12pt 两端对齐，1.5倍行距，首行缩进2字符
- 图注/表注：宋体 10.5pt 居中（以"图"或"表"开头）
- 参考文献标题为一级标题，条目为宋体10.5pt

严格按以下JSON格式输出，不要输出其他内容：

{
  "title": "论文标题",
  "abstract": "摘要内容的前100字",
  "sections": [
    {
      "level": 1,
      "title": "一级标题名称",
      "content_summary": "该节内容概述",
      "has_figures": false,
      "has_tables": false,
      "start_marker": "用于定位的起始文本片段（前20字）"
    }
  ],
  "references_count": 0,
  "has_toc": false,
  "has_abstract_section": false
}

规则：
- level: 1=一级标题(如"第一章"), 2=二级标题(如"1.1"), 3=三级标题(如"1.1.1")
- 从论文实际内容中提取标题文本，不要编造
- start_marker: 【重要】填写该节标题文字本身的前20字，用于程序精确定位标题段落。注意：一定要写标题行本身的文字，不要写正文内容！
- 识别所有层级的标题，包括"参考文献""致谢"等
- 如果无法读取文件内容，sections为空数组
- 图注和表注不列入sections
"""


def analyze_paper_structure(file_path: str, file_type: str) -> dict:
    text_content = _extract_text(file_path, file_type)
    if len(text_content) > 20000:
        text_content = text_content[:20000]

    client = Client(timeout=Timeout(120.0))
    try:
        response = client.post(
            f"{settings.deepseek_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"请分析以下论文内容的结构：\n\n{text_content}"},
                ],
                "temperature": 0.1,
                "max_tokens": 8000,
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # 截断响应时尝试修复：补全末尾括号
            cleaned = content.strip()
            open_braces = cleaned.count("{")
            close_braces = cleaned.count("}")
            open_brackets = cleaned.count("[")
            close_brackets = cleaned.count("]")
            cleaned += "]" * (open_brackets - close_brackets)
            cleaned += "}" * (open_braces - close_braces)
            return json.loads(cleaned)
    finally:
        client.close()


def detect_format_warnings(structure: dict) -> dict:
    """Detect missing structures, missing labels, and format conflicts."""
    warnings = {
        "missing_abstract": not structure.get("abstract") or len(structure.get("abstract", "")) < 10,
        "missing_toc": not structure.get("has_toc", False),
        "missing_references": structure.get("references_count", 0) == 0,
        "missing_figure_labels": [],
        "missing_table_labels": [],
        "conflicting_headings": [],
    }

    # Check sections for figures/tables without labels
    level_counts = {}
    for s in structure.get("sections", []):
        lv = s.get("level", 0)
        level_counts[lv] = level_counts.get(lv, 0) + 1
        if s.get("has_figures") and not _has_figure_label(s):
            warnings["missing_figure_labels"].append(s.get("title", "?"))
        if s.get("has_tables") and not _has_table_label(s):
            warnings["missing_table_labels"].append(s.get("title", "?"))

    # Check for missing heading levels (e.g., H3 without H2)
    if level_counts.get(3, 0) > 0 and level_counts.get(2, 0) == 0:
        warnings["conflicting_headings"].append("存在三级标题但缺少二级标题")

    return warnings


def _has_figure_label(section: dict) -> bool:
    s = section.get("content_summary", "") + section.get("start_marker", "")
    return "图" in s


def _has_table_label(section: dict) -> bool:
    s = section.get("content_summary", "") + section.get("start_marker", "")
    return "表" in s


def _extract_text(file_path: str, file_type: str) -> str:
    if file_type == "docx":
        from app.services.docx_processor import extract_text as docx_extract
        return docx_extract(file_path)
    elif file_type == "pdf":
        from app.services.pdf_processor import extract_text as pdf_extract
        return pdf_extract(file_path)
    return ""
