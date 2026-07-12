import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import UploadFile
from app.config import settings

try:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET
    )
except Exception as e:
    print(f"Cloudinary config skipped: {e}")

def upload_image(file: UploadFile):
    """
    ផ្ទុករូបភាពទៅ Cloudinary
    """
    try:
        result = cloudinary.uploader.upload(
            file.file,
            folder="ecommerce_products",
            resource_type="auto"
        )
        return {
            "secure_url": result["secure_url"],
            "public_id": result["public_id"],
            "url": result["url"]
        }
    except Exception as e:
        print("="*50)
        print("CLOUDINARY ERROR DETAILS:")
        print(str(e))
        print("="*50)
        raise Exception(f"Cloudinary upload error: {str(e)}")

def delete_image(public_id: str):
    """
    លុបរូបភាពពី Cloudinary
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result
    except Exception as e:
        print("="*50)
        print("CLOUDINARY DELETE ERROR DETAILS:")
        print(str(e))
        print("="*50)
        raise Exception(f"Cloudinary delete error: {str(e)}")
