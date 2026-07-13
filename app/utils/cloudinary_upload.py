# app/utils/cloudinary_upload.py
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
import os
from app.config import settings

# កំណត់រចនាសម្ព័ន្ធ Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

async def upload_image(file: UploadFile):
    """
    ផ្ទុករូបភាពទៅ Cloudinary
    """
    try:
        # អានមាតិការបស់ File
        file_content = await file.read()
        
        # ផ្ទុកទៅ Cloudinary
        result = cloudinary.uploader.upload(
            file_content,
            folder="e-commerce",
            resource_type="auto"
        )
        return result
    except Exception as e:
        raise Exception(f"Cloudinary upload failed: {str(e)}")

def delete_image(public_id: str):
    """
    លុបរូបភាពពី Cloudinary
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result
    except Exception as e:
        raise Exception(f"Cloudinary delete failed: {str(e)}")