from __future__ import annotations

import io
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image, UnidentifiedImageError


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "freshness_model.keras"
LABELS_PATH = BASE_DIR / "models" / "freshness_labels.json"

IMAGE_SIZE = (224, 224)
MAX_IMAGE_BYTES = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
}


@lru_cache(maxsize=1)
def load_freshness_model():
    """Load the trained freshness model once and reuse it."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Freshness model is not available."
        )

    return tf.keras.models.load_model(
        MODEL_PATH,
        compile=False,
    )


@lru_cache(maxsize=1)
def load_class_names():
    """Load the freshness class labels."""
    if not LABELS_PATH.exists():
        raise FileNotFoundError(
            "Freshness label configuration is not available."
        )

    with LABELS_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    class_names = data.get("class_names")

    if not isinstance(class_names, list) or len(class_names) != 3:
        raise ValueError(
            "Freshness label configuration is invalid."
        )

    return class_names


def _read_and_validate_image(file_storage):
    """Validate and prepare an uploaded image in memory."""
    if file_storage is None:
        raise ValueError("Please select an image.")

    filename = (file_storage.filename or "").strip()

    if not filename:
        raise ValueError("Please select an image.")

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported image format. Use JPG, JPEG, or PNG."
        )

    image_bytes = file_storage.read(
        MAX_IMAGE_BYTES + 1
    )

    if not image_bytes:
        raise ValueError("The uploaded image is empty.")

    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ValueError(
            "Image must be 5 MB or smaller."
        )

    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            image.verify()

        with Image.open(io.BytesIO(image_bytes)) as image:
            image = image.convert("RGB")
            image = image.resize(IMAGE_SIZE)

            image_array = np.asarray(
                image,
                dtype=np.float32,
            )

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
    ) as error:
        raise ValueError(
            "The uploaded file is not a valid image."
        ) from error

    return image_array


def predict_freshness(file_storage):
    """Return an advisory freshness classification."""
    image_array = _read_and_validate_image(
        file_storage
    )

    model = load_freshness_model()
    class_names = load_class_names()

    batch = np.expand_dims(
        image_array,
        axis=0,
    )

    predictions = model.predict(
        batch,
        verbose=0,
    )[0]

    predicted_index = int(
        np.argmax(predictions)
    )

    confidence = float(
        predictions[predicted_index] * 100
    )

    return {
        "label": class_names[predicted_index],
        "confidence": round(confidence, 2),
    }