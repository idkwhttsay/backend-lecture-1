import io

from fastapi import FastAPI, File, HTTPException, UploadFile
from google.cloud import storage

app = FastAPI()

BUCKET_NAME = "5lectuer"
CHUNK_SIZE = 8 * 1024 * 1024  # 8MB chunks


def upload_large_file_to_gcs(file: UploadFile, bucket_name: str,
                             chunk_size: int = CHUNK_SIZE):
    """Upload large files to GCS using chunked uploads"""
    try:
        # Create GCS client
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"shoqqan_test/{file.filename}")
        
        # Get file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        # If file is small, use regular upload
        if file_size <= chunk_size:
            blob.upload_from_file(file.file, content_type=file.content_type)
            blob.make_public()
            return blob.public_url
        
        # For large files, use chunked upload
        # Set chunk size for the blob
        blob.chunk_size = chunk_size
        
        # Upload the file in chunks
        blob.upload_from_file(
            file.file, 
            content_type=file.content_type,
            size=file_size,
            checksum=None
        )
        
        # Make blob public and return URL
        blob.make_public()
        return blob.public_url
        
    except Exception as e:
        error_msg = f"Upload failed: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


def upload_file_in_chunks(file: UploadFile, bucket_name: str, chunk_size: int):
    """Alternative chunked upload implementation using manual chunking"""
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"shoqqan_test/{file.filename}")
        
        # Get file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        # Read and upload file in chunks
        chunks_uploaded = 0
        total_chunks = (file_size + chunk_size - 1) // chunk_size
        
        # Create a bytes buffer to collect all chunks
        file_data = io.BytesIO()
        
        while True:
            chunk = file.file.read(chunk_size)
            if not chunk:
                break
            file_data.write(chunk)
            chunks_uploaded += 1
        
        # Reset buffer position and upload
        file_data.seek(0)
        blob.upload_from_file(
            file_data,
            content_type=file.content_type,
            size=file_size
        )
        
        return blob.public_url, chunks_uploaded, total_chunks
        
    except Exception as e:
        error_msg = f"Chunked upload failed: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


def upload_to_gcs(file: UploadFile, bucket_name: str):
    """Simple upload for smaller files (kept for backward compatibility)"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"shoqqan_test/{file.filename}")
    blob.upload_from_file(file.file, content_type=file.content_type)
    blob.make_public()
    return blob.public_url


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Upload endpoint that automatically handles both small and large files"""
    try:
        url = upload_large_file_to_gcs(file, BUCKET_NAME)
        return {
            "filename": file.filename, 
            "url": url,
            "message": "File uploaded successfully using chunked upload"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload/chunked/")
async def upload_file_chunked(file: UploadFile = File(...),
                              chunk_size_mb: int = 8):
    """Upload endpoint with configurable chunk size (in MB)"""
    try:
        chunk_size_bytes = chunk_size_mb * 1024 * 1024
        url, chunks_uploaded, total_chunks = upload_file_in_chunks(
            file, BUCKET_NAME, chunk_size_bytes
        )
        return {
            "filename": file.filename,
            "url": url,
            "chunk_size_mb": chunk_size_mb,
            "chunks_uploaded": chunks_uploaded,
            "total_chunks": total_chunks,
            "message": f"File uploaded using {chunk_size_mb}MB chunks"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {
        "message": "File Upload API with Chunked Upload Support",
        "endpoints": {
            "/upload/": "Upload files (auto chunked for large files)",
            "/upload/chunked/": "Upload files with configurable chunk size",
        }
    }
