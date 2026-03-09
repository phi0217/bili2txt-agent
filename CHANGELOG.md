# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 📜 Apache License 2.0 - Changed from MIT to Apache 2.0 for better patent protection
- 📋 Comprehensive documentation structure
- 🔧 Enhanced `.env.example` with detailed comments and validation checklist
- 📝 Type annotations for all public functions
- 📚 Google-style docstrings for better code documentation
- 🎯 GitHub issue and pull request templates
- 📦 `pyproject.toml` for modern Python project configuration
- 🎨 `.editorconfig` for consistent editor settings across team
- 🌐 Open source readiness optimizations

### Changed
- ✨ Improved README.md with badges, better structure, and clearer instructions
- 💬 Enhanced error messages with user-friendly formatting and troubleshooting tips
- 🎨 Optimized Block-based API for Markdown rendering
  - Support for headings (# ## ### #### #####)
  - Support for bold (**text**) and italic (*text*)
  - Support for bulleted lists with automatic bullet conversion
  - Support for horizontal rules
- 🔄 Updated LLM prompt to include 4-space paragraph indentation requirement
- 📦 Improved code organization and modularity

### Fixed
- ✅ File upload API parameter validation issues in Import API
- 🎨 TextElementStyle usage for proper text formatting (bold, italic)
- 🔄 Import API fallback mechanism stability
- 🐛 Bug: File object not being closed after upload

### Removed
- 🗑️ Import API as primary approach (using stable Block-based API instead)

### Security
- 🔒 Added comprehensive `.env.example` validation
- 🔒 Enhanced secrets management documentation

### Documentation
- 📚 Created comprehensive documentation structure
- 📖 Added architecture and flow diagrams
- 📝 Enhanced deployment guides
- 🆕 Added troubleshooting documentation

## [2.2.0] - 2026-03-09

### Added
- Enhanced Block-based API with Markdown rendering support
  - Heading rendering (1-5 levels) with bold formatting
  - Text formatting (bold, italic) using TextElementStyle
  - Bulleted lists with automatic bullet conversion
  - Horizontal rules
- Comprehensive error handling and logging
- Batch document writing for large content (50 blocks per batch)

### Changed
- Simplified `create_and_share_document()` to use Block-based API directly
- Improved file upload using file objects instead of bytes
- Better text formatting with TextElementStyle
- Updated `write_content_to_document()` to parse and render Markdown

## [2.1.0] - 2026-03-08

### Added
- Import API functionality for Markdown file upload to Feishu
- Automatic fallback mechanism (Import API → Block-based API)
- Custom exception classes (FileUploadError, ImportTaskError, PollingTimeoutError, DocumentCreationError)
- Comprehensive test suite for Import API functionality
- Documentation for Import API implementation

### Changed
- Refactored `create_document()` to `create_document_via_blocks()`
- Modified `create_and_share_document()` to support dual-approach with automatic fallback

## [2.0.0] - 2026-03-07

### Added
- yt-dlp audio-only download (300x speed improvement over full video download)
- Automatic fallback to you-get when yt-dlp fails
- Short link support (b23.tv)
- Markdown document caching
- WebSocket client with auto-reconnect
- Comprehensive documentation structure

### Changed
- Major refactoring from video download to audio-only download
- Improved performance: 2-5x faster overall processing time
- Reduced storage: 99.8% space savings (1MB audio vs 500MB video)

### Removed
- Full video download as default behavior

## [1.0.0] - 2026-03-06

### Added
- Initial release
- Feishu WebSocket integration
- Bilibili video download via you-get
- Whisper speech recognition (base model)
- DeepSeek API text refinement
- Feishu document creation and sharing
- Basic error handling
- Test suite

---

## Version Format

- **Major** (X.0.0): Breaking changes, major features
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, small improvements

## Release Notes

For detailed release notes, see: [docs/releases/](docs/releases/)

---

**Maintained by**: bili2txt-agent project team
**Last updated**: 2026-03-09
**License**: Apache License 2.0
