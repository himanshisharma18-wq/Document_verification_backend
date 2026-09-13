# DOCUMENT VERIFICATION SERVICE


import os
import uuid


from backend.ocr.ocr_engine import extract_mrz

from backend.mrz.mrz_parser import parse_mrz

from backend.documents.passport.validator import (
    validate_passport_data
)

from backend.database.demo_database import (
    find_passport
)

from backend.face.face_detector import (
    detect_face_from_path
)

from backend.face.face_embedding import (
    generate_face_embedding
)

from backend.face.face_verifier import (
    verify_faces
)

from backend.risk.risk_engine import (
    calculate_risk
)

from backend.report.report_generator import (
    generate_verification_report
)

from backend.report.pdf_generator import (
    generate_pdf_report
)



# PATHS


# Project root:
# document_verification_backend/

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# backend/
#     services/
# BASE_DIR points to backend/

REPORTS_DIRECTORY = os.path.join(
    BASE_DIR,
    "reports"
)

os.makedirs(
    REPORTS_DIRECTORY,
    exist_ok=True
)



# MAIN VERIFICATION PIPELINE


def verify_document(
    passport_image,
    reference_face_image
):

    
    # 1. OCR
    

    print()
    print("")
    print("1. OCR")
    print("")

    ocr_result = extract_mrz(
        passport_image
    )

    ocr_success = bool(
        ocr_result.get(
            "success",
            False
        )
    )

    print(
        "OCR SUCCESS:",
        ocr_success
    )

    if not ocr_success:

        return {
            "success": False,
            "error": "OCR failed"
        }


    
    # 2. MRZ PARSING
    

    print()
    print("")
    print("2. MRZ PARSING")
    print("")

    parsed = parse_mrz(
        ocr_result["mrz_lines"]
    )

    mrz_valid = bool(
        parsed.get(
            "mrz_valid",
            False
        )
    )

    print(
        "MRZ VALID:",
        mrz_valid
    )

    if not parsed.get(
        "success",
        False
    ):

        return {
            "success": False,
            "error": "MRZ parsing failed"
        }


    passport_data = parsed["data"]


    
    # 3. PASSPORT VALIDATION
    

    print()
    print("")
    print("3. PASSPORT VALIDATION")
    print("")

    validation = validate_passport_data(
        passport_data
    )

    passport_valid = bool(
        validation.get(
            "valid",
            False
        )
    )

    print(
        "PASSPORT VALID:",
        passport_valid
    )


    
    # 4. DATABASE VERIFICATION
    

    print()
    print("")
    print("4. DATABASE VERIFICATION")
    print("")

    passport_number = passport_data.get(
        "passport_number"
    )

    database_record = find_passport(
        passport_number
    )

    database_match = (
        database_record is not None
    )

    print(
        "DATABASE MATCH:",
        database_match
    )


    
    # 5. FACE DETECTION
    

    print()
    print("")
    print("5. FACE DETECTION")
    print("")

    face_a = detect_face_from_path(
        passport_image
    )

    face_b = detect_face_from_path(
        reference_face_image
    )

    face_detected = (
        face_a is not None
        and
        face_b is not None
    )

    print(
        "FACE DETECTED:",
        face_detected
    )


    
    # 6. FACE VERIFICATION
    

    print()
    print("")
    print("6. FACE VERIFICATION")
    print("")

    face_match = False

    face_similarity = 0.0


    if face_detected:

        
        # Passport face embedding
        

        embedding_a = generate_face_embedding(
            passport_image
        )


        
        # Selfie face embedding
        

        embedding_b = generate_face_embedding(
            reference_face_image
        )


        
        # Verify faces
        

        if (
            embedding_a is not None
            and
            embedding_b is not None
        ):

            face_result = verify_faces(
                embedding_a,
                embedding_b
            )

            face_match = bool(
                face_result.get(
                    "match",
                    False
                )
            )

            face_similarity = float(
                face_result.get(
                    "similarity",
                    0.0
                )
            )


    print(
        "FACE MATCH:",
        face_match
    )

    print(
        "FACE SIMILARITY:",
        face_similarity
    )


    
    # 7. FORENSICS
    
    #
    # Currently not implemented.
    #
    # We explicitly mark it unavailable.
    #
    

    print()
    print("")
    print("7. FORENSICS")
    print("")

    forensics_result = None

    # The current risk engine expects a boolean.
    #
    # Since forensics is not implemented yet,
    # we keep this neutral so it does not
    # artificially increase the risk score.

    forensics_valid = True

    print(
        "FORENSICS: NOT IMPLEMENTED"
    )


    
    # 8. RISK ENGINE
    

    print()
    print("")
    print("8. RISK ENGINE")
    print("")

    risk_result = calculate_risk(

        ocr_success=ocr_success,

        mrz_valid=mrz_valid,

        passport_valid=passport_valid,

        face_detected=face_detected,

        face_match=face_match,

        face_similarity=face_similarity,

        database_match=database_match,

        forensics_valid=forensics_valid
    )


    print(
        "RISK SCORE:",
        risk_result.get(
            "risk_score"
        )
    )

    print(
        "RISK LEVEL:",
        risk_result.get(
            "risk_level"
        )
    )

    print(
        "DECISION:",
        risk_result.get(
            "decision"
        )
    )


    
    # 9. GENERATE JSON VERIFICATION REPORT
    

    print()
    print("")
    print("9. GENERATING VERIFICATION REPORT")
    print("")

    report = generate_verification_report(

        passport_data=passport_data,

        ocr_success=ocr_success,

        mrz_valid=mrz_valid,

        passport_valid=passport_valid,

        face_detected=face_detected,

        face_match=face_match,

        face_similarity=face_similarity,

        database_match=database_match,

        forensics_result=forensics_result,

        risk_result=risk_result
    )


    print(
        "VERIFICATION REPORT GENERATED"
    )


    
    # 10. GENERATE PDF REPORT
    

    print()
    print("")
    print("10. GENERATING PDF REPORT")
    print("")


    verification_id = passport_data.get(
        "passport_number"
    )


    if not verification_id:

        verification_id = uuid.uuid4().hex


    
    # Remove unsafe characters from filename
    

    safe_verification_id = "".join(

        character

        for character in str(
            verification_id
        )

        if (
            character.isalnum()
            or
            character in (
                "-",
                "_"
            )
        )
    )


    pdf_filename = (
        "verification_report_"
        f"{safe_verification_id}.pdf"
    )


    pdf_path = os.path.join(
        REPORTS_DIRECTORY,
        pdf_filename
    )


    print(
        "PDF WILL BE SAVED AT:"
    )

    print(
        pdf_path
    )


    
    # Generate PDF
    

    try:

        generate_pdf_report(

            report=report,

            document_image_path=passport_image,

            output_path=pdf_path
        )

        print(
            "PDF GENERATED SUCCESSFULLY"
        )

        print(
            "PDF PATH:",
            pdf_path
        )

    except Exception as pdf_error:

        print()
        print("")
        print("PDF GENERATION ERROR")
        print("")

        print(
            pdf_error
        )

        # We do NOT stop verification completely.
        #
        # The JSON verification result can still
        # be returned even if PDF generation fails.

        pdf_filename = None


    
    # 11. PDF URL
    

    if pdf_filename:

        pdf_url = (
            "/api/reports/"
            f"{pdf_filename}"
        )

    else:

        pdf_url = None


    
    # 12. FINAL RESPONSE
    

    print()
    print("")
    print("VERIFICATION COMPLETE")
    print("")


    return {

        "success": True,


        
        # Verification ID
        

        "verification_id":
            passport_data.get(
                "passport_number",
                "UNKNOWN"
            ),


        
        # Document information
        

        "document": {

            "type":
                "PASSPORT",

            "filename":
                passport_image

        },


        
        # Identity information
        

        "identity":
            passport_data,


        
        # Individual verification checks
        

        "checks": {

           
            # OCR
           

            "ocr": {

                "success":
                    ocr_success,

                "percentage":
                    risk_result[
                        "match_details"
                    ].get(
                        "ocr",
                        0
                    )

            },


           
            # MRZ
           

            "mrz": {

                "valid":
                    mrz_valid,

                "percentage":
                    risk_result[
                        "match_details"
                    ].get(
                        "mrz",
                        0
                    )

            },


           
            # Passport validation
           

            "passport": {

                "valid":
                    passport_valid,

                "percentage":
                    risk_result[
                        "match_details"
                    ].get(
                        "passport",
                        0
                    )

            },


           
            # Face verification
           

            "face": {

                "detected":
                    face_detected,

                "match":
                    face_match,

                "similarity":
                    round(
                        face_similarity * 100,
                        2
                    ),

                "percentage":
                    round(
                        face_similarity * 100,
                        2
                    )

            },


           
            # Database
           

            "database": {

                "match":
                    database_match,

                "percentage":
                    risk_result[
                        "match_details"
                    ].get(
                        "database",
                        0
                    )

            },


           
            # Forensics
           

            "forensics": {

                "available":
                    False,

                "status":
                    "NOT_IMPLEMENTED",

                "percentage":
                    None

            }

        },


        
        # Risk engine
        

        "risk": {

            "score":
                risk_result[
                    "risk_score"
                ],

            "level":
                risk_result[
                    "risk_level"
                ],

            "decision":
                risk_result[
                    "decision"
                ],

            "overall_match":
                risk_result[
                    "overall_match_percentage"
                ],

            "match_details":
                risk_result[
                    "match_details"
                ],

            "reasons":
                risk_result[
                    "reasons"
                ]

        },


        
        # Complete generated report
        

        "report":
            report,


        
        # PDF REPORT
        

        "pdfUrl":
            pdf_url

    }