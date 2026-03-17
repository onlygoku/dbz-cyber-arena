import cloudinary
import cloudinary.uploader
from flask import current_app


def init_cloudinary():
    cloudinary.config(
        cloud_name=current_app.config.get('CLOUDINARY_CLOUD_NAME'),
        api_key=current_app.config.get('CLOUDINARY_API_KEY'),
        api_secret=current_app.config.get('CLOUDINARY_API_SECRET'),
    )


def upload_file(file, challenge_id, filename):
    """Upload a file to Cloudinary and return its URL and metadata."""
    init_cloudinary()
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=f'ctf/challenges/{challenge_id}',
            public_id=filename.rsplit('.', 1)[0],
            resource_type='raw',
            use_filename=True,
            unique_filename=False,
            overwrite=True,
        )
        return {
            'name': filename,
            'url': result['secure_url'],
            'size': _format_size(result['bytes']),
        }
    except Exception as e:
        current_app.logger.error(f'Cloudinary upload error: {e}')
        return None


def delete_file(challenge_id, filename):
    """Delete a file from Cloudinary."""
    init_cloudinary()
    try:
        public_id = f'ctf/challenges/{challenge_id}/{filename.rsplit(".", 1)[0]}'
        cloudinary.uploader.destroy(public_id, resource_type='raw')
        return True
    except Exception as e:
        current_app.logger.error(f'Cloudinary delete error: {e}')
        return False


def _format_size(bytes):
    if bytes >= 1024 * 1024:
        return f'{bytes // (1024 * 1024)} MB'
    elif bytes >= 1024:
        return f'{bytes // 1024} KB'
    return f'{bytes} B'