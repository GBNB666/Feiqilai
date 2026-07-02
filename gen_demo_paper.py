# -*- coding: utf-8 -*-
"""Generate a realistic nursing thesis demo paper on Desktop."""
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

OUT = r"D:\HuaweiMoveData\Users\博博\Desktop\护理学论文-演示用.docx"

def sf(run, cn, en, sz, bold=False):
    run.font.size = Pt(sz)
    run.bold = bold
    rPr = run._element.get_or_add_rPr()
    rf = rPr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rPr.insert(0, rf)
    rf.set(qn('w:eastAsia'), cn)
    rf.set(qn('w:ascii'), en)
    rf.set(qn('w:hAnsi'), en)
    rf.set(qn('w:cs'), en)

def ap(doc, text, cn="宋体", en="Times New Roman", sz=12, bold=False, al="justify",
       indent=True, sb=0, sa=0, ls=22):
    p = doc.add_paragraph()
    r = p.add_run(text)
    sf(r, cn, en, sz, bold)
    am = {"center": WD_ALIGN_PARAGRAPH.CENTER, "left": WD_ALIGN_PARAGRAPH.LEFT,
          "justify": WD_ALIGN_PARAGRAPH.JUSTIFY}
    p.paragraph_format.alignment = am.get(al, WD_ALIGN_PARAGRAPH.JUSTIFY)
    p.paragraph_format.space_before = Pt(sb)
    p.paragraph_format.space_after = Pt(sa)
    p.paragraph_format.line_spacing = Pt(ls)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.AT_LEAST
    if indent:
        p.paragraph_format.first_line_indent = Pt(24)
    return p

def h1(doc, t): return ap(doc, t, "黑体", "Times New Roman", 14, True, "left", False, 12, 6, 28)
def h2(doc, t): return ap(doc, t, "黑体", "Times New Roman", 12, True, "left", False, 8, 4, 22)
def h3(doc, t): return ap(doc, t, "宋体", "Times New Roman", 12, True, "left", False, 6, 2, 22)
def h4(doc, t): return ap(doc, t, "宋体", "Times New Roman", 12, True, "left", False, 4, 2, 22)
def body(doc, t): return ap(doc, t, "宋体", "Times New Roman", 12, False, "justify", True, 0, 0, 22)
def spec(doc, t): return ap(doc, t, "黑体", "Times New Roman", 12, True, "justify", False, 12, 0, 22)

doc = Document()
for sec in doc.sections:
    sec.top_margin = Cm(2.54)
    sec.bottom_margin = Cm(2.54)
    sec.left_margin = Cm(3.17)
    sec.right_margin = Cm(3.17)

# ── TITLE ──
ap(doc, "", "宋体", "Times New Roman", 12, al="center", indent=False, sb=72)
ap(doc, "新型冠状病毒感染患者康复期呼吸功能训练方案的构建与效果评价",
   "黑体", "Times New Roman", 16, True, "center", False, 0, 8, 30)

# ── ABSTRACT ──
spec(doc, "【摘要】")
body(doc, "目的  构建适用于新型冠状病毒感染康复期患者的呼吸功能训练方案，"
     "并评价其对肺功能、运动耐力及生活质量的干预效果。"
     "方法  采用Delphi法对16名呼吸科、康复科及护理学专家进行两轮函询，"
     "构建呼吸功能训练方案；便利选取2024年3月至2025年1月在武汉市某三甲医院"
     "呼吸科收治的COVID-19康复期患者86例，按随机数字表法分为观察组（n=43）"
     "及对照组（n=43）。对照组接受常规康复护理，观察组在此基础上实施本研究"
     "构建的呼吸功能训练方案，干预周期为8周。比较两组干预前后的肺功能指标"
     "（FVC、FEV1、FEV1/FVC）、6分钟步行距离（6MWD）及圣乔治呼吸问卷（SGRQ）评分。"
     "结果  最终形成的呼吸功能训练方案包含呼吸肌训练、胸廓活动度训练、"
     "渐进式有氧运动及心理行为干预4个维度、18个条目。干预8周后，观察组FVC、"
     "FEV1、FEV1/FVC分别为（2.89±0.41）L、（2.31±0.38）L、（79.93±6.21）%，"
     "均优于对照组（2.54±0.39）L、（1.98±0.35）L、（77.95±5.84）%（均P<0.05）；"
     "观察组6MWD为（438.72±52.16）m，高于对照组（392.45±48.93）m（P<0.001）；"
     "观察组SGRQ总分为（24.56±8.37）分，低于对照组（32.18±10.05）分（P<0.001）。"
     "结论  本研究构建的呼吸功能训练方案科学、可行，能够有效改善COVID-19康复期"
     "患者的肺功能及运动耐力，提升生活质量。")
spec(doc, "【关键词】新型冠状病毒感染；康复期；呼吸功能训练；肺康复；护理")

# ── ENGLISH ABSTRACT ──
spec(doc, "【Abstract】")
body(doc, "Objective  To construct a respiratory function training program for "
     "patients in the convalescent phase of COVID-19 and evaluate its effects "
     "on pulmonary function, exercise tolerance, and quality of life. "
     "Methods  A two-round Delphi consultation was conducted with 16 experts "
     "from respiratory, rehabilitation, and nursing disciplines to develop the "
     "training program. A total of 86 convalescent COVID-19 patients were "
     "recruited and randomly assigned to an observation group (n=43) and a "
     "control group (n=43). The control group received routine rehabilitation "
     "nursing, while the observation group underwent the 8-week respiratory "
     "function training program. Pulmonary function indicators (FVC, FEV1, "
     "FEV1/FVC), 6-minute walking distance (6MWD), and St. George's Respiratory "
     "Questionnaire (SGRQ) scores were compared between the two groups. "
     "Results  The final training program comprised 4 dimensions (respiratory "
     "muscle training, thoracic mobility training, progressive aerobic exercise, "
     "and psychological-behavioral intervention) with 18 items. After 8 weeks, "
     "the observation group demonstrated significantly better outcomes compared "
     "to the control group in all measured indicators (P<0.05). "
     "Conclusion  The respiratory function training program is scientifically "
     "sound and feasible, effectively improving pulmonary function, exercise "
     "tolerance, and quality of life in convalescent COVID-19 patients.")
spec(doc, "【Keywords】COVID-19; convalescent phase; respiratory function training; "
     "pulmonary rehabilitation; nursing")

# ── 一、前言 ──
h1(doc, "一、前言")

body(doc, "新型冠状病毒感染（Coronavirus Disease 2019, COVID-19）是由严重急性呼吸"
     "综合征冠状病毒2型（SARS-CoV-2）引起的急性呼吸道传染病，自2019年12月暴发"
     "以来迅速席卷全球，对人类健康及公共卫生体系造成了前所未有的冲击[1]。据世界"
     "卫生组织统计，截至2025年6月，全球累计确诊病例已超过7.8亿例，其中相当比例"
     "的患者在急性期后存在持续性的呼吸系统症状及功能障碍[2]。")

body(doc, "临床研究表明，COVID-19康复期患者普遍存在不同程度的肺功能损伤，主要表现"
     "为用力肺活量（FVC）下降、第一秒用力呼气容积（FEV1）降低以及肺弥散功能"
     "（DLCO）减退[3-4]。Huang等[5]对1733例COVID-19出院患者进行了为期6个月的"
     "随访，发现约76%的患者在急性感染后仍至少存在一种症状，其中以疲劳/肌无力"
     "（63%）、睡眠困难（26%）及呼吸困难（22%）最为常见。此外，部分重症患者在"
     "康复期出现了肺纤维化的影像学表现，进一步加重了呼吸功能障碍的程度[6]。")

body(doc, "呼吸功能训练是肺康复的核心组成部分，已被广泛应用于慢性阻塞性肺疾病"
     "（COPD）、支气管哮喘及间质性肺疾病等多种呼吸系统疾病的康复管理中，并取得"
     "了确切的临床效果[7-8]。然而，目前国内外尚缺乏针对COVID-19康复期患者这一"
     "特殊人群的系统化、规范化的呼吸功能训练方案。现有研究多为小样本的初步探索，"
     "干预方案的构建缺乏科学的方法学支撑，训练内容、强度、频率及周期存在较大的"
     "异质性[9]。")

body(doc, "基于上述背景，本研究旨在通过Delphi专家函询法，构建一套适用于COVID-19"
     "康复期患者的系统化呼吸功能训练方案，并采用随机对照试验设计评价其临床应用"
     "效果，以期为COVID-19康复期患者的护理干预提供科学依据和实践指导。")

# ── 二、对象与方法 ──
h1(doc, "二、对象与方法")

h2(doc, "（一）方案构建")

h3(doc, "1. 成立研究小组")
body(doc, "研究小组由7名成员组成，包括主任医师1名（呼吸科）、副主任护师2名（呼吸科"
     "及康复科）、主管护师2名、护理学硕士研究生2名。研究小组负责文献检索与证据"
     "综合、专家函询问卷的编制与发放、函询结果的统计分析以及训练方案的最终确定。")

h3(doc, "2. 专家函询")

h4(doc, "（1）专家遴选标准")
body(doc, "纳入标准：具有本科及以上学历、副高级及以上专业技术职称；在呼吸科、康复"
     "医学科或相关护理领域从事临床或教学工作10年及以上；对肺康复及呼吸功能训练"
     "有较深的专业认知和实践经验；自愿参与本研究并能够保证完成两轮函询。共选取"
     "来自北京、上海、广州、武汉、成都5个城市的16名专家参与函询。")

h4(doc, "（2）函询过程")
body(doc, "第一轮函询问卷包含三个部分：卷首语，说明研究背景、目的及填写要求；专家"
     "基本信息调查表；呼吸功能训练方案初稿条目池，请专家对各条目的重要性采用"
     "Likert 5级评分法进行评分（1=很不重要，5=非常重要），并设有开放性问题供"
     "专家提出修改意见。第二轮函询问卷在第一轮分析结果的基础上进行修订，再次请"
     "专家对条目进行重要性评分。条目筛选标准为：重要性赋值均数大于等于4.0且变异"
     "系数（CV）小于等于0.25，同时结合专家的文字意见进行综合判断。")

h3(doc, "3. 方案形成")
body(doc, "两轮函询的专家积极系数分别为100%（16/16）及93.75%（15/16），专家权威系数"
     "（Cr）为0.87±0.06，表明专家权威程度较高。两轮函询的Kendall协调系数W分别"
     "为0.312（P<0.001）及0.378（P<0.001），表明专家意见趋于一致。最终形成的"
     "呼吸功能训练方案包含4个维度、18个条目，具体方案内容详见表1。")

h2(doc, "（二）临床应用评价")

h3(doc, "1. 研究对象")
h4(doc, "（1）纳入标准")
body(doc, "符合国家卫生健康委员会发布的《新型冠状病毒感染诊疗方案（试行第十版）》"
     "确诊标准，且已处于康复期的患者；年龄18-75岁；意识清楚，能够配合完成呼吸"
     "功能训练及各项评估；自愿参加本研究并签署知情同意书。")

h4(doc, "（2）排除标准")
body(doc, "合并严重心脑血管疾病、肝肾功能不全或恶性肿瘤等严重影响运动能力的疾病；"
     "合并严重骨关节疾病、神经肌肉疾病等影响呼吸训练实施的疾病；存在认知功能"
     "障碍或精神疾病，无法配合完成训练及评估；妊娠期或哺乳期妇女。")

h3(doc, "2. 分组方法")
body(doc, "采用随机数字表法，将86例符合纳入及排除标准的患者按入院顺序编号，从随机"
     "数字表第5行第3列开始依次读取86个随机数，将随机数按从小到大排序，前43例为"
     "观察组，后43例为对照组。本研究已通过医院伦理委员会审批（审批号：2024-LW-0317），"
     "所有患者均签署了知情同意书。")

# ── 三、结果 ──
h1(doc, "三、结果")

h2(doc, "（一）两组患者基线资料比较")
body(doc, "观察组43例，其中男25例（58.14%），女18例（41.86%）；年龄（52.37±12.45）"
     "岁；病程（28.64±6.32）天；临床分型中，普通型21例（48.84%），重型/危重型"
     "22例（51.16%）。对照组43例，其中男23例（53.49%），女20例（46.51%）；年龄"
     "（54.18±11.93）岁；病程（27.95±7.01）天。两组患者在性别、年龄、病程、"
     "临床分型及合并症等方面的差异均无统计学意义（P>0.05），具有可比性。")

h2(doc, "（二）干预前后肺功能指标比较")
body(doc, "干预前，两组患者的FVC、FEV1及FEV1/FVC差异均无统计学意义（P>0.05）。"
     "干预8周后，观察组上述三项指标均较干预前有明显改善（P<0.05），且观察组改善"
     "幅度均优于对照组（P<0.05）。观察组干预前后FVC提高了（0.43±0.15）L，FEV1"
     "提高了（0.37±0.13）L，而对照组仅分别提高了（0.17±0.11）L和（0.14±0.10）L。")

h2(doc, "（三）干预前后运动耐力比较")
body(doc, "干预前，观察组6MWD为（374.51±46.28）m，对照组为（371.83±44.67）m，差异"
     "无统计学意义（t=0.273, P=0.785）。干预8周后，观察组6MWD提高至（438.72±"
     "52.16）m，对照组为（392.45±48.93）m。观察组6MWD改善值（64.21±28.74）m"
     "显著优于对照组（20.62±22.39）m，差异具有统计学意义（t=7.842, P<0.001）。")

h2(doc, "（四）干预前后生活质量比较")
body(doc, "干预前，两组SGRQ各维度评分及总分差异均无统计学意义（P>0.05）。干预8周后，"
     "观察组SGRQ症状部分、活动部分、影响部分评分及总分均显著低于对照组（P<0.01），"
     "其中总分由干预前的（41.32±12.64）分降至（24.56±8.37）分。对照组虽亦有"
     "一定程度的改善，但幅度远不及观察组。")

# ── 四、讨论 ──
h1(doc, "四、讨论")

h2(doc, "（一）呼吸功能训练方案的科学性分析")
body(doc, "本研究基于Delphi专家函询法，融合了当前肺康复领域的循证证据和中国临床实践"
     "的真实需求，构建了适用于COVID-19康复期患者的系统化呼吸功能训练方案。方案"
     "构建过程中，两轮函询的专家积极系数均超过90%，专家权威系数为0.87，Kendall"
     "协调系数在两轮函询中均达到统计学显著水平，表明专家意见具有较好的一致性"
     "和可靠性，方案的科学性得到了充分保障[10]。")

body(doc, "方案内容涵盖了呼吸肌训练（缩唇呼吸、腹式呼吸、吸气肌阻力训练）、胸廓活动"
     "度训练（胸廓扩张训练、肋间肌牵伸）、渐进式有氧运动（平地步行、上下楼梯训练）"
     "及心理行为干预（呼吸放松技术、健康教育）四大模块。这一设计充分考虑了"
     "COVID-19康复期患者呼吸功能障碍的多维度特征——既有呼吸肌力的下降，也有胸廓"
     "顺应性的减退，还涉及到由于长期卧床导致的全身体能下降及焦虑情绪[11]。"
     "四大模块相互协同，形成了一个完整的闭环干预体系。")

h2(doc, "（二）呼吸功能训练对肺功能的影响")
body(doc, "本研究发现，经过8周的呼吸功能训练，观察组FVC、FEV1及FEV1/FVC均较对照组"
     "有明显改善。呼吸肌力量训练（尤其是吸气肌阻力训练）通过增加膈肌和肋间肌的"
     "肌力与耐力，提高了胸腔内负压的产生效率，从而增大了肺容积和通气量[12]。"
     "缩唇呼吸产生的呼气末正压效应可防止小气道过早陷闭，促进肺泡内残余气体的排出，"
     "改善通气/血流比例[13]。此外，胸廓活动度训练通过增加肋椎关节和胸肋关节的"
     "活动范围，降低了胸廓的僵硬程度，使呼吸运动更为高效[14]。")

h2(doc, "（三）本研究的局限性")
body(doc, "本研究存在以下局限性：第一，样本量相对较小且仅在一家医院开展，可能影响"
     "研究结果的外推性；第二，干预周期仅8周，未能评估该方案的远期效果及可持续性；"
     "第三，未实现干预实施者的盲法，可能存在一定的实施偏倚。未来研究应开展"
     "多中心、大样本的随机对照试验，延长随访周期，以进一步验证和完善本研究结果。")

# ── 五、结论 ──
h1(doc, "五、结论")
body(doc, "本研究通过Delphi法构建了包含4个维度、18个条目的COVID-19康复期患者呼吸"
     "功能训练方案，经随机对照试验验证，该方案能够有效改善患者的肺功能指标（FVC、"
     "FEV1、FEV1/FVC）、提高运动耐力（6MWD）及生活质量（SGRQ评分）。该方案具有"
     "较好的科学性、可行性和临床推广价值，建议在临床护理实践中推广应用。")

# ── 参考文献 ──
h1(doc, "参考文献")

refs = [
    "[1] Zhu N, Zhang D, Wang W, et al. A novel coronavirus from patients "
    "with pneumonia in China, 2019[J]. New England Journal of Medicine, 2020, "
    "382(8): 727-733.",

    "[2] World Health Organization. WHO coronavirus (COVID-19) dashboard[EB/OL]. "
    "(2025-06-01)[2025-06-10]. https://covid19.who.int.",

    "[3] Torres-Castro R, Vasconcello-Castillo L, Acosta-Dighero R, et al. "
    "Respiratory function in patients post-infection by COVID-19: a systematic "
    "review and meta-analysis[J]. Pulmonology, 2021, 27(4): 328-337.",

    "[4] Mo X, Jian W, Su Z, et al. Abnormal pulmonary function in COVID-19 "
    "patients at time of hospital discharge[J]. European Respiratory Journal, "
    "2020, 55(6): 2001217.",

    "[5] Huang C, Huang L, Wang Y, et al. 6-month consequences of COVID-19 in "
    "patients discharged from hospital: a cohort study[J]. Lancet, 2021, "
    "397(10270): 220-232.",

    "[6] Han X, Fan Y, Alwalid O, et al. Six-month follow-up chest CT findings "
    "after severe COVID-19 pneumonia[J]. Radiology, 2021, 299(1): E177-E186.",

    "[7] Spruit MA, Singh SJ, Garvey C, et al. An official American Thoracic "
    "Society/European Respiratory Society statement: key concepts and advances "
    "in pulmonary rehabilitation[J]. American Journal of Respiratory and "
    "Critical Care Medicine, 2013, 188(8): e13-e64.",

    "[8] 中华医学会呼吸病学分会慢性阻塞性肺疾病学组. 慢性阻塞性肺疾病诊治指南"
    "（2021年修订版）[J]. 中华结核和呼吸杂志, 2021, 44(3): 170-205.",

    "[9] Wang TJ, Chau B, Lui M, et al. Physical medicine and rehabilitation "
    "and pulmonary rehabilitation for COVID-19[J]. American Journal of Physical "
    "Medicine & Rehabilitation, 2020, 99(9): 769-774.",

    "[10] McPherson S, Reese C, Wendler MC. Methodology update: Delphi studies[J]. "
    "Nursing Research, 2018, 67(5): 404-410.",

    "[11] Zhao HM, Xie YX, Wang C, et al. Recommendations for respiratory "
    "rehabilitation in adults with coronavirus disease 2019[J]. Chinese Medical "
    "Journal, 2020, 133(13): 1595-1602.",

    "[12] Bissett B, Leditschke IA, Green M, et al. Inspiratory muscle training "
    "for intensive care unit patients: a multidisciplinary practical guide for "
    "clinicians[J]. Australian Critical Care, 2019, 32(3): 249-255.",

    "[13] 南登崑. 康复医学[M]. 第5版. 北京: 人民卫生出版社, 2018: 145-168.",

    "[14] Postolache PA, Nechifor A, Gavriluta C, et al. Chest wall mobilization "
    "techniques in the management of respiratory disorders[J]. European "
    "Respiratory Journal, 2023, 50(3): 178-185.",

    "[15] Liu K, Zhang W, Yang Y, et al. Respiratory rehabilitation in elderly "
    "patients with COVID-19: a randomized controlled study[J]. Complementary "
    "Therapies in Clinical Practice, 2020, 39: 101166.",

    "[16] ATS Committee on Proficiency Standards for Clinical Pulmonary Function "
    "Laboratories. ATS statement: guidelines for the six-minute walk test[J]. "
    "American Journal of Respiratory and Critical Care Medicine, 2002, 166(1): "
    "111-117.",

    "[17] Holland AE, Spruit MA, Troosters T, et al. An official European "
    "Respiratory Society/American Thoracic Society technical standard: field "
    "walking tests in chronic respiratory disease[J]. European Respiratory "
    "Journal, 2014, 44(6): 1428-1446.",

    "[18] Ambrosino N, Fracchia C. The role of tele-medicine in patients with "
    "respiratory diseases[J]. Expert Review of Respiratory Medicine, 2017, "
    "11(11): 893-900.",
]

for ref in refs:
    p = doc.add_paragraph()
    r = p.add_run(ref)
    sf(r, "宋体", "Times New Roman", 10.5, False)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = Pt(18)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.AT_LEAST

doc.save(OUT)
print(f"Done: {OUT}")
print(f"Size: {os.path.getsize(OUT)} bytes")
