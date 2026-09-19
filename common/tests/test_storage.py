import uuid

import pytest
from botocore.exceptions import ClientError

from common import storage
from common.config import settings


def _minio_up() -> bool:
    try:
        storage.internal.list_buckets()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _minio_up(), reason="MinIO is not running")


@pytest.fixture(scope="module", autouse=True)
def bucket():
    storage.ensure_bucket()


def test_ensure_bucket_is_idempotent():
    storage.ensure_bucket()
    storage.ensure_bucket()


def test_exists_true_after_upload():
    key = f"tests/{uuid.uuid4()}.txt"
    storage.internal.put_object(Bucket=storage.BUCKET, Key=key, Body=b"hello")
    assert storage.exists(key) is True


def test_exists_false_for_missing_key():
    assert storage.exists(f"tests/{uuid.uuid4()}.txt") is False


def test_upload_url_is_signed_for_the_key():
    url = storage.upload_url("projects/abc.blend")
    assert "projects/abc.blend" in url
    assert "X-Amz-Signature" in url


def test_exists_raises_on_bad_credentials(monkeypatch):
    wrong = storage.make_client(settings.S3_INTERNAL_ENDPOINT,
                                settings.S3_ACCESS_KEY, "definitely-wrong-secret")
    monkeypatch.setattr(storage, "internal", wrong)
    with pytest.raises(ClientError):
        storage.exists("anything")