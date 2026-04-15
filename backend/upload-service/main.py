from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import aiofiles
from datetime import datetime
import uvicorn

app = FastAPI(title="Upload Service", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 上传配置
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "images"), exist_ok=True)

class UploadResponse(BaseModel):
    url: str
    filename: str
    size: int

class UploadResult(BaseModel):
    success: bool
    data: UploadResponse
    message: str

@app.get("/")
def read_root():
    return {"service": "Upload Service", "status": "running"}

@app.post("/api/upload/image", response_model=UploadResult)
async def upload_image(file: UploadFile = File(...)):
    """上传单张图片"""
    try:
        # 验证文件类型
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型，仅支持: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # 读取文件内容检查大小
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="文件大小超过5MB限制")

        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        new_filename = f"{timestamp}_{unique_id}{ext}"

        # 保存文件
        file_path = os.path.join(UPLOAD_DIR, "images", new_filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)

        # 返回URL（实际环境应使用CDN或MinIO）
        url = f"/uploads/images/{new_filename}"

        return UploadResult(
            success=True,
            data=UploadResponse(
                url=url,
                filename=new_filename,
                size=len(content)
            ),
            message="上传成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/images", response_model=dict)
async def upload_images(files: list[UploadFile] = File(...)):
    """批量上传图片"""
    if len(files) > 9:
        raise HTTPException(status_code=400, detail="最多上传9张图片")

    results = []
    for file in files:
        try:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "message": "不支持的文件类型"
                })
                continue

            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "message": "文件过大"
                })
                continue

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_id = uuid.uuid4().hex[:8]
            new_filename = f"{timestamp}_{unique_id}{ext}"

            file_path = os.path.join(UPLOAD_DIR, "images", new_filename)
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)

            results.append({
                "filename": new_filename,
                "url": f"/uploads/images/{new_filename}",
                "success": True,
                "message": "上传成功"
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "message": str(e)
            })

    return {"results": results}

@app.delete("/api/upload/image/{filename}")
async def delete_image(filename: str):
    """删除图片"""
    try:
        file_path = os.path.join(UPLOAD_DIR, "images", filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": "删除成功"}
        else:
            raise HTTPException(status_code=404, detail="文件不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
