from typing import List, Dict, Tuple
from PIL import Image
import numpy as np
import cv2
import torch
from transformers import Owlv2Processor, Owlv2ForObjectDetection


class UIDetector:
    def __init__(self, model_name: str = "google/owlv2-base-patch16"):
        self.processor = Owlv2Processor.from_pretrained(model_name)
        self.model = Owlv2ForObjectDetection.from_pretrained(model_name)
        self.model.eval()

    def detect(self, image: Image.Image, labels: List[str], score_thresh: float = 0.3) -> List[Dict]:
        """Run zero-shot detection on an image.

        Returns list of dicts: {label, score, bbox=(x1,y1,x2,y2)}
        """
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(device)

        # OWL-ViT expects list of texts per image, each can be list of queries
        text_queries = [labels]
        inputs = self.processor(text=text_queries, images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Post-process to get boxes/scores per label
        # target_sizes expects (h, w)
        w, h = image.size
        processed = self.processor.post_process_object_detection(
            outputs=outputs, target_sizes=[(h, w)]
        )[0]

        boxes = processed["boxes"].cpu().numpy()
        scores = processed["scores"].cpu().numpy()
        labels_idx = processed["labels"].cpu().numpy()  # index into provided labels list

        detections: List[Dict] = []
        for box, score, lbl_idx in zip(boxes, scores, labels_idx):
            if score < score_thresh:
                continue
            x1, y1, x2, y2 = box.astype(int).tolist()
            label = labels[int(lbl_idx)]
            detections.append({
                "label": label,
                "score": float(score),
                "bbox": (x1, y1, x2, y2),
            })
        return detections

    @staticmethod
    def draw_detections(image: Image.Image, detections: List[Dict]) -> np.ndarray:
        """Draw bounding boxes and labels onto image. Returns BGR numpy array suitable for cv2.imwrite."""
        bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            label = det["label"]
            score = det["score"]
            cv2.rectangle(bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
            text = f"{label} {score:.2f}"
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            y_text = max(y1 - 6, th + 2)
            cv2.rectangle(bgr, (x1, y_text - th - 4), (x1 + tw + 4, y_text + 2), (0, 255, 0), -1)
            cv2.putText(bgr, text, (x1 + 2, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        return bgr


