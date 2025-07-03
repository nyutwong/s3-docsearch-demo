import os
import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Body, File, UploadFile, Form
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import io

load_dotenv()
MOCK_BUCKET_NAME = "docsearch-s3-bucket"

s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
        region_name='ap-southeast-2'
    )

app = FastAPI()

class ImageMetadata(BaseModel):
    name: str
    user_id: str

@app.post("/upload_image", summary="Upload an image with metadata", description="Upload an image to S3 with metadata.", response_description="Confirmation of upload", tags=["Image Operations"])
async def upload_image(
    image_id: str = Query(..., example="image_123"), 
    file: UploadFile = File(...),
    alt: str = Form(...),
    user_id: str = Form(...)
):
    file_bytes = await file.read()  # Read uploaded file content
    metadata_dict = {"alt": alt, "user_id": user_id}
    s3.put_object(
        Bucket=MOCK_BUCKET_NAME,
        Key=f'{image_id}',  # Use image_id directly as the key
        Body=file_bytes,
        ContentType=file.content_type,
        ACL='private',
        Metadata=metadata_dict
    )
    return JSONResponse(content={"message": f"Uploaded {image_id} with metadata {metadata_dict}"})

@app.get("/get_image_url")
def get_image_url(image_id: str = Query(..., example="image_123")):
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': MOCK_BUCKET_NAME, 'Key': f'{image_id}'},
        ExpiresIn=3600
    )
    return JSONResponse(content={"url": url})

@app.get("/get_image_content")
def get_image_content(image_id: str = Query(..., example="image_123")):
    response = s3.get_object(Bucket=MOCK_BUCKET_NAME, Key=f'{image_id}')
    return StreamingResponse(io.BytesIO(response['Body'].read()), media_type="image/jpeg")

def main():
    pass  # Placeholder for the main function

if __name__ == "__main__":
    print("FastAPI server is ready")
