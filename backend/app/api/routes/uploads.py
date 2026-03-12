import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.config import get_settings
from app.core.deps import get_current_user, require_csrf
from app.models import User


router = APIRouter()

ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


@router.post("/image")
async def upload_image(
    _: None = Depends(require_csrf),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
) -> dict:
    settings = get_settings()
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    content = await file.read()
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")
    suffix = ALLOWED_TYPES[file.content_type]
    sub_dir = settings.uploads_dir / "images"
    sub_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{current_user.id}-{secrets.token_hex(8)}{suffix}"
    target = Path(sub_dir / filename)
    target.write_bytes(content)
    return {"url": f"/uploads/images/{filename}"}
