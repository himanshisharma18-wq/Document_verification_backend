

# FACE VERIFICATION TEST


import os
import cv2

from backend.face.face_detector import detect_face_from_path
from backend.face.face_embedding import generate_face_embedding
from backend.face.face_verifier import verify_faces



# IMAGE PATHS


IMAGE_A = "passport.jpeg"
IMAGE_B = "face_detected.jpg"



# HEADER


print()
print("========================================")
print("FACE VERIFICATION TEST")
print("========================================")



# CHECK IMAGES


print()
print("IMAGE A:", IMAGE_A)
print("EXISTS:", os.path.exists(IMAGE_A))

print()
print("IMAGE B:", IMAGE_B)
print("EXISTS:", os.path.exists(IMAGE_B))


if not os.path.exists(IMAGE_A):
    print()
    print("ERROR: Image A not found:")
    print(IMAGE_A)
    raise SystemExit


if not os.path.exists(IMAGE_B):
    print()
    print("ERROR: Image B not found:")
    print(IMAGE_B)
    raise SystemExit



# LOAD IMAGES


image_a = cv2.imread(IMAGE_A)
image_b = cv2.imread(IMAGE_B)

print()
print("IMAGE A LOAD:", image_a is not None)
print("IMAGE B LOAD:", image_b is not None)


if image_a is None:
    print("ERROR: Could not read Image A.")
    raise SystemExit


if image_b is None:
    print("ERROR: Could not read Image B.")
    raise SystemExit



# FACE DETECTION - IMAGE A


print()
print("========================================")
print("FACE DETECTION - IMAGE A")
print("========================================")

face_a = detect_face_from_path(
    IMAGE_A
)

print(
    "FACE A DETECTION SUCCESS:",
    face_a is not None
)

if face_a is None:
    print("NO FACE DETECTED IN IMAGE A")
    raise SystemExit



# FACE DETECTION - IMAGE B


print()
print("========================================")
print("FACE DETECTION - IMAGE B")
print("========================================")

face_b = detect_face_from_path(
    IMAGE_B
)

print(
    "FACE B DETECTION SUCCESS:",
    face_b is not None
)

if face_b is None:
    print("NO FACE DETECTED IN IMAGE B")
    raise SystemExit



# EMBEDDING A


print()
print("========================================")
print("FACE EMBEDDING A")
print("========================================")

embedding1 = generate_face_embedding(
    IMAGE_A
)

print(
    "EMBEDDING A SUCCESS:",
    embedding1 is not None
)

if embedding1 is None:
    print("FAILED TO GENERATE EMBEDDING A")
    raise SystemExit

print("Embedding A shape:")
print(embedding1.shape)



# EMBEDDING B


print()
print("========================================")
print("FACE EMBEDDING B")
print("========================================")

embedding2 = generate_face_embedding(
    IMAGE_B
)

print(
    "EMBEDDING B SUCCESS:",
    embedding2 is not None
)

if embedding2 is None:
    print("FAILED TO GENERATE EMBEDDING B")
    raise SystemExit

print("Embedding B shape:")
print(embedding2.shape)



# CHECK WHETHER EMBEDDINGS ARE IDENTICAL


print()
print("========================================")
print("EMBEDDING COMPARISON")
print("========================================")

identical = (embedding1 == embedding2).all()

print(
    "EMBEDDINGS IDENTICAL:",
    identical
)



# FACE VERIFICATION


print()
print("========================================")
print("FACE VERIFICATION")
print("========================================")

result = verify_faces(
    embedding1,
    embedding2
)


print()
print("Similarity:")
print(result["similarity"])


print()
print("Threshold:")
print(result["threshold"])


print()
print("FACE MATCH:")
print(result["match"])



# FINAL RESULT


print()
print("========================================")
print("FINAL FACE RESULT")
print("========================================")

if result["match"]:

    print("FACE VERIFIED: True")

else:

    print("FACE VERIFIED: False")