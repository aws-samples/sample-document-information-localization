# Document Information Localization with MLLMs

A Python Sample for extracting and evaluating bounding boxes in document images using Multi-modal Large Language Models (MLLMs) on Amazon Bedrock.

## Features

- Extract bounding boxes from document images using MLLMs
- Evaluate predictions against ground truth with comprehensive metrics
- Support for multiple AWS Bedrock models
- Configurable field schemas and prompt templates
- Built-in evaluation metrics (IoU, precision, recall, F1, AP)

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from src.localization import BoundingBoxExtractor, BBoxEvaluator
from src.utils.bedrock_helper import NOVA_PRO_MODEL_ID

# Initialize extractor
extractor = BoundingBoxExtractor(
    model_id=NOVA_PRO_MODEL_ID,
    prompt_template_file="src/prompts/localization_normalized.txt",
    field_config={"invoice_number": {"type": "string"}},
    norm=1000  # For normalized coordinates
)

# Extract bounding boxes
with open("document.png", "rb") as f:
    image_bytes = f.read()
    
bboxes, metadata = extractor.get_bboxes(image_bytes)
print(f"Extracted bboxes: {bboxes}")
```

## Project Structure

```
├── src/                    # Main source code
│   ├── localization.py     # Core extraction and evaluation classes
│   ├── prompts/           # Prompt templates
│   └── utils/             # Utility functions
│       ├── bedrock_helper.py  # AWS Bedrock client
│       ├── json_parser.py     # JSON parsing utilities
│       ├── bbox_drawing.py    # Bounding box visualization
│       ├── image_utils.py     # Image processing utilities
│       ├── s3_helper.py       # S3 utilities
│       └── schema_utils.py    # Schema manipulation
├── examples/              # Usage examples and sample data
│   ├── simple_demo.ipynb # Getting started notebook
│   └── resources/         # Sample documents and annotations
└── requirements.txt       # Python dependencies
```

## Configuration

1. Set up AWS credentials with Bedrock access
2. Customize field schemas and prompts in `src/prompts/`
3. Available prompt templates:
   - `localization_normalized.txt` - For normalized coordinates (0-1000)
   - `localization_dimensions.txt` - For absolute pixel coordinates

## Examples

See `examples/simple_usage.ipynb` for a complete walkthrough.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

