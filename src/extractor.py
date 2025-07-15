# © 2024 Amazon Web Services, Inc. or its affiliates. All Rights Reserved
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at http://aws.amazon.com/agreement or other written agreement between Customer and either Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
# License terms can be found at: https://aws.amazon.com/legal/aws-ip-license-terms/

from typing import Dict, List, Optional, Any
from io import BytesIO
from PIL import Image

from utils.bedrock_helper import get_converse_response
from utils.json_parser import parse_json_response

class BoundingBoxExtractor:
    """Extracts bounding boxes from document images."""

    def __init__(self, model_id: str, prompt_template_file: str, field_config: Dict, norm: Optional[int] = None):
        self.model_id = model_id
        self.prompt_template_path = prompt_template_file
        self.field_config = field_config
        self.norm = norm
    
    def get_bboxes(self, document_image: bytes, document_text: Optional[str] = None) -> Optional[Dict]:
        """Extract bounding boxes from the document image."""
        img = Image.open(BytesIO(document_image))
        width, height = img.size
        image_ext = "jpeg" if img.format == "JPG" else img.format.lower()     

        system_prompt = self._create_prompt(width, height)
        response = get_converse_response(
            messages=[{"role": "user", "content": [{"image": {"format": image_ext, "source": {"bytes": document_image}}}]}],
            system=[{"text": system_prompt}],
            max_tokens=3000, temperature=0, model_id=self.model_id
        )
        bboxes = parse_json_response(response["output"]["message"]["content"][0]["text"])
        metadata = {
            "usage": response['usage'],
            "metrics": response['metrics']
        }
        return self._adjust_bboxes(bboxes, width, height), metadata

    def _create_prompt(self, width, height):
        """"Optional parameters to use as input for the prompts are "w" for width, "h" for height, "elements" for the elements to be detected, and "schema" for the schema of the bounding boxes"""
        schema = self.field_config
        elements = ", ".join(schema.keys())
        
        with open(self.prompt_template_path, 'r') as file:
            system_prompt = file.read().format(w=width, h=height, elements=elements, schema=schema)
        return system_prompt

    def _adjust_bboxes(self, data: Any, width: int, height: int) -> Any:
        """Adjust bounding boxes based on image dimensions."""
        if isinstance(data, dict):
            return {k: self._normalize_bbox(v, width, height) if k == "bbox" 
                    else self._adjust_bboxes(v, width, height) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._adjust_bboxes(item, width, height) for item in data]
        return data

    def _normalize_bbox(self, bbox: List[Any], width: int, height: int) -> List[float]:
        """Normalize bounding box coordinates."""
        
        # Flatten the bbox if it's nested
        if isinstance(bbox[0], list):
            bbox = [coord for sublist in bbox for coord in sublist]
        
        # Ensure we have exactly 4 coordinates
        if len(bbox) != 4:
            raise ValueError(f"Expected 4 coordinates, got {len(bbox)}")

        x1, y1, x2, y2 = map(float, bbox)
        
        if self.norm is not None:
            x1, x2 = x1 * width / self.norm, x2 * width / self.norm
            y1, y2 = y1 * height / self.norm, y2 * height / self.norm
        
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        return [[x1, height - y2], [x2, height - y1]]