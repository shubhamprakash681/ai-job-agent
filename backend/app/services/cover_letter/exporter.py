import os
from pathlib import Path
from datetime import datetime
import structlog

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT

logger = structlog.get_logger(__name__)


class CoverLetterExporter:
    """
    Exporters for ATS-friendly and professional PDF and Markdown Cover Letters.
    """

    @staticmethod
    def export_markdown(content: str, output_path: str) -> str:
        """Write Markdown cover letter to disk."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return str(p.absolute())

    @staticmethod
    def export_pdf(
        content: str,
        output_path: str,
        candidate_name: str = "Shubham Prakash",
        contact_info: str = "Mumbai, India | +91 9934305886 | shubhamprakash230@gmail.com | Portfolio: https://www.shubhamprakash681.in/ | LinkedIn: linkedin.com/in/shubhamprakash681",
        company: str = "Hiring Team",
        title: str = "Software Engineer",
        date_str: str | None = None,
    ) -> str:
        """
        Export cover letter to a clean, executive ATS-compliant PDF using ReportLab.
        """
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        if not date_str:
            date_str = datetime.now().strftime("%B %d, %Y")

        doc = SimpleDocTemplate(
            str(p.absolute()),
            pagesize=letter,
            leftMargin=54,  # 0.75 in
            rightMargin=54,
            topMargin=54,
            bottomMargin=54,
        )

        styles = getSampleStyleSheet()

        name_style = ParagraphStyle(
            "CLName",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=3,
        )

        contact_style = ParagraphStyle(
            "CLContact",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#475569"),
            spaceAfter=8,
        )

        meta_style = ParagraphStyle(
            "CLMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=3,
        )

        subject_style = ParagraphStyle(
            "CLSubject",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#1e3a8a"),
            spaceBefore=8,
            spaceAfter=12,
        )

        body_style = ParagraphStyle(
            "CLBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=10,
        )

        signoff_style = ParagraphStyle(
            "CLSignoff",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=8,
            spaceAfter=2,
        )

        signoff_name_style = ParagraphStyle(
            "CLSignoffName",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=14,
            spaceAfter=2,
        )

        story = []

        # 1. Candidate Header
        story.append(Paragraph(candidate_name.upper(), name_style))
        story.append(Paragraph(contact_info, contact_style))
        story.append(
            HRFlowable(
                width="100%",
                thickness=1,
                color=colors.HexColor("#cbd5e1"),
                spaceBefore=2,
                spaceAfter=14,
            )
        )

        # 2. Date
        story.append(Paragraph(date_str, meta_style))
        story.append(Spacer(1, 8))

        # 3. Recipient Block
        story.append(Paragraph("<b>Hiring Team / Engineering Leadership</b>", meta_style))
        story.append(Paragraph(f"<b>{company}</b>", meta_style))
        story.append(Spacer(1, 10))

        # 4. Subject Line
        story.append(Paragraph(f"<b>RE: Application for {title}</b>", subject_style))

        # 5. Body paragraphs
        # Clean up markdown / headers if present in content
        cleaned_paragraphs = []
        raw_paragraphs = [p_text.strip() for p_text in content.split("\n\n") if p_text.strip()]

        for raw_p in raw_paragraphs:
            # Skip any existing salutations or sign-offs if duplicated
            lowered = raw_p.lower()
            if lowered.startswith("dear ") or lowered.startswith("sincerely") or lowered.startswith("best regards") or lowered == candidate_name.lower():
                continue
            if raw_p.startswith("#"):
                # Strip markdown header hash
                raw_p = raw_p.lstrip("#").strip()
            # Escape HTML characters or format bolding
            formatted_p = raw_p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            # Convert **bold** to <b>bold</b>
            while "**" in formatted_p:
                formatted_p = formatted_p.replace("**", "<b>", 1).replace("**", "</b>", 1)
            cleaned_paragraphs.append(formatted_p)

        # Salutation
        story.append(Paragraph(f"Dear Hiring Team at {company},", body_style))
        story.append(Spacer(1, 4))

        # Body
        for p_text in cleaned_paragraphs:
            story.append(Paragraph(p_text, body_style))

        # 6. Sign-off
        story.append(Spacer(1, 8))
        story.append(Paragraph("Sincerely,", signoff_style))
        story.append(Paragraph(candidate_name, signoff_name_style))
        story.append(Paragraph("Full Stack &amp; Backend Software Engineer", meta_style))

        doc.build(story)
        logger.info("Cover letter PDF generated", output_path=str(p.absolute()))
        return str(p.absolute())

