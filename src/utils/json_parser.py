# © 2024 Amazon Web Services, Inc. or its affiliates. All Rights Reserved
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at http://aws.amazon.com/agreement or other written agreement between Customer and either Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
# License terms can be found at: https://aws.amazon.com/legal/aws-ip-license-terms/

import json
import re
from typing import Dict, Optional


def parse_json_response(response_text: str) -> Optional[Dict]:
    """Extract and parse JSON response enclosed in ```json ... ``` markers."""
    try:
        # Extract content between ```json and ``` markers
        pattern = r'```json\n(.*?)```'
        match = re.search(pattern, response_text, re.DOTALL)
        
        if not match:
            print("No JSON block found between ```json ... ``` markers.")
            return None
        
        json_text = match.group(1)
        
        # Replace single quotes with double quotes
        json_text = json_text.replace("'", '"')
        
        # Parse the JSON
        return json.loads(json_text)
        
    except Exception as e:
        print(f"Error parsing JSON: {str(e)}")
        return None

def get_local_json(path: str) -> Dict:
    """Load JSON data from local file."""
    with open(path, 'r') as f:
        json_data = json.load(f)
    return json_data