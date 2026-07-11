from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.cloudinary_upload import upload_image, delete_image

router = APIRouter(prefix="/api/upload", tags=["Upload"])

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        result = upload_image(file)
        return {"url": result["secure_url"], "public_id": result["public_id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{public_id}")
async def delete_file(public_id: str):
    try:
        result = delete_image(public_id)
        return {"message": "File deleted successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))