import os
import boto3
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
        region_name='ap-southeast-2'
    )

def upload_image(file_bytes, image_id, bucket_name):
        s3.put_object(
            Bucket=bucket_name,
            Key=f'images/{image_id}.jpg',
            Body=file_bytes,
            ContentType='image/jpeg',
            ACL='private'
        )
        
def get_image_url(image_id, bucket_name, expires_in=3600):
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': f'images/{image_id}.jpg'},
        ExpiresIn=expires_in  # วินาที
    )
    return url

def main():
    bucket_name = os.getenv('AWS_BUCKET_NAME')
    images_folder = 'images/'

    for image_name in os.listdir(images_folder):
        image_path = os.path.join(images_folder, image_name)
        with open(image_path, 'rb') as image_file:
            upload_image(image_file.read(), image_name.split('.')[0], bucket_name)
            print(f"Uploaded {image_name} to S3")

            url = get_image_url(image_name.split('.')[0], bucket_name)
            print(f"Access URL: {url}")


if __name__ == "__main__":
    main()
