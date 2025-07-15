# © 2024 Amazon Web Services, Inc. or its affiliates. All Rights Reserved
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at http://aws.amazon.com/agreement or other written agreement between Customer and either Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
# License terms can be found at: https://aws.amazon.com/legal/aws-ip-license-terms/

import boto3
import json
from typing import Dict, Any

boto3.setup_default_session(profile_name='early_access', region_name='us-west-2')

S3_CLIENT = boto3.client('s3')


def get_s3_json(bucket: str, key: str) -> Dict[str, Any]:
    """Retrieve and parse JSON object from S3."""
    response = S3_CLIENT.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')
    return json.loads(content)


def get_s3_image(bucket: str, key: str) -> bytes:
    """Retrieve image bytes from S3."""
    response = S3_CLIENT.get_object(Bucket=bucket, Key=key)
    image_bytes = response['Body'].read()
    return image_bytes
