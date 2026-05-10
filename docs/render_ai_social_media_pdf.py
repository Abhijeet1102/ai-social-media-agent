import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
TEX_PATH = ROOT / "ai_social_media_research_ieee.tex"
PDF_PATH = ROOT / "ai_social_media_research_ieee.pdf"


def clean_latex(text):
    text = re.sub(r"\\cite\{([^}]+)\}", lambda m: "[" + m.group(1) + "]", text)
    text = re.sub(r"\\texttt\{([^}]+)\}", r"\1", text)
    text = re.sub(r"\\emph\{([^}]+)\}", r"\1", text)
    text = text.replace("\\_", "_")
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^]]*\])?(?:\{[^}]*\})?", " ", text)
    text = re.sub(r"[{}]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_between(text, start, end):
    match = re.search(start + r"(.*?)" + end, text, re.S)
    return clean_latex(match.group(1)) if match else ""


def remove_blocks(text):
    for env in ["figure", "table"]:
        text = re.sub(rf"\\begin\{{{env}\}}.*?\\end\{{{env}\}}", "", text, flags=re.S)
    return text


def extract_sections(text):
    body = remove_blocks(text)
    body = re.sub(r"\\begin\{thebibliography\}.*", "", body, flags=re.S)
    matches = list(re.finditer(r"\\section\{([^}]+)\}", body))
    sections = []
    for index, match in enumerate(matches):
        title = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = clean_latex(body[start:end])
        if content:
            sections.append((title, content))
    return sections


def extract_references(text):
    bib = re.search(r"\\begin\{thebibliography\}\{00\}(.*?)\\end\{thebibliography\}", text, re.S)
    if not bib:
        return []
    items = re.split(r"\\bibitem\{[^}]+\}", bib.group(1))
    return [clean_latex(item) for item in items if clean_latex(item)]


class ArchitectureDiagram(Flowable):
    def __init__(self, width=500, height=145):
        super().__init__()
        self.width = width
        self.height = height

    def draw_box(self, canvas, x, y, w, h, label):
        canvas.roundRect(x, y, w, h, 5, stroke=1, fill=0)
        for idx, line in enumerate(label.split("\n")):
            canvas.drawCentredString(x + w / 2, y + h / 2 + 5 - idx * 10, line)

    def draw_arrow(self, canvas, x1, y1, x2, y2):
        canvas.line(x1, y1, x2, y2)
        canvas.circle(x2, y2, 1.8, fill=1)

    def draw(self):
        c = self.canv
        c.setFont("Helvetica", 7)
        boxes = {
            "User": (8, 96, 55, 24, "User"),
            "React": (78, 96, 65, 24, "React\nFrontend"),
            "API": (158, 96, 65, 24, "FastAPI\nBackend"),
            "LLM": (255, 116, 62, 24, "OpenAI\nLLM"),
            "Mongo": (255, 76, 62, 24, "MongoDB\nAtlas"),
            "OAuth": (350, 96, 70, 24, "Social APIs\nOAuth"),
            "Worker": (255, 28, 70, 24, "Scheduler\nWorker"),
            "Publish": (360, 28, 78, 24, "Platform\nPublishing"),
        }
        for item in boxes.values():
            self.draw_box(c, *item)
        self.draw_arrow(c, 63, 108, 78, 108)
        self.draw_arrow(c, 143, 108, 158, 108)
        self.draw_arrow(c, 223, 108, 255, 128)
        self.draw_arrow(c, 223, 98, 255, 88)
        self.draw_arrow(c, 223, 108, 350, 108)
        self.draw_arrow(c, 286, 76, 286, 52)
        self.draw_arrow(c, 325, 40, 360, 40)
        c.setFont("Helvetica-Oblique", 7)
        c.drawCentredString(self.width / 2, 6, "Fig. 1. Architecture of the AI-enabled social media automation agent.")


class WorkflowDiagram(Flowable):
    def __init__(self, width=500, height=170):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        c.setFont("Helvetica", 7)
        steps = [
            "User enters topic and requests AI caption",
            "Backend calls LLM and stores generated draft",
            "User selects Post Now or Schedule",
            "Backend checks connected account and platform scope",
            "Immediate publish or pending schedule record",
            "Worker publishes due posts and updates status",
        ]
        y = 138
        for step in steps:
            c.roundRect(70, y, 360, 18, 5, stroke=1, fill=0)
            c.drawCentredString(250, y + 5, step)
            if y > 38:
                c.line(250, y, 250, y - 10)
                c.circle(250, y - 10, 1.8, fill=1)
            y -= 24
        c.setFont("Helvetica-Oblique", 7)
        c.drawCentredString(self.width / 2, 6, "Fig. 2. Generation, posting, and scheduling workflow.")


def make_pdf():
    tex = TEX_PATH.read_text(encoding="utf-8")
    title = re.search(r"\\title\{([^}]+)\}", tex).group(1)
    abstract = extract_between(tex, r"\\begin\{abstract\}", r"\\end\{abstract\}")
    keywords = extract_between(tex, r"\\begin\{IEEEkeywords\}", r"\\end\{IEEEkeywords\}")
    sections = extract_sections(tex)
    references = extract_references(tex)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleIEEE", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=16, leading=19, alignment=1)
    author_style = ParagraphStyle("AuthorIEEE", parent=styles["Normal"], fontSize=9, leading=11, alignment=1)
    heading_style = ParagraphStyle("HeadingIEEE", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10, leading=12, spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle("BodyIEEE", parent=styles["BodyText"], fontSize=8.2, leading=9.7, alignment=4, spaceAfter=4)
    small_style = ParagraphStyle("SmallIEEE", parent=styles["BodyText"], fontSize=7.4, leading=8.7, alignment=4, spaceAfter=3)

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        rightMargin=0.62 * inch,
        leftMargin=0.62 * inch,
        topMargin=0.58 * inch,
        bottomMargin=0.58 * inch,
    )

    story = [
        Paragraph(title, title_style),
        Paragraph("Abhijeet Rai<br/>Department of Computer Science and Engineering<br/>AI Social Media Automation Agent Project<br/>Email: abhijeet1104a@gmail.com", author_style),
        Spacer(1, 8),
        Paragraph("<b>Abstract--</b> " + abstract, body_style),
        Paragraph("<b>Index Terms--</b> " + keywords, body_style),
        Spacer(1, 5),
    ]

    inserted_architecture = False
    inserted_tables = False
    inserted_workflow = False

    for title_text, content in sections:
        story.append(Paragraph(title_text.upper(), heading_style))
        paragraphs = [p.strip() for p in re.split(r"(?<=\.)\s+(?=[A-Z])", content) if p.strip()]
        grouped = []
        chunk = ""
        for paragraph in paragraphs:
            chunk = (chunk + " " + paragraph).strip()
            if len(chunk.split()) > 95:
                grouped.append(chunk)
                chunk = ""
        if chunk:
            grouped.append(chunk)
        for paragraph in grouped:
            story.append(Paragraph(paragraph, body_style))

        if title_text == "System Overview" and not inserted_architecture:
            story.append(Spacer(1, 5))
            story.append(ArchitectureDiagram())
            story.append(Spacer(1, 5))
            inserted_architecture = True
        if title_text == "Methodology" and not inserted_tables:
            story.append(Paragraph("TABLE I. MAIN BACKEND MODULES", small_style))
            module_table = Table(
                [
                    ["Module", "Responsibility"],
                    ["main.py", "FastAPI app setup, CORS, router registration"],
                    ["controllers", "Authentication, posts, account connection, system routes"],
                    ["services", "LinkedIn, YouTube, Instagram, and Facebook API logic"],
                    ["auth.py", "Password hashing, JWT creation, token verification"],
                    ["database.py", "MongoDB client and collection references"],
                    ["worker.py", "Polling scheduled posts and executing due publishing tasks"],
                ],
                colWidths=[1.25 * inch, 4.8 * inch],
            )
            module_table.setStyle(TableStyle([
                ("FONT", (0, 0), (-1, -1), "Helvetica", 7),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(module_table)
            story.append(Spacer(1, 6))
            story.append(WorkflowDiagram())
            story.append(Spacer(1, 6))
            story.append(Paragraph("TABLE II. CORE MONGODB COLLECTIONS", small_style))
            data_table = Table(
                [
                    ["Collection", "Stored Data"],
                    ["users", "Username and bcrypt-hashed password"],
                    ["posts", "Generated draft content, topic, owner, timestamp"],
                    ["scheduled_posts", "Content, date, time, platforms, status, publish results"],
                    ["connected_accounts", "OAuth tokens, scopes, profile data, platform metadata"],
                    ["oauth_states", "Temporary state values for callback validation"],
                    ["logs", "Worker success and failure records"],
                ],
                colWidths=[1.45 * inch, 4.6 * inch],
            )
            data_table.setStyle(TableStyle([
                ("FONT", (0, 0), (-1, -1), "Helvetica", 7),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(data_table)
            inserted_tables = True

    story.append(PageBreak())
    story.append(Paragraph("REFERENCES", heading_style))
    for idx, ref in enumerate(references, start=1):
        story.append(Paragraph(f"[{idx}] {ref}", small_style))

    doc.build(story)


if __name__ == "__main__":
    make_pdf()
    print(PDF_PATH)
