
# FACE EMBEDDING


import cv2
import numpy as np
from insightface.app import FaceAnalysis



# INSIGHTFACE MODEL


face_app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

face_app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)



# GENERATE FACE EMBEDDING


def generate_face_embedding(image_path: str):
    """
    Detect a face and generate a 512-dimensional
    InsightFace embedding.

    Returns:
        numpy.ndarray of shape (512,)
        or None if no face is detected.
    """

    
    # Load image
    

    image = cv2.imread(image_path)

    if image is None:
        return None

    
    # Detect faces
    

    faces = face_app.get(image)

    if not faces:
        return None

    
    # Select largest face
    

    face = max(
        faces,
        key=lambda f: (
            f.bbox[2] - f.bbox[0]
        ) * (
            f.bbox[3] - f.bbox[1]
        )
    )

    
    # Get embedding
    

    embedding = face.embedding

    if embedding is None:
        return None

    
    # Convert to numpy array
    

    embedding = np.asarray(
        embedding,
        dtype=np.float32
    )

    
    # Normalize embedding
    

    norm = np.linalg.norm(embedding)

    if norm == 0:
        return None

    embedding = embedding / norm

    return embedding