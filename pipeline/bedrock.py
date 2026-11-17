"""Portable Bedrock Converse adapter, adapted from the existing report service.

No client is created at import time. Credentials use the normal AWS chain or
AWS_BEARER_TOKEN_BEDROCK; they never enter saved requests or metadata.
"""
import json
import os
from pathlib import Path

DEFAULT_MODEL = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
DEFAULT_REGION = "ap-southeast-1"


def configuration(root=None):
    defaults = {}
    if root is not None:
        root = Path(root)
        from dotenv import load_dotenv
        load_dotenv(root / ".env", override=False)
        path = root / "config" / "report.json"
        if path.is_file():
            defaults = json.loads(path.read_text()).get("bedrock", {})
    return {
        "model": os.getenv("BEDROCK_MODEL_ID", defaults.get("model_id", DEFAULT_MODEL)),
        "region": os.getenv("BEDROCK_REGION", os.getenv("AWS_REGION", defaults.get("region", DEFAULT_REGION))),
        "max_tokens": int(os.getenv("BEDROCK_MAX_TOKENS", defaults.get("max_tokens", 12000))),
    }


def output_schema(schema):
    """Adapt the known Converse schema subset; keep full limits for local validation."""
    unsupported = {"default", "title", "minimum", "maximum", "exclusiveMinimum",
                   "exclusiveMaximum", "multipleOf", "minLength", "maxLength",
                   "pattern", "maxItems", "uniqueItems", "minProperties", "maxProperties"}

    def adapt(node):
        if isinstance(node, list):
            return [adapt(value) for value in node]
        if not isinstance(node, dict):
            return node
        result = {}
        for key, value in node.items():
            if key in unsupported or (key == "minItems" and value not in (0, 1)):
                continue
            if key in ("properties", "$defs", "definitions"):
                result[key] = {name: adapt(item) for name, item in value.items()}
            else:
                result[key] = adapt(value)
        if result.get("type") == "object":
            result["additionalProperties"] = False
            result["required"] = list(result.get("properties", {}))
        return result

    return adapt(schema.model_json_schema())


def create_client(settings):
    import boto3
    from botocore.config import Config
    # Boto3 supports both bearer authentication and the configured credential
    # provider chain. Unlike the old service, a bearer token is not mandatory.
    return boto3.client(
        "bedrock-runtime", region_name=settings["region"],
        endpoint_url=os.getenv("BEDROCK_ENDPOINT_URL") or None,
        config=Config(connect_timeout=10, read_timeout=600,
                      retries={"mode": "standard", "total_max_attempts": 1}),
    )


def generate_structured(system_prompt, content, schema, settings, client=None):
    if "claude-haiku-4-5" not in settings["model"]:
        raise ValueError("This packaged transport is configured for Claude Haiku 4.5; review transport settings before switching model families.")
    client = client or create_client(settings)
    response = client.converse(
        modelId=settings["model"],
        messages=[{"role": "user", "content": content}],
        system=[{"text": system_prompt}],
        inferenceConfig={"maxTokens": settings["max_tokens"]},
        additionalModelRequestFields={"thinking": {"type": "disabled"}},
        outputConfig={"textFormat": {
            "type": "json_schema", "structure": {"jsonSchema": {
                "name": schema.__name__,
                "schema": json.dumps(output_schema(schema), ensure_ascii=False),
            }},
        }},
    )
    if response.get("stopReason") != "end_turn":
        raise ValueError("Bedrock did not finish the section; no accepted output was written.")
    text = "".join(block["text"] for block in
                   response.get("output", {}).get("message", {}).get("content", [])
                   if "text" in block)
    if not text:
        raise ValueError("Bedrock returned no structured section.")
    result = schema.model_validate_json(text).model_dump()
    metadata = {"model": settings["model"], "region": settings["region"],
                "stop_reason": response["stopReason"], "usage": response.get("usage", {})}
    return result, metadata
