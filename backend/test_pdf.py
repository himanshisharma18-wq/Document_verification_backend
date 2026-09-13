
# PDF REPORT TEST


import os

from backend.services.verification_service import verify_document
from backend.report.pdf_generator import generate_pdf_report



# INPUT FILES


DOCUMENT_IMAGE = "passport.jpeg"
SELFIE_IMAGE = "differ_person.jpg"

OUTPUT_PDF = "reports/verification_report.pdf"



# HEADER


print()
print("=" * 50)
print("PDF VERIFICATION REPORT TEST")
print("=" * 50)



# CHECK INPUT FILES


print()
print("DOCUMENT:", DOCUMENT_IMAGE)
print("EXISTS:", os.path.exists(DOCUMENT_IMAGE))

print()
print("SELFIE:", SELFIE_IMAGE)
print("EXISTS:", os.path.exists(SELFIE_IMAGE))


if not os.path.exists(DOCUMENT_IMAGE):

    print()
    print("ERROR: Document image not found.")
    raise SystemExit


if not os.path.exists(SELFIE_IMAGE):

    print()
    print("ERROR: Selfie image not found.")
    raise SystemExit



# RUN ACTUAL VERIFICATION PIPELINE


print()
print("=" * 50)
print("RUNNING VERIFICATION PIPELINE")
print("=" * 50)

result = verify_document(

    passport_image=DOCUMENT_IMAGE,

    reference_face_image=SELFIE_IMAGE
)



# CHECK PIPELINE


print()
print("VERIFICATION SUCCESS:")

print(
    result.get(
        "success",
        False
    )
)


if not result.get("success"):

    print()
    print("VERIFICATION FAILED:")

    print(
        result.get(
            "error",
            "Unknown error"
        )
    )

    raise SystemExit



# GET REPORT


report = result["report"]


print()
print("=" * 50)
print("VERIFICATION COMPLETED")
print("=" * 50)



# PRINT IMPORTANT RESULTS


risk = report.get(
    "risk",
    {}
)

verification = report.get(
    "verification",
    {}
)


print()
print("OCR:")

print(
    verification["ocr"]["percentage"],
    "%"
)


print()
print("MRZ:")

print(
    verification["mrz"]["percentage"],
    "%"
)


print()
print("PASSPORT:")

print(
    verification["passport"]["percentage"],
    "%"
)


print()
print("FACE:")

print(
    verification["face"]["percentage"],
    "%"
)


print()
print("DATABASE:")

print(
    verification["database"]["percentage"],
    "%"
)


print()
print("FORENSICS:")

print(
    verification["forensics"]["percentage"]
)


print()
print("OVERALL MATCH:")

print(
    risk["overall_match"],
    "%"
)


print()
print("RISK SCORE:")

print(
    risk["score"]
)


print()
print("RISK LEVEL:")

print(
    risk["level"]
)


print()
print("DECISION:")

print(
    risk["decision"]
)



# GENERATE PDF


print()
print("=" * 50)
print("GENERATING PDF")
print("=" * 50)


pdf_path = generate_pdf_report(

    report=report,

    document_image_path=DOCUMENT_IMAGE,

    output_path=OUTPUT_PDF
)



# CHECK PDF


print()
print("=" * 50)
print("PDF RESULT")
print("=" * 50)

print()
print("PDF GENERATED:")

print(
    os.path.exists(pdf_path)
)

print()
print("PDF PATH:")

print(
    os.path.abspath(pdf_path)
)


if os.path.exists(pdf_path):

    print()
    print("=" * 50)
    print("PDF GENERATION SUCCESS")
    print("=" * 50)

else:

    print()
    print("ERROR: PDF was not generated.")