from fastapi import APIRouter, UploadFile, File, Query, HTTPException
import os
import shutil
import uuid

router = APIRouter()

BASE_UPLOAD_DIR = "uploads"

ALLOWED_MIME_TYPES = ["image/jpeg", "image/png"]
MAX_FILE_SIZE_MB = 5

@router.post("/upload-image")
async def upload_image(
    folder: str = Query(..., description="Folder name like 'profiles', 'documents', etc."),
    file: UploadFile = File(...)
):
    # Validate file type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG or PNG images allowed")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB")

    # Reset file read pointer
    await file.seek(0)

    target_dir = os.path.join(BASE_UPLOAD_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)

    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(target_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_url = f"/uploads/{folder}/{filename}"

    return {"message": "Image uploaded successfully", "url": file_url}
