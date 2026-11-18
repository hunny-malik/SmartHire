"""
Generate a clean, parser-friendly DOCX resume for Hunny Malik.

The resume is structured so SmartHire's section-segmentation parser can
correctly extract every field:
  - Skills listed comma-separated under a clear SKILLS header
  - Projects with a single "Technologies: X, Y, Z" line (not one tech per line)
  - Education with Degree | University | Year on consecutive lines
  - Certifications only contain real credentials (no skill tokens)
  - Experience uses "Title | Company" pipe-delimited format with date range

Run:
    cd backend/sample_resumes
    python generate_hunny_resume.py
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _add_hr(doc: Document) -> None:
    """Add a thin horizontal rule."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "4F46E5")
    pBdr.append(bottom)
    pPr.append(pBdr)


def _section_header(doc: Document, title: str) -> None:
    """Bold uppercase section heading with a rule underneath."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(1)
    run = p.add_run(title.upper())
    run.bold = True
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x4F, 0x46, 0xE5)   # indigo-600
    _add_hr(doc)


def _bullet(doc: Document, text: str, indent: float = 0.3) -> None:
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Inches(indent)
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    run = p.add_run(text)
    run.font.size = Pt(9.5)


def _body(doc: Document, text: str, bold: bool = False, size: float = 9.5,
          color: RGBColor | None = None, space_after: float = 2) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color


def _two_col(doc: Document, left: str, right: str,
             left_bold: bool = False, right_bold: bool = False,
             size: float = 9.5) -> None:
    """Single paragraph with left text and right-aligned text via tab."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(1)
    # Set a right-aligned tab stop at page width minus margins
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    pPr = p._p.get_or_add_pPr()
    tabs = OxmlElement("w:tabs")
    tab = OxmlElement("w:tab")
    tab.set(qn("w:val"), "right")
    tab.set(qn("w:pos"), "9360")   # ~6.5 inches in twips (1 inch = 1440 twips)
    tabs.append(tab)
    pPr.append(tabs)

    r_left = p.add_run(left)
    r_left.bold = left_bold
    r_left.font.size = Pt(size)

    r_tab = p.add_run("\t")
    r_tab.font.size = Pt(size)

    r_right = p.add_run(right)
    r_right.bold = right_bold
    r_right.font.size = Pt(size)
    r_right.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)  # slate-500


# ---------------------------------------------------------------------------
# Resume content
# ---------------------------------------------------------------------------

def build_resume(out_path: str) -> None:
    doc = Document()

    # ── Page margins ────────────────────────────────────────────────────────
    for section in doc.sections:
        section.top_margin    = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin   = Cm(2.0)
        section.right_margin  = Cm(2.0)

    # ── Default paragraph style ─────────────────────────────────────────────
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(9.5)

    # ════════════════════════════════════════════════════════════════════════
    # HEADER
    # ════════════════════════════════════════════════════════════════════════
    name_p = doc.add_paragraph()
    name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name_p.paragraph_format.space_after = Pt(2)
    name_run = name_p.add_run("Hunny Malik")
    name_run.bold = True
    name_run.font.size = Pt(22)
    name_run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    contact_p = doc.add_paragraph()
    contact_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    contact_p.paragraph_format.space_after = Pt(4)
    contact_run = contact_p.add_run(
        "hunny.malik@email.com  |  +91 9XXXXXXXXX  |  "
        "linkedin.com/in/hunny-malik  |  github.com/hunny-malik"
    )
    contact_run.font.size = Pt(9)
    contact_run.font.color.rgb = RGBColor(0x4F, 0x46, 0xE5)

    _add_hr(doc)

    # ════════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ════════════════════════════════════════════════════════════════════════
    _section_header(doc, "Summary")
    _body(
        doc,
        "B.Tech CSE (Data Science) student at Bennett University (CGPA 8.99/10) with hands-on "
        "experience building distributed data-engineering systems, AI-powered security platforms, "
        "and full-stack web applications. Proficient in Python, FastAPI, React, Kafka, Spark, and "
        "cloud-native deployment on AWS and Docker. AWS Certified Machine Learning Engineer – Associate.",
        size=9.5,
    )

    # ════════════════════════════════════════════════════════════════════════
    # SKILLS  — comma-separated single block so parser maps it cleanly
    # ════════════════════════════════════════════════════════════════════════
    _section_header(doc, "Skills")

    skills_data = {
        "Languages":        "Python, JavaScript, TypeScript, C++, SQL",
        "Frameworks":       "FastAPI, Flask, Django, React, Node.js, Express",
        "Data & Streaming": "Apache Kafka, Apache Spark, HDFS, Pandas, NumPy",
        "AI / ML":          "Machine Learning, NLP, Computer Vision, Scikit-learn, TensorFlow",
        "Databases":        "PostgreSQL, MongoDB, MySQL, Redis",
        "DevOps & Cloud":   "Docker, AWS (EC2, S3, SageMaker), Git, CI/CD, Linux",
        "Design":           "System Design, Microservices, Distributed Systems, REST APIs, WebRTC",
        "Frontend":         "HTML, CSS, Bootstrap, Tailwind CSS",
    }

    for category, skills in skills_data.items():
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        label = p.add_run(f"{category}: ")
        label.bold = True
        label.font.size = Pt(9.5)
        val = p.add_run(skills)
        val.font.size = Pt(9.5)

    # ════════════════════════════════════════════════════════════════════════
    # PROJECTS
    # ════════════════════════════════════════════════════════════════════════
    _section_header(doc, "Projects")

    # ── ThreatLens ──────────────────────────────────────────────────────────
    _two_col(doc, "ThreatLens — AI-Powered SOC Platform",
             "Sep 2026 – Oct 2026", left_bold=True, size=10)
    _body(doc, "GitHub: github.com/hunny-malik/ThreatLens",
          color=RGBColor(0x4F, 0x46, 0xE5))
    _bullet(doc, "Built a Security Operations Centre (SOC) platform that converts raw alert floods "
                 "into risk-ranked incidents via deduplication, multi-attack disentanglement, and "
                 "MITRE ATT&CK kill-chain reconstruction.")
    _bullet(doc, "Designed a distributed pipeline (Kafka partitioning, Spark-style RDD partitioning, "
                 "HDFS archival) and a temporal-graph clustering engine that separated 10 simultaneous "
                 "attack campaigns in a 100,000-alert dataset with zero false positives.")
    _bullet(doc, "Benchmarked 106,669 events/sec ingestion with a 6.17 s end-to-end run on 100K alerts, "
                 "collapsing 99.9% of noise; scaled testing to 1 M generated logs.")
    _bullet(doc, "Implemented asset-criticality risk scoring, statistical anomaly detection for zero-day "
                 "behaviour, and evidence-grounded AI incident briefs with analyst feedback loops and an "
                 "audit trail.")
    _body(doc, "Technologies: Python, FastAPI, React, Kafka, Apache Spark, HDFS, Docker, PostgreSQL",
          bold=True, color=RGBColor(0x64, 0x74, 0x8B))

    doc.add_paragraph()   # small gap

    # ── Privacy Cam ─────────────────────────────────────────────────────────
    _two_col(doc, "Privacy Cam — AI-Powered Secure Video Chat",
             "2025", left_bold=True, size=10)
    _bullet(doc, "Separated the React/Node.js client and WebRTC signaling layer from the FastAPI "
                 "inference service, keeping the architecture modular and independently deployable.")
    _bullet(doc, "Implemented real-time AI inference (background blur, object redaction) with sub-100 ms "
                 "latency by streaming video frames over WebSockets to the FastAPI service.")
    _bullet(doc, "Containerised all three services with Docker Compose for one-command local development "
                 "and seamless cloud deployment.")
    _body(doc, "Technologies: Python, FastAPI, React, Node.js, WebRTC, Docker, TensorFlow",
          bold=True, color=RGBColor(0x64, 0x74, 0x8B))

    # ════════════════════════════════════════════════════════════════════════
    # EXPERIENCE
    # ════════════════════════════════════════════════════════════════════════
    _section_header(doc, "Experience")

    _two_col(doc, "Open-Source Contributor | Independent",
             "2024 – Present", left_bold=True, size=10)
    _bullet(doc, "Contributed distributed-systems utilities and documentation patches to open-source "
                 "projects in the Python and data-engineering ecosystem.")
    _bullet(doc, "Ranked 21 of 640 teams in SmartBU, Bennett University's internal selection round "
                 "for Smart India Hackathon.")

    # ════════════════════════════════════════════════════════════════════════
    # EDUCATION
    # ════════════════════════════════════════════════════════════════════════
    _section_header(doc, "Education")

    _two_col(doc, "B.Tech, Computer Science & Engineering (Data Science)",
             "2024 – 2028", left_bold=True, size=10)
    _body(doc, "Bennett University, Greater Noida   |   CGPA: 8.99 / 10")

    doc.add_paragraph()

    _two_col(doc, "Senior Secondary (Class XII)",
             "Completed 2024", left_bold=True, size=10)
    _body(doc, "Khalsa College Public School")

    # ════════════════════════════════════════════════════════════════════════
    # CERTIFICATIONS
    # ════════════════════════════════════════════════════════════════════════
    _section_header(doc, "Certifications")

    certs = [
        "AWS Certified Machine Learning Engineer – Associate  (Amazon Web Services)",
        "Microsoft Innovate 2026 Hackathon — Ranked #2 of 500 teams",
        "SmartBU (Bennett University's Smart India Hackathon internal round) — Ranked 21 of 640 teams",
    ]
    for c in certs:
        _bullet(doc, c)

    # ════════════════════════════════════════════════════════════════════════
    # Save
    # ════════════════════════════════════════════════════════════════════════
    doc.save(out_path)
    print(f"[OK] Resume saved -> {out_path}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "hunny_malik_resume.docx")
    build_resume(out)
