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
    request_checksum_calculation="when_required",
    response_checksum_validation="when_supported",
    retries={"max_attempts": 5, "mode": "standard"},
)

NOT_FOUND = {"404", "NoSuchKey", "NoSuchBucket", "NotFound"}

def _client(endpoint: str):
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name="us-east-1",
        config=S3_CONFIG
    )

internal = _client(settings.S3_INTERNAL_ENDPOINT)
public = _client(settings.S3_PUBLIC_ENDPOINT)

def _code(exc: ClientError) -> str:
    return str(exc.response.get("Error", {}).get("Code", ""))

def ensure_bucket() -> None:
    try:
        internal.head_bucket(Bucket=BUCKET)
        return
    except ClientError as exc:
        if _code(exc) not in NOT_FOUND:
            raise
    try:
        internal.create_bucket(Bucket=BUCKET)
    except ClientError as exc:
        if _code(exc) not in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            raise


def upload_url(key: str, expires: int = 900) -> str:
    return public.generate_presigned_url(
        "put_object", Params={"Bucket": BUCKET, "Key": key}, ExpiresIn=expires
    )


def download_url(key: str, expires: int = 900) -> str:
    return public.generate_presigned_url(
        "get_object", Params={"Bucket": BUCKET, "Key": key}, ExpiresIn=expires
    )


def exists(key: str) -> bool:
    try:
        internal.head_object(Bucket=BUCKET, Key=key)
        return True
    except ClientError as exc:
        if _code(exc) in NOT_FOUND:
            return False
        raise