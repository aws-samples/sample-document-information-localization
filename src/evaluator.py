# © 2024 Amazon Web Services, Inc. or its affiliates. All Rights Reserved
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at http://aws.amazon.com/agreement or other written agreement between Customer and either Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
# License terms can be found at: https://aws.amazon.com/legal/aws-ip-license-terms/

from typing import Dict, List, Optional, Tuple, Union, NamedTuple
import numpy as np

class BBoxEvaluator:
    """Evaluates bounding box predictions against ground truth."""

    class FieldResult(NamedTuple):
        iou: float
        precision: float
        recall: float
        f1: float
        ap: float

    def __init__(self, field_config: Dict):
        self.field_config = field_config
        self.iou_threshold = 0.5
        self.margin_percent = 5

    def evaluate(self, y_pred: Dict, y_true: Dict) -> Dict:
        """Evaluate predictions against ground truth."""
        scores = {}
        for field, config in self.field_config.items():
            true_config = y_true.get(field, None)
            true_bbox = self._extract_bbox(true_config)
            pred_config = y_pred.get(field, None)
            pred_bbox = self._extract_bbox(pred_config)
            
            if true_bbox is not None:
                if pred_bbox is not None:
                    try:
                        metrics = self._get_metrics(pred_bbox, true_bbox, y_true, field)
                        if isinstance(metrics, (list, tuple)) and len(metrics) == 5:
                            precision, recall, f1, ap, iou = metrics
                            scores[field] = self.FieldResult(iou=iou, precision=precision, recall=recall, f1=f1, ap=ap)
                        else:
                            print(f"Unexpected metrics format for field {field}: {metrics}")
                            scores[field] = self.FieldResult(iou=0, precision=0, recall=0, f1=0, ap=0)
                    except Exception as e:
                        print(f"Error processing field {field}: {str(e)}")
                        scores[field] = self.FieldResult(iou=0, precision=0, recall=0, f1=0, ap=0)
                else:
                    scores[field] = self.FieldResult(iou=0, precision=0, recall=0, f1=0, ap=0)

        mean_ap = np.mean([result.ap for result in scores.values()]) if scores else 0
        return {
            "mean_ap": mean_ap,
            "field_scores": scores
        }

    def _extract_bbox(self, value: Union[Dict, List]) -> Optional[List[List[float]]]:
        """Extract bounding box from data structure based on the config schema."""
        def _extract_bbox_dict(data_dict: Dict) -> Optional[List[List[float]]]:
            if 'bbox' in data_dict and isinstance(data_dict['bbox'], list):
                return data_dict['bbox']
            return None

        if isinstance(value, list):
            for v in value:
                bbox = self._extract_bbox(v)
                if bbox is not None:
                    return bbox
        elif isinstance(value, dict):
            return _extract_bbox_dict(value)

        return None
    
    def _get_metrics(self, preds: List[List[float]], gt_results: List[List[float]], bbox_list: Dict, entity: str) -> Tuple[float, float, float, float, float]:
        """Calculate evaluation metrics."""
        iou = self._get_iou(preds, gt_results, bbox_list, entity)
        
        tp = 1 if iou >= self.iou_threshold else 0
        fp = 1 - tp
        fn = 0 if tp == 1 else 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        ap = precision * recall

        return precision, recall, f1, ap, iou

    def _get_iou(self, prediction: List[List[float]], gt: List[List[float]], bboxes: Dict, entity: str) -> float:
        """Calculate Intersection over Union (IoU)."""
        xp1, yp1 = min(prediction[0][0], prediction[1][0]), min(prediction[0][1], prediction[1][1])
        xp2, yp2 = max(prediction[0][0], prediction[1][0]), max(prediction[0][1], prediction[1][1])
        
        xg1, yg1 = min(gt[0][0], gt[1][0]), min(gt[0][1], gt[1][1])
        xg2, yg2 = max(gt[0][0], gt[1][0]), max(gt[0][1], gt[1][1])
        
        margin = (self.margin_percent / 100) * abs(yp1 - yg1)
        
        if xp1 <= xg1 and (abs(yp1 - yg1) < margin) and xg2 <= xp2 and (abs(yp1 - yg1) < margin):
            if not self._predicted_overlap(prediction, bboxes, entity):
                xp1, yp1, xp2, yp2 = xg1, yg1, xg2, yg2
            
        x_left, y_top = max(xp1, xg1), max(yp1, yg1)
        x_right, y_bottom = min(xp2, xg2), min(yp2, yg2)
        
        inter_area = max(0, x_right - x_left) * max(0, y_bottom - y_top)
        box1_area = (xp2 - xp1) * (yp2 - yp1)
        box2_area = (xg2 - xg1) * (yg2 - yg1)

        union_area = (box1_area + box2_area) - inter_area
        iou = inter_area / union_area if union_area > 0 else 0
        
        return iou

    def _predicted_overlap(self, prediction: List[List[float]], json_content: Dict, current_entity: str) -> bool:
        """Check if prediction overlaps with other entities."""
        xp1, yp1 = min(prediction[0][0], prediction[1][0]), min(prediction[0][1], prediction[1][1])
        xp2, yp2 = max(prediction[0][0], prediction[1][0]), max(prediction[0][1], prediction[1][1])
        
        bounding_list = []
        for field, config in self.field_config.items():
            if field != current_entity:
                bbox = self._extract_bbox(json_content.get(field))
                if bbox:
                    bounding_list.append(bbox)
        
        for bbox in bounding_list:
            xb1, yb1 = min(bbox[0][0], bbox[1][0]), min(bbox[0][1], bbox[1][1])
            xb2, yb2 = max(bbox[0][0], bbox[1][0]), max(bbox[0][1], bbox[1][1])
            
            if not (xp2 < xb1 or xp1 > xb2 or yp2 < yb1 or yp1 > yb2):
                return True
        
        return False