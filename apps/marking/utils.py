from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors


def generate_marked_exam_pdf(result):
    """Generate a marked exam PDF summarizing marks and annotating questions.

    This produces a clean digital copy including:
    - Candidate (Dreva) and Exam info
    - Per-question awarded marks and optional comments
    - Overall score, percentage, status, marker and dates

    Args:
        result: ExamResult instance

    Returns:
        bytes: PDF bytes
    """
    dreva = result.dreva
    exam = result.exam

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'MarkedTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1a1a1a'), alignment=1
    )
    heading_style = ParagraphStyle(
        'MarkedHeading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#333333')
    )
    normal_style = ParagraphStyle('MarkedNormal', parent=styles['Normal'], fontSize=10)

    # Header
    story.append(Paragraph('MARKED EXAM PAPER', title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Candidate/Exam info
    info_data = [
        [
            Paragraph(f"<b>Driver (Dreva) Name:</b> {dreva.full_name}", normal_style),
            Paragraph(f"<b>Driver ID:</b> {dreva.driver_id}", normal_style),
        ],
        [
            Paragraph(f"<b>Organization:</b> {dreva.organization.name}", normal_style),
            Paragraph(f"<b>Exam:</b> {exam.title}", normal_style),
        ],
        [
            Paragraph(f"<b>Subject:</b> {exam.subject}", normal_style),
            Paragraph(f"<b>Exam Date:</b> {result.exam_date.strftime('%d/%m/%Y') if result.exam_date else '-'}", normal_style),
        ],
    ]
    info_table = Table(info_data, colWidths=[3.5 * inch, 3.5 * inch])
    info_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.2 * inch))

    # Summary
    total_marks = result.total_marks or exam.max_marks
    obtained = result.obtained_marks if result.obtained_marks is not None else 0
    percentage = result.percentage if result.percentage is not None else 0

    summary_data = [
        [
            Paragraph(f"<b>Total Marks:</b> {total_marks}", normal_style),
            Paragraph(f"<b>Obtained:</b> {obtained}", normal_style),
            Paragraph(f"<b>Percentage:</b> {percentage:.2f}%", normal_style),
            Paragraph(f"<b>Status:</b> {result.get_status_display()}", normal_style),
        ]
    ]
    summary_table = Table(summary_data, colWidths=[1.8 * inch, 1.8 * inch, 1.8 * inch, 1.6 * inch])
    summary_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3 * inch))

    # Per-question marks
    story.append(Paragraph('<b>QUESTION ANNOTATIONS</b>', heading_style))
    story.append(Spacer(1, 0.1 * inch))

    questions = exam.examquestion_set.all().order_by('question_number')
    responses = {r.question_id: r for r in result.responses.all()}

    rows = [[
        Paragraph('<b>No.</b>', normal_style),
        Paragraph('<b>Question</b>', normal_style),
        Paragraph('<b>Marks</b>', normal_style),
        Paragraph('<b>Comments</b>', normal_style),
    ]]

    for q in questions:
        resp = responses.get(q.id)
        awarded = resp.marks_awarded if resp and resp.marks_awarded is not None else '-'
        comments = resp.comments if resp and resp.comments else ''
        rows.append([
            Paragraph(str(q.question_number), normal_style),
            Paragraph(q.question_text, normal_style),
            Paragraph(f"{awarded}/{q.marks}", normal_style),
            Paragraph(comments, normal_style),
        ])

    table = Table(rows, colWidths=[0.6 * inch, 3.6 * inch, 1.0 * inch, 2.2 * inch])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f3f5')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3 * inch))

    # Footer (marker)
    marker = result.marked_by or ''
    footer_data = [[
        Paragraph(f"<i>Marked By:</i> {marker}", normal_style),
        Paragraph(f"<i>Marked On:</i> {result.marking_date.strftime('%d/%m/%Y') if result.marking_date else datetime.now().strftime('%d/%m/%Y')}", normal_style),
    ]]
    footer = Table(footer_data, colWidths=[3.5 * inch, 3.5 * inch])
    footer.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT')]))
    story.append(footer)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
