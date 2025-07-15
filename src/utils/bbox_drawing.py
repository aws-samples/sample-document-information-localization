# © 2024 Amazon Web Services, Inc. or its affiliates. All Rights Reserved
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at http://aws.amazon.com/agreement or other written agreement between Customer and either Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
# License terms can be found at: https://aws.amazon.com/legal/aws-ip-license-terms/

import secrets
import colorsys
from io import BytesIO
from typing import Dict, List, Tuple, Union
from PIL import Image, ImageDraw, ImageColor, ImageFont


def get_random_color() -> str:
    """
    Generate a random color with good contrast using secure random.
    
    Returns:
        Hex color string
    """
    hue = secrets.randbelow(1000000) / 1000000.0
    hue = (hue * 0.618033988749895) % 1.0 
    rgb = colorsys.hsv_to_rgb(hue, 0.9, 0.9)
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

def draw_single_bbox(image: Image.Image, bbox: List[List[float]], label: str, color: str = None, min_font_size: int = 12, min_line_width: int = 2) -> None:
    """
    Draw a single bounding box with its label on the image.
    
    Args:
        image: PIL Image object
        bbox: List of coordinates [[x1,y1], [x2,y2]]
        label: String label for the bbox
        color: Color for the bbox and label (optional)
        min_font_size: Minimum font size (optional)
        min_line_width: Minimum line width (optional)
    """
    draw = ImageDraw.Draw(image, "RGBA")
    
    # Calculate scaling factors based on image size
    width, height = image.size
    min_dimension = min(width, height)
    line_width = max(min_line_width, int(min_dimension * 0.003))
    font_size = max(min_font_size, int(min_dimension * 0.015))
    
    # Use default font with larger size
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", font_size) 
    except:
        font = ImageFont.load_default()
    
    # Generate random color if not provided
    if color is None:
        color = get_random_color()

    # Extract coordinates
    x1, y1 = bbox[0]
    x2, y2 = bbox[1]

    # Ensure coordinates are in correct order
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = height - max(y1, y2), height - min(y1, y2)

    # Draw rectangle
    draw.rectangle([x1, y1, x2, y2], outline=ImageColor.getrgb(color) + (100,), width=line_width)

    # Calculate label dimensions
    label_bbox = draw.textbbox((0, 0), label, font=font)
    text_width = label_bbox[2] - label_bbox[0]
    text_height = label_bbox[3] - label_bbox[1]
    
    # Draw label background and text
    draw.rectangle([x1, y1-text_height-2, x1+text_width+4, y1-2], fill=color)
    draw.text((x1+2, y1-text_height-1), label, fill="white", font=font)


def draw_single_bbox(image: Image.Image, bbox: List[List[float]], label: str, color: str = None, min_font_size: int = 12, min_line_width: int = 2) -> None:
    """
    Draw a single bounding box with its label on the image, using the same bbox logic as BBoxEvaluator.
    """
    draw = ImageDraw.Draw(image, "RGBA")
    
    # Calculate scaling factors based on image size
    width, height = image.size
    min_dimension = min(width, height)
    line_width = max(min_line_width, int(min_dimension * 0.003))
    font_size = max(min_font_size, int(min_dimension * 0.015))
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", font_size) 
    except:
        font = ImageFont.load_default()
    
    if color is None:
        color = get_random_color()

    # Extract coordinates using same logic as BBoxEvaluator._get_iou
    xp1, yp1 = min(bbox[0][0], bbox[1][0]), height - max(bbox[0][1], bbox[1][1])
    xp2, yp2 = max(bbox[0][0], bbox[1][0]), height - min(bbox[0][1], bbox[1][1])
    
    # Draw rectangle
    draw.rectangle([xp1, yp1, xp2, yp2], outline=ImageColor.getrgb(color) + (100,), width=line_width)

    # Calculate label dimensions
    label_bbox = draw.textbbox((0, 0), label, font=font)
    text_width = label_bbox[2] - label_bbox[0]
    text_height = label_bbox[3] - label_bbox[1]
    
    # Draw label background and text
    draw.rectangle([xp1, yp1-text_height-2, xp1+text_width+4, yp1-2], fill=color)
    draw.text((xp1+2, yp1-text_height-1), label, fill="white", font=font)

def draw_bounding_boxes(image_bytes: bytes, bounding_data: Dict) -> Image.Image:
    """
    Draw bounding boxes using the same bbox extraction logic as BBoxEvaluator.
    """
    image = Image.open(BytesIO(image_bytes))

    def extract_bbox(value):
        if isinstance(value, dict) and 'bbox' in value:
            return value['bbox']
        return None

    for key, value in bounding_data.items():
        color = get_random_color()
        
        if key == 'TABLE':
            # Handle TABLE separately
            for row in value:
                for cell in row:
                    bbox = extract_bbox(cell)
                    if bbox:
                        draw_single_bbox(image, bbox, f"{key}", color)
        else:
            bbox = extract_bbox(value)
            if bbox:
                draw_single_bbox(image, bbox, key, color)

    return image



def create_masked_image(image_bytes: bytes, predictions: Dict) -> Tuple[Image.Image, bytes]:
    """
    Create masked image from image bytes, masking out areas defined in predictions.
    
    Args:
        image_bytes: Image as bytes
        predictions: Dictionary containing prediction data with bounding boxes
        
    Returns:
        Tuple of (PIL Image, bytes) containing masked image
    """
    import numpy as np
    import io
    
    # Convert bytes to PIL Image
    img = Image.open(io.BytesIO(image_bytes))
    mask = np.ones(np.array(img).shape[:2], dtype=np.uint8) * 255
    
    for category in predictions.values():
        for item in category:
            x1, y1, x2, y2 = map(int, item['bbox'])
            mask[y1:y2, x1:x2] = 0
    
    masked = Image.composite(img, Image.new('RGB', img.size, 0), Image.fromarray(mask))
    
    # Convert masked image back to bytes
    img_byte_array = io.BytesIO()
    masked.save(img_byte_array, format='JPEG')
    img_byte_array = img_byte_array.getvalue()
    
    return masked, img_byte_array
