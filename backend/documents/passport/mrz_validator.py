
import re



# ICAO MRZ CHECK DIGIT


MRZ_WEIGHTS = [7, 3, 1]


def character_value(char: str) -> int:
    """
    ICAO 9303 character values:

    0-9 -> 0-9
    A-Z -> 10-35
    <   -> 0
    """

    if char == "<":
        return 0

    if "0" <= char <= "9":
        return int(char)

    if "A" <= char <= "Z":
        return ord(char) - ord("A") + 10

    raise ValueError(
        f"Invalid MRZ character: {char}"
    )


def calculate_check_digit(data: str) -> str:
    """
    Calculate an ICAO MRZ check digit.

    Weights repeat:

        7, 3, 1, 7, 3, 1, ...
    """

    total = 0

    for index, char in enumerate(data):

        value = character_value(char)

        weight = MRZ_WEIGHTS[
            index % 3
        ]

        total += value * weight

    return str(total % 10)


def validate_check_digit(
    data: str,
    check_digit: str
) -> bool:
    """
    Validate one MRZ check digit.
    """

    if len(check_digit) != 1:
        return False

    if not check_digit.isdigit():
        return False

    calculated = calculate_check_digit(
        data
    )

    return calculated == check_digit



# MRZ NORMALIZATION


def normalize_mrz_line(
    line: str
) -> str:
    """
    Normalize an OCR-generated MRZ line.

    Allowed characters:

        A-Z
        0-9
        <
    """

    line = line.upper()

    # Remove spaces
    line = line.replace(
        " ",
        ""
    )

    # Remove invalid OCR characters
    line = re.sub(
        r"[^A-Z0-9<]",
        "",
        line
    )

    return line


def normalize_mrz_lines(
    lines: list[str]
) -> list[str]:

    return [
        normalize_mrz_line(line)
        for line in lines
    ]



# TD3 STRUCTURE VALIDATION


def validate_td3_structure(
    line1: str,
    line2: str
) -> tuple[bool, str]:
    """
    Validate the basic ICAO TD3 passport structure.

    TD3:

        Line 1 = 44 characters
        Line 2 = 44 characters
    """

    
    # Length
    

    if len(line1) != 44:

        return (
            False,
            "MRZ line 1 must contain exactly 44 characters"
        )

    if len(line2) != 44:

        return (
            False,
            "MRZ line 2 must contain exactly 44 characters"
        )

    
    # Allowed characters
    

    if not re.fullmatch(
        r"[A-Z0-9<]{44}",
        line1
    ):

        return (
            False,
            "Invalid characters in MRZ line 1"
        )

    if not re.fullmatch(
        r"[A-Z0-9<]{44}",
        line2
    ):

        return (
            False,
            "Invalid characters in MRZ line 2"
        )

    
    # Document type
    

    if line1[0] != "P":

        return (
            False,
            "Invalid passport document type"
        )

    
    # Document subtype
    

    if not (
        line1[1].isalpha()
        or line1[1] == "<"
    ):

        return (
            False,
            "Invalid passport document subtype"
        )

    
    # Issuing state
    

    issuing_state = line1[2:5]

    if not re.fullmatch(
        r"[A-Z<]{3}",
        issuing_state
    ):

        return (
            False,
            "Invalid issuing state code"
        )

    
    # Nationality
    

    nationality = line2[10:13]

    if not re.fullmatch(
        r"[A-Z<]{3}",
        nationality
    ):

        return (
            False,
            "Invalid nationality code"
        )

    
    # Sex
    

    sex = line2[20]

    if sex not in {
        "M",
        "F",
        "<"
    }:

        return (
            False,
            "Invalid sex field"
        )

    return (
        True,
        "TD3 structure is valid"
    )



# TD3 CHECK DIGITS


def validate_td3_check_digits(
    line2: str
) -> dict:
    """
    Validate all TD3 MRZ check digits.

    TD3 line 2 layout:

        0-8    Passport number
        9      Passport number check digit

        10-12  Nationality

        13-18  Date of birth
        19     DOB check digit

        20     Sex

        21-26  Expiry date
        27     Expiry check digit

        28-42  Optional data
        43     Composite check digit
    """

    if len(line2) != 44:

        return {
            "passport_number": False,
            "date_of_birth": False,
            "expiry_date": False,
            "composite": False,
            "all_valid": False
        }

    
    # Passport number
    

    passport_number = line2[0:9]

    passport_check_digit = line2[9]

    passport_valid = validate_check_digit(
        passport_number,
        passport_check_digit
    )

    
    # Date of birth
    

    date_of_birth = line2[13:19]

    dob_check_digit = line2[19]

    dob_valid = validate_check_digit(
        date_of_birth,
        dob_check_digit
    )

    
    # Expiry date
    

    expiry_date = line2[21:27]

    expiry_check_digit = line2[27]

    expiry_valid = validate_check_digit(
        expiry_date,
        expiry_check_digit
    )

    
    # Composite check digit
    

    composite_data = (
        line2[0:10]
        + line2[13:20]
        + line2[21:43]
    )

    composite_check_digit = line2[43]

    composite_valid = validate_check_digit(
        composite_data,
        composite_check_digit
    )

    
    # Final result
    

    all_valid = (
        passport_valid
        and dob_valid
        and expiry_valid
        and composite_valid
    )

    return {
        "passport_number": passport_valid,
        "date_of_birth": dob_valid,
        "expiry_date": expiry_valid,
        "composite": composite_valid,
        "all_valid": all_valid
    }



# COMPLETE MRZ VALIDATION


def validate_mrz(
    line1: str,
    line2: str
) -> dict:
    """
    Complete TD3 MRZ validation.

    Flow:

        Normalize
           ↓
        Structure
           ↓
        Check digits
           ↓
        Final result
    """

    line1 = normalize_mrz_line(
        line1
    )

    line2 = normalize_mrz_line(
        line2
    )

    
    # Structure validation
    

    structure_valid, structure_message = (
        validate_td3_structure(
            line1,
            line2
        )
    )

    if not structure_valid:

        return {
            "valid": False,
            "structure_valid": False,
            "message": structure_message,
            "check_digits": {}
        }

    
    # Check-digit validation
    

    check_digits = validate_td3_check_digits(
        line2
    )

    
    # Final result
    

    if check_digits["all_valid"]:

        message = "MRZ is valid"

    else:

        message = (
            "One or more MRZ check digits are invalid"
        )

    return {
        "valid": check_digits["all_valid"],
        "structure_valid": True,
        "message": message,
        "check_digits": check_digits
    }