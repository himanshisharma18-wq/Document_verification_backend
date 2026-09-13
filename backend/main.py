# DOCUMENT VERIFICATION API


from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os
import shutil
import uuid

from backend.services.verification_service import verify_document



# APP


app = FastAPI(
    title="ID Verify API",
    description="Document Authenticity & Identity Verification System",
    version="1.0.0"
)



# CORS


app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)



# UPLOAD DIRECTORY


UPLOAD_DIR = "backend/uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)











# REPORT DIRECTORY


REPORT_DIR = "backend/reports"

os.makedirs(
    REPORT_DIR,
    exist_ok=True
)



# SERVE PDF REPORTS


app.mount(
    "/api/reports",
    StaticFiles(directory=REPORT_DIR),
    name="reports"
)


# ROOT


@app.get("/")
def root():

    return {
        "message": "ID Verify API is running",
        "status": "OK"
    }



# HEALTH CHECK


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }



# VERIFY DOCUMENT


@app.post("/api/verify")
async def verify(

    document: UploadFile = File(...),

    selfie: UploadFile = File(...)
):

    
    # Validate document
    

    if not document.filename:

        raise HTTPException(
            status_code=400,
            detail="Document file is required."
        )


    
    # Validate selfie
    

    if not selfie.filename:

        raise HTTPException(
            status_code=400,
            detail="Selfie file is required."
        )


    
    # Generate unique filenames
    

    document_extension = os.path.splitext(
        document.filename
    )[1]

    selfie_extension = os.path.splitext(
        selfie.filename
    )[1]


    document_filename = (
        f"document_{uuid.uuid4().hex}"
        f"{document_extension}"
    )

    selfie_filename = (
        f"selfie_{uuid.uuid4().hex}"
        f"{selfie_extension}"
    )


    document_path = os.path.join(
        UPLOAD_DIR,
        document_filename
    )

    selfie_path = os.path.join(
        UPLOAD_DIR,
        selfie_filename
    )


    
    # Save document
    

    try:

        with open(
            document_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                document.file,
                buffer
            )


        
        # Save selfie
        

        with open(
            selfie_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                selfie.file,
                buffer
            )


        
        # RUN COMPLETE VERIFICATION
        

        result = verify_document(

            passport_image=document_path,

            reference_face_image=selfie_path

        )


        
        # Return report
        

        return result


    except Exception as e:

        print()
        print("========================================")
        print("VERIFICATION ERROR")
        print("========================================")
        print(e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )