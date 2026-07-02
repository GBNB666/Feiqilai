"""字数统计与页数预估"""
import re
from docx import Document


def count_text(file_path: str) -> dict:
    """统计文档字数。中文按字计，英文按词计。"""
    doc = Document(file_path)
    all_text = ""
    for para in doc.paragraphs:
        all_text += para.text

    # 中文字符（含标点）
    cjk = len(re.findall(r"[一-鿿㐀-䶿]", all_text))
    # 英文单词（排除中文后的连续字母）
    non_cjk = re.sub(r"[一-鿿㐀-䶿]", " ", all_text)
    english_words = len(re.findall(r"[a-zA-Z]+", non_cjk))
    # 数字序列
    numbers = len(re.findall(r"\d+", non_cjk))

    total = cjk + english_words + numbers

    return {
        "char_count": total,
        "cjk_chars": cjk,
        "english_words": english_words,
        "numbers": numbers,
    }


def estimate_pages(
    char_count: int,
    font_size_pt: float = 12.0,
    line_spacing: float = 1.5,
    margin_left: float = 3.17,
    margin_right: float = 3.17,
    margin_top: float = 2.54,
    margin_bottom: float = 2.54,
) -> int:
    """根据字数和排版参数估算页数。"""
    if char_count <= 0:
        return 0

    # A4: 21cm x 29.7cm
    usable_w_cm = 21.0 - margin_left - margin_right
    usable_h_cm = 29.7 - margin_top - margin_bottom

    # 每字符宽度约 font_size_pt * 0.0353 cm
    char_w_cm = font_size_pt * 0.0353
    chars_per_line = max(1, usable_w_cm / char_w_cm)

    # 每行高度约 font_size_pt * line_spacing * 0.0353 cm
    if isinstance(line_spacing, (int, float)) and line_spacing < 5:
        line_h_cm = font_size_pt * line_spacing * 0.0353
    else:
        line_h_cm = float(line_spacing) * 0.0353

    lines_per_page = max(1, usable_h_cm / line_h_cm)

    chars_per_page = chars_per_line * lines_per_page
    pages = char_count / chars_per_page
    return max(1, round(pages))
