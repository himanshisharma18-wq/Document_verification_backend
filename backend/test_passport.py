from backend.ocr.ocr_engine import extract_mrz
from backend.mrz.mrz_parser import parse_mrz
from backend.documents.passport.validator import validate_passport_data


def main():

    print()
    print("=" * 40)
    print("PASSPORT OCR")
    print("=" * 40)

    
    # OCR
    

    mrz_result = extract_mrz(
        "passport.jpeg"
    )

    print()
    print("FINAL MRZ LINES:")
    print("-" * 40)

    for line in mrz_result["mrz_lines"]:
        print(line)

    print("-" * 40)

    print()
    print("OCR SUCCESS:")
    print(mrz_result["success"])

    
    # OCR failed
    

    if not mrz_result["success"]:

        print()
        print("OCR failed.")
        return

    
    # MRZ PARSER
    

    print()
    print("=" * 40)
    print("MRZ PARSER")
    print("=" * 40)

    parsed = parse_mrz(
        mrz_result["mrz_lines"]
    )

    print()
    print("MRZ VALID:")
    print(parsed["mrz_valid"])

    
    # Parser failed
    

    if not parsed["success"]:

        print()
        print("MRZ ERROR:")
        print(parsed["error"])

        return

    
    # Passport data
    

    data = parsed["data"]

    print()
    print("PASSPORT DATA:")
    print("-" * 40)

    print(
        "Document Type:",
        data["document_type"]
    )

    print(
        "Issuing Country:",
        data["issuing_country"]
    )

    print(
        "Surname:",
        data["surname"]
    )

    print(
        "Given Names:",
        data["given_names"]
    )

    print(
        "Passport Number:",
        data["passport_number"]
    )

    print(
        "Nationality:",
        data["nationality"]
    )

    print(
        "Date of Birth:",
        data["date_of_birth"]
    )

    print(
        "Sex:",
        data["sex"]
    )

    print(
        "Date of Expiry:",
        data["date_of_expiry"]
    )

    
    # PASSPORT VALIDATOR
    

    print()
    print("=" * 40)
    print("PASSPORT VALIDATOR")
    print("=" * 40)

    validation = validate_passport_data(
        data
    )

    print()
    print("PASSPORT VALID:")
    print(validation["valid"])

    print()
    print("EXPIRY STATUS:")
    print(validation["expiry_status"])

    
    # Validation errors
    

    if validation["errors"]:

        print()
        print("VALIDATION ERRORS:")
        print("-" * 40)

        for error in validation["errors"]:
            print("-", error)

    else:

        print()
        print("NO PASSPORT VALIDATION ERRORS.")

    
    # FINAL RESULT
    

    final_valid = (
        parsed["mrz_valid"]
        and validation["valid"]
    )

    print()
    print("=" * 40)
    print("FINAL PASSPORT RESULT")
    print("=" * 40)

    print()
    print("FINAL VALID:")
    print(final_valid)


if __name__ == "__main__":
    main()