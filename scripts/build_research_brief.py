"""Build the versioned public research brief as a polished PDF."""

from pathlib import Path
from shutil import copy2

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "research-brief-v1.0.0.pdf"
WEB_COPY = ROOT / "website" / "assets" / "research-brief-v1.0.0.pdf"

INK = colors.HexColor("#14221f")
SOFT = colors.HexColor("#43534f")
PAPER = colors.HexColor("#f7f4ed")
GREEN = colors.HexColor("#0d6b57")
MINT = colors.HexColor("#73f2b6")
ORANGE = colors.HexColor("#ec6f3b")
DARK = colors.HexColor("#10201d")
LINE = colors.HexColor("#d9d4c9")
WHITE = colors.HexColor("#fffdf7")


class ResearchBrief(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=17 * mm,
            title="Generative AI and Structural Change in Crowdsourced Music Information Platforms",
            author="RunJie Sun",
            subject="Version 1.0.0 research brief",
        )
        cover = Frame(18 * mm, 18 * mm, A4[0] - 36 * mm, A4[1] - 36 * mm, id="cover")
        body = Frame(18 * mm, 17 * mm, A4[0] - 36 * mm, A4[1] - 35 * mm, id="body")
        self.addPageTemplates(
            [
                PageTemplate(id="Cover", frames=[cover], onPage=self._cover_page),
                PageTemplate(id="Body", frames=[body], onPage=self._body_page),
            ]
        )

    def afterPage(self):
        if self.page == 1:
            self.handle_nextPageTemplate("Body")

    def _cover_page(self, canvas, doc):
        width, height = A4
        canvas.saveState()
        canvas.setFillColor(DARK)
        canvas.rect(0, 0, width, height, fill=1, stroke=0)
        canvas.setStrokeColor(colors.HexColor("#24463e"))
        canvas.setLineWidth(0.7)
        cx, cy = width - 105, height - 128
        for radius in (18, 34, 50, 66, 82):
            canvas.circle(cx, cy, radius, fill=0, stroke=1)
        canvas.setFillColor(MINT)
        canvas.circle(cx, cy, 5, fill=1, stroke=0)
        canvas.setFillColor(colors.HexColor("#18322c"))
        canvas.roundRect(width - 205, height - 245, 165, 210, 30, fill=1, stroke=0)
        canvas.setFillColor(MINT)
        canvas.circle(32 * mm, height - 27 * mm, 4, fill=1, stroke=0)
        canvas.restoreState()

    def _body_page(self, canvas, doc):
        width, height = A4
        canvas.saveState()
        canvas.setFillColor(PAPER)
        canvas.rect(0, 0, width, height, fill=1, stroke=0)
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(18 * mm, height - 13 * mm, width - 18 * mm, height - 13 * mm)
        canvas.setFont("Helvetica-Bold", 7.3)
        canvas.setFillColor(GREEN)
        canvas.drawString(18 * mm, height - 10 * mm, "AI AND MUSIC INFORMATION ECOSYSTEMS")
        canvas.setFont("Helvetica", 7.3)
        canvas.setFillColor(SOFT)
        canvas.drawRightString(width - 18 * mm, height - 10 * mm, "RESEARCH BRIEF - V1.0.0")
        canvas.setStrokeColor(LINE)
        canvas.line(18 * mm, 12 * mm, width - 18 * mm, 12 * mm)
        canvas.setFont("Helvetica", 7.2)
        canvas.drawString(18 * mm, 8 * mm, "RunJie Sun - Nanjing University - 16 August 2026")
        canvas.drawRightString(width - 18 * mm, 8 * mm, str(doc.page))
        canvas.restoreState()


def styles():
    base = getSampleStyleSheet()
    return {
        "cover_kicker": ParagraphStyle("cover_kicker", fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=MINT, tracking=1.4, spaceAfter=18),
        "cover_title": ParagraphStyle("cover_title", fontName="Times-Roman", fontSize=35, leading=38, textColor=WHITE, spaceAfter=20),
        "cover_subtitle": ParagraphStyle("cover_subtitle", fontName="Helvetica", fontSize=12.2, leading=18, textColor=colors.HexColor("#d4dfda"), spaceAfter=42),
        "cover_meta": ParagraphStyle("cover_meta", fontName="Helvetica", fontSize=9, leading=15, textColor=colors.HexColor("#aabcb5")),
        "kicker": ParagraphStyle("kicker", fontName="Helvetica-Bold", fontSize=8.2, leading=11, textColor=GREEN, tracking=1.2, spaceAfter=7),
        "h1": ParagraphStyle("h1", fontName="Times-Roman", fontSize=25, leading=28, textColor=INK, spaceAfter=13),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=INK, spaceBefore=8, spaceAfter=5),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.2, leading=14, textColor=SOFT, spaceAfter=7),
        "body_strong": ParagraphStyle("body_strong", fontName="Helvetica", fontSize=9.6, leading=14.5, textColor=INK, spaceAfter=8),
        "quote": ParagraphStyle("quote", fontName="Times-Italic", fontSize=16, leading=22, textColor=INK, leftIndent=12, rightIndent=12, borderColor=GREEN, borderWidth=2, borderPadding=(3, 10, 3, 12), spaceBefore=8, spaceAfter=12),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=7.7, leading=11, textColor=SOFT),
        "small_white": ParagraphStyle("small_white", fontName="Helvetica", fontSize=8.3, leading=12, textColor=colors.HexColor("#d4dfda")),
        "number": ParagraphStyle("number", fontName="Times-Roman", fontSize=24, leading=26, textColor=GREEN, alignment=TA_CENTER),
        "label": ParagraphStyle("label", fontName="Helvetica-Bold", fontSize=7.5, leading=10, textColor=SOFT, alignment=TA_CENTER),
        "citation": ParagraphStyle("citation", fontName="Helvetica", fontSize=8.2, leading=12.5, textColor=INK, backColor=colors.HexColor("#ece7dc"), borderPadding=12),
        "table_head": ParagraphStyle("table_head", fontName="Helvetica-Bold", fontSize=7.2, leading=9.2, textColor=WHITE),
        "table_cell": ParagraphStyle("table_cell", fontName="Helvetica", fontSize=7.2, leading=9.4, textColor=INK),
        "table_bold": ParagraphStyle("table_bold", fontName="Helvetica-Bold", fontSize=7.2, leading=9.4, textColor=INK),
        "table_id": ParagraphStyle("table_id", fontName="Helvetica-Bold", fontSize=7.8, leading=10, textColor=ORANGE),
    }


def section_header(st, number, title, subtitle=None):
    items = [Paragraph(number, st["kicker"]), Paragraph(title, st["h1"])]
    if subtitle:
        items.append(Paragraph(subtitle, st["body_strong"]))
    return items


def bullet(text, st):
    return Paragraph(f"<font color='#0d6b57'>-</font>&nbsp;&nbsp;{text}", st["body"])


def figure(path: Path, width=165 * mm):
    img = Image(str(path))
    img._restrictSize(width, 92 * mm)
    return img


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    WEB_COPY.parent.mkdir(parents=True, exist_ok=True)
    st = styles()
    story = []

    story.extend(
        [
            Spacer(1, 76 * mm),
            Paragraph("COMPUTATIONAL SOCIAL SCIENCE - 2026", st["cover_kicker"]),
            Paragraph("Generative AI and Structural Change in Crowdsourced Music Information Platforms", st["cover_title"]),
            Paragraph("Evidence, mechanisms, and open questions from Album of the Year and Rate Your Music", st["cover_subtitle"]),
            Paragraph("RunJie Sun<br/>School of Information Management, Nanjing University", st["cover_meta"]),
            Spacer(1, 10 * mm),
            Paragraph("Version 1.0.0&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;16 August 2026&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;Open research object", st["cover_meta"]),
            PageBreak(),
        ]
    )

    story.extend(section_header(st, "01 - RESEARCH PROBLEM", "When text becomes cheap, what sustains trust?"))
    story.append(Paragraph("This study examines how generative AI may alter the institutional foundations of crowdsourced music-information platforms. Album of the Year (AOTY) and Rate Your Music (RYM) provide cases for studying evaluative content, visibility and rating weight, and the provenance of community knowledge.", st["body_strong"]))
    story.append(Paragraph("The empirical baseline identifies structures through which low-cost generated contributions could affect information quality and trust. It does not establish that a post-2022 transformation has occurred.", st["body"]))
    story.append(Paragraph("Textual plausibility is no longer a sufficient signal of effort, experience, or origin.", st["quote"]))
    story.append(Paragraph("Research question", st["h2"]))
    story.append(Paragraph("When review-like prose becomes inexpensive to produce, which institutional resources sustain the credibility and value of crowdsourced music knowledge?", st["body_strong"]))
    story.append(Paragraph("Analytical proposition", st["h2"]))
    for item in (
        "Technology lowers the production cost of coherent review-like text.",
        "Institutional rules determine how uncertain contributions enter rankings and archives.",
        "Organizational responses divide across disclosure, detection, review, and appeals.",
        "Information value increasingly depends on provenance, contribution history, taxonomy, and governance.",
    ):
        story.append(bullet(item, st))
    story.append(Spacer(1, 5 * mm))
    stats = Table(
        [
            [Paragraph("32,358", st["number"]), Paragraph("5,000", st["number"]), Paragraph("5,000", st["number"]), Paragraph("116,384", st["number"])],
            [Paragraph("AOTY historical albums", st["label"]), Paragraph("AOTY high-rated snapshot", st["label"]), Paragraph("RYM popular snapshot", st["label"]), Paragraph("critic excerpts", st["label"])],
        ],
        colWidths=[40 * mm] * 4,
    )
    stats.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ece7dc")), ("BOX", (0, 0), (-1, -1), 0.6, LINE), ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, 0), 10), ("BOTTOMPADDING", (0, 1), (-1, 1), 10)]))
    story.append(stats)
    story.append(PageBreak())

    story.extend(section_header(st, "02 - EVIDENCE ARCHITECTURE", "Four evidence classes, four scopes of inference", "Provenance is an analytical variable. Every output is labeled according to the type of input that supports it."))
    evidence_rows = [
        [Paragraph(x, st["table_head"]) for x in ["Class", "Input", "Permitted inference", "Boundary"]],
        [Paragraph(x, st["table_cell"]) for x in ["Observed archive", "Dated third-party records", "Description within selected files", "No causal timing claim"]],
        [Paragraph(x, st["table_cell"]) for x in ["Controlled comparison", "Contrasted fixed corpus", "Pipeline behavior in that corpus", "No detector or prevalence estimate"]],
        [Paragraph(x, st["table_cell"]) for x in ["Synthetic method check", "Known designed input", "Implementation behavior", "No platform finding"]],
        [Paragraph(x, st["table_cell"]) for x in ["Scenario", "Stated parameters or coded scores", "Conditional mechanism", "No calibrated forecast"]],
    ]
    table = Table(evidence_rows, colWidths=[33 * mm, 42 * mm, 53 * mm, 38 * mm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), DARK), ("TEXTCOLOR", (0, 0), (-1, 0), WHITE), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 7.4), ("LEADING", (0, 0), (-1, -1), 10), ("GRID", (0, 0), (-1, -1), 0.45, LINE), ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f0ece3")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    story.append(table)
    story.append(Spacer(1, 7 * mm))
    story.append(Paragraph("Source archives", st["h2"]))
    source_rows = [
        [Paragraph(x, st["table_head"]) for x in ["Source", "Rows", "Selection/date", "License", "Use"]],
        [Paragraph(x, st["table_cell"]) for x in ["AOTY/Metacritic historical", "32,358", "Through Oct. 2020", "GPL-2.0", "Critic-user; matching"]],
        [Paragraph(x, st["table_cell"]) for x in ["AOTY highest user-rated", "5,000", "Updated 20 Oct. 2024", "CC BY 3.0", "Attention; genre"]],
        [Paragraph(x, st["table_cell"]) for x in ["RYM most-popular", "5,000", "Collected 11 Mar. 2022", "Not specified", "Ratings; reviews; genre"]],
    ]
    sources = Table(source_rows, colWidths=[49 * mm, 18 * mm, 39 * mm, 26 * mm, 34 * mm], repeatRows=1)
    sources.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), WHITE), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 7.2), ("GRID", (0, 0), (-1, -1), 0.45, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(sources)
    story.append(Spacer(1, 7 * mm))
    story.append(Paragraph("Integrity controls", st["h2"]))
    for item in (
        "Source URL, publisher, snapshot date, selection rule, stated license, limitation, and SHA-256 checksum are retained.",
        "The default empirical pipeline excludes synthetic and unknown-provenance rows.",
        "Longitudinal methods return not_testable when no repeated observed series exists.",
        "Random sampling, cross-validation, and method checks use global seed 42.",
    ):
        story.append(bullet(item, st))
    story.append(PageBreak())

    story.extend(section_header(st, "03 - OBSERVED FINDING", "Shared rank order, different score calibration"))
    story.append(Paragraph("Across 4,102 exact artist-title-year matches, AOTY and RYM user scores have Pearson correlation <b>0.910</b> and Spearman correlation <b>0.836</b>. After rescaling AOTY scores to 0-5, <b>87.4%</b> of matches differ by no more than 0.5 points. The median AOTY score is <b>0.34 points higher</b>.", st["body_strong"]))
    story.append(figure(ROOT / "figures" / "analysis" / "rating_distribution_evolution.png"))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("Interpretation boundary: the archives were collected at different dates and under different selection rules. The result describes agreement and calibration within exact-matched records; it is not evidence of longitudinal stability.", st["small"]))
    story.append(PageBreak())

    story.extend(section_header(st, "04 - OBSERVED FINDING", "Attention concentrates; written participation stays thin"))
    story.append(Paragraph("The rating-count Gini coefficient is <b>0.617</b> in the AOTY high-rated file and <b>0.400</b> in the RYM popular file. The RYM snapshot has a median review-to-rating ratio of <b>1.65%</b>. Across the 32,358-record AOTY historical archive, critic and user scores correlate at <b>0.536</b>.", st["body_strong"]))
    story.append(figure(ROOT / "figures" / "analysis" / "genre_impact_heatmap.png"))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("Interpretation boundary: these values describe concentration, participation, and genre strata inside selected files. The AOTY and RYM snapshots use different selection rules and are not estimates of total platform size.", st["small"]))
    story.append(PageBreak())

    story.extend(section_header(st, "05 - METHODS AND NON-CLAIMS", "Methods designed to fail visibly when evidence is absent"))
    method_rows = [
        [Paragraph(x, st["table_head"]) for x in ["Module", "Input", "Output", "Non-claim"]],
        [Paragraph(x, st["table_cell"]) for x in ["Entity matching", "Observed AOTY + RYM", "Agreement and score differences", "No longitudinal inference"]],
        [Paragraph(x, st["table_cell"]) for x in ["Attention + genre", "Selected snapshots", "Gini, shares, genre cells", "No market-size comparison"]],
        [Paragraph(x, st["table_cell"]) for x in ["Structural change", "Synthetic benchmark only", "Procedure behavior", "No post-2022 platform break"]],
        [Paragraph(x, st["table_cell"]) for x in ["Text comparison", "15 critic + 15 controls", "Out-of-fold accuracy/AUC", "No AI detector evaluation"]],
        [Paragraph(x, st["table_cell"]) for x in ["Trust + policy", "Assumed parameters", "Sensitivity and scenarios", "No calibrated forecast"]],
    ]
    methods = Table(method_rows, colWidths=[35 * mm, 41 * mm, 47 * mm, 43 * mm], repeatRows=1)
    methods.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), DARK), ("TEXTCOLOR", (0, 0), (-1, 0), WHITE), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 7.2), ("LEADING", (0, 0), (-1, -1), 9.5), ("GRID", (0, 0), (-1, -1), 0.45, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(methods)
    story.append(Spacer(1, 7 * mm))
    story.append(Paragraph("Controlled text exercise", st["h2"]))
    story.append(Paragraph("A five-fold out-of-fold TF-IDF classifier separates 15 published critic excerpts from 15 fixed assistant-style controls with 96.7% accuracy and AUC 0.996. The controls are not outputs from a documented generative model, and there is no external platform-user holdout. These metrics describe separation between two deliberately contrasted groups.", st["body"]))
    story.append(Paragraph("Claims that remain open", st["h2"]))
    for item in (
        "Whether ChatGPT caused a post-2022 structural change on AOTY or RYM.",
        "The prevalence of AI-written reviews on either platform.",
        "A calibrated threshold at which user trust will collapse.",
        "Observed organizational readiness inferred from analyst-coded platform scores.",
    ):
        story.append(bullet(item, st))
    story.append(PageBreak())

    story.extend(section_header(st, "06 - NEXT DESIGN", "The decisive evidence is longitudinal", "A causal timing claim needs repeated, provenance-rich observations and explicit alternative explanations."))
    design_rows = [
        [Paragraph("D1", st["table_id"]), Paragraph("Repeat the same albums or users", st["table_bold"]), Paragraph("Preserve rating counts, review counts, score distributions, and contribution activity across dated snapshots.", st["table_cell"])],
        [Paragraph("D2", st["table_id"]), Paragraph("Record rule and interface changes", st["table_bold"]), Paragraph("Ranking, moderation, export, visibility, and chart-weight changes can shift outcomes independently.", st["table_cell"])],
        [Paragraph("D3", st["table_id"]), Paragraph("Prespecify exclusions and alternatives", st["table_bold"]), Paragraph("Distinguish catalog mix, cohort turnover, seasonality, platform growth, and policy changes from an AI-related shock.", st["table_cell"])],
        [Paragraph("D4", st["table_id"]), Paragraph("Measure contributor-level mechanisms", st["table_bold"]), Paragraph("Review depth, taxonomy work, retention, trust, and appeals may change before aggregate traffic does.", st["table_cell"])],
    ]
    design = Table(design_rows, colWidths=[13 * mm, 49 * mm, 104 * mm])
    design.setStyle(TableStyle([("TEXTCOLOR", (0, 0), (0, -1), ORANGE), ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"), ("FONTNAME", (2, 0), (2, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 8), ("LEADING", (0, 0), (-1, -1), 11.2), ("LINEBELOW", (0, 0), (-1, -1), 0.45, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story.append(design)
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Reproducible release", st["h2"]))
    story.append(Paragraph("Version 1.0.0 provides a Python 3.12.10 reference environment, a hash-locked dependency file, Conda and Docker entry points, an automated GitHub Actions check, fixed seed 42, archive checksums, and explicit empirical, collection, and demonstration modes.", st["body"]))
    story.append(Paragraph("A successful reproduction rebuilds the reported descriptive baseline. It does not widen the inferential scope of the underlying evidence.", st["quote"]))
    story.append(PageBreak())

    story.extend(section_header(st, "07 - CITATION AND ACCESS", "A versioned research object"))
    story.append(Paragraph("Recommended citation", st["h2"]))
    citation_box = Table([[Paragraph("Sun, R. (2026). <i>Generative AI and structural change in crowdsourced music information platforms: Evidence, mechanisms, and open questions from AOTY and RYM</i> (Version 1.0.0) [Research report and software]. GitHub. https://github.com/SunRunJie/AI-Driven-Transformation-of-Music-Information-Ecosystems", st["body_strong"])]] , colWidths=[166 * mm])
    citation_box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ece7dc")), ("BOX", (0, 0), (-1, -1), 0.5, LINE), ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12), ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(citation_box)
    story.append(Spacer(1, 7 * mm))
    access_rows = [
        ["Research website", "sunrunjie.github.io/AI-Driven-Transformation-of-Music-Information-Ecosystems/"],
        ["Repository", "github.com/SunRunJie/AI-Driven-Transformation-of-Music-Information-Ecosystems"],
        ["Evidence ledger", "Website: Sources and references"],
        ["Citation metadata", "CITATION.cff"],
        ["Archive metadata", ".zenodo.json"],
        ["Contact", "251820093@smail.nju.edu.cn"],
    ]
    access = Table(access_rows, colWidths=[43 * mm, 123 * mm])
    access.setStyle(TableStyle([("TEXTCOLOR", (0, 0), (0, -1), GREEN), ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("FONTNAME", (1, 0), (1, -1), "Helvetica"), ("FONTSIZE", (0, 0), (-1, -1), 8.2), ("LINEBELOW", (0, 0), (-1, -1), 0.45, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    story.append(access)
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Archive status", st["h2"]))
    story.append(Paragraph("Machine-readable citation and Zenodo metadata are included. A DOI is not shown because no public archival deposit has yet assigned one. After the v1.0.0 GitHub release is deposited, the DOI must replace the repository URL across the citation surfaces.", st["body"]))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Evidence status: descriptive archives available; causal timing unestimated.", st["quote"]))

    doc = ResearchBrief(str(OUTPUT))
    doc.build(story)
    copy2(OUTPUT, WEB_COPY)
    print(f"Built {OUTPUT}")
    print(f"Copied {WEB_COPY}")


if __name__ == "__main__":
    build()
