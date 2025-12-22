# Supabase Storage Setup Guide

This guide explains how to set up Supabase Storage for file uploads in the mOdoo ERP system.

## Prerequisites

1. **Supabase Account**: Create an account at [supabase.com](https://supabase.com)
2. **Supabase Project**: Create a new project in your Supabase dashboard

## Configuration Steps

### 1. Get Your Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **API**
3. Copy the following values:
   - **Project URL**: `https://your-project-id.supabase.co`
   - **service_role key**: Your service role API key

### 2. Create Storage Bucket

1. In your Supabase dashboard, go to **Storage** in the sidebar
2. Click **Create bucket**
4. Set bucket to **Private** for security
5. Click **Create bucket**

### 3. Configure Bucket Policies (Optional)

By default, public buckets allow public access. If you need more restrictive access:

1. Go to **Storage** → **Policies**
2. Create policies for your bucket as needed

### 4. Update Django Settings

Edit `<project-dir>/settings.py` and replace the placeholder values:

```python
# Supabase Storage Configuration
SUPABASE_URL = 'https://your-project-id.supabase.co'  # Your actual project URL (NO trailing slash)
SUPABASE_SERVICE_KEY = 'your-service-key'  # Your actual service key
SUPABASE_STORAGE_BUCKET = 'your-bucket-name'  # Bucket name you created
```

**Important**: The `SUPABASE_URL` should NOT include a trailing slash. Use the format `https://your-project.supabase.co` (without `/` at the end).

### 5. Install Dependencies

Install the official Supabase Python package:

```bash
pip install supabase
```


## Implementation

### SDK Usage
The system uses the official Supabase Python SDK (`supabase-py`) for all storage operations:

- **Upload**: `supabase.storage.from_(bucket).upload(path, file, options)`
- **Delete**: `supabase.storage.from_(bucket).remove([path])`
- **Get signed URLs**: `supabase.storage.from_(bucket).create_signed_url(path, expires_in)`

This provides better error handling, automatic retries, and cleaner API integration compared to raw HTTP requests.

## Features

### Image Upload & Compression
- **Automatic Compression**: Images are compressed to WebP format
- **Size Optimization**: Images are resized if larger than 1920x1080
- **Quality Control**: WebP compression with 85% quality

### File Organization
- **Directory Structure**: Files organized by type (products/, avatars/, documents/)
- **Unique Naming**: Files get unique names with timestamps
- **Path Format**: `{directory}/{timestamp}_{uuid}.{extension}`

## API Usage

### Upload Product Image
```javascript
const formData = new FormData();
formData.append('action', 'upload_image');
formData.append('product_id', productId);
formData.append('image', imageFile);

fetch('/product/api/', {
    method: 'POST',
    body: formData,
    headers: {
        'X-CSRFToken': csrfToken
    }
});
```

### Response Format
```json
{
    "success": true,
    "message": "Image uploaded successfully",
    "data": {
        "image_url": "https://your-project.supabase.co/storage/v1/object/public/uploads/products/123/image.webp"
    }
}
```
