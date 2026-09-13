import numpy as np



# FACE MATCH THRESHOLD


FACE_MATCH_THRESHOLD = 0.45



# COSINE SIMILARITY


def cosine_similarity(
    embedding1: np.ndarray,
    embedding2: np.ndarray
) -> float:

    embedding1 = np.asarray(
        embedding1,
        dtype=np.float32
    ).flatten()

    embedding2 = np.asarray(
        embedding2,
        dtype=np.float32
    ).flatten()

    if embedding1.shape != embedding2.shape:
        raise ValueError(
            "Face embeddings must have the same shape."
        )

    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)

    if norm1 == 0 or norm2 == 0:
        raise ValueError(
            "Face embedding cannot have zero magnitude."
        )

    similarity = np.dot(
        embedding1,
        embedding2
    ) / (norm1 * norm2)

    return float(similarity)



# VERIFY TWO FACES


def verify_faces(
    embedding1: np.ndarray,
    embedding2: np.ndarray,
    threshold: float = FACE_MATCH_THRESHOLD
) -> dict:

    similarity = cosine_similarity(
        embedding1,
        embedding2
    )

    return {
        "match": similarity >= threshold,
        "similarity": similarity,
        "threshold": threshold
    }