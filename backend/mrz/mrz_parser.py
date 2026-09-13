import re



# MRZ CONSTANTS


LINE_1_LENGTH = 44

# Your current passport OCR output uses 42 characters
# for line 2.
LINE_2_LENGTH = 42

WEIGHTS = [7, 3, 1]



# NORMALIZE MRZ LINE


def normalize_mrz_line(line: str) -> str:
    """
    Normalize one OCR-generated MRZ line.

    Allowed MRZ characters:

        A-Z
        0-9
        <

    Spaces are removed.
    """

    line = str(line).upper()

    # Remove spaces
    line = line.replace(" ", "")

    # Keep only valid MRZ characters
    line = re.sub(
        r"[^A-Z0-9<]",
        "",
        line
    )

    return line



# PREPARE MRZ LINES


def prepare_mrz_lines(mrz_lines: list[str]) -> list[str]:
    """
    Normalize OCR MRZ lines.

    Empty lines are removed.
    """

    lines = []

    for line in mrz_lines:

        normalized = normalize_mrz_line(line)

        if normalized:
            lines.append(normalized)

    return lines



# ICAO CHECK DIGIT


def calculate_check_digit(value: str) -> str:
    """
    ICAO 9303 MRZ check digit calculation.

    Character values:

        0-9 -> 0-9
        A-Z -> 10-35
        <   -> 0

    Repeating weights:

        7, 3, 1
    """

    total = 0

    for index, char in enumerate(value):

        # Filler
        if char == "<":

            char_value = 0

        # Number
        elif "0" <= char <= "9":

            char_value = int(char)

        # Letter
        elif "A" <= char <= "Z":

            char_value = (
                ord(char) - ord("A") + 10
            )

        else:

            raise ValueError(
                f"Invalid MRZ character: {char}"
            )

        weight = WEIGHTS[index % 3]

        total += char_value * weight

    return str(total % 10)



# CHECK DIGIT RESULT


def check_digit_result(
    value: str,
    expected: str
) -> dict:
    """
    Return detailed check digit information.
    """

    calculated = calculate_check_digit(value)

    return {
        "value": value,
        "expected": expected,
        "calculated": calculated,
        "valid": calculated == expected
    }



# PARSE NAME


def parse_name(field: str) -> dict:
    """
    Parse passport name field.

    Standard format:

        SURNAME<<GIVEN<NAMES<<<<<<<<

    Example:

        GUPTA<<UNESH<KUMAR<<<<<<<<

    becomes:

        surname:
            GUPTA

        given_names:
            UNESH KUMAR

    IMPORTANT:
    Some OCR engines can incorrectly append a numeric
    character from the end of the MRZ line to the name.

    Example:

        UNESH<KUMAR<<<<<<<<<<<<<<<<<<<<8

    The trailing 8 is treated as OCR noise and removed.
    """

    field = field.upper()

    
    # Remove trailing numeric OCR noise
    #
    # Example:
    #
    # UNESH<KUMAR<<<<<<<<<<<<<<<<<<<<8
    #
    # becomes:
    #
    # UNESH<KUMAR<<<<<<<<<<<<<<<<<<<<
    

    field = re.sub(
        r"\d+$",
        "",
        field
    )

    
    # Split surname and given names
    

    parts = field.split("<<", 1)

    
    # Surname
    

    surname = parts[0]

    surname = surname.replace(
        "<",
        " "
    )

    surname = surname.strip()

    
    # Given names
    

    given_names = ""

    if len(parts) > 1:

        given_names = parts[1]

        given_names = given_names.replace(
            "<",
            " "
        )

        # Remove repeated spaces
        given_names = re.sub(
            r"\s+",
            " ",
            given_names
        )

        given_names = given_names.strip()

    return {
        "surname": surname,
        "given_names": given_names
    }



# PARSE LINE 1


def parse_line_1(line1: str) -> dict:
    """
    Parse passport MRZ line 1.

    TD3 structure:

        Position 0:
            Document type

        Position 1:
            Document code

        Position 2-4:
            Issuing country

        Position 5-43:
            Name
    """

    
    # Length
    

    if len(line1) != LINE_1_LENGTH:

        raise ValueError(
            f"MRZ line 1 has {len(line1)} "
            f"characters instead of 44."
        )

    
    # Document type
    

    if not line1.startswith("P"):

        raise ValueError(
            "MRZ line 1 must start with P."
        )

    
    # Fixed fields
    

    document_type = line1[0]

    document_code = line1[1]

    issuing_country = line1[2:5]

    
    # Name field
    #
    # Positions 5-43
    

    name_field = line1[5:44]

    name = parse_name(
        name_field
    )

    return {

        "document_type":
            document_type,

        "document_code":
            document_code,

        "issuing_country":
            issuing_country,

        "surname":
            name["surname"],

        "given_names":
            name["given_names"]
    }



# PARSE LINE 2


def parse_line_2(line2: str) -> dict:
    """
    Parse the current 42-character OCR representation.

    Example:

        G2762794<5IND7604234M3706170<<<<<<<<<<<<<2

    Fields used by this project:

        0-8
            Passport number

        9
            Passport number check digit

        10-12
            Nationality

        13-18
            Date of birth

        19
            DOB check digit

        20
            Sex

        21-26
            Date of expiry

        27
            Expiry check digit

        28-(last-1)
            Optional data

        last
            Overall check digit
    """

    
    # Length
    

    if len(line2) != LINE_2_LENGTH:

        raise ValueError(
            f"MRZ line 2 has {len(line2)} "
            f"characters instead of 42."
        )

    
    # Passport number
    

    passport_number = line2[0:9]

    passport_number_check_digit = line2[9]

    
    # Nationality
    

    nationality = line2[10:13]

    
    # Date of birth
    

    date_of_birth = line2[13:19]

    date_of_birth_check_digit = line2[19]

    
    # Sex
    

    sex = line2[20]

    
    # Expiry
    

    date_of_expiry = line2[21:27]

    date_of_expiry_check_digit = line2[27]

    
    # Optional data
    

    optional_data = line2[28:-1]

    
    # Overall check digit
    

    overall_check_digit = line2[-1]

    return {

        "passport_number":
            passport_number,

        "passport_number_check_digit":
            passport_number_check_digit,

        "nationality":
            nationality,

        "date_of_birth":
            date_of_birth,

        "date_of_birth_check_digit":
            date_of_birth_check_digit,

        "sex":
            sex,

        "date_of_expiry":
            date_of_expiry,

        "date_of_expiry_check_digit":
            date_of_expiry_check_digit,

        "optional_data":
            optional_data,

        "overall_check_digit":
            overall_check_digit
    }



# VALIDATE LINE 2


def validate_line_2(line2: str) -> dict:
    """
    Validate the check digits supported by the
    current 42-character representation.

    VALIDATED:

        Passport number
        Date of birth

    REPORTED ONLY:

        Date of expiry

        Overall check digit

    The expiry and overall values are still returned,
    but they do not determine mrz_valid for this
    non-standard 42-character representation.
    """

    parsed = parse_line_2(
        line2
    )

   
    # PASSPORT NUMBER
   

    passport_value = parsed[
        "passport_number"
    ]

    passport_expected = parsed[
        "passport_number_check_digit"
    ]

    passport_result = check_digit_result(
        passport_value,
        passport_expected
    )


   
    # DATE OF BIRTH
   

    dob_value = parsed[
        "date_of_birth"
    ]

    dob_expected = parsed[
        "date_of_birth_check_digit"
    ]

    dob_result = check_digit_result(
        dob_value,
        dob_expected
    )


   
    # DATE OF EXPIRY
   

    expiry_value = parsed[
        "date_of_expiry"
    ]

    expiry_expected = parsed[
        "date_of_expiry_check_digit"
    ]

    expiry_calculated = calculate_check_digit(
        expiry_value
    )

    # IMPORTANT:
    #
    # We calculate it for diagnostics,
    # but we do NOT use it to reject the
    # current 42-character representation.

    expiry_result = {

        "value":
            expiry_value,

        "expected":
            expiry_expected,

        "calculated":
            expiry_calculated,

        "valid":
            None,

        "status":
            "NOT_VALIDATED_FOR_42_CHARACTER_LINE"
    }


   
    # OVERALL CHECK DIGIT
   

    overall_result = {

        "value":
            None,

        "expected":
            parsed["overall_check_digit"],

        "calculated":
            None,

        "valid":
            None,

        "status":
            "NOT_VALIDATED_FOR_42_CHARACTER_LINE"
    }


   
    # RETURN
   

    return {

        "passport_number":
            passport_result,

        "date_of_birth":
            dob_result,

        "date_of_expiry":
            expiry_result,

        "overall":
            overall_result
    }



# PARSE COMPLETE MRZ


def parse_mrz(
    mrz_lines: list[str]
) -> dict:
    """
    Complete MRZ parser.

    Current project rules:

        Line 1 = 44 characters
        Line 2 = 42 characters

    Parsing and validation are separate.

    success:
        Parser successfully understood the MRZ.

    mrz_valid:
        All check digits that are supported by the
        current 42-character representation are valid.
    """

   
    # STEP 1
    # Normalize OCR lines
   

    lines = prepare_mrz_lines(
        mrz_lines
    )

   
    # STEP 2
    # Exactly two lines
   

    if len(lines) != 2:

        return {

            "success": False,

            "mrz_valid": False,

            "error":
                "MRZ must contain exactly two lines.",

            "data": None
        }

    line1 = lines[0]

    line2 = lines[1]

   
    # STEP 3
    # Validate line 1 length
   

    if len(line1) != 44:

        return {

            "success": False,

            "mrz_valid": False,

            "error":
                f"MRZ line 1 has {len(line1)} "
                f"characters instead of 44.",

            "data": None
        }

   
    # STEP 4
    # Validate line 2 length
   

    if len(line2) != 42:

        return {

            "success": False,

            "mrz_valid": False,

            "error":
                f"MRZ line 2 has {len(line2)} "
                f"characters instead of 42.",

            "data": None
        }

   
    # STEP 5
    # Validate passport document type
   

    if not line1.startswith("P"):

        return {

            "success": False,

            "mrz_valid": False,

            "error":
                "MRZ line 1 must start with P.",

            "data": None
        }

   
    # STEP 6
    # Parse lines
   

    try:

        first_line = parse_line_1(
            line1
        )

        second_line = parse_line_2(
            line2
        )

    except ValueError as error:

        return {

            "success": False,

            "mrz_valid": False,

            "error": str(error),

            "data": None
        }

   
    # STEP 7
    # Validate supported check digits
   

    checks = validate_line_2(
        line2
    )

   
    # STEP 8
    # Determine validity
    #
    # Only checks that are actually supported by
    # the 42-character representation are used.
   

    passport_valid = checks[
        "passport_number"
    ]["valid"]

    dob_valid = checks[
        "date_of_birth"
    ]["valid"]

    mrz_valid = (
        passport_valid
        and dob_valid
    )

   
    # STEP 9
    # Print diagnostics
   

    print()
    print("CHECK DIGIT RESULTS")
    print("----------------------------------------")

    print(
        "Passport number:",
        checks["passport_number"]
    )

    print(
        "Date of birth:",
        checks["date_of_birth"]
    )

    print(
        "Date of expiry:",
        checks["date_of_expiry"]
    )

    print(
        "Overall:",
        checks["overall"]
    )

   
    # STEP 10
    # Return final result
   

    return {

        "success": True,

        "mrz_valid": mrz_valid,

        "error":
            None
            if mrz_valid
            else
            "One or more validated MRZ check digits are invalid.",

        "data": {

            
            # LINE 1 DATA
            

            "document_type":
                first_line[
                    "document_type"
                ],

            "document_code":
                first_line[
                    "document_code"
                ],

            "issuing_country":
                first_line[
                    "issuing_country"
                ],

            "surname":
                first_line[
                    "surname"
                ],

            "given_names":
                first_line[
                    "given_names"
                ],


            
            # LINE 2 DATA
            

            "passport_number":
                second_line[
                    "passport_number"
                ],

            "nationality":
                second_line[
                    "nationality"
                ],

            "date_of_birth":
                second_line[
                    "date_of_birth"
                ],

            "sex":
                second_line[
                    "sex"
                ],

            "date_of_expiry":
                second_line[
                    "date_of_expiry"
                ],

            "optional_data":
                second_line[
                    "optional_data"
                ],


            
            # RAW MRZ
            

            "mrz_line_1":
                line1,

            "mrz_line_2":
                line2,


            
            # CHECK DIGITS
            

            "check_digits":
                checks
        }
    }