# © 2024 Amazon Web Services, Inc. or its affiliates. All Rights Reserved
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at http://aws.amazon.com/agreement or other written agreement between Customer and either Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
# License terms can be found at: https://aws.amazon.com/legal/aws-ip-license-terms/

from typing import Dict, List, Any


def get_structure(obj: Any) -> Any:
    """Extract schema structure from a given object."""
    if isinstance(obj, dict):
        if 'bbox' in obj:
            return {'bbox': get_structure(obj['bbox'])}
        else:
            return {k: get_structure(v) for k, v in obj.items() if get_structure(v)}
    elif isinstance(obj, list):
        return [get_structure(obj[0])] if obj else []
    else:
        return type(obj).__name__


def split_schema(schema: Dict, num_parts: int) -> List[Dict]:
    """Split schema into multiple parts for processing."""
    if num_parts == 1:
        return [schema]
    else:
        part_size = len(schema) // num_parts
        parts = [dict(list(schema.items())[i:i+part_size]) for i in range(0, len(schema), part_size)]
        return parts