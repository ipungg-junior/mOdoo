
# Rupiah Formatting Utility
def format_rupiah(amount):
    """Format a number into Indonesian Rupiah currency format.

    Args:
        amount (float or int): The amount of money to format.

    Returns:
        str: The formatted currency string in Rupiah.
    """
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        raise ValueError("Invalid amount. Please provide a numeric value.")

    is_negative = amount < 0
    amount = abs(amount)

    # Format the number with thousands separator and two decimal places
    formatted_amount = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    if is_negative:
        return f"{formatted_amount}"
    else:
        return f"{formatted_amount}"


# Supabase Storage Service
import os
import uuid
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from supabase import create_client, Client


class SupabaseStorageService:
    """
    Supabase Storage service for handling media uploads with compression and organization.

    Features:
    - Image compression to WebP format
    - Organized directory structure
    - Support for various file types
    - Automatic file naming
    """

    def __init__(self):
        """Initialize Supabase Storage service"""
        try:
            # Get Supabase configuration from Django settings
            self.supabase_url = getattr(settings, 'SUPABASE_URL', None)
            self.supabase_key = getattr(settings, 'SUPABASE_ANON_KEY', None)
            self.bucket_name = getattr(settings, 'SUPABASE_STORAGE_BUCKET', 'uploads')

            if not all([self.supabase_url, self.supabase_key]):
                print("Warning: Supabase configuration not found in settings.")
                self.supabase: Client = None
                self.initialized = False
            else:
                # Supabase SDK expects URL without trailing slash
                self.supabase_url = self.supabase_url.rstrip('/')
                print(f"Initializing Supabase with URL: {self.supabase_url}")
                try:
                    self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
                    self.initialized = True
                    print("Supabase Storage initialized successfully")
                except Exception as e:
                    print(f"Failed to initialize Supabase client: {e}")
                    self.supabase = None
                    self.initialized = False
        except Exception as e:
            print(f"Warning: Supabase Storage initialization failed: {e}")
            self.supabase = None
            self.initialized = False

    def _compress_image(self, image_file, quality=85, max_size=(1920, 1080)):
        """
        Compress and convert image to WebP format.

        Args:
            image_file: Django InMemoryUploadedFile or file-like object
            quality: JPEG/WebP quality (1-100)
            max_size: Maximum dimensions as (width, height) tuple

        Returns:
            BytesIO: Compressed image data
        """
        try:
            # Open image with PIL
            if isinstance(image_file, InMemoryUploadedFile):
                image = Image.open(image_file.file)
            else:
                image = Image.open(image_file)

            # Convert to RGB if necessary (for PNG with transparency)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background

            # Resize if larger than max_size
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert to WebP
            output = BytesIO()
            image.save(output, format='WebP', quality=quality, optimize=True)
            output.seek(0)

            return output

        except Exception as e:
            print(f"Warning: Image compression failed: {e}")
            # Return original file if compression fails
            if isinstance(image_file, InMemoryUploadedFile):
                image_file.file.seek(0)
                return image_file.file
            return image_file

    def _generate_filename(self, original_filename, directory='uploads'):
        """
        Generate a unique filename with directory structure.

        Args:
            original_filename: Original file name
            directory: Directory path

        Returns:
            str: Generated filename with path
        """
        # Get file extension
        _, ext = os.path.splitext(original_filename)

        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        timestamp = str(int(__import__('time').time()))

        # Create filename
        filename = f"{timestamp}_{unique_id}{ext}"

        # Return full path
        return f"{directory}/{filename}"

    def upload_file(self, file_obj, directory='uploads', compress_image=True):
        """
        Upload a file to Supabase Storage.

        Args:
            file_obj: Django InMemoryUploadedFile or file-like object
            directory: Directory path in storage
            compress_image: Whether to compress images

        Returns:
            dict: Upload result with URL and metadata
        """
        if not self.initialized:
            return {
                'success': False,
                'error': 'Supabase Storage not initialized',
                'url': None
            }

        try:
            # Determine if file is an image
            content_type = getattr(file_obj, 'content_type', '')
            is_image = content_type.startswith('image/') or file_obj.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'))

            # Compress image if requested and it's an image
            if compress_image and is_image:
                file_data = self._compress_image(file_obj)
                filename = self._generate_filename(file_obj.name, directory)
                # Update content type for WebP
                content_type = 'image/webp'
            else:
                # Use original file
                if isinstance(file_obj, InMemoryUploadedFile):
                    file_obj.file.seek(0)
                    file_data = file_obj.file
                else:
                    file_data = file_obj
                filename = self._generate_filename(file_obj.name, directory)

            # Prepare file content for upload
            if hasattr(file_data, 'read'):
                # For file-like objects (BytesIO, etc.)
                file_data.seek(0)  # Ensure we're at the beginning
                file_content = file_data.read()
                if isinstance(file_content, str):
                    file_content = file_content.encode('utf-8')
            else:
                file_content = file_data

            # Ensure file_content is bytes
            if not isinstance(file_content, bytes):
                file_content = bytes(str(file_content), 'utf-8')

            # Upload using Supabase SDK
            try:
                response = self.supabase.storage.from_(self.bucket_name).upload(
                    path=filename,
                    file=file_content,
                    file_options={
                        "content-type": content_type,
                        "cache-control": "3600"
                    }
                )
            except Exception as upload_error:
                print(f"Supabase upload error: {upload_error}")
                return {
                    'success': False,
                    'error': f'Upload failed: {str(upload_error)}',
                    'url': None
                }
                

            if response.full_path:
                return {
                    'success': True,
                    'path': response.path}
                
            else:
                return {
                    'success': False,
                    'error': 'Upload failed: No path returned',
                    'url': None
                }


        except Exception as e:
            print(f"Warning: File upload failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': None
            }

    def upload_product_image(self, image_file, product_id=None):
        """
        Upload product image with optimized settings.

        Args:
            image_file: Image file to upload
            product_id: Optional product ID for organization

        Returns:
            dict: Upload result
        """
        directory = f"products/{product_id}" if product_id else "products"
        return self.upload_file(image_file, directory, compress_image=True)

    def upload_user_avatar(self, image_file, user_id):
        """
        Upload user avatar with optimized settings.

        Args:
            image_file: Avatar image file
            user_id: User ID for organization

        Returns:
            dict: Upload result
        """
        directory = f"avatars/{user_id}"
        return self.upload_file(image_file, directory, compress_image=True)

    def upload_document(self, file_obj, category='documents'):
        """
        Upload document file without compression.

        Args:
            file_obj: Document file to upload
            category: Document category (e.g., 'invoices', 'reports')

        Returns:
            dict: Upload result
        """
        directory = f"documents/{category}"
        return self.upload_file(file_obj, directory, compress_image=False)

    def get_url_from(self, file_path):
        """
        Get the Signed URL of a file stored in Supabase Storage.

        Args:
            file_path: Path of the file in the storage bucket

        Returns:
            str: Signed URL of the file
        """
        if not self.initialized:
            return None

        try:
            print(f"Generating signedURL for file: {file_path} in bucket: {self.bucket_name}")
            signed_url = self.supabase.storage.from_(self.bucket_name).create_signed_url(file_path, 3600)
            return signed_url['signedURL']            
        except Exception as e:
            print(f"Warning: Could not get signed URL: {e}")
            return None

    def delete_file(self, file_url):
        """
        Delete a file from Supabase Storage.

        Args:
            file_url: Public URL of the file to delete

        Returns:
            bool: Success status
        """
        if not self.initialized:
            return False

        try:
            # Extract filename from Supabase public URL
            # URL format: https://project.supabase.co/storage/v1/object/public/bucket/filename
            if '/storage/v1/object/public/' not in file_url:
                print(f"Warning: Invalid Supabase URL format: {file_url}")
                return False

            # Split on the public path marker
            path_part = file_url.split('/storage/v1/object/public/', 1)[1]

            # Remove bucket name prefix if present
            if path_part.startswith(f'{self.bucket_name}/'):
                filename = path_part[len(f'{self.bucket_name}/'):]
            else:
                filename = path_part

            print(f"Attempting to delete file: {filename} from bucket: {self.bucket_name}")

            # Delete using Supabase SDK
            response = self.supabase.storage.from_(self.bucket_name).remove([filename])
            print(f"Delete response: {response}")

            # Check if deletion was successful
            if isinstance(response, list) and len(response) > 0:
                return response[0].get('name') == filename
            return False

        except Exception as e:
            print(f"Warning: File deletion failed: {e}")
            return False


# Global instance for easy import
supabase_storage = SupabaseStorageService()