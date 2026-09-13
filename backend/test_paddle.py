from paddleocr import PaddleOCR


ocr = PaddleOCR(
    lang="en",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

image_path = "passport.jpeg"

print("Starting PaddleOCR test...")

result = ocr.predict(image_path)

print("PaddleOCR completed successfully!")

for res in result:
    print(res)