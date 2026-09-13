import cv2



# FACE DETECTOR


# OpenCV's built-in Haar Cascade.
# It does not require downloading another model.
FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)



# DETECT FACES


def detect_faces(image):
    """
    Detect faces in an image.

    Returns:
        list of face bounding boxes

    Each box is:
        (x, y, width, height)
    """

    if image is None:
        return []

    # Convert to grayscale
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Detect faces
    faces = FACE_CASCADE.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    return list(faces)



# GET LARGEST FACE


def get_largest_face(image):
    """
    Find the largest detected face.

    Useful for passport images because normally
    there should be one main face.
    """

    faces = detect_faces(image)

    if not faces:
        return None

    largest_face = max(
        faces,
        key=lambda box: box[2] * box[3]
    )

    return largest_face



# CROP FACE


def crop_face(image, face_box):
    """
    Crop a detected face from the image.
    """

    if image is None or face_box is None:
        return None

    x, y, width, height = face_box

    face = image[
        y:y + height,
        x:x + width
    ]

    if face.size == 0:
        return None

    return face



# DETECT AND CROP MAIN FACE


def detect_and_crop_face(image):
    """
    Detect the largest face and return the cropped face.

    Returns:
        cropped face
        or None if no face is detected
    """

    face_box = get_largest_face(image)

    if face_box is None:
        return None

    return crop_face(
        image,
        face_box
    )



# IMAGE PATH VERSION


def detect_face_from_path(image_path):
    """
    Read an image from disk and detect the largest face.

    Returns:
        {
            "success": True,
            "face": cropped_face,
            "box": (x, y, w, h)
        }

    or:

        {
            "success": False,
            "face": None,
            "box": None
        }
    """

    image = cv2.imread(image_path)

    if image is None:
        return {
            "success": False,
            "face": None,
            "box": None
        }

    face_box = get_largest_face(image)

    if face_box is None:
        return {
            "success": False,
            "face": None,
            "box": None
        }

    face = crop_face(
        image,
        face_box
    )

    if face is None:
        return {
            "success": False,
            "face": None,
            "box": None
        }

    return {
        "success": True,
        "face": face,
        "box": face_box
    }