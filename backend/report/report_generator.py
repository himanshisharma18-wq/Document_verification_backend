
# VERIFICATION REPORT GENERATOR


from datetime import datetime



# GENERATE VERIFICATION REPORT


def generate_verification_report(
    passport_data,
    ocr_success,
    mrz_valid,
    passport_valid,
    face_detected,
    face_match,
    face_similarity,
    database_match,
    forensics_result,
    risk_result
):

    
    # Face similarity
    

    if face_similarity is not None:
        photo_percentage = round(
            face_similarity * 100,
            2
        )
    else:
        photo_percentage = None


    
    # Match details from risk engine
    

    match_details = risk_result.get(
        "match_details",
        {}
    )


    
    # Forensics
    

    if forensics_result is None:

        forensics_available = False
        forensics_percentage = None

    else:

        forensics_available = forensics_result.get(
            "available",
            True
        )

        forensics_percentage = forensics_result.get(
            "percentage"
        )


    
    # FINAL REPORT
    

    report = {

        
        # Report information
        

        "report_info": {

            "generated_at":
                datetime.now().isoformat(),

            "report_type":
                "Document Verification Report"

        },


        
        # Identity information
        

        "identity": {

            "document_type":
                passport_data.get(
                    "document_type"
                ),

            "issuing_country":
                passport_data.get(
                    "issuing_country"
                ),

            "surname":
                passport_data.get(
                    "surname"
                ),

            "given_names":
                passport_data.get(
                    "given_names"
                ),

            "passport_number":
                passport_data.get(
                    "passport_number"
                ),

            "nationality":
                passport_data.get(
                    "nationality"
                ),

            "date_of_birth":
                passport_data.get(
                    "date_of_birth"
                ),

            "sex":
                passport_data.get(
                    "sex"
                ),

            "date_of_expiry":
                passport_data.get(
                    "date_of_expiry"
                )

        },


        
        # VERIFICATION
        

        "verification": {

            
            # OCR
            

            "ocr": {

                "success":
                    ocr_success,

                "percentage":
                    match_details.get(
                        "ocr",
                        100 if ocr_success else 0
                    )

            },


            
            # MRZ
            

            "mrz": {

                "valid":
                    mrz_valid,

                "percentage":
                    match_details.get(
                        "mrz",
                        100 if mrz_valid else 0
                    )

            },


            
            # Passport validation
            

            "passport": {

                "valid":
                    passport_valid,

                "percentage":
                    match_details.get(
                        "passport",
                        100 if passport_valid else 0
                    )

            },


            
            # Face verification
            

            "face": {

                "detected":
                    face_detected,

                "match":
                    face_match,

                "similarity":
                    photo_percentage,

                "percentage":
                    photo_percentage

            },


            
            # Database
            

            "database": {

                "match":
                    database_match,

                "percentage":
                    match_details.get(
                        "database",
                        100 if database_match else 0
                    )

            },


            
            # Forensics
            

            "forensics": {

                "available":
                    forensics_available,

                "percentage":
                    forensics_percentage

            }

        },


        
        # RISK ASSESSMENT
        

        "risk": {

            "score":
                risk_result.get(
                    "risk_score"
                ),

            "level":
                risk_result.get(
                    "risk_level"
                ),

            "decision":
                risk_result.get(
                    "decision"
                ),

            "overall_match":
                risk_result.get(
                    "overall_match_percentage"
                ),

            "reasons":
                risk_result.get(
                    "reasons",
                    []
                )

        }

    }


    return report