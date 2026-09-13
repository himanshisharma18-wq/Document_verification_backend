
# PDF VERIFICATION REPORT GENERATOR


import os

from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)



# GENERATE PDF REPORT


def generate_pdf_report(
    report,
    document_image_path,
    output_path="verification_report.pdf"
):

   
    # Create output directory
   

    output_directory = os.path.dirname(output_path)

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True
        )


    
    # IMPORTANT
    
    #
    # report_generator.py returns:
    #
    # {
    #     "report_info": {...},
    #     "identity": {...},
    #     "verification": {...},
    #     "risk": {...}
    # }
    #
    # NOT:
    #
    # {
    #     "report": {...}
    # }
    #
    

    report_info = report.get(
        "report_info",
        {}
    )

    identity = report.get(
        "identity",
        {}
    )

    verification = report.get(
        "verification",
        {}
    )

    risk = report.get(
        "risk",
        {}
    )


    
    # PDF DOCUMENT
    

    doc = SimpleDocTemplate(

        output_path,

        pagesize=A4,

        rightMargin=15 * mm,

        leftMargin=15 * mm,

        topMargin=15 * mm,

        bottomMargin=15 * mm
    )


    
    # STYLES
    

    styles = getSampleStyleSheet()


    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=8
    )


    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        alignment=TA_CENTER
    )


    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=8,
        spaceAfter=6
    )


    normal_style = ParagraphStyle(
        "NormalReport",
        parent=styles["Normal"],
        fontSize=9,
        leading=12
    )


    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        leading=10
    )


    
    # STORY
    

    story = []


    
    # TITLE
    

    story.append(
        Paragraph(
            "DOCUMENT VERIFICATION REPORT",
            title_style
        )
    )


    generated_at = report_info.get(
        "generated_at",
        datetime.now().isoformat()
    )


    story.append(
        Paragraph(
            f"Generated: {generated_at}",
            subtitle_style
        )
    )


    story.append(
        Spacer(
            1,
            8
        )
    )


    
    # DOCUMENT IMAGE
    

    story.append(
        Paragraph(
            "DOCUMENT IMAGE",
            heading_style
        )
    )


    if (
        document_image_path
        and
        os.path.exists(document_image_path)
    ):

        try:

            document_image = Image(
                document_image_path
            )

            document_image._restrictSize(
                170 * mm,
                85 * mm
            )

            story.append(
                document_image
            )

        except Exception as error:

            print(
                "PDF document image error:",
                error
            )

            story.append(
                Paragraph(
                    "Document image could not be loaded.",
                    normal_style
                )
            )

    else:

        story.append(
            Paragraph(
                "Document image not available.",
                normal_style
            )
        )


    story.append(
        Spacer(
            1,
            8
        )
    )


    
    # IDENTITY INFORMATION
    

    story.append(
        Paragraph(
            "IDENTITY INFORMATION",
            heading_style
        )
    )


    identity_rows = [

        ["Field", "Value"],

        [
            "Document Type",
            identity.get(
                "document_type",
                "N/A"
            )
        ],

        [
            "Issuing Country",
            identity.get(
                "issuing_country",
                "N/A"
            )
        ],

        [
            "Surname",
            identity.get(
                "surname",
                "N/A"
            )
        ],

        [
            "Given Names",
            identity.get(
                "given_names",
                "N/A"
            )
        ],

        [
            "Passport Number",
            identity.get(
                "passport_number",
                "N/A"
            )
        ],

        [
            "Nationality",
            identity.get(
                "nationality",
                "N/A"
            )
        ],

        [
            "Date of Birth",
            identity.get(
                "date_of_birth",
                "N/A"
            )
        ],

        [
            "Sex",
            identity.get(
                "sex",
                "N/A"
            )
        ],

        [
            "Date of Expiry",
            identity.get(
                "date_of_expiry",
                "N/A"
            )
        ]
    ]


    identity_table = Table(
        identity_rows,
        colWidths=[
            55 * mm,
            115 * mm
        ],
        repeatRows=1
    )


    identity_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#E8E8E8")
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "FONTNAME",
                (0, 1),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8.5
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                6
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                6
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )

        ])
    )


    story.append(
        identity_table
    )


    
    # VERIFICATION RESULTS
    

    story.append(
        Paragraph(
            "VERIFICATION RESULTS",
            heading_style
        )
    )


    def status_text(
        value,
        success_text="PASSED",
        failure_text="FAILED"
    ):

        if value is None:
            return "NOT AVAILABLE"

        if value:
            return success_text

        return failure_text


    ocr = verification.get(
        "ocr",
        {}
    )

    mrz = verification.get(
        "mrz",
        {}
    )

    passport = verification.get(
        "passport",
        {}
    )

    face = verification.get(
        "face",
        {}
    )

    database = verification.get(
        "database",
        {}
    )

    forensics = verification.get(
        "forensics",
        {}
    )


    verification_rows = [

        [
            "Check",
            "Status",
            "Match / Score"
        ],

        [
            "OCR",
            status_text(
                ocr.get("success")
            ),
            f'{ocr.get("percentage", 0)}%'
        ],

        [
            "MRZ Validation",
            status_text(
                mrz.get("valid")
            ),
            f'{mrz.get("percentage", 0)}%'
        ],

        [
            "Passport Validation",
            status_text(
                passport.get("valid")
            ),
            f'{passport.get("percentage", 0)}%'
        ],

        [
            "Face Detection",
            status_text(
                face.get("detected")
            ),
            "-"
        ],

        [
            "Face Verification",
            status_text(
                face.get("match")
            ),
            f'{face.get("percentage", 0)}%'
        ],

        [
            "Database",
            status_text(
                database.get("match")
            ),
            f'{database.get("percentage", 0)}%'
        ],

        [
            "Forensics",

            (
                "PASSED"
                if (
                    forensics.get("available")
                    and
                    forensics.get("percentage") == 100
                )

                else "NOT AVAILABLE"
                if not forensics.get("available")

                else "FAILED"
            ),

            (
                f'{forensics.get("percentage")}%'
                if forensics.get("percentage") is not None
                else "N/A"
            )
        ]
    ]


    verification_table = Table(
        verification_rows,
        colWidths=[
            65 * mm,
            50 * mm,
            55 * mm
        ],
        repeatRows=1
    )


    verification_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#E8E8E8")
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8.5
            ),

            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "CENTER"
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )

        ])
    )


    story.append(
        verification_table
    )


    
    # RISK ASSESSMENT
    

    story.append(
        Paragraph(
            "RISK ASSESSMENT",
            heading_style
        )
    )


    risk_rows = [

        [
            "Overall Match",
            f'{risk.get("overall_match", 0)}%'
        ],

        [
            "Risk Score",
            f'{risk.get("score", 0)} / 100'
        ],

        [
            "Risk Level",
            risk.get(
                "level",
                "N/A"
            )
        ],

        [
            "System Recommendation",
            risk.get(
                "decision",
                "N/A"
            )
        ]
    ]


    risk_table = Table(
        risk_rows,
        colWidths=[
            65 * mm,
            105 * mm
        ]
    )


    risk_table.setStyle(
        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            )

        ])
    )


    story.append(
        risk_table
    )


    
    # FLAGS / REASONS
    

    story.append(
        Paragraph(
            "FLAGS / REASONS",
            heading_style
        )
    )


    reasons = risk.get(
        "reasons",
        []
    )


    if reasons:

        reason_rows = [
            ["Flag"]
        ]

        for reason in reasons:

            reason_rows.append(
                [f"• {reason}"]
            )


        reason_table = Table(
            reason_rows,
            colWidths=[
                170 * mm
            ]
        )


        reason_table.setStyle(
            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#E8E8E8")
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8.5
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                )

            ])
        )

        story.append(
            reason_table
        )

    else:

        story.append(
            Paragraph(
                "No risk factors detected.",
                normal_style
            )
        )


    
    # FOOTER
    

    story.append(
        Spacer(
            1,
            12
        )
    )


    story.append(
        Paragraph(
            "This report is an automated verification assessment. "
            "A flagged document should be manually reviewed by an "
            "authorized officer before any final action.",
            small_style
        )
    )


    
    # BUILD PDF
    

    doc.build(
        story
    )


    print(
        "PDF REPORT GENERATED:",
        output_path
    )


    return output_path