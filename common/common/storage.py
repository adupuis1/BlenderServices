import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from common.config import settings

BUCKET = settings.S3_BUCKET


# request_checksum_calculation="when_required" stops boto3 adding a checksum
# header the presigned URL was not signed for. Without it a plain PUT from
# curl or a browser against a URL this module generated is rejected.

S3_CONFIG = Config(
    signature_version="s3v4",
    request_checksum_calculations="when_required",
    response_checksum_validation="when_supported",
    retries={"max_attempts": 5, "mode": "standard"},
)

NOT_FOUND = {"404", "NoSuchKey", "NoSuchBucket", "NotFound"}