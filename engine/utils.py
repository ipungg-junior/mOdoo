
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


# Firebase Storage Service
import os
import uuid
from io import BytesIO
from PIL import Image
import firebase_admin
from firebase_admin import credentials, storage
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile


class FirebaseStorageService:
    """
    Firebase Storage service for handling media uploads with compression and organization.

    Features:
    - Image compression to WebP format
    - Organized directory structure
    - Support for various file types
    - Automatic file naming
    """

    def __init__(self):
        """Initialize Firebase Storage service"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Get Firebase credentials from Django settings
                firebase_config = getattr(settings, 'FIREBASE_CONFIG', None)
                if firebase_config:
                    cred = credentials.Certificate(firebase_config)
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': getattr(settings, 'FIREBASE_STORAGE_BUCKET', None)
                    })
                else:
                    print("Warning: Firebase configuration not found in settings.")

            self.bucket = storage.bucket()
        except Exception as e:
            print(f"Warning: Firebase Storage initialization failed: {e}")
            self.bucket = None

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
        Upload a file to Firebase Storage.

        Args:
            file_obj: Django InMemoryUploadedFile or file-like object
            directory: Directory path in storage
            compress_image: Whether to compress images

        Returns:
            dict: Upload result with URL and metadata
        """
        if not self.bucket:
            return {
                'success': False,
                'error': 'Firebase Storage not initialized',
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

            # Upload to Firebase Storage
            blob = self.bucket.blob(filename)
            blob.upload_from_file(file_data, content_type=content_type)

            # Make the file publicly accessible
            blob.make_public()

            return {
                'success': True,
                'url': blob.public_url,
                'filename': filename,
                'size': getattr(file_obj, 'size', 0),
                'content_type': content_type,
                'compressed': compress_image and is_image
            }

        except Exception as e:
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

    def delete_file(self, file_url):
        """
        Delete a file from Firebase Storage.

        Args:
            file_url: Public URL of the file to delete

        Returns:
            bool: Success status
        """
        if not self.bucket:
            return False

        try:
            # Extract filename from URL
            # Firebase URLs typically end with /bucket/filename
            url_parts = file_url.split('/')
            filename = '/'.join(url_parts[-2:])  # Get bucket/filename part

            blob = self.bucket.blob(filename)
            blob.delete()

            return True

        except Exception as e:
            print(f"Warning: File deletion failed: {e}")
            return False


# Global instance for easy import
firebase_storage = FirebaseStorageService()