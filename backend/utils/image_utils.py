"""
NavAI - Image Utility Functions
Helper functions for image loading and processing.
"""

import io
import logging
import numpy as np
from PIL import Image
from fastapi import UploadFile

logger = logging.getLogger("NavAI.ImageUtils")


async def load_image_from_upload(upload: UploadFile) -> np.ndarray:
    """
    Load an uploaded image file into a NumPy array.

    Args:
        upload: FastAPI UploadFile object

    Returns:
        NumPy array in RGB format

    Raises:
        ValueError: If the file is not a valid image
    """
    try:
        contents = await upload.read()
        image = Image.open(io.BytesIO(contents))

        # Convert to RGB if necessary
        if image.mode != "RGB":
            image = image.convert("RGB")

        img_array = np.array(image)
        logger.info(f"Image loaded: {img_array.shape} ({upload.filename})")
        return img_array

    except Exception as e:
        logger.error(f"Failed to load image: {e}")
        raise ValueError(f"Invalid image file: {e}")


def resize_image(image: np.ndarray, max_size: int = 640) -> np.ndarray:
    """
    Resize image while maintaining aspect ratio.

    Args:
        image: NumPy array
        max_size: Maximum dimension (width or height)

    Returns:
        Resized NumPy array
    """
    h, w = image.shape[:2]

    if max(h, w) <= max_size:
        return image

    scale = max_size / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)

    pil_image = Image.fromarray(image)
    pil_image = pil_image.resize((new_w, new_h), Image.LANCZOS)

    return np.array(pil_image)


def image_to_bytes(image: np.ndarray, format: str = "JPEG") -> bytes:
    """
    Convert NumPy array to bytes.

    Args:
        image: NumPy array
        format: Image format (JPEG, PNG)

    Returns:
        Image bytes
    """
    pil_image = Image.fromarray(image)
    buffer = io.BytesIO()
    pil_image.save(buffer, format=format)
    return buffer.getvalue()
