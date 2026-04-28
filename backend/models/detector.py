"""
NavAI - YOLOv8 Object Detection Module
Detects objects and computes spatial positions.
"""

import logging
import numpy as np
from ultralytics import YOLO

logger = logging.getLogger("NavAI.Detector")

# Priority classes relevant for visually impaired navigation
PRIORITY_CLASSES = {
    "person", "chair", "bench", "bottle", "cup", "dining table",
    "door", "stairs", "car", "bus", "truck", "motorcycle", "bicycle",
    "dog", "cat", "fire hydrant", "stop sign", "traffic light",
    "backpack", "handbag", "suitcase", "cell phone", "laptop",
    "tv", "toilet", "sink", "refrigerator", "microwave", "oven",
    "book", "clock", "potted plant", "bed", "couch",
}


class ObjectDetector:
    """
    YOLOv8-based object detector with spatial position estimation.

    Divides the image into thirds (left/center/right) and estimates
    the approximate position of each detected object.
    """

    def __init__(self, model_path: str = "yolov8n.pt", confidence: float = 0.4):
        """
        Initialize the YOLO model.

        Args:
            model_path: Path to YOLO weights (auto-downloads if not found)
            confidence: Minimum confidence threshold for detections
        """
        logger.info(f"Loading YOLO model: {model_path}")
        self.model = YOLO(model_path)
        self.confidence = confidence
        logger.info(f"YOLO model loaded. Classes: {len(self.model.names)}")

    def _get_position(self, bbox: list, img_width: int) -> str:
        """
        Estimate spatial position of an object based on bounding box center.

        Divides image into three vertical zones:
        - Left third: "left"
        - Middle third: "center" (front)
        - Right third: "right"

        Args:
            bbox: [x1, y1, x2, y2] bounding box coordinates
            img_width: Width of the source image

        Returns:
            Position string: "left", "center", or "right"
        """
        center_x = (bbox[0] + bbox[2]) / 2
        third = img_width / 3

        if center_x < third:
            return "left"
        elif center_x < 2 * third:
            return "center"
        else:
            return "right"

    def _get_distance_estimate(self, bbox: list, img_height: int) -> str:
        """
        Rough distance estimate based on bounding box size relative to image.

        Args:
            bbox: [x1, y1, x2, y2] coordinates
            img_height: Height of the image

        Returns:
            Distance estimate: "close", "medium", or "far"
        """
        box_height = bbox[3] - bbox[1]
        ratio = box_height / img_height

        if ratio > 0.5:
            return "very close"
        elif ratio > 0.3:
            return "close"
        elif ratio > 0.15:
            return "medium distance"
        else:
            return "far"

    def detect(self, image: np.ndarray) -> list:
        """
        Run object detection on an image.

        Args:
            image: NumPy array (BGR or RGB format)

        Returns:
            List of detection dictionaries:
            [
                {
                    "label": "person",
                    "confidence": 0.92,
                    "position": "center",
                    "distance": "close",
                    "bbox": [x1, y1, x2, y2]
                },
                ...
            ]
        """
        try:
            results = self.model(image, conf=self.confidence, verbose=False)
            detections = []
            img_height, img_width = image.shape[:2]

            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue

                for box in boxes:
                    cls_id = int(box.cls[0])
                    label = self.model.names[cls_id]
                    conf = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()

                    # Compute spatial info
                    position = self._get_position(bbox, img_width)
                    distance = self._get_distance_estimate(bbox, img_height)

                    detections.append({
                        "label": label,
                        "confidence": round(conf, 3),
                        "position": position,
                        "distance": distance,
                        "bbox": [round(c, 1) for c in bbox],
                        "is_priority": label in PRIORITY_CLASSES,
                    })

            # Sort: priority objects first, then by confidence
            detections.sort(
                key=lambda d: (not d["is_priority"], -d["confidence"])
            )

            logger.info(f"Detected {len(detections)} objects")
            return detections

        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return []

    def detect_obstacles(self, image: np.ndarray) -> list:
        """
        Specifically detect potential obstacles in the path.

        Focuses on objects in the center zone that are close.

        Args:
            image: NumPy array

        Returns:
            List of obstacle warnings
        """
        detections = self.detect(image)
        obstacles = []

        for det in detections:
            if det["position"] == "center" and det["distance"] in ["very close", "close"]:
                obstacles.append({
                    "label": det["label"],
                    "distance": det["distance"],
                    "warning": f"Warning: {det['label']} detected {det['distance']} ahead!",
                })

        return obstacles
