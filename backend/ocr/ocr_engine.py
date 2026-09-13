from paddleocr import PaddleOCR



# OCR ENGINE


ocr = PaddleOCR(
    lang="en",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    enable_mkldnn=False
)



# EXTRACT TEXT


def extract_text(image_path: str) -> list[str]:

    print()
    print("RUNNING PADDLE OCR...")
    print("----------------------------------------")

    result = ocr.predict(image_path)

    lines = []

    for res in result:

        print("PADDLE RESULT OBJECT:")
        print(res)

        print("----------------------------------------")

        # IMPORTANT:
        # PaddleOCR 3.x result object behaves like a dictionary
        # in your working direct test.

        try:

            if "rec_texts" in res:

                texts = res["rec_texts"]

                for text in texts:

                    if text:
                        lines.append(
                            str(text)
                        )

        except Exception as e:

            print(
                "Dictionary extraction failed:",
                e
            )

        
        # Backup method
        

        if not lines:

            try:

                data = res.json

                if callable(data):
                    data = data()

                print("JSON DATA:")
                print(data)

                if isinstance(data, dict):

                    texts = data.get(
                        "rec_texts",
                        []
                    )

                    for text in texts:

                        if text:
                            lines.append(
                                str(text)
                            )

            except Exception as e:

                print(
                    "JSON extraction failed:",
                    e
                )

    print()
    print("EXTRACTED OCR LINES:")
    print("----------------------------------------")

    for line in lines:
        print(line)

    print("----------------------------------------")

    return lines



# MRZ NORMALIZATION


def normalize_mrz_text(text: str) -> str:

    text = str(text).upper()

    # OCR Unicode I → normal I
    text = text.replace("Ⅰ", "I")
    text = text.replace("І", "I")
    text = text.replace("ı", "I")

    # Common OCR confusion
    text = text.replace("|", "I")
    text = text.replace("!", "I")

    # Remove spaces
    text = text.replace(" ", "")

    # Keep valid MRZ characters
    text = "".join(
        char
        for char in text
        if (
            "A" <= char <= "Z"
            or "0" <= char <= "9"
            or char == "<"
        )
    )

    return text



# FIND MRZ


def extract_mrz_lines(
    ocr_lines: list[str]
) -> list[str]:

    candidates = []

    for line in ocr_lines:

        normalized = normalize_mrz_text(
            line
        )

        print(
            "CHECKING OCR LINE:",
            repr(line),
            "→",
            normalized
        )

        
        # First MRZ line
        

        if normalized.startswith("P"):

            if len(normalized) >= 30:

                candidates.append(
                    normalized
                )

        
        # Second MRZ line
        

        elif len(normalized) >= 30:

            if any(
                char.isdigit()
                for char in normalized
            ):

                candidates.append(
                    normalized
                )

    
    # Separate line 1 and line 2
    

    line1 = None
    line2 = None

    for candidate in candidates:

        if candidate.startswith("P"):

            line1 = candidate

        elif line2 is None:

            line2 = candidate

    mrz_lines = []

    if line1 is not None:
        mrz_lines.append(line1)

    if line2 is not None:
        mrz_lines.append(line2)

    return mrz_lines



# COMPLETE MRZ EXTRACTION


def extract_mrz(
    image_path: str
) -> dict:

    ocr_lines = extract_text(
        image_path
    )

    mrz_lines = extract_mrz_lines(
        ocr_lines
    )

    print()
    print("FINAL MRZ LINES:")
    print("----------------------------------------")

    for line in mrz_lines:
        print(line)

    print("----------------------------------------")

    return {
        "success": len(mrz_lines) == 2,
        "mrz_lines": mrz_lines,
        "ocr_lines": ocr_lines
    }