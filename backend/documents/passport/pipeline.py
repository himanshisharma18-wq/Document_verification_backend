from .extractor import extract_mrz

from .correct_mrz import correct_td3_mrz

from .mrz_validator import (
    validate_mrz,
    normalize_mrz_line
)

from .validator import (
    validate_passport_data
)



# TD3 MRZ PARSER


def parse_td3_mrz(
    line1: str,
    line2: str
) -> dict:
    """
    Parse a valid ICAO TD3 passport MRZ.
    """

    line1 = normalize_mrz_line(line1)
    line2 = normalize_mrz_line(line2)

   
    # LINE 1
   

    document_type = line1[0:2]

    issuing_country = line1[2:5]

    name_field = line1[5:44]

    # Name format:
    #
    # SURNAME<<GIVEN<NAMES
    #

    name_parts = name_field.split(
        "<<",
        1
    )

    surname = (
        name_parts[0]
        .replace("<", " ")
        .strip()
    )

    given_names = ""

    if len(name_parts) > 1:

        given_names = (
            name_parts[1]
            .replace("<", " ")
            .strip()
        )

   
    # LINE 2
   

    passport_number = line2[0:9]

    passport_number = passport_number.replace(
        "<",
        ""
    )

    nationality = line2[10:13]

    date_of_birth = line2[13:19]

    sex = line2[20]

    expiry_date = line2[21:27]

    optional_data = line2[28:43]

   
    # RETURN STRUCTURED DATA
   

    return {
        "document_type": document_type,
        "issuing_country": issuing_country,
        "surname": surname,
        "given_names": given_names,
        "names": name_field,
        "passport_number": passport_number,
        "nationality": nationality,
        "date_of_birth": date_of_birth,
        "sex": sex,
        "expiry_date": expiry_date,
        "optional_data": optional_data
    }



# PASSPORT PIPELINE


def process_passport(
    image_path: str
) -> dict:
    """
    Complete passport processing pipeline.

    Image
      ↓
    MRZ extraction
      ↓
    OCR correction
      ↓
    MRZ validation
      ↓
    MRZ parsing
      ↓
    Passport field validation
      ↓
    Final result
    """

   
    # STEP 1: Extract MRZ
   

    extraction_result = extract_mrz(
        image_path
    )

    if not extraction_result["success"]:

        return {
            "success": False,
            "stage": "extraction",
            "message": "Could not detect two MRZ lines",
            "mrz_lines": extraction_result["mrz_lines"]
        }

    line1, line2 = extraction_result[
        "mrz_lines"
    ]

   
    # STEP 2: Correct line ordering
   

    # TD3 passport MRZ line 1 starts with P.

    if (
        not line1.startswith("P")
        and line2.startswith("P")
    ):

        line1, line2 = line2, line1

   
    # STEP 3: OCR correction
   

    line1, line2 = correct_td3_mrz(
        line1,
        line2
    )

   
    # STEP 4: Validate MRZ
   

    mrz_validation = validate_mrz(
        line1,
        line2
    )

    if not mrz_validation["valid"]:

        return {
            "success": False,
            "stage": "mrz_validation",
            "mrz_lines": [
                line1,
                line2
            ],
            "mrz_validation": mrz_validation
        }

   
    # STEP 5: Parse passport data
   

    passport_data = parse_td3_mrz(
        line1,
        line2
    )

   
    # STEP 6: Validate passport fields
   

    passport_validation = validate_passport_data(
        passport_data
    )

   
    # FINAL RESULT
   

    return {
        "success": passport_validation["valid"],
        "stage": "completed",

        "mrz_lines": [
            line1,
            line2
        ],

        "passport_data": passport_data,

        "mrz_validation": mrz_validation,

        "passport_validation": passport_validation
    }