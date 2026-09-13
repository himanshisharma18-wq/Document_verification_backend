FACE_HIGH_THRESHOLD = 0.80
FACE_MEDIUM_THRESHOLD = 0.60

LOW_RISK_MAX = 20
MEDIUM_RISK_MAX = 50



# RISK ENGINE


def calculate_risk(
    ocr_success: bool,
    mrz_valid: bool,
    passport_valid: bool,
    face_detected: bool,
    face_match: bool,
    face_similarity: float | None,
    database_match: bool,
    forensics_valid: bool | None = None
) -> dict:

    risk_score = 0

    reasons = []


    
    # 1. OCR
    

    if not ocr_success:

        risk_score += 20

        reasons.append(
            "OCR failed"
        )


    
    # 2. MRZ
    

    if not mrz_valid:

        risk_score += 25

        reasons.append(
            "MRZ validation failed"
        )


    
    # 3. PASSPORT VALIDATION
    

    if not passport_valid:

        risk_score += 25

        reasons.append(
            "Passport validation failed"
        )


    
    # 4. FACE DETECTION
    

    if not face_detected:

        risk_score += 25

        reasons.append(
            "Face could not be detected in one or both images"
        )


    
    # 5. FACE SIMILARITY
    

    if face_similarity is None:

        face_match_percentage = 0.0

        risk_score += 40

        reasons.append(
            "Face similarity could not be calculated"
        )

    else:

        face_similarity = max(
            0.0,
            min(
                1.0,
                float(face_similarity)
            )
        )

        face_match_percentage = round(
            face_similarity * 100,
            2
        )


        
        # VERY LOW SIMILARITY
        

        if face_similarity < FACE_MEDIUM_THRESHOLD:

            risk_score += 40

            reasons.append(
                f"Low facial similarity ({face_match_percentage}%)"
            )


        
        # MEDIUM SIMILARITY
        

        elif face_similarity < FACE_HIGH_THRESHOLD:

            risk_score += 20

            reasons.append(
                f"Moderate facial similarity ({face_match_percentage}%)"
            )


        
        # HIGH SIMILARITY
        

        else:

            # No risk points.
            pass


    
    # 6. FACE MATCH RESULT
    

    if face_detected and not face_match:

        # Only add this if it wasn't already strongly
        # penalized by very low similarity.

        if face_similarity is not None:

            if face_similarity >= FACE_MEDIUM_THRESHOLD:

                risk_score += 20

                reasons.append(
                    "Face verification failed"
                )


    
    # 7. DATABASE
    

    if not database_match:

        risk_score += 30

        reasons.append(
            "Passport data does not match the demo database"
        )


    
    # 8. FORENSICS
    
    #
    # None = NOT IMPLEMENTED / NOT AVAILABLE
    #
    # False = ACTUAL FORENSICS FAILURE
    #
    # True = FORENSICS PASSED
    #
    

    if forensics_valid is False:

        risk_score += 20

        reasons.append(
            "Document forensics check failed"
        )


    
    # CAP RISK SCORE
    

    risk_score = min(
        risk_score,
        100
    )


    
    # RISK LEVEL
    

    if risk_score <= LOW_RISK_MAX:

        risk_level = "LOW"

    elif risk_score <= MEDIUM_RISK_MAX:

        risk_level = "MEDIUM"

    else:

        risk_level = "HIGH"


    
    # FINAL DECISION
    

    if risk_level == "LOW":

        decision = "VERIFIED"

    elif risk_level == "MEDIUM":

        decision = "REVIEW"

    else:

        decision = "REJECT STILL MANUAL RIVEW RIQURED"


    
    # MATCH DETAILS
    

    ocr_percentage = (
        100
        if ocr_success
        else 0
    )


    mrz_percentage = (
        100
        if mrz_valid
        else 0
    )


    passport_percentage = (
        100
        if passport_valid
        else 0
    )


    database_percentage = (
        100
        if database_match
        else 0
    )


    
    # Forensics percentage
    

    if forensics_valid is None:

        forensics_percentage = None

    elif forensics_valid:

        forensics_percentage = 100

    else:

        forensics_percentage = 0


    
    # OVERALL MATCH
    
    #
    # Only include checks that were actually performed.
    #
    

    checks = [

        ocr_percentage,

        mrz_percentage,

        passport_percentage,

        face_match_percentage,

        database_percentage

    ]


    if forensics_percentage is not None:

        checks.append(
            forensics_percentage
        )


    overall_match_percentage = round(
        sum(checks) / len(checks),
        2
    )


    
    # RESULT
    

    return {

        "risk_score":
            risk_score,

        "risk_level":
            risk_level,

        "decision":
            decision,

        "overall_match_percentage":
            overall_match_percentage,

        "match_details": {

            "ocr":
                ocr_percentage,

            "mrz":
                mrz_percentage,

            "passport":
                passport_percentage,

            "photo":
                face_match_percentage,

            "database":
                database_percentage,

            "forensics":
                forensics_percentage
        },

        "reasons":
            reasons
    }