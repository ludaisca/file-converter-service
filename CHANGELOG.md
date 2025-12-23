# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial documentation updates
- MIT License file
- CHANGELOG.md for version tracking

---

## [1.0.0] - 2024-12-23

### Added
- REST API for file conversion
- Support for document conversion (DOCX, DOC, ODT → PDF, HTML, TXT)
- Support for image conversion (JPG, PNG, GIF, BMP → JPG, PNG, PDF, WebP)
- Support for video conversion (MP4, AVI, MOV, MKV → MP4, AVI, GIF)
- Support for audio conversion (MP3, WAV, OGG, M4A, FLAC → MP3, WAV, OGG)
- File upload support
- URL download support for remote files
- Advanced health check endpoint with system metrics
- Structured logging with configurable levels
- GZIP compression for API responses
- Automatic file cleanup with configurable TTL
- Docker and Docker Compose support
- Environment variable configuration
- UUID-based file naming for security
- File size validation (upload and download)
- LibreOffice integration for document conversion
- ImageMagick integration for image conversion
- FFmpeg integration for audio/video conversion
- Pandoc integration for advanced document conversion

### Security
- Secure filename sanitization
- File size limits to prevent abuse
- Download timeout protection (30s)
- Stream-based downloads to prevent memory overflow
- Modified ImageMagick policy for safe PDF handling

### Configuration
- `MAX_FILE_SIZE`: Maximum upload size (default: 50MB)
- `MAX_DOWNLOAD_SIZE`: Maximum download size (default: 100MB)
- `CLEANUP_INTERVAL`: Cleanup frequency (default: 3600s)
- `FILE_TTL`: File time-to-live (default: 3600s)
- `LOG_LEVEL`: Logging verbosity
- Health monitoring toggle

---

## [0.1.0] - Initial Development

### Added
- Project structure
- Basic Flask application
- Docker configuration
- Initial converter implementations

---

[Unreleased]: https://github.com/thecocoblue/file-converter-service/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/thecocoblue/file-converter-service/releases/tag/v1.0.0
[0.1.0]: https://github.com/thecocoblue/file-converter-service/releases/tag/v0.1.0
