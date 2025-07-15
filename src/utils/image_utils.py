# © 2024 Amazon Web Services, Inc. or its affiliates. All Rights Reserved
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at http://aws.amazon.com/agreement or other written agreement between Customer and either Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
# License terms can be found at: https://aws.amazon.com/legal/aws-ip-license-terms/

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


def draw_gridlines(image: Image.Image, grid_spacing: int = 20, add_gridnumbers: bool = False) -> Image.Image:
    """
    Draw gridlines on the image with a specified spacing.
    
    Args:
        image: PIL Image object
        grid_spacing: Spacing between gridlines (in pixels)
        add_gridnumbers: Whether to add coordinate numbers
    
    Returns:
        PIL Image with gridlines drawn
    """
    draw_image = image.copy()
    draw = ImageDraw.Draw(draw_image)
    width, height = image.size
    font = ImageFont.load_default()
    
    # Draw vertical lines
    for x in range(grid_spacing, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill='black', width=1)
        if add_gridnumbers:
            draw.text((x + 5, 5), str(x), font=font, fill='black')
    
    # Draw horizontal lines
    for y in range(grid_spacing, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill='black', width=1)
        if add_gridnumbers:
            draw.text((5, y - 10), str(y), font=font, fill='black')
    
    return draw_image


def get_image_bytes_with_gridlines(image_bytes: bytes, grid_spacing: int = 20, add_gridnumbers: bool = False) -> bytes:
    """Convert image bytes to image with gridlines and return as bytes."""
    with Image.open(BytesIO(image_bytes)) as image:
        image_with_grid = draw_gridlines(image, grid_spacing, add_gridnumbers)
        buffer = BytesIO()
        image_with_grid.save(buffer, format='PNG')
        return buffer.getvalue()