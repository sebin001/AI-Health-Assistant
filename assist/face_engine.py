import base64

import cv2
import numpy as np

from insightface.app import FaceAnalysis


_face_app = None


def get_face_app():
    global _face_app

    if _face_app is None:

        _face_app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"]
        )

        _face_app.prepare(
            ctx_id=-1,
            det_size=(640, 640)
        )

    return _face_app


def decode_base64_image(image_data):

    if "," in image_data:
        image_data = image_data.split(",", 1)[1]

    try:

        image_bytes = base64.b64decode(image_data)

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        return image

    except Exception:

        return None


def compute_image_sharpness(image):
    """Calculate focus/sharpness score using Laplacian variance."""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        score = cv2.Laplacian(gray, cv2.CV_64F).var()
        return round(float(score), 2)
    except Exception:
        return 100.0


def detect_faces(image_data):

    image = decode_base64_image(image_data)

    if image is None:

        return {
            "success": False,
            "message": "Invalid camera image."
        }

    sharpness = compute_image_sharpness(image)
    is_sharp = sharpness >= 40.0

    app = get_face_app()

    faces = app.get(image)

    face_count = len(faces)

    boxes = []

    for face in faces:

        bbox = face.bbox.astype(int).tolist()

        boxes.append({
            "x1": bbox[0],
            "y1": bbox[1],
            "x2": bbox[2],
            "y2": bbox[3],
        })

    if face_count == 0:

        return {
            "success": True,
            "face_count": 0,
            "status": "no_face",
            "message": "No face detected.",
            "sharpness": sharpness,
            "is_sharp": is_sharp,
            "boxes": []
        }

    if face_count > 1:

        return {
            "success": True,
            "face_count": face_count,
            "status": "multiple_faces",
            "message": "Multiple faces detected. Only one person is allowed.",
            "sharpness": sharpness,
            "is_sharp": is_sharp,
            "boxes": boxes
        }

    # If 1 face, check positioning & blur
    if not is_sharp:
        return {
            "success": True,
            "face_count": 1,
            "status": "blurry",
            "message": "Face detected, but image is blurry. Hold steady.",
            "sharpness": sharpness,
            "is_sharp": False,
            "boxes": boxes
        }

    return {
        "success": True,
        "face_count": 1,
        "status": "single_face",
        "message": "Face verified & sharp.",
        "sharpness": sharpness,
        "is_sharp": True,
        "boxes": boxes
    }


def get_face_embedding(image_data):

    image = decode_base64_image(image_data)

    if image is None:

        return {
            "success": False,
            "message": "Invalid camera image."
        }

    # Sharpness guard
    sharpness = compute_image_sharpness(image)
    if sharpness < 30.0:
        return {
            "success": False,
            "message": f"Camera image is too blurry (sharpness score: {sharpness}). Please hold still in good lighting."
        }

    app = get_face_app()

    faces = app.get(image)

    if len(faces) == 0:

        return {
            "success": False,
            "message": "No face detected."
        }

    if len(faces) > 1:

        return {
            "success": False,
            "message": (
                "Multiple faces detected. "
                "Only one person is allowed."
            )
        }

    face = faces[0]

    # Face area size check (make sure face isn't a tiny speck)
    h, w = image.shape[:2]
    bbox = face.bbox
    face_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
    frame_area = w * h
    if frame_area > 0 and (face_area / frame_area) < 0.04:
        return {
            "success": False,
            "message": "Face is too far from camera. Please move closer."
        }

    embedding = face.embedding

    if embedding is None:

        return {
            "success": False,
            "message": "Unable to generate Face ID."
        }

    embedding = embedding.astype(np.float32)

    norm = np.linalg.norm(embedding)

    if norm == 0:

        return {
            "success": False,
            "message": "Invalid Face ID embedding."
        }

    embedding = embedding / norm

    return {
        "success": True,
        "embedding": embedding.tolist(),
        "sharpness": sharpness
    }