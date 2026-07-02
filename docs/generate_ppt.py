#!/usr/bin/env python3
"""Generate ZhiPai AI pitch deck PPT using python-pptx."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn, nsmap
from pptx.oxml import parse_xml
import math

# Namespace URI for 'a' prefix (DrawingML main)
NS_A = nsmap('a')['a']

# Constants
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

BG_COLOR      = RGBColor(15, 15, 25)
CARD_COLOR    = RGBColor(25, 25, 40)
ACCENT_INDI   = RGBColor(0x63, 0x66, 0xF1)
ACCENT_VIO    = RGBColor(0x8B, 0x5C, 0xF6)
WHITE         = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY    = RGBColor(0xBB, 0xBB, 0xCC)
DIM_GRAY      = RGBColor(0x66, 0x66, 0x88)
BORDER_COLOR  = RGBColor(0x3A, 0x3A, 0x50)
TRANSPARENT   = RGBColor(0x22, 0x22, 0x35)
GREEN         = RGBColor(0x34, 0xD3, 0x99)
ORANGE        = RGBColor(0xF5, 0x9E, 0x0B)

FONT_CN = 'SimHei'
FONT_EN = 'Arial'


def set_slide_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def set_line_spacing(paragraph, spacing_pct):
    pPr = paragraph._p.get_or_add_pPr()
    existing = pPr.find(qn('a:lnSpc'))
    if existing is not None:
        pPr.remove(existing)
    lnSpc = parse_xml(
        f'<a:lnSpc xmlns:a="{NS_A}"><a:spcPct val="{int(spacing_pct * 100)}"/></a:lnSpc>'
    )
    pPr.append(lnSpc)


def set_run_font(run, font_name=FONT_CN, font_size=Pt(16), bold=False, color=WHITE):
    run.font.name = font_name
    run.font.size = font_size
    run.font.bold = bold
    run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = parse_xml(f'<a:ea xmlns:a="{NS_A}" typeface="{FONT_CN}"/>')
        rPr.append(ea)
    else:
        ea.set('typeface', FONT_CN)


def add_textbox(slide, left, top, width, height, text="", font_name=FONT_CN,
                font_size=Pt(16), bold=False, color=WHITE, alignment=PP_ALIGN.LEFT,
                line_spacing=1.5, space_after=Pt(0), space_before=Pt(0),
                anchor=MSO_ANCHOR.TOP, word_wrap=True):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    txBox.word_wrap = word_wrap
    tf = txBox.text_frame
    tf.word_wrap = word_wrap
    tf.auto_size = None

    bodyPr = tf._txBody.find(qn('a:bodyPr'))
    if bodyPr is not None:
        anchor_map = {MSO_ANCHOR.TOP: 't', MSO_ANCHOR.MIDDLE: 'ctr', MSO_ANCHOR.BOTTOM: 'b'}
        bodyPr.set('anchor', anchor_map.get(anchor, 't'))

    if text:
        p = tf.paragraphs[0]
        p.text = text
        p.alignment = alignment
        p.space_after = space_after
        p.space_before = space_before
        set_line_spacing(p, line_spacing)
        for run in p.runs:
            set_run_font(run, font_name, font_size, bold, color)

    return txBox, tf


def add_para(tf, text, font_name=FONT_CN, font_size=Pt(16), bold=False,
             color=WHITE, alignment=PP_ALIGN.LEFT, line_spacing=1.5,
             space_after=Pt(4), space_before=Pt(2)):
    p = tf.add_paragraph()
    p.text = text
    p.alignment = alignment
    p.space_after = space_after
    p.space_before = space_before
    set_line_spacing(p, line_spacing)
    for run in p.runs:
        set_run_font(run, font_name, font_size, bold, color)
    return p


def add_footer(slide):
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.0), Inches(11.733), Pt(1)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = ACCENT_INDI
    line.line.fill.background()

    add_textbox(slide, Inches(0.8), Inches(7.08), Inches(11.733), Inches(0.35),
                text="智排AI", font_size=Pt(10), color=DIM_GRAY,
                alignment=PP_ALIGN.RIGHT)


def add_corner_decor(slide):
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.3), Inches(0.3), Pt(6), Pt(6))
    dot.fill.solid()
    dot.fill.fore_color.rgb = ACCENT_INDI
    dot.line.fill.background()

    line_tl = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.3), Inches(0.36), Inches(0.6), Pt(1.5)
    )
    line_tl.fill.solid()
    line_tl.fill.fore_color.rgb = ACCENT_VIO
    line_tl.line.fill.background()

    dot2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(12.8), Inches(0.3), Pt(6), Pt(6))
    dot2.fill.solid()
    dot2.fill.fore_color.rgb = ACCENT_INDI
    dot2.line.fill.background()


def add_card_bg(slide, left, top, width, height):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_COLOR
    card.line.color.rgb = BORDER_COLOR
    card.line.width = Pt(0.5)
    return card


def add_slide_number(slide, num):
    add_textbox(slide, Inches(12.2), Inches(7.1), Inches(0.8), Inches(0.3),
                text=str(num), font_size=Pt(9), color=DIM_GRAY,
                alignment=PP_ALIGN.RIGHT)


def add_icon_block(slide, left, top, width, icon, label, desc_lines,
                   label_size=Pt(15), desc_size=Pt(12)):
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, Pt(36), Pt(36))
    circle.fill.solid()
    circle.fill.fore_color.rgb = TRANSPARENT
    circle.line.color.rgb = ACCENT_INDI
    circle.line.width = Pt(1.5)
    tf = circle.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = icon
    for run in p.runs:
        run.font.size = Pt(16)
        run.font.color.rgb = ACCENT_INDI
        run.font.name = FONT_EN

    add_textbox(slide, left + Pt(46), top + Pt(2), width - Pt(46), Pt(32),
                text=label, font_size=label_size, bold=True, color=WHITE)

    y_off = top + Pt(40)
    for line in desc_lines:
        add_textbox(slide, left + Pt(46), y_off, width - Pt(46), Pt(24),
                    text=line, font_size=desc_size, color=LIGHT_GRAY, line_spacing=1.4)
        y_off += Pt(22)


def add_arrow_icon(slide, left, top, size, color=ACCENT_INDI, rotation=0):
    arrow = slide.shapes.add_shape(
        MSO_SHAPE.RIGHT_ARROW, left, top, size, size
    )
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = color
    arrow.line.fill.background()
    if rotation:
        arrow.rotation = rotation


# ================ SLIDE BUILDERS ================

def build_slide1(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_COLOR)
    add_corner_decor(slide)

    # Decorative vertical line
    vline = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(2.0), Pt(3), Inches(3.5)
    )
    vline.fill.solid()
    vline.fill.fore_color.rgb = ACCENT_INDI
    vline.line.fill.background()

    # Title
    add_textbox(slide, Inches(1.8), Inches(2.0), Inches(10.0), Inches(1.0),
                text="你有没有被论文格式逼疯过？",
                font_size=Pt(38), bold=True, color=WHITE, line_spacing=1.3)

    # Subtitle
    add_textbox(slide, Inches(1.8), Inches(3.0), Inches(8.0), Inches(0.5),
                text="EVER BEEN DRIVEN CRAZY BY PAPER FORMATTING?",
                font_name=FONT_EN, font_size=Pt(13), color=DIM_GRAY, line_spacing=1.2)

    # Card
    add_card_bg(slide, Inches(1.8), Inches(3.8), Inches(9.5), Inches(2.7))

    points = [
        "调格式占 4-6 个小时，比写内容还花时间",
        "一个地方改错，整个文档格式全塌",
        "全国 1200 多万毕业生，每个人都要过这一关",
        "现有工具的套路：办公软件太复杂，在线工具识别不准还有隐私风险",
    ]

    _, tf = add_textbox(slide, Inches(2.2), Inches(4.0), Inches(8.8), Inches(2.3),
                        font_size=Pt(17), color=LIGHT_GRAY, line_spacing=1.7)

    for i, pt_text in enumerate(points):
        if i == 0:
            p = tf.paragraphs[0]
            p.clear()
        else:
            p = tf.add_paragraph()

        run_icon = p.add_run()
        run_icon.text = "▸ "
        set_run_font(run_icon, font_size=Pt(17), color=ACCENT_INDI)

        run_text = p.add_run()
        run_text.text = pt_text
        set_run_font(run_text, font_size=Pt(17), color=LIGHT_GRAY)

        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(8)
        p.space_before = Pt(4)
        set_line_spacing(p, 1.7)

    add_footer(slide)
    add_slide_number(slide, 1)

    notes = slide.notes_slide
    notes.notes_text_frame.text = (
        "我先说一个每个人都遇到过的事。写论文，最烦的不是写内容，是调格式。"
        "标题用什么字号、行距多少、参考文献怎么排——光这一堆事就要花掉四到六个小时。"
        "最崩溃的是什么？一个地方改错了，整个文档格式全塌了。"
        "全国一千两百多万毕业生，每个人都要过这一关。"
        "那现在有没有工具能帮忙呢？电脑自带的办公软件，功能太多太复杂。"
        "网上的一些排版工具呢，号称自动排版，但是经常把标题级别认错，"
        "而且要求你把论文上传到它们的服务器上——毕业论文是每个人的心血，"
        "你愿意随便传到别人的服务器上吗？这个问题，有一个人在认真解决。"
    )


def build_slide2(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_COLOR)
    add_corner_decor(slide)

    # Title
    add_textbox(slide, Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.7),
                text="智排AI —— 上传 / 分级 / 排版 / 下载",
                font_size=Pt(34), bold=True, color=WHITE, line_spacing=1.3)

    add_textbox(slide, Inches(0.8), Inches(1.05), Inches(11.5), Inches(0.4),
                text="ZHIPAI AI: UPLOAD / CLASSIFY / FORMAT / DOWNLOAD",
                font_name=FONT_EN, font_size=Pt(11), color=DIM_GRAY, line_spacing=1.2)

    # Left side feature blocks
    features = [
        ("\U0001f4f1", "微信小程序，点开即用", ["无需下载安装，扫码就能排版"]),
        ("✋",  "自己先标标题级别",     ["你的论文你最清楚，不靠AI瞎猜"]),
        ("⚡",  "AI 精准执行排版",       ["几秒钟出结果，格式标准统一"]),
        ("\U0001f512","全程本地处理",        ["论文不上传，隐私零泄露"]),
        ("\U0001f464","项目负责人",           ["护理学专业在校生，零基础自学编程"]),
    ]

    y_start = Inches(1.6)
    for icon, label, desc in features:
        add_icon_block(slide, Inches(0.8), y_start, Inches(5.8),
                       icon, label, desc, label_size=Pt(15), desc_size=Pt(12))
        y_start += Inches(0.78)

    # Video placeholder - right side
    vid_left = Inches(7.2)
    vid_top = Inches(1.8)
    vid_w = Inches(5.5)
    vid_h = Inches(4.5)

    vid_card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, vid_left, vid_top, vid_w, vid_h
    )
    vid_card.fill.solid()
    vid_card.fill.fore_color.rgb = CARD_COLOR
    vid_card.line.color.rgb = BORDER_COLOR
    vid_card.line.width = Pt(1)

    # Dashed border
    dash_rect = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        vid_left + Inches(0.4), vid_top + Inches(0.4),
        vid_w - Inches(0.8), vid_h - Inches(0.8)
    )
    dash_rect.fill.background()
    dash_rect.line.color.rgb = ACCENT_INDI
    dash_rect.line.width = Pt(1.5)

    spPr = dash_rect._element.find(qn('a:spPr'))
    if spPr is None:
        spPr = parse_xml(f'<a:spPr xmlns:a="{NS_A}"/>')
        dash_rect._element.insert(0, spPr)
    ln = spPr.find(qn('a:ln'))
    if ln is None:
        ln = parse_xml(f'<a:ln xmlns:a="{NS_A}" w="19050"><a:prstDash val="dash"/></a:ln>')
        spPr.append(ln)
    else:
        ln.set('w', '19050')
        prstDash = ln.find(qn('a:prstDash'))
        if prstDash is not None:
            prstDash.set('val', 'dash')
        else:
            prstDash = parse_xml(f'<a:prstDash xmlns:a="{NS_A}" val="dash"/>')
            ln.append(prstDash)

    # Play triangle
    play_size = Pt(60)
    play = slide.shapes.add_shape(
        MSO_SHAPE.ISOSCELES_TRIANGLE,
        vid_left + vid_w / 2 - play_size / 2,
        vid_top + vid_h / 2 - play_size / 2 - Pt(10),
        play_size, play_size
    )
    play.fill.solid()
    play.fill.fore_color.rgb = ACCENT_INDI
    play.line.fill.background()
    play.rotation = 90.0

    # Video label
    add_textbox(slide, vid_left + Inches(0.5), vid_top + vid_h / 2 + Pt(30),
                vid_w - Inches(1.0), Inches(0.5),
                text="演示视频",
                font_size=Pt(16), bold=True, color=ACCENT_INDI,
                alignment=PP_ALIGN.CENTER, line_spacing=1.2)

    add_footer(slide)
    add_slide_number(slide, 2)

    notes = slide.notes_slide
    notes.notes_text_frame.text = (
        "这个人做的东西叫智排AI，一个微信小程序，点开就能用。"
        "用起来很简单：你把论文上传上去，先自己标一下哪个是大标题、哪个是小标题、"
        "哪个是正文——为什么要自己标？因为你的论文写了什么只有你最清楚，让软件去猜一定会出错。"
        "标完之后点一个按钮，几秒钟，全文的格式就给你排得规规整整，直接就能下载。"
        "最关键的一点：整个过程都在你的手机或电脑本地完成，你的论文从头到尾没有离开过你自己的设备，"
        "没有被上传到任何地方。做这个项目的人，不是什么计算机大神。他是一个护理学专业的在校学生，"
        "零编程基础，一行代码没写过。因为自己被论文格式折磨得太惨了，于是借助现在的人工智能工具，"
        "自学编程，从零开始把这个系统搭了出来。"
    )


def build_slide3(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_COLOR)
    add_corner_decor(slide)

    add_textbox(slide, Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.7),
                text="为什么不一样？",
                font_size=Pt(36), bold=True, color=WHITE, line_spacing=1.3)

    add_textbox(slide, Inches(0.8), Inches(1.05), Inches(11.5), Inches(0.4),
                text="WHAT MAKES US DIFFERENT?",
                font_name=FONT_EN, font_size=Pt(11), color=DIM_GRAY, line_spacing=1.2)

    cards_data = [
        ("01", "先分级、后排版",
         "用户掌握控制权，AI 精准执行，不瞎猜。\n你标记好标题层级，AI 只负责排版执行。",
         ACCENT_INDI),
        ("02", "本地处理、隐私安全",
         "论文不离开你的设备，零泄露风险。\n所有运算在本地完成，无需上传服务器。",
         ACCENT_VIO),
        ("03", "排版完就能下载",
         "无水印、不付费、不套路。\n完整 DOCX 文件直接下载，每月还送免费次数。",
         GREEN),
    ]

    card_w = Inches(3.7)
    card_h = Inches(4.8)
    gap = Inches(0.3)
    start_x = Inches(0.8)

    for i, (num, title, desc, accent) in enumerate(cards_data):
        cx = start_x + i * (card_w + gap)
        cy = Inches(1.7)

        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, cx, cy, card_w, card_h
        )
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_COLOR
        card.line.color.rgb = accent
        card.line.width = Pt(1)

        add_textbox(slide, cx + Inches(0.3), cy + Inches(0.3), Inches(0.8), Inches(0.6),
                    text=num, font_size=Pt(42), bold=True, color=accent, line_spacing=1.0)

        add_textbox(slide, cx + Inches(0.3), cy + Inches(1.1),
                    card_w - Inches(0.6), Inches(0.6),
                    text=title, font_size=Pt(22), bold=True, color=WHITE, line_spacing=1.3)

        aline = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, cx + Inches(0.3), cy + Inches(1.75),
            Inches(1.0), Pt(2.5)
        )
        aline.fill.solid()
        aline.fill.fore_color.rgb = accent
        aline.line.fill.background()

        add_textbox(slide, cx + Inches(0.3), cy + Inches(2.0),
                    card_w - Inches(0.6), Inches(2.5),
                    text=desc, font_size=Pt(15), color=LIGHT_GRAY, line_spacing=1.8)

    add_footer(slide)
    add_slide_number(slide, 3)

    notes = slide.notes_slide
    notes.notes_text_frame.text = (
        "和现在市面上已有的工具相比，这个东西有三点不一样。"
        "第一，你先自己分好标题级别，软件帮你精准排版，而不是软件自己瞎猜瞎排。"
        "第二，全部在你自己的设备上完成，论文不上传到任何地方，隐私完全安全。"
        "第三，排版完了就能下载完整文件，没有水印，不用先交钱，不搞那些花里胡哨的套路。"
    )


def build_slide4(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_COLOR)
    add_corner_decor(slide)

    add_textbox(slide, Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.7),
                text="怎么赚钱？市场多大？",
                font_size=Pt(36), bold=True, color=WHITE, line_spacing=1.3)

    add_textbox(slide, Inches(0.8), Inches(1.05), Inches(11.5), Inches(0.4),
                text="BUSINESS MODEL & MARKET SIZE",
                font_name=FONT_EN, font_size=Pt(11), color=DIM_GRAY, line_spacing=1.2)

    # Left panel
    add_card_bg(slide, Inches(0.8), Inches(1.7), Inches(5.6), Inches(4.8))

    add_textbox(slide, Inches(1.2), Inches(1.9), Inches(4.8), Inches(0.5),
                text="盈利模式", font_size=Pt(22), bold=True, color=ACCENT_INDI, line_spacing=1.2)

    model_items = [
        ("每月免费 1 次", "应急够用，降低使用门槛"),
        ("超量每次 3-5 元", "约等于一杯奶茶的价格"),
        ("降重功能 8 折", "按市场价 8 折收费"),
        ("广告免费通道", "看广告也能免费排版"),
    ]

    y_pos = Inches(2.6)
    for title, sub in model_items:
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(1.2), y_pos + Pt(5), Pt(8), Pt(8)
        )
        dot.fill.solid()
        dot.fill.fore_color.rgb = ACCENT_INDI
        dot.line.fill.background()

        add_textbox(slide, Inches(1.6), y_pos, Inches(4.4), Inches(0.35),
                    text=title, font_size=Pt(17), bold=True, color=WHITE, line_spacing=1.2)

        add_textbox(slide, Inches(1.6), y_pos + Inches(0.35), Inches(4.4), Inches(0.3),
                    text=sub, font_size=Pt(13), color=LIGHT_GRAY, line_spacing=1.2)

        y_pos += Inches(0.82)

    # Right panel
    add_card_bg(slide, Inches(6.8), Inches(1.7), Inches(5.7), Inches(4.8))

    add_textbox(slide, Inches(7.2), Inches(1.9), Inches(4.8), Inches(0.5),
                text="市场空间", font_size=Pt(22), bold=True, color=ACCENT_VIO, line_spacing=1.2)

    add_textbox(slide, Inches(7.2), Inches(2.6), Inches(4.8), Inches(0.8),
                text="4,800 万+", font_size=Pt(44), bold=True, color=ACCENT_VIO, line_spacing=1.0)

    add_textbox(slide, Inches(7.2), Inches(3.3), Inches(4.8), Inches(0.4),
                text="全国高校在校生总数", font_size=Pt(14), color=LIGHT_GRAY, line_spacing=1.2)

    calc_items = [
        ("千分之一渗透", "= 年 20 万篇次"),
        ("保守预估", "足够养活小团队"),
    ]

    y_pos2 = Inches(3.9)
    for label, value in calc_items:
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(7.2), y_pos2 + Pt(6), Pt(8), Pt(8)
        )
        dot.fill.solid()
        dot.fill.fore_color.rgb = ACCENT_VIO
        dot.line.fill.background()

        add_textbox(slide, Inches(7.6), y_pos2, Inches(2.5), Inches(0.35),
                    text=label, font_size=Pt(15), color=LIGHT_GRAY, line_spacing=1.2)

        add_textbox(slide, Inches(10.2), y_pos2, Inches(1.8), Inches(0.35),
                    text=value, font_size=Pt(15), bold=True, color=WHITE, line_spacing=1.2)

        y_pos2 += Inches(0.55)

    add_footer(slide)
    add_slide_number(slide, 4)

    notes = slide.notes_slide
    notes.notes_text_frame.text = (
        "怎么赚钱呢？很简单。每个月免费送你一次，够你应急用。"
        "超过一次，每次收三到五块钱，就是一杯奶茶的钱。"
        "后面还会加上降重功能，按市场价的八折收费。"
        "小程序里面也会放广告，不想花钱的话，看广告也能免费排版。"
        "市场有多大？全国高校在校生四千八百万。"
        "哪怕只有千分之一的人用，一年也是二十万篇次，最保守算也足够养活一个小团队了。"
    )


def build_slide5(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_COLOR)
    add_corner_decor(slide)

    add_textbox(slide, Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.7),
                text="走到哪了？下一步？",
                font_size=Pt(36), bold=True, color=WHITE, line_spacing=1.3)

    add_textbox(slide, Inches(0.8), Inches(1.05), Inches(11.5), Inches(0.4),
                text="PROGRESS & ROADMAP",
                font_name=FONT_EN, font_size=Pt(11), color=DIM_GRAY, line_spacing=1.2)

    # Left - Current progress
    add_card_bg(slide, Inches(0.8), Inches(1.7), Inches(5.6), Inches(2.3))

    add_textbox(slide, Inches(1.2), Inches(1.85), Inches(4.8), Inches(0.4),
                text="当前进度", font_size=Pt(20), bold=True, color=GREEN, line_spacing=1.2)

    progress_items = [
        "核心功能全流程跑通（上传/分级/排版/下载）",
        "小程序准备上线，从本校和创业比赛起步",
        "明年 3-6 月毕业季集中发力",
    ]
    py2 = Inches(2.4)
    for item in progress_items:
        add_textbox(slide, Inches(1.2), py2, Inches(4.8), Inches(0.35),
                    text=item, font_size=Pt(14), color=LIGHT_GRAY, line_spacing=1.4)
        py2 += Inches(0.42)

    # Right - Roadmap
    add_card_bg(slide, Inches(6.8), Inches(1.7), Inches(5.7), Inches(2.3))

    add_textbox(slide, Inches(7.2), Inches(1.85), Inches(4.8), Inches(0.4),
                text="未来规划", font_size=Pt(20), bold=True, color=ACCENT_INDI, line_spacing=1.2)

    roadmap_items = [
        ("V1.5", "AI 论文结构分析", ACCENT_INDI),
        ("V2.0", "AI 降重功能", ACCENT_VIO),
        ("V3.0", "模板市场 + Web 端", GREEN),
    ]

    ry = Inches(2.4)
    for ver, desc, clr in roadmap_items:
        badge = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), ry, Inches(0.7), Inches(0.3)
        )
        badge.fill.solid()
        badge.fill.fore_color.rgb = clr
        badge.line.fill.background()
        tf = badge.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = ver
        for run in p.runs:
            run.font.size = Pt(10)
            run.font.color.rgb = WHITE
            run.font.bold = True
            run.font.name = FONT_EN

        add_textbox(slide, Inches(8.05), ry, Inches(0.4), Inches(0.3),
                    text=">", font_size=Pt(14), bold=True, color=clr,
                    alignment=PP_ALIGN.CENTER, line_spacing=1.0)

        add_textbox(slide, Inches(8.5), ry + Pt(1), Inches(3.5), Inches(0.3),
                    text=desc, font_size=Pt(15), bold=True, color=WHITE, line_spacing=1.2)

        ry += Inches(0.62)

    # Bottom note
    add_textbox(slide, Inches(0.8), Inches(4.5), Inches(11.5), Inches(0.5),
                text="技术框架已就绪，开发速度会很快",
                font_size=Pt(13), color=DIM_GRAY, alignment=PP_ALIGN.LEFT, line_spacing=1.2)

    # Timeline
    timeline_y = Inches(5.3)
    hline = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(1.5), timeline_y, Inches(10.3), Pt(2)
    )
    hline.fill.solid()
    hline.fill.fore_color.rgb = BORDER_COLOR
    hline.line.fill.background()

    milestones = [
        ("Q2 2025", "核心功能\n跑通", True),
        ("Q3 2025", "小程序\n上线", True),
        ("Q1 2026", "毕业季\n发力", False),
        ("Q2 2026", "V2.0\n降重", False),
        ("Q4 2026", "V3.0\n模板市场", False),
    ]

    for j, (time_label, desc, done) in enumerate(milestones):
        mx = Inches(1.5 + j * 2.1)

        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, mx + Inches(0.5), timeline_y - Pt(5), Pt(12), Pt(12)
        )
        dot.fill.solid()
        dot.fill.fore_color.rgb = GREEN if done else BORDER_COLOR
        dot.line.fill.background()

        add_textbox(slide, mx, timeline_y - Inches(0.7), Inches(1.5), Inches(0.35),
                    text=time_label, font_size=Pt(11), bold=True,
                    color=GREEN if done else LIGHT_GRAY,
                    alignment=PP_ALIGN.CENTER, line_spacing=1.2)

        add_textbox(slide, mx, timeline_y + Inches(0.15), Inches(1.5), Inches(0.7),
                    text=desc, font_size=Pt(11),
                    color=WHITE if done else DIM_GRAY,
                    alignment=PP_ALIGN.CENTER, line_spacing=1.4)

    add_footer(slide)
    add_slide_number(slide, 5)

    notes = slide.notes_slide
    notes.notes_text_frame.text = (
        "现在做到什么程度了？最核心的功能已经全部跑通了——"
        "上传论文、划分层级、自动排版、下载文件，整个流程顺顺利利。"
        "接下来，小程序准备上线，先从自己学校和创新创业比赛圈子开始推。"
        "抓住明年三月到六月的毕业季集中发力。"
        "后面还有两个大功能要加：一个是自动降重，一个是文献格式自动生成，"
        "技术框架已经准备好了，开发速度会很快。"
    )


def build_slide6(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_COLOR)
    add_corner_decor(slide)

    # Large subtle circle
    circle_bg = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, Inches(4.0), Inches(1.0), Inches(5.333), Inches(5.333)
    )
    circle_bg.fill.solid()
    circle_bg.fill.fore_color.rgb = RGBColor(20, 20, 40)
    circle_bg.line.fill.background()

    # Small accent circles around
    for angle_deg in [0, 120, 240]:
        rad = math.radians(angle_deg)
        r = Inches(2.8)
        cx = Inches(6.667)
        cy = Inches(3.3)
        px = int(cx + r * math.cos(rad)) - Pt(4)
        py = int(cy + r * math.sin(rad)) - Pt(4)
        small_dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, px, py, Pt(8), Pt(8)
        )
        small_dot.fill.solid()
        small_dot.fill.fore_color.rgb = ACCENT_INDI
        small_dot.line.fill.background()

    # Main title
    add_textbox(slide, Inches(1.5), Inches(2.0), Inches(10.333), Inches(1.0),
                text="让论文排版，一键搞定",
                font_size=Pt(42), bold=True, color=WHITE,
                alignment=PP_ALIGN.CENTER, line_spacing=1.3)

    # Subtitle
    add_textbox(slide, Inches(2.0), Inches(3.1), Inches(9.333), Inches(0.6),
                text="每月免费一次 / 超量几块钱 / 先跑通校园再做大",
                font_size=Pt(18), color=LIGHT_GRAY,
                alignment=PP_ALIGN.CENTER, line_spacing=1.4)

    # Divider
    divider = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(5.5), Inches(3.9), Inches(2.333), Pt(2)
    )
    divider.fill.solid()
    divider.fill.fore_color.rgb = ACCENT_INDI
    divider.line.fill.background()

    # Thank you
    add_textbox(slide, Inches(5.0), Inches(4.3), Inches(3.333), Inches(0.5),
                text="谢谢",
                font_size=Pt(28), bold=True, color=WHITE,
                alignment=PP_ALIGN.CENTER, line_spacing=1.2)

    add_textbox(slide, Inches(5.0), Inches(4.85), Inches(3.333), Inches(0.35),
                text="THANK YOU",
                font_name=FONT_EN, font_size=Pt(12), color=DIM_GRAY,
                alignment=PP_ALIGN.CENTER, line_spacing=1.2)

    # Bottom tagline
    add_textbox(slide, Inches(3.0), Inches(5.6), Inches(7.333), Inches(0.4),
                text="智排AI - 微信小程序 - 让每个人都能轻松搞定论文格式",
                font_size=Pt(12), color=DIM_GRAY,
                alignment=PP_ALIGN.CENTER, line_spacing=1.2)

    add_footer(slide)
    add_slide_number(slide, 6)

    notes = slide.notes_slide
    notes.notes_text_frame.text = (
        "最后总结一下：论文排版太烦人了，我们把它变成一键搞定。"
        "每个月免费一次，超过收几块钱。"
        "先从校园做起，跑通再做更大。谢谢大家。"
    )


# ================ MAIN ================

def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    build_slide1(prs)
    build_slide2(prs)
    build_slide3(prs)
    build_slide4(prs)
    build_slide5(prs)
    build_slide6(prs)

    output_path = r"C:\Users\博博\paper-formatter\docs\智排AI_比赛PPT.pptx"
    prs.save(output_path)
    print("PPT saved to: " + output_path)
    print("Done! 6 slides generated.")


if __name__ == '__main__':
    main()
