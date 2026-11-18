import os
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.core.logging import logger
from app.core.datetime_utils import utc_now

class InterviewReportGenerator:
    """
    Generates professional PDF evaluation reports for completed mock interviews.
    """
    @staticmethod
    def generate_pdf_report(report_data: Dict[str, Any], output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#4B5563'),
            spaceAfter=15
        )
        h2_style = ParagraphStyle(
            'SectionH2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#1F2937'),
            spaceBefore=12,
            spaceAfter=8
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            leading=14
        )

        story = []

        # Title Header
        story.append(Paragraph("SmartHire — Mock Interview Evaluation Report", title_style))
        cand_name = report_data.get("candidate_name", "Candidate")
        target_role = report_data.get("target_role", "Software Engineer")
        date_str = report_data.get("interview_date", utc_now().strftime("%B %d, %Y"))
        story.append(Paragraph(f"<b>Candidate:</b> {cand_name} &nbsp;|&nbsp; <b>Target Role:</b> {target_role} &nbsp;|&nbsp; <b>Date:</b> {date_str}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3B82F6'), spaceAfter=15))

        # Overall Score Banner Table
        overall = report_data.get("overall_score", 80.0)
        tech = report_data.get("technical_score", 82.0)
        comm = report_data.get("communication_score", 78.0)
        ps = report_data.get("problem_solving_score", 85.0)
        conf = report_data.get("confidence_score", 80.0)

        score_table_data = [
            ["Overall Score", "Technical Accuracy", "Communication", "Problem Solving", "Confidence"],
            [f"{overall}%", f"{tech}%", f"{comm}%", f"{ps}%", f"{conf}%"]
        ]
        score_table = Table(score_table_data, colWidths=[105, 110, 105, 110, 100])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EFF6FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 8),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 14),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#111827')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DBEAFE')),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 15))

        # Executive Summary
        story.append(Paragraph("Executive Performance Summary", h2_style))
        summary_text = report_data.get("summary", "Candidate demonstrated solid foundational understanding and structured communication throughout the interview session.")
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 12))

        # Strengths & Weaknesses
        strengths = report_data.get("strengths", ["Clear explanation of system architecture", "Strong problem-solving approach"])
        weaknesses = report_data.get("weaknesses", ["Elaborate deeper on distributed caching and concurrency", "Incorporate more quantitative metrics"])
        
        sw_data = [
            [
                Paragraph("<b>Key Strengths</b>", h2_style),
                Paragraph("<b>Areas for Growth</b>", h2_style)
            ],
            [
                Paragraph("<br/>".join([f"• {s}" for s in strengths]), body_style),
                Paragraph("<br/>".join([f"• {w}" for w in weaknesses]), body_style)
            ]
        ]
        sw_table = Table(sw_data, colWidths=[265, 265])
        sw_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(sw_table)
        story.append(Spacer(1, 12))

        # Recommended Revision Topics
        revisions = report_data.get("revision_topics", ["Database Optimization", "Low-Level Design", "Distributed Systems"])
        story.append(Paragraph("Recommended Topics to Revise Before Live Interview", h2_style))
        story.append(Paragraph(", ".join(revisions), body_style))
        story.append(Spacer(1, 15))

        # Question by Question Transcript & Analysis
        story.append(Paragraph("Question & Answer Breakdown", h2_style))
        qa_records = report_data.get("qa_records", [])
        for record in qa_records:
            q_text = record.get("question_text", "")
            a_text = record.get("candidate_answer", "")
            feedback = record.get("feedback", "")
            q_num = record.get("sequence_order", 1)

            qa_box = [
                [Paragraph(f"<b>Q{q_num}: {q_text}</b>", ParagraphStyle('QTitle', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#1E3A8A')))],
                [Paragraph(f"<b>Candidate Answer:</b> {a_text}", body_style)],
                [Paragraph(f"<b>AI Evaluator Feedback:</b> {feedback}", ParagraphStyle('FBack', parent=body_style, textColor=colors.HexColor('#047857')))]
            ]
            box_table = Table(qa_box, colWidths=[530])
            box_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(box_table)
            story.append(Spacer(1, 8))

        doc.build(story)
        logger.info(f"Generated PDF interview report at {output_path}")
        return output_path

report_generator = InterviewReportGenerator()
