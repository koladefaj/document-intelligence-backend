from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
import uuid
from app.infrastructure.db.session import get_session
from app.infrastructure.storage.s3 import upload_file
from app.infrastructure.auth.dependencies import get_current_user
from app.infrastructure.db.models import Document


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def upload_document(
        file: UploadFile = File(...),
        session: AsyncSession = Depends(get_session),
        user = Depends(get_current_user),
):
    try:
        file_bytes = await file.read()
        file_id = f"{uuid.uuid4()}-{file.filename}"

        # Upload to S3 / MinIO
        url = upload_file(file_id, file_bytes, file.content_type)

        # Save metadata in database
        doc = Document(
            file_name=file.filename,
            content = file.content_type,
            url=url,
            owner_id=user.id
        )
        session.add(doc)
        await session.commit()

        return {
            "message": "Upload Successful",
            "document_id": str(doc.id),
            "file_name": file.filename,
            "url": url
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
