# REAL END-TO-END RISK ENGINE TEST


import os

from backend.ocr.ocr_engine import extract_mrz
from backend.mrz.mrz_parser import parse_mrz
from backend.documents.passport.validator import validate_passport_data

from backend.database.demo_database import find_passport

from backend.face.face_detector import detect_face_from_path
from backend.face.face_embedding import generate_face_embedding
from backend.face.face_verifier import verify_faces

from backend.risk.risk_engine import calculate_risk



# IMAGE PATHS


PASSPORT_IMAGE = "passport.jpeg"
FACE_IMAGE = "face_detected.jpg"



# HEADER


print()
print("=" * 60)
print("REAL DOCUMENT VERIFICATION + RISK ENGINE")
print("=" * 60)



# CHECK PASSPORT IMAGE


print()
print("PASSPORT IMAGE")
print("-" * 60)

if not os.path.exists(PASSPORT_IMAGE):

    print("ERROR: Passport image not found:")
    print(PASSPORT_IMAGE)

    raise SystemExit

print("IMAGE:", PASSPORT_IMAGE)
print("EXISTS: True")



# 1. OCR


print()
print("=" * 60)
print("1. OCR")
print("=" * 60)

ocr_result = extract_mrz(
    PASSPORT_IMAGE
)

ocr_success = bool(
    ocr_result.get("success", False)
)

print()
print("OCR SUCCESS:")
print(ocr_success)


if ocr_result.get("mrz_lines"):

    print()
    print("MRZ LINES:")
    print("-" * 60)

    for line in ocr_result["mrz_lines"]:

        print(line)



# STOP IF OCR FAILED


if not ocr_success:

    print()
    print("OCR FAILED.")
    print("Cannot continue to MRZ validation.")

    risk_result = calculate_risk(
        ocr_success=False,
        mrz_valid=False,
        passport_valid=False,
        face_detected=False,
        face_match=False,
        face_similarity=0.0,
        database_match=False,
        forensics_valid=True
    )

    print()
    print("RISK SCORE:", risk_result["risk_score"])
    print("RISK LEVEL:", risk_result["risk_level"])
    print("DECISION:", risk_result["decision"])

    raise SystemExit



# 2. MRZ PARSER


print()
print("=" * 60)
print("2. MRZ PARSER")
print("=" * 60)

parsed = parse_mrz(
    ocr_result["mrz_lines"]
)

mrz_valid = bool(
    parsed.get("mrz_valid", False)
)

print()
print("MRZ PARSER SUCCESS:")
print(parsed.get("success"))

print()
print("MRZ VALID:")
print(mrz_valid)


if parsed.get("error"):

    print()
    print("MRZ ERROR:")
    print(parsed["error"])



# PASSPORT DATA


data = parsed.get(
    "data",
    {}
)


if data:

    print()
    print("PASSPORT DATA")
    print("-" * 60)

    print(
        "Document Type:",
        data.get("document_type")
    )

    print(
        "Issuing Country:",
        data.get("issuing_country")
    )

    print(
        "Surname:",
        data.get("surname")
    )

    print(
        "Given Names:",
        data.get("given_names")
    )

    print(
        "Passport Number:",
        data.get("passport_number")
    )

    print(
        "Nationality:",
        data.get("nationality")
    )

    print(
        "Date of Birth:",
        data.get("date_of_birth")
    )

    print(
        "Sex:",
        data.get("sex")
    )

    print(
        "Date of Expiry:",
        data.get("date_of_expiry")
    )



# 3. PASSPORT VALIDATOR


print()
print("=" * 60)
print("3. PASSPORT VALIDATOR")
print("=" * 60)

if data:

    validation = validate_passport_data(
        data
    )

else:

    validation = {
        "valid": False,
        "errors": [
            "Passport data could not be parsed"
        ],
        "expiry_status": "invalid"
    }


passport_valid = bool(
    validation.get("valid", False)
)

print()
print("PASSPORT VALID:")
print(passport_valid)

print()
print("EXPIRY STATUS:")
print(
    validation.get(
        "expiry_status",
        "unknown"
    )
)


if validation.get("errors"):

    print()
    print("VALIDATION ERRORS:")
    print("-" * 60)

    for error in validation["errors"]:

        print("-", error)

else:

    print()
    print("NO PASSPORT VALIDATION ERRORS.")



# 4. DATABASE


print()
print("=" * 60)
print("4. DATABASE VERIFICATION")
print("=" * 60)

passport_number = data.get(
    "passport_number",
    ""
)

database_record = None

if passport_number:

    database_record = find_passport(
        passport_number
    )

database_match = database_record is not None


print()
print("PASSPORT NUMBER:")
print(passport_number)

print()
print("DATABASE MATCH:")
print(database_match)


if database_record:

    print()
    print("DATABASE RECORD:")
    print("-" * 60)
    print(database_record)

else:

    print()
    print("NO MATCHING DATABASE RECORD.")



# 5. FACE VERIFICATION


print()
print("=" * 60)
print("5. FACE VERIFICATION")
print("=" * 60)


face_detected = False
face_match = False
face_similarity = 0.0



# Check second image


if not os.path.exists(FACE_IMAGE):

    print()
    print("REFERENCE FACE IMAGE NOT FOUND:")
    print(FACE_IMAGE)

else:

    print()
    print("PASSPORT FACE:")
    print(PASSPORT_IMAGE)

    print()
    print("REFERENCE FACE:")
    print(FACE_IMAGE)


    
    # Detect face A
    

    face_a = detect_face_from_path(
        PASSPORT_IMAGE
    )


    
    # Detect face B
    

    face_b = detect_face_from_path(
        FACE_IMAGE
    )


    passport_face_detected = (
        face_a is not None
    )

    reference_face_detected = (
        face_b is not None
    )


    print()
    print("PASSPORT FACE DETECTED:")
    print(passport_face_detected)

    print()
    print("REFERENCE FACE DETECTED:")
    print(reference_face_detected)


    
    # Both faces must exist
    

    face_detected = (
        passport_face_detected
        and reference_face_detected
    )


    if face_detected:

        
        # Generate embedding A
        

        print()
        print("GENERATING PASSPORT FACE EMBEDDING...")

        embedding_a = generate_face_embedding(
            PASSPORT_IMAGE
        )


        
        # Generate embedding B
        

        print()
        print("GENERATING REFERENCE FACE EMBEDDING...")

        embedding_b = generate_face_embedding(
            FACE_IMAGE
        )


        if (
            embedding_a is not None
            and embedding_b is not None
        ):

            print()
            print("EMBEDDING A:")
            print(embedding_a.shape)

            print()
            print("EMBEDDING B:")
            print(embedding_b.shape)


            
            # Actual face verification
            

            face_result = verify_faces(
                embedding_a,
                embedding_b
            )


            face_similarity = float(
                face_result["similarity"]
            )

            face_match = bool(
                face_result["match"]
            )


            print()
            print("FACE SIMILARITY:")
            print(face_similarity)


            print()
            print("PHOTO MATCH:")
            print(
                f"{face_similarity * 100:.2f}%"
            )


            print()
            print("FACE THRESHOLD:")
            print(
                face_result["threshold"]
            )


            print()
            print("FACE MATCH:")
            print(face_match)


        else:

            print()
            print("FACE EMBEDDING FAILED.")



# 6. FORENSICS

#
# Forensics module has not been implemented yet.
#
# We temporarily keep it outside the risk calculation.
#


print()
print("=" * 60)
print("6. FORENSICS")
print("=" * 60)

print()
print("FORENSICS:")
print("NOT IMPLEMENTED YET")



# 7. RISK ENGINE


print()
print("=" * 60)
print("7. RISK ENGINE")
print("=" * 60)


risk_result = calculate_risk(

    ocr_success=ocr_success,

    mrz_valid=mrz_valid,

    passport_valid=passport_valid,

    face_detected=face_detected,

    face_match=face_match,

    face_similarity=face_similarity,

    database_match=database_match,

    # Temporary:
    # forensics is not implemented yet.
    forensics_valid=True
)



# MATCH DETAILS


print()
print("=" * 60)
print("MATCH DETAILS")
print("=" * 60)

details = risk_result[
    "match_details"
]


print()
print(
    f"OCR:        {details['ocr']:.2f}%"
)

print(
    f"MRZ:        {details['mrz']:.2f}%"
)

print(
    f"PASSPORT:   {details['passport']:.2f}%"
)

print(
    f"PHOTO:      {details['photo']:.2f}%"
)

print(
    f"DATABASE:   {details['database']:.2f}%"
)

print(
    "FORENSICS:  N/A"
)



# OVERALL MATCH


print()
print("-" * 60)

print(
    "OVERALL MATCH:",
    f"{risk_result['overall_match_percentage']:.2f}%"
)



# RISK RESULT


print()
print("=" * 60)
print("FINAL RISK RESULT")
print("=" * 60)

print()
print(
    "RISK SCORE:",
    risk_result["risk_score"]
)

print()
print(
    "RISK LEVEL:",
    risk_result["risk_level"]
)

print()
print(
    "DECISION:",
    risk_result["decision"]
)



# REASONS


print()
print("RISK REASONS")
print("-" * 60)

if risk_result["reasons"]:

    for reason in risk_result["reasons"]:

        print("-", reason)

else:

    print("No risk factors detected.")



# FINAL


print()
print("=" * 60)
print("FINAL DOCUMENT VERIFICATION")
print("=" * 60)

if risk_result["decision"] == "VERIFIED":

    print()
    print("DOCUMENT VERIFIED: TRUE")

elif risk_result["decision"] == "REVIEW":

    print()
    print("DOCUMENT VERIFIED: REVIEW REQUIRED")

else:

    print()
    print("DOCUMENT VERIFIED: FALSE")

print()
print("=" * 60)