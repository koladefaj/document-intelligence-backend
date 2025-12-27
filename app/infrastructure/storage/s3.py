from minio import Minio
from io import BytesIO
from app.infrastructure.config import settings

client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=settings.minio_secure,
)

def ensure_bucket():
    if not client.bucket_exists(settings.minio_bucket):
        client.make_bucket(settings.minio_bucket)

def upload_file(file_name: str, data: bytes, content_type: str):
    ensure_bucket()

    buffer = BytesIO(data)
    client.put_object(
        bucket_name=settings.minio_bucket,
        object_name=file_name,
        data=buffer,
        length=len(data),
        content_type=content_type,
    )
    return f"{settings.minio_bucket}/{file_name}"


