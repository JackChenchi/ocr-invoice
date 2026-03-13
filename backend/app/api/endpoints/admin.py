from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.services.cleanup_service import cleanup_old_records

router = APIRouter()


@router.post("/cleanup")
def cleanup(
    *,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="没有权限执行清理")
    result = cleanup_old_records(
        db,
        settings.DATA_RETENTION_DAYS,
        settings.IMAGE_RETENTION_DAYS
    )
    return {"message": "清理完成", "result": result}
