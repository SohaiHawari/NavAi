"""
NavAI - EasyOCR Text Extraction Module
Extracts readable text from images (signboards, labels, etc.)
"""

import logging
import numpy as np
import easyocr

logger = logging.getLogger("NavAI.OCR")


class OCREngine:
    """
    OCR engine using EasyOCR for text extraction.

    Supports multiple languages including English and Hindi.
    Optimized for signboards, labels, and printed text.
    """

    def __init__(self, languages: list = None):
        """
        Initialize EasyOCR reader.

        Args:
            languages: List of language codes (e.g., ['en', 'hi'])
        """
        if languages is None:
            languages = ["en"]

        logger.info(f"Initializing EasyOCR with languages: {languages}")
        self.reader = easyocr.Reader(languages, gpu=False)
        logger.info("EasyOCR initialized successfully")

    def extract_text(self, image: np.ndarray) -> list:
        """
        Extract text from an image.

        Args:
            image: NumPy array (BGR or RGB)

        Returns:
            List of text detection results:
            [
                {
                    "text": "EXIT",
                    "confidence": 0.95,
                    "bbox": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]],
                    "position": "center"
                },
                ...
            ]
        """
        try:
            results = self.reader.readtext(image)
            texts = []
            img_width = image.shape[1]

            for (bbox, text, confidence) in results:
                if confidence < 0.3:  # Skip low confidence
                    continue

                # Clean text
                clean_text = text.strip()
                if not clean_text:
                    continue

                # Estimate position from bbox center
                center_x = sum(p[0] for p in bbox) / 4
                position = self._get_text_position(center_x, img_width)

                texts.append({
                    "text": clean_text,
                    "confidence": round(float(confidence), 3),
                    "position": position,
                })

            logger.info(f"Extracted {len(texts)} text regions")
            return texts

        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return []

    def _get_text_position(self, center_x: float, img_width: int) -> str:
        """Estimate text position in the image."""
        third = img_width / 3

        if center_x < third:
            return "left"
        elif center_x < 2 * third:
            return "center"
        else:
            return "right"

    def extract_text_simple(self, image: np.ndarray) -> str:
        """
        Extract and concatenate all text from an image.

        Args:
            image: NumPy array

        Returns:
            Combined text string
        """
        results = self.extract_text(image)
        return " ".join(r["text"] for r in results)
