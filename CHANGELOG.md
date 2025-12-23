# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Batch conversion support (multiple files)
- Webhook notifications on conversion completion
- Rate limiting per IP
- User authentication with API keys
- Conversion queue with Redis

## [1.0.0] - 2024-12-23

### Added
- Advanced health check endpoint with system metrics (CPU, memory, disk)
- Structured logging system with file rotation
- Gzip compression for API responses
- Download from URL support (remote file conversion)
- Comprehensive validation system
- Docker healthcheck configuration
- Automatic cleanup thread for temporary files
- Support for document conversion (DOCX, DOC, ODT → PDF, HTML, TXT)
- Support for image conversion (JPG, PNG, GIF, BMP → JPG, PNG, PDF, WebP)
- Support for video conversion (MP4, AVI, MOV, MKV → MP4, AVI, GIF)
- Support for audio conversion (MP3, WAV, OGG, M4A, FLAC → MP3, WAV, OGG)
- Factory pattern for converter management
- File size validation (configurable max size)
- Secure filename handling with UUID
- Docker and Docker Compose support
- Persistent volumes for uploads, conversions, and logs

### Security
- ImageMagick policy configuration for safe PDF handling
- File size limits to prevent DoS attacks
- Secure filename sanitization
- Automatic cleanup of uploaded files after conversion

### Infrastructure
- LibreOffice for document conversion
- ImageMagick for image processing
- FFmpeg for audio/video conversion
- Pandoc for advanced document conversion
- Ghostscript and Poppler for PDF utilities
- Python 3.11 slim base image
- Flask web framework
- psutil for system monitoring

### Documentation
- README with installation and usage examples
- VALIDATION checklist for deployment
- Environment variables example (.env.example)
- Docker Compose configuration with healthcheck

## [0.1.0] - 2024-12-01

### Added
- Initial project structure
- Basic Flask API
- Simple file upload and conversion
- Dockerfile for containerization

---

## Version History Notes

### How to Release

1. Update version in this CHANGELOG
2. Create git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
3. Push tag: `git push origin v1.0.0`
4. Create GitHub release from tag
5. Build and push Docker image with version tag

### Version Numbering

- **MAJOR**: Breaking changes, incompatible API modifications
- **MINOR**: New features, backwards-compatible
- **PATCH**: Bug fixes, minor improvements

[Unreleased]: https://github.com/thecocoblue/file-converter-service/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/thecocoblue/file-converter-service/releases/tag/v1.0.0
[0.1.0]: https://github.com/thecocoblue/file-converter-service/releases/tag/v0.1.0
