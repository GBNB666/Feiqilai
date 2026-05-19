from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import FormatJob
from app.schemas.job import JobResponse
from app.utils.file_utils import validate_file, save_upload

router = APIRouter()


@router.post("/upload", response_model=JobResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()

    error = validate_file(file.filename or "unknown", len(content))
    if error:
        raise HTTPException(status_code=400, detail=error)

    file_path, file_type = save_upload(content, file.filename or "unknown")

    job = FormatJob(
        original_filename=file.filename or "unknown",
        file_path=file_path,
        file_type=file_type,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return JobResponse.model_validate(job)
