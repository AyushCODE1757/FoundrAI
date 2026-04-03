import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

OUTPUT_PATH = "/tmp/foundrai_report.pdf"

SECTION_COLORS = {
    "Executive Summary": colors.HexColor("#3b82f6"),
    "Technology Stack":  colors.HexColor("#8b5cf6"),
    "Financial Model":   colors.HexColor("#10b981"),
    "Marketing Strategy": colors.HexColor("#f59e0b"),
    "Risk Assessment":   colors.HexColor("#ef4444"),
}

def generate_pdf(idea: str, final_proposal: str, critiques: list, plan: dict) -> str:
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=28,
        textColor=colors.HexColor("#3b82f6"),
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#9ca3af"),
        spaceAfter=16,
        alignment=TA_CENTER,
    )
    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=14,
        spaceAfter=6,
        spaceBefore=14,
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=16,
        textColor=colors.HexColor("#374151"),
        spaceAfter=8,
    )
    proposal_style = ParagraphStyle(
        "Proposal",
        parent=styles["Normal"],
        fontSize=11,
        leading=18,
        textColor=colors.HexColor("#1f2937"),
        leftIndent=10,
        borderPad=8,
        spaceAfter=12,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#6b7280"),
        fontName="Helvetica-Bold",
    )

    story = []

    # ── HEADER ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("FoundrAI 2.0", title_style))
    story.append(Paragraph("AI-Generated Business Plan", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#3b82f6")))
    story.append(Spacer(1, 6*mm))

    # Idea box
    story.append(Paragraph("STARTUP IDEA", label_style))
    story.append(Paragraph(f'"{idea}"', proposal_style))
    story.append(Spacer(1, 4*mm))

    # ── FINAL PROPOSAL ────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb")))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("VALIDATED PROPOSAL", label_style))
    story.append(Paragraph(final_proposal, proposal_style))

    # ── BUSINESS PLAN SECTIONS ────────────────────────────────────────────────
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#8b5cf6")))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("CONSENSUS BUSINESS PLAN", section_header_style))
    story.append(Spacer(1, 2*mm))

    sections = [
        "Executive Summary", "Technology Stack",
        "Financial Model", "Marketing Strategy", "Risk Assessment"
    ]

    for section in sections:
        color = SECTION_COLORS.get(section, colors.HexColor("#3b82f6"))
        content = plan.get(section, "See full proposal above.")
        story.append(HRFlowable(width="100%", thickness=1.5, color=color))
        hdr = ParagraphStyle(
            "DynSection",
            parent=section_header_style,
            textColor=color,
        )
        story.append(Paragraph(section, hdr))
        story.append(Paragraph(content, body_style))

    # ── AGENT CRITIQUE TABLE ───────────────────────────────────────────────────
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#10b981")))
    story.append(Spacer(1, 2*mm))
    hdr2 = ParagraphStyle("Hdr2", parent=section_header_style, textColor=colors.HexColor("#10b981"))
    story.append(Paragraph("AGENT CRITIQUE SUMMARY", hdr2))
    story.append(Spacer(1, 2*mm))

    table_data = [["Agent", "Score", "Key Insight"]]
    for c in critiques:
        snippet = c["content"][:120] + ("..." if len(c["content"]) > 120 else "")
        table_data.append([c["agent"], f"{c['score']}/10", snippet])

    table = Table(table_data, colWidths=[30*mm, 20*mm, None])
    table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f9fafb"), colors.white]),
        ("FONTSIZE",     (0, 1), (-1, -1), 9),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    story.append(table)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb")))
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontSize=8, textColor=colors.HexColor("#9ca3af"), alignment=TA_CENTER,
    )
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("Generated by FoundrAI 2.0 — Deliberative Multi-Agent AI System", footer_style))

    doc.build(story)
    return OUTPUT_PATH
