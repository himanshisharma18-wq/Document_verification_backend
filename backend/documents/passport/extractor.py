# import cv2
# import re

# from paddleocr import PaddleOCR


# 
# # OCR ENGINE
# 

# ocr = PaddleOCR(
#     lang="en"
# )


# 
# # IMAGE PREPROCESSING
# 

# def preprocess_passport_image(image_path: str):
#     """
#     Read and preprocess the passport image.

#     The image is:
#         1. Read
#         2. Converted to grayscale
#         3. Upscaled
#         4. Contrast enhanced
#         5. Thresholded
#     """

#     image = cv2.imread(image_path)

#     if image is None:
#         raise ValueError(
#             f"Unable to read passport image: {image_path}"
#         )

#     gray = cv2.cvtColor(
#         image,
#         cv2.COLOR_BGR2GRAY
#     )

#     # Upscale the image
#     gray = cv2.resize(
#         gray,
#         None,
#         fx=2,
#         fy=2,
#         interpolation=cv2.INTER_CUBIC
#     )

#     # Improve contrast
#     gray = cv2.equalizeHist(gray)

#     # Convert to binary image
#     processed = cv2.threshold(
#         gray,
#         0,
#         255,
#         cv2.THRESH_BINARY + cv2.THRESH_OTSU
#     )[1]

#     return image, processed


# 
# # MRZ CHARACTER NORMALIZATION
# 

# def normalize_mrz_text(text: str) -> str:
#     """
#     Normalize OCR text so that it follows the
#     allowed ICAO MRZ character set.

#     Allowed:
#         A-Z
#         0-9
#         <
#     """

#     text = text.upper()

#     # Remove spaces
#     text = text.replace(" ", "")

#     # Keep only valid MRZ characters
#     text = re.sub(
#         r"[^A-Z0-9<]",
#         "",
#         text
#     )

#     return text


# 
# # OCR
# 

# def run_ocr(image):
#     """
#     Run PaddleOCR on the image.

#     Returns:
#         [
#             {
#                 "text": "...",
#                 "score": 0.98
#             }
#         ]
#     """

#     result = ocr.predict(image)

#     text_lines = []

#     for page in result:

#         try:
#             data = page.json

#             if callable(data):
#                 data = data()

#         except Exception:

#             try:
#                 data = page.to_json()

#             except Exception:
#                 continue

#         if isinstance(data, str):
#             import json

#             data = json.loads(data)

#         if not isinstance(data, dict):
#             continue

#         rec_texts = data.get(
#             "rec_texts",
#             []
#         )

#         rec_scores = data.get(
#             "rec_scores",
#             []
#         )

#         for index, text in enumerate(rec_texts):

#             score = 0.0

#             if index < len(rec_scores):
#                 score = float(
#                     rec_scores[index]
#                 )

#             text_lines.append({
#                 "text": str(text),
#                 "score": score
#             })

#     return text_lines


# 
# # MRZ CANDIDATE DETECTION
# 

# def is_possible_mrz_line(text: str) -> bool:
#     """
#     Check whether an OCR result looks like an MRZ line.

#     TD3 passport MRZ lines are normally 44 characters.
#     """

#     normalized = normalize_mrz_text(text)

#     # MRZ lines should be reasonably long
#     if len(normalized) < 30:
#         return False

#     # Calculate how much of the text consists of
#     # valid MRZ characters.
#     valid_characters = sum(
#         1
#         for char in normalized
#         if (
#             "A" <= char <= "Z"
#             or "0" <= char <= "9"
#             or char == "<"
#         )
#     )

#     ratio = (
#         valid_characters / len(normalized)
#         if normalized
#         else 0
#     )

#     return ratio >= 0.90


# 
# # FIND MRZ LINES
# 

# def find_mrz_lines(ocr_lines: list[dict]) -> list[str]:
#     """
#     Find possible passport MRZ lines from OCR output.
#     """

#     candidates = []

#     for item in ocr_lines:

#         text = item["text"]
#         score = item["score"]

#         normalized = normalize_mrz_text(
#             text
#         )

#         if is_possible_mrz_line(normalized):

#             candidates.append({
#                 "text": normalized,
#                 "score": score
#             })

#     # Prefer lines closest to the expected
#     # TD3 length of 44 characters.
#     candidates.sort(
#         key=lambda item: (
#             abs(len(item["text"]) - 44),
#             -item["score"]
#         )
#     )

#     return [
#         item["text"]
#         for item in candidates[:2]
#     ]


# 
# # COMPLETE MRZ EXTRACTION
# 

# def extract_mrz(image_path: str) -> dict:
#     """
#     Extract possible MRZ lines from a passport image.

#     Flow:

#         Passport image
#               ↓
#         Preprocessing
#               ↓
#         PaddleOCR
#               ↓
#         MRZ candidate detection
#     """

#     _, processed_image = preprocess_passport_image(
#         image_path
#     )

#     ocr_lines = run_ocr(
#         processed_image
#     )

#     mrz_lines = find_mrz_lines(
#         ocr_lines
#     )

#     return {
#         "success": len(mrz_lines) == 2,
#         "mrz_lines": mrz_lines,
#         "ocr_lines": ocr_lines
#     }











































# import cv2
# import re

# from paddleocr import PaddleOCR


# 
# # OCR ENGINE
# 

# ocr = PaddleOCR(
#     lang="en",
#     use_doc_orientation_classify=False,
#     use_doc_unwarping=False,
#     use_textline_orientation=False
# )


# 
# # IMAGE LOADING
# 

# def load_passport_image(image_path: str):
#     """
#     Load the passport image.
#     """

#     image = cv2.imread(image_path)

#     if image is None:
#         raise ValueError(
#             f"Unable to read passport image: {image_path}"
#         )

#     return image


# 
# # MRZ REGION EXTRACTION
# 

# def crop_mrz_region(image):
#     """
#     Extract the lower portion of the passport image
#     where the TD3 MRZ is expected to be located.

#     TD3 passport MRZ contains two lines and is positioned
#     at the bottom of the passport data page.

#     We keep a sufficiently large lower region rather than
#     taking an extremely tight crop, because passport images
#     can have different layouts and margins.
#     """

#     height, width = image.shape[:2]

#     # Start from approximately the lower 40% of the image.
#     start_y = int(height * 0.60)

#     mrz_region = image[
#         start_y:height,
#         0:width
#     ]

#     return mrz_region


# 
# # IMAGE PREPROCESSING
# 

# def preprocess_mrz_image(image):
#     """
#     Preprocess the MRZ region for OCR.

#     Steps:

#         BGR
#          ↓
#         Grayscale
#          ↓
#         Upscaling
#          ↓
#         Contrast enhancement
#          ↓
#         OTSU thresholding
#     """

#     gray = cv2.cvtColor(
#         image,
#         cv2.COLOR_BGR2GRAY
#     )

#     # Increase resolution for OCR.
#     gray = cv2.resize(
#         gray,
#         None,
#         fx=2,
#         fy=2,
#         interpolation=cv2.INTER_CUBIC
#     )

#     # Improve contrast.
#     gray = cv2.equalizeHist(
#         gray
#     )

#     # Convert to binary image.
#     processed = cv2.threshold(
#         gray,
#         0,
#         255,
#         cv2.THRESH_BINARY + cv2.THRESH_OTSU
#     )[1]














#     processed = cv2.cvtColor(
#     processed,
#     cv2.COLOR_GRAY2BGR
# )

#     return processed


# 
# # MRZ CHARACTER NORMALIZATION
# 

# def normalize_mrz_text(text: str) -> str:
#     """
#     Normalize OCR-generated MRZ text.

#     ICAO MRZ permits:

#         A-Z
#         0-9
#         <

#     OCR may introduce spaces or other symbols,
#     so those are removed.
#     """

#     text = text.upper()

#     # Remove spaces.
#     text = text.replace(
#         " ",
#         ""
#     )

#     # Keep only valid MRZ characters.
#     text = re.sub(
#         r"[^A-Z0-9<]",
#         "",
#         text
#     )

#     return text


# 
# # OCR
# 

# def run_ocr(image):
#     """
#     Run PaddleOCR on the processed MRZ image.

#     Returns a list containing recognized text
#     and confidence score.
#     """










#     print("OCR INPUT SHAPE:", image.shape)
#     print("OCR INPUT DTYPE:", image.dtype)
#     print("OCR INPUT DIMENSIONS:", len(image.shape))

#     result = ocr.predict(
#         image
#     )

#     text_lines = []

#     for page in result:

#         # PaddleOCR 3.x result handling.
#         try:

#             data = page.json

#             if callable(data):
#                 data = data()

#         except Exception:

#             try:
#                 data = page.to_json()

#             except Exception:
#                 continue

#         # Some versions return JSON as a string.
#         if isinstance(data, str):

#             import json

#             data = json.loads(
#                 data
#             )

#         if not isinstance(data, dict):
#             continue

#         rec_texts = data.get(
#             "rec_texts",
#             []
#         )

#         rec_scores = data.get(
#             "rec_scores",
#             []
#         )

#         for index, text in enumerate(
#             rec_texts
#         ):

#             score = 0.0

#             if index < len(
#                 rec_scores
#             ):
#                 score = float(
#                     rec_scores[index]
#                 )

#             text_lines.append({
#                 "text": str(text),
#                 "score": score
#             })

#     return text_lines


# 
# # MRZ CANDIDATE CHECK
# 

# def is_possible_mrz_line(
#     text: str
# ) -> bool:
#     """
#     Determine whether OCR text could be
#     one of the two TD3 MRZ lines.
#     """

#     normalized = normalize_mrz_text(
#         text
#     )

#     # A real TD3 MRZ line is 44 characters.
#     # We allow shorter OCR results here because
#     # OCR may occasionally miss characters.
#     if len(normalized) < 30:
#         return False

#     valid_characters = 0

#     for char in normalized:

#         if (
#             "A" <= char <= "Z"
#             or "0" <= char <= "9"
#             or char == "<"
#         ):
#             valid_characters += 1

#     ratio = (
#         valid_characters / len(normalized)
#     )

#     return ratio >= 0.90


# 
# # FIND MRZ LINES
# 

# def find_mrz_lines(
#     ocr_lines: list[dict]
# ) -> list[str]:
#     """
#     Find the two strongest MRZ candidates.

#     Preference is given to lines closest to
#     the expected TD3 length of 44 characters.
#     """

#     candidates = []

#     for item in ocr_lines:

#         text = item["text"]
#         score = item["score"]

#         normalized = normalize_mrz_text(
#             text
#         )

#         if is_possible_mrz_line(
#             normalized
#         ):

#             candidates.append({
#                 "text": normalized,
#                 "score": score
#             })

#     # Prefer:
#     # 1. Length closest to 44
#     # 2. Higher OCR confidence
#     candidates.sort(
#         key=lambda item: (
#             abs(
#                 len(item["text"]) - 44
#             ),
#             -item["score"]
#         )
#     )

#     return [
#         item["text"]
#         for item in candidates[:2]
#     ]


# 
# # MRZ LINE ORDERING
# 

# def order_mrz_lines(
#     mrz_lines: list[str]
# ) -> list[str]:
#     """
#     Ensure TD3 MRZ line 1 comes before line 2.

#     Line 1 begins with P.
#     """

#     if len(mrz_lines) != 2:
#         return mrz_lines

#     line1 = mrz_lines[0]
#     line2 = mrz_lines[1]

#     if (
#         not line1.startswith("P")
#         and line2.startswith("P")
#     ):
#         return [
#             line2,
#             line1
#         ]

#     return [
#         line1,
#         line2
#     ]


# 
# # COMPLETE MRZ EXTRACTION
# 

# def extract_mrz(
#     image_path: str
# ) -> dict:
#     """
#     Complete passport MRZ extraction.

#     Passport image
#           ↓
#     Load image
#           ↓
#     Crop MRZ region
#           ↓
#     Preprocess
#           ↓
#     PaddleOCR
#           ↓
#     Find MRZ candidates
#           ↓
#     Order MRZ lines
#     """

#     
#     # STEP 1: Load passport
#     

#     image = load_passport_image(
#         image_path
#     )

#     
#     # STEP 2: Crop MRZ region
#     

#     mrz_region = crop_mrz_region(
#         image
#     )

#     
#     # STEP 3: Preprocess MRZ
#     

#     processed_image = preprocess_mrz_image(
#         mrz_region
#     )

#     
#     # STEP 4: OCR
#     

#     ocr_lines = run_ocr(
#         processed_image
#     )

#     
#     # STEP 5: Find MRZ candidates
#     

#     mrz_lines = find_mrz_lines(
#         ocr_lines
#     )

#     
#     # STEP 6: Correct line ordering
#     

#     mrz_lines = order_mrz_lines(
#         mrz_lines
#     )

#     
#     # STEP 7: Return extraction result
#     

#     return {
#         "success": len(mrz_lines) == 2,

#         "mrz_lines": mrz_lines,

#         "ocr_lines": ocr_lines
#     }




















































































import cv2
import re

from paddleocr import PaddleOCR



# OCR ENGINE


ocr = PaddleOCR(
    lang="en",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)



# IMAGE LOADING


def load_passport_image(image_path: str):
    """
    Load the passport image using OpenCV.
    """

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            f"Unable to read passport image: {image_path}"
        )

    return image



# MRZ REGION EXTRACTION


def crop_mrz_region(image):
    """
    Extract the lower portion of the passport data page.

    TD3 passports normally contain a two-line MRZ at the
    bottom of the passport data page.

    We intentionally keep a relatively large region so
    that different passport layouts are supported.
    """

    height, width = image.shape[:2]

    # Lower 40% of the passport image.
    start_y = int(height * 0.60)

    mrz_region = image[
        start_y:height,
        0:width
    ]

    return mrz_region



# IMAGE PREPROCESSING


def preprocess_mrz_image(image):
    """
    Prepare the MRZ region for OCR.

    BGR
      ↓
    Grayscale
      ↓
    Upscale
      ↓
    Contrast enhancement
      ↓
    OTSU threshold
      ↓
    Convert back to BGR

    PaddleOCR expects a 3-channel image in this pipeline.
    """

    # Convert BGR → grayscale
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Upscale the image.
    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    # Improve contrast.
    gray = cv2.equalizeHist(
        gray
    )

    # OTSU thresholding.
    processed = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    # Convert grayscale → BGR.
    processed = cv2.cvtColor(
        processed,
        cv2.COLOR_GRAY2BGR
    )

    return processed



# MRZ CHARACTER NORMALIZATION


def normalize_mrz_text(text: str) -> str:
    """
    Normalize OCR output into characters permitted by ICAO MRZ.

    Valid MRZ characters:

        A-Z
        0-9
        <

    Some OCR engines may produce visually similar Unicode
    characters. These are corrected where possible.
    """

    text = str(text).upper().strip()

    
    # Common OCR substitutions
    

    replacements = {
        "Ⅰ": "I",
        "І": "I",
        "l": "I",
        "|": "I",

        "Ｏ": "O",
        "０": "0",

        "１": "1",
        "２": "2",
        "３": "3",
        "４": "4",
        "５": "5",
        "６": "6",
        "７": "7",
        "８": "8",
        "９": "9",

        "＜": "<",

        "«": "<",
        "‹": "<",
        "«": "<",

        "–": "",
        "-": "",
        "_": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove whitespace.
    text = re.sub(
        r"\s+",
        "",
        text
    )

    # Keep only valid MRZ characters.
    text = re.sub(
        r"[^A-Z0-9<]",
        "",
        text
    )

    return text



# OCR


def run_ocr(image):
    """
    Run PaddleOCR and return recognized text lines.

    Each item has:

        {
            "text": "...",
            "score": 0.99
        }
    """

    print("OCR INPUT SHAPE:", image.shape)
    print("OCR INPUT DTYPE:", image.dtype)
    print("OCR INPUT DIMENSIONS:", len(image.shape))

    result = ocr.predict(
        image
    )

    text_lines = []

    for page in result:

        
        # PaddleOCR 3.x JSON extraction
        

        try:

            data = page.json

            if callable(data):
                data = data()

        except Exception:

            try:

                data = page.to_json()

            except Exception:
                continue

        
        # JSON string → dictionary
        

        if isinstance(data, str):

            import json

            try:
                data = json.loads(data)

            except Exception:
                continue

        if not isinstance(data, dict):
            continue

        
        # Get OCR text
        

        rec_texts = data.get(
            "rec_texts",
            []
        )

        rec_scores = data.get(
            "rec_scores",
            []
        )

        
        # Store OCR results
        

        for index, text in enumerate(rec_texts):

            score = 0.0

            if index < len(rec_scores):

                try:
                    score = float(
                        rec_scores[index]
                    )

                except Exception:
                    score = 0.0

            text_lines.append({
                "text": str(text),
                "score": score
            })

    return text_lines



# MRZ CANDIDATE CHECK


def is_possible_mrz_line(text: str) -> bool:
    """
    Determine whether OCR text looks like a TD3 MRZ line.

    A standard TD3 MRZ line contains exactly 44 characters.

    We allow a little flexibility because OCR can miss
    characters or misread characters.
    """

    normalized = normalize_mrz_text(
        text
    )

    # Too short to realistically be a TD3 MRZ line.
    if len(normalized) < 30:
        return False

    
    # Character validity
    

    valid_characters = 0

    for char in normalized:

        if (
            "A" <= char <= "Z"
            or "0" <= char <= "9"
            or char == "<"
        ):
            valid_characters += 1

    if len(normalized) == 0:
        return False

    ratio = (
        valid_characters /
        len(normalized)
    )

    if ratio < 0.90:
        return False

    
    # Strong indicator:
    # TD3 line 1 normally begins with P
    

    if normalized.startswith("P"):
        return True

    
    # Strong indicator:
    # TD3 line 2 normally contains digits and '<'
    

    digit_count = sum(
        char.isdigit()
        for char in normalized
    )

    filler_count = normalized.count("<")

    if digit_count >= 5 and filler_count >= 3:
        return True

    return False



# MRZ CANDIDATE SCORE


def mrz_candidate_score(
    text: str,
    ocr_score: float
) -> float:
    """
    Calculate a score for an OCR line being an MRZ line.

    Higher score = more likely to be MRZ.
    """

    normalized = normalize_mrz_text(
        text
    )

    if len(normalized) < 30:
        return -1000

    score = 0.0

    
    # OCR confidence
    

    score += ocr_score * 10

    
    # Length
    

    # 44 is the official TD3 length.
    length_difference = abs(
        len(normalized) - 44
    )

    score -= length_difference * 2

    
    # Starts with P
    

    if normalized.startswith("P"):
        score += 30

    
    # MRZ filler character
    

    filler_count = normalized.count("<")

    if filler_count >= 3:
        score += 15

    
    # Digits
    

    digit_count = sum(
        char.isdigit()
        for char in normalized
    )

    if digit_count >= 5:
        score += 10

    return score



# FIND MRZ LINES


def find_mrz_lines(
    ocr_lines: list[dict]
) -> list[str]:
    """
    Find the strongest two MRZ candidates.

    We do not simply take the longest two OCR strings.

    Candidates are evaluated using:

        - MRZ character validity
        - OCR confidence
        - closeness to 44 characters
        - P prefix
        - '<' filler characters
        - numeric content
    """

    candidates = []

    for item in ocr_lines:

        original_text = item.get(
            "text",
            ""
        )

        ocr_score = float(
            item.get(
                "score",
                0.0
            )
        )

        normalized = normalize_mrz_text(
            original_text
        )

        # Check if candidate resembles MRZ.
        if not is_possible_mrz_line(
            normalized
        ):
            continue

        candidate_score = mrz_candidate_score(
            normalized,
            ocr_score
        )

        candidates.append({
            "text": normalized,
            "score": candidate_score,
            "ocr_score": ocr_score
        })

    
    # Sort strongest candidates first
    

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    
    # Separate line 1 and line 2
    

    line1_candidates = [
        item
        for item in candidates
        if item["text"].startswith("P")
    ]

    line2_candidates = [
        item
        for item in candidates
        if not item["text"].startswith("P")
    ]

    
    # Best possible line 1
    

    best_line1 = None

    if line1_candidates:
        best_line1 = line1_candidates[0]

    
    # Best possible line 2
    

    best_line2 = None

    if line2_candidates:
        best_line2 = line2_candidates[0]

    
    # Preferred result:
    # one line 1 + one line 2
    

    if best_line1 and best_line2:

        return [
            best_line1["text"],
            best_line2["text"]
        ]

    
    # Fallback:
    # take two strongest candidates
    

    return [
        item["text"]
        for item in candidates[:2]
    ]



# MRZ LINE ORDERING


def order_mrz_lines(
    mrz_lines: list[str]
) -> list[str]:
    """
    Ensure line 1 comes before line 2.

    TD3 line 1 starts with:

        P

    Example:

        P<IND...
        G276...
    """

    if len(mrz_lines) != 2:
        return mrz_lines

    line1 = mrz_lines[0]
    line2 = mrz_lines[1]

    if (
        not line1.startswith("P")
        and line2.startswith("P")
    ):

        return [
            line2,
            line1
        ]

    return [
        line1,
        line2
    ]



# MRZ LENGTH INFORMATION


def validate_mrz_lengths(
    mrz_lines: list[str]
) -> bool:
    """
    Check whether both extracted lines have
    the official TD3 MRZ length.

    Each TD3 line should contain exactly 44 characters.
    """

    if len(mrz_lines) != 2:
        return False

    return (
        len(mrz_lines[0]) == 44
        and
        len(mrz_lines[1]) == 44
    )



# COMPLETE MRZ EXTRACTION


def extract_mrz(
    image_path: str
) -> dict:
    """
    Complete passport MRZ extraction.

    Pipeline:

        passport.jpeg
              ↓
        Load image
              ↓
        Crop lower passport region
              ↓
        Preprocess
              ↓
        PaddleOCR
              ↓
        Find MRZ candidates
              ↓
        Order MRZ lines
              ↓
        Validate length
              ↓
        Return result
    """

    
    # STEP 1: LOAD PASSPORT
    

    image = load_passport_image(
        image_path
    )

    
    # STEP 2: CROP MRZ REGION
    

    mrz_region = crop_mrz_region(
        image
    )

    
    # STEP 3: PREPROCESS
    

    processed_image = preprocess_mrz_image(
        mrz_region
    )

    
    # STEP 4: OCR
    

    ocr_lines = run_ocr(
        processed_image
    )

    
    # DEBUG: SHOW OCR LINES
    

    print()
    print("OCR LINES DETECTED:")
    print("----------------------------------------")

    for index, item in enumerate(ocr_lines):

        print(
            f"{index}: "
            f"{item['text']} "
            f"(score={item['score']:.3f})"
        )

    print("----------------------------------------")

    
    # STEP 5: FIND MRZ
    

    mrz_lines = find_mrz_lines(
        ocr_lines
    )

    
    # STEP 6: ORDER MRZ
    

    mrz_lines = order_mrz_lines(
        mrz_lines
    )

    
    # STEP 7: VALIDATE
    

    valid_length = validate_mrz_lengths(
        mrz_lines
    )

    
    # FINAL RESULT
    

    success = (
        len(mrz_lines) == 2
    )

    return {
        "success": success,

        "mrz_lines": mrz_lines,

        "valid_td3_length": valid_length,

        "ocr_lines": ocr_lines
    }