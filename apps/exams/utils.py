from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.pdfgen import canvas

def generate_exam_paper_pdf(assignment):
    """Generate a PDF exam paper for a dreva.
    
    Args:
        assignment: ExamAssignment instance
    
    Returns:
        BytesIO object containing the PDF
    """
    dreva = assignment.dreva
    exam = assignment.exam
    organization = dreva.organization
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    # Style sheets
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=1
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
    )
    
    # Header
    header_data = [
        [
            Paragraph(f"<b>{organization.name}</b>", title_style),
        ],
        [
            Paragraph("DRIVER TRAINING AND EXAMINATION SYSTEM", heading_style),
        ],
    ]
    header_table = Table(header_data, colWidths=[7*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Exam and Driver Information
    info_data = [
        [
            Paragraph(f"<b>Driver (Dreva) Name:</b> {dreva.full_name}", normal_style),
            Paragraph(f"<b>Driver ID:</b> {dreva.driver_id}", normal_style),
        ],
        [
            Paragraph(f"<b>Organization:</b> {organization.name}", normal_style),
            Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}", normal_style),
        ],
        [
            Paragraph(f"<b>Exam Title:</b> {exam.title}", normal_style),
            Paragraph(f"<b>Subject:</b> {exam.subject}", normal_style),
        ],
        [
            Paragraph(f"<b>Max Marks:</b> {exam.max_marks}", normal_style),
            Paragraph(f"<b>Duration:</b> {exam.duration_minutes} minutes", normal_style),
        ],
    ]
    
    info_table = Table(info_data, colWidths=[3.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Instructions
    story.append(Paragraph("<b>INSTRUCTIONS:</b>", heading_style))
    instructions = [
        "1. Write your answers clearly and legibly.",
        "2. Use blue or black ink only.",
        "3. Do not write on the margins.",
        "4. Attempt all questions.",
        "5. Write the question number before each answer.",
    ]
    for instruction in instructions:
        story.append(Paragraph(instruction, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Questions
    story.append(Paragraph("<b>QUESTIONS:</b>", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    questions = exam.examquestion_set.all().order_by('question_number')
    for question in questions:
        q_text = f"<b>Q{question.question_number} ({question.marks} marks):</b> {question.question_text}"
        story.append(Paragraph(q_text, normal_style))
        
        if question.question_type == 'mcq' and question.options:
            # Show options for MCQ
            options = question.options if isinstance(question.options, list) else []
            for option in options:
                story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;( ) {option}", normal_style))
        
        # Add space for answer
        story.append(Spacer(1, 0.8*inch))
    
    # Footer
    story.append(Spacer(1, 0.2*inch))
    footer_data = [
        [
            Paragraph(f"<i>Examiner's Signature: ________________</i>", normal_style),
            Paragraph(f"<i>Date: ________________</i>", normal_style),
        ]
    ]
    footer_table = Table(footer_data, colWidths=[3.5*inch, 3.5*inch])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    story.append(footer_table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
