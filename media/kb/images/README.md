# Knowledge Base Images Directory

This directory stores uploaded images for the Knowledge Base system.

## Directory Structure

```
images/
├── articles/     # Images uploaded for articles
├── thumbnails/   # Generated thumbnail images (if implemented)
└── README.md     # This file
```

## Supported Formats
- JPG, JPEG
- PNG  
- GIF
- WebP
- SVG

## File Size Limits
- Maximum file size: 10MB
- Recommended size: Under 2MB for better performance

## Security Features
- File extension validation
- MIME type checking
- Filename sanitization
- Directory listing disabled

## Development vs Production

### Development
- Files stored locally in `media/kb/images/`
- Served directly by Django development server
- URL pattern: `http://localhost:8000/uploads/kb/images/filename.jpg`

### Production
- Files can be stored locally or on cloud storage (S3)
- Served by web server (nginx/apache) for better performance
- URL pattern: `https://yourdomain.com/uploads/kb/images/filename.jpg`

## Troubleshooting

If image uploads fail:
1. Check directory permissions (755 recommended)
2. Verify MEDIA_ROOT and MEDIA_URL settings
3. Check web server configuration for /uploads/ path
4. Ensure file size is under the limit
5. Check browser console for JavaScript errors

## Environment Variables

For production deployment:
- `MEDIA_ROOT=/mnt/safaridesk` (or your preferred path)
- `MEDIA_URL=/uploads/`

For development (default):
- `MEDIA_ROOT=project_root/media/`
- `MEDIA_URL=/uploads/`
