# © 2024 Amazon Web Services, Inc. or its affiliates. All Rights Reserved
# This AWS Content is provided subject to the terms of the AWS Customer Agreement available at http://aws.amazon.com/agreement or other written agreement between Customer and either Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
# License terms can be found at: https://aws.amazon.com/legal/aws-ip-license-terms/

import boto3
from botocore.config import Config

NOVA_PREMIER_MODEL_ID = "us.amazon.nova-premier-v1:0"
NOVA_PRO_MODEL_ID = "us.amazon.nova-pro-v1:0"
NOVA_LITE_MODEL_ID = "us.amazon.nova-lite-v1:0"
SONNET_37_MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
SONNET_35_V2_MODEL_ID = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

BEDROCK_WEST_CONFIG = Config(
    region_name='us-west-2',
    signature_version='v4',
    read_timeout=500,
    retries={
        'max_attempts': 10,
        'mode': 'adaptive'
    }
)

BEDROCK_RT_WEST = boto3.client("bedrock-runtime", config=BEDROCK_WEST_CONFIG)

def get_converse_response(messages, system, max_tokens, temperature, model_id):
    response = BEDROCK_RT_WEST.converse(
        modelId= model_id,
        messages=messages,
        system=system,
        inferenceConfig={'maxTokens': max_tokens, "temperature": temperature}
    )
    return response