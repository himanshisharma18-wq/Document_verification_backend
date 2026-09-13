import re



# OCR CORRECTION TABLES


# Characters OCR commonly confuses with numbers.
OCR_TO_DIGIT = {
    "O": "0",
    "Q": "0",
    "D": "0",
    "I": "1",
    "L": "1",
    "Z": "2",
    "S": "5",
    "G": "6",
    "T": "7",
    "B": "8"
}


# Characters OCR commonly confuses with letters.
OCR_TO_LETTER = {
    "0": "O",
    "1": "I",
    "2": "Z",
    "5": "S",
    "6": "G",
    "8": "B"
}



# BASIC NORMALIZATION


def normalize_line(line: str) -> str:
    """
    Basic MRZ normalization.

    Keeps only:
        A-Z
        0-9
        <
    """

    line = line.upper()

    line = line.replace(
        " ",
        ""
    )

    line = re.sub(
        r"[^A-Z0-9<]",
        "",
        line
    )

    return line



# DIGIT FIELD CORRECTION


def correct_digit_field(
    value: str
) -> str:
    """
    Correct OCR mistakes in a field that should
    contain only digits.

    Example:

        9O0101
          ↓
        900101
    """

    corrected = []

    for char in value:

        if char in OCR_TO_DIGIT:
            corrected.append(
                OCR_TO_DIGIT[char]
            )

        else:
            corrected.append(
                char
            )

    return "".join(corrected)



# DATE CORRECTION


def correct_date_field(
    value: str
) -> str:
    """
    Correct an MRZ date field.

    Expected format:

        YYMMDD

    Exactly 6 characters.
    """

    if len(value) != 6:
        return value

    return correct_digit_field(
        value
    )



# CHECK DIGIT CORRECTION


def correct_check_digit(
    value: str
) -> str:
    """
    Correct a single MRZ check digit.

    Expected:
        0-9
    """

    if len(value) != 1:
        return value

    return correct_digit_field(
        value
    )



# PASSPORT NUMBER CORRECTION


def correct_passport_number(
    value: str
) -> str:
    """
    Passport number is an alphanumeric field.

    IMPORTANT:
    We do NOT convert every O/0 or I/1 here.

    Both letters and numbers can legitimately occur
    in a passport number.

    Therefore, only obvious invalid OCR characters
    are removed.
    """

    value = normalize_line(
        value
    )

    return value



# COUNTRY CODE CORRECTION


def correct_country_code(
    value: str
) -> str:
    """
    Country/nationality fields should contain
    three alphabetic characters.

    Here numeric-looking OCR characters can safely
    be interpreted as letters.
    """

    value = normalize_line(
        value
    )

    corrected = []

    for char in value:

        if char in OCR_TO_LETTER:
            corrected.append(
                OCR_TO_LETTER[char]
            )

        else:
            corrected.append(
                char
            )

    return "".join(corrected)



# SEX FIELD CORRECTION


def correct_sex(
    value: str
) -> str:
    """
    Correct the sex field.

    Valid ICAO values:

        M
        F
        <
    """

    if not value:
        return value

    value = value.upper()

    # Common OCR confusion.
    if value == "N":
        return "M"

    if value == "P":
        return "F"

    return value



# COMPLETE TD3 LINE 2 CORRECTION


def correct_td3_line2(
    line2: str
) -> str:
    """
    Apply field-specific OCR correction to TD3 line 2.

    TD3 line 2:

        0-8    Passport number
        9      Passport check digit
        10-12  Nationality
        13-18  Date of birth
        19     DOB check digit
        20     Sex
        21-26  Expiry date
        27     Expiry check digit
        28-42  Optional data
        43     Composite check digit
    """

    line2 = normalize_line(
        line2
    )

    # We need enough characters to address
    # the TD3 positions safely.
    if len(line2) < 44:
        return line2

    # --------------------------------------------------------
    # Passport number
    # --------------------------------------------------------

    passport_number = correct_passport_number(
        line2[0:9]
    )

    # --------------------------------------------------------
    # Passport number check digit
    # --------------------------------------------------------

    passport_check = correct_check_digit(
        line2[9]
    )

    # --------------------------------------------------------
    # Nationality
    # --------------------------------------------------------

    nationality = correct_country_code(
        line2[10:13]
    )

    # --------------------------------------------------------
    # Date of birth
    # --------------------------------------------------------

    date_of_birth = correct_date_field(
        line2[13:19]
    )

    # --------------------------------------------------------
    # DOB check digit
    # --------------------------------------------------------

    dob_check = correct_check_digit(
        line2[19]
    )

    # --------------------------------------------------------
    # Sex
    # --------------------------------------------------------

    sex = correct_sex(
        line2[20]
    )

    # --------------------------------------------------------
    # Expiry date
    # --------------------------------------------------------

    expiry_date = correct_date_field(
        line2[21:27]
    )

    # --------------------------------------------------------
    # Expiry check digit
    # --------------------------------------------------------

    expiry_check = correct_check_digit(
        line2[27]
    )

    # --------------------------------------------------------
    # Optional data
    # --------------------------------------------------------

    optional_data = line2[28:43]

    # --------------------------------------------------------
    # Composite check digit
    # --------------------------------------------------------

    composite_check = correct_check_digit(
        line2[43]
    )

    # --------------------------------------------------------
    # Reconstruct line
    # --------------------------------------------------------

    return (
        passport_number
        + passport_check
        + nationality
        + date_of_birth
        + dob_check
        + sex
        + expiry_date
        + expiry_check
        + optional_data
        + composite_check
    )



# COMPLETE TD3 CORRECTION


def correct_td3_mrz(
    line1: str,
    line2: str
) -> tuple[str, str]:
    """
    Correct OCR output for a TD3 passport MRZ.
    """

    line1 = normalize_line(
        line1
    )

    line2 = correct_td3_line2(
        line2
    )

    return line1, line2