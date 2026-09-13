import re
from datetime import date



# COUNTRY CODE


def validate_country_code(country_code: str) -> bool:
    """
    Validate 3-letter ICAO country code.

    Example:
        IND
        USA
        GBR
    """

    if not country_code:
        return False

    return bool(
        re.fullmatch(
            r"[A-Z]{3}",
            country_code
        )
    )



# PASSPORT NUMBER


def validate_passport_number(
    passport_number: str
) -> bool:
    """
    TD3 passport number = exactly 9 MRZ characters.

    Allowed:
        A-Z
        0-9
        <
    """

    if not passport_number:
        return False

    return bool(
        re.fullmatch(
            r"[A-Z0-9<]{9}",
            passport_number
        )
    )



# MRZ DATE PARSING


def parse_mrz_date(
    value: str,
    date_type: str = "general"
):
    """
    Convert YYMMDD MRZ date to Python date.

    For DOB:
        Date must be in the past.

    For expiry:
        We use a rolling 100-year interpretation.
    """

    if not value:
        return None

    if not re.fullmatch(
        r"\d{6}",
        value
    ):
        return None

    try:

        yy = int(value[0:2])
        mm = int(value[2:4])
        dd = int(value[4:6])

    except ValueError:

        return None

    today = date.today()

    current_year = today.year

    current_yy = current_year % 100

    
    # MRZ two-digit year interpretation
    

    if date_type == "expiry":

        # Expiry dates are normally interpreted as
        # the nearest sensible future/past year.
        #
        # Example:
        #
        # 37 -> 2037
        #
        # 30 -> 2030
        #
        # 99 -> 2099 if appropriate.
        #
        # For current passport data this gives the
        # expected 2037 for 370617.

        century = (
            current_year // 100
        ) * 100

        full_year = century + yy

        # If date would be more than 80 years in the past,
        # treat it as next century.
        if full_year < current_year - 20:
            full_year += 100

    else:

        # DOB normally belongs to the current or previous
        # century.

        century = (
            current_year // 100
        ) * 100

        full_year = century + yy

        # Future DOB -> previous century.
        if full_year > current_year:
            full_year -= 100

    try:

        return date(
            full_year,
            mm,
            dd
        )

    except ValueError:

        return None



# GENERIC DATE VALIDATION


def validate_date(
    value: str
) -> bool:

    return (
        parse_mrz_date(value)
        is not None
    )



# DATE OF BIRTH


def validate_date_of_birth(
    date_of_birth: str
) -> tuple[bool, str]:

    dob = parse_mrz_date(
        date_of_birth,
        "dob"
    )

    if dob is None:

        return (
            False,
            "Invalid date of birth"
        )

    today = date.today()

    if dob > today:

        return (
            False,
            "Date of birth cannot be in the future"
        )

    age = (
        today.year
        - dob.year
    )

    if (
        today.month,
        today.day
    ) < (
        dob.month,
        dob.day
    ):
        age -= 1

    if age > 120:

        return (
            False,
            "Invalid date of birth"
        )

    return True, ""



# EXPIRY DATE


def validate_expiry_date(
    expiry_date: str
) -> tuple[bool, str]:

    expiry = parse_mrz_date(
        expiry_date,
        "expiry"
    )

    if expiry is None:

        return (
            False,
            "Invalid expiry date"
        )

    return True, ""



# EXPIRY STATUS


def get_expiry_status(
    expiry_date: str
) -> str:

    expiry = parse_mrz_date(
        expiry_date,
        "expiry"
    )

    if expiry is None:

        return "invalid"

    today = date.today()

    if expiry < today:

        return "expired"

    if expiry == today:

        return "expires_today"

    return "valid"



# SEX


def validate_sex(
    sex: str
) -> bool:

    return sex in {
        "M",
        "F",
        "<"
    }



# NAME


def validate_name_field(
    name: str
) -> bool:
    """
    Validate CLEANED passport names.

    Parser output:

        GUPTA

        UNESH KUMAR

    is valid.

    We also allow '<' because this function can
    receive raw MRZ name fields.
    """

    if not name:
        return False

    name = name.upper().strip()

    return bool(
        re.fullmatch(
            r"[A-Z< ]+",
            name
        )
    )



# DOCUMENT TYPE


def validate_document_type(
    document_type: str
) -> bool:
    """
    MRZ parser gives:

        P

    Therefore accept P directly.

    We also support P< in case another part of
    the application passes the complete TD3 prefix.
    """

    if not document_type:
        return False

    # Parser output
    if document_type == "P":
        return True

    # Full MRZ document code
    if document_type == "P<":
        return True

    return False



# COMPLETE PASSPORT VALIDATION


def validate_passport_data(
    data: dict
) -> dict:

    errors = []

    
    # Extract fields
    

    passport_number = data.get(
        "passport_number",
        ""
    )

    nationality = data.get(
        "nationality",
        ""
    )

    issuing_country = data.get(
        "issuing_country",
        ""
    )

    date_of_birth = data.get(
        "date_of_birth",
        ""
    )

    # IMPORTANT:
    #
    # mrz_parser.py returns:
    #
    # date_of_expiry
    #
    # not expiry_date.

    expiry_date = data.get(
        "date_of_expiry",
        data.get(
            "expiry_date",
            ""
        )
    )

    sex = data.get(
        "sex",
        ""
    )

    surname = data.get(
        "surname",
        ""
    )

    given_names = data.get(
        "given_names",
        ""
    )

    document_type = data.get(
        "document_type",
        ""
    )

    
    # DOCUMENT TYPE
    

    if not validate_document_type(
        document_type
    ):

        errors.append(
            "Invalid document type"
        )

    
    # PASSPORT NUMBER
    

    if not validate_passport_number(
        passport_number
    ):

        errors.append(
            "Invalid passport number"
        )

    
    # NATIONALITY
    

    if not validate_country_code(
        nationality
    ):

        errors.append(
            "Invalid nationality code"
        )

    
    # ISSUING COUNTRY
    

    if not validate_country_code(
        issuing_country
    ):

        errors.append(
            "Invalid issuing country code"
        )

    
    # SURNAME
    

    if not validate_name_field(
        surname
    ):

        errors.append(
            "Invalid surname"
        )

    
    # GIVEN NAMES
    

    if not validate_name_field(
        given_names
    ):

        errors.append(
            "Invalid given name"
        )

    
    # DATE OF BIRTH
    

    dob_valid, dob_error = (
        validate_date_of_birth(
            date_of_birth
        )
    )

    if not dob_valid:

        errors.append(
            dob_error
        )

    
    # EXPIRY DATE
    

    expiry_valid, expiry_error = (
        validate_expiry_date(
            expiry_date
        )
    )

    if not expiry_valid:

        errors.append(
            expiry_error
        )

    
    # EXPIRY STATUS
    

    expiry_status = get_expiry_status(
        expiry_date
    )

    if expiry_status == "expired":

        errors.append(
            "Passport has expired"
        )

    
    # SEX
    

    if not validate_sex(sex):

        errors.append(
            "Invalid sex field"
        )

    
    # FINAL RESULT
    

    return {

        "valid":
            len(errors) == 0,

        "errors":
            errors,

        "expiry_status":
            expiry_status,

        "data": {

            "document_type":
                document_type,

            "issuing_country":
                issuing_country,

            "surname":
                surname,

            "given_names":
                given_names,

            "passport_number":
                passport_number,

            "nationality":
                nationality,

            "date_of_birth":
                date_of_birth,

            "sex":
                sex,

            "date_of_expiry":
                expiry_date
        }
    }