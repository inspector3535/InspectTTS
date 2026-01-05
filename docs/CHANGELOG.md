# Changelog

All notable changes to InspectTTS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/SemVer).

## [1.0.2] - 2026-01-04

### Added
- **Standalone Executable**: Created single-file portable Windows executable with PyInstaller
- **Distribution Package**: All dependencies and data files bundled inside the exe
- **Enhanced AI UX**: Improved user experience during AI response generation with persistent waiting messages and disabled controls
- **FFmpeg Integration**: Bundled FFmpeg binary for complete audio processing functionality without external dependencies

### Changed
- **Manual File Paths**: Updated to use current working directory instead of script directory for better portability
- **Shortcuts File Location**: Moved shortcuts.txt to shortcuts.md in docs/ folder for better organization
- **AI Dialog Behavior**: Disabled user interaction during AI generation to prevent confusion

### Added
- **GitHub Contact Button**: Added "Contact me on GitHub" button in About section that opens https://github.com/inspector3535/Inspect-TTS-issues

### Fixed
- **Bundled File Access**: Fixed README and manual file access in standalone executable using sys._MEIPASS
- **Double Dialog Prompt**: Removed duplicate "What would you like to do?" dialog after TTS conversion
- **Escape Key Handling**: Improved escape key functionality in TTS success dialog
- **Fetch Page Buttons**: Fixed Summarize with AI button functionality in standalone exe using proper event handlers
- **API Error Messages**: Improved error message for invalid API keys to be more user-friendly
- **AI Response Focus**: Fixed focus management during AI response generation
- **UI Responsiveness**: Prevented user interaction conflicts during background processing

### Technical Improvements
- **PyInstaller Configuration**: Created single-file spec with dependency exclusions for truly standalone executable
- **File Inclusion**: Embedded manual files, README, shortcuts, and documentation inside the exe
- **Build Cleanup**: Automated removal of temporary build files
- **FFmpeg Bundling**: Integrated complete FFmpeg binary for audio processing without system dependencies
- **License Compliance**: Added FFmpeg GPL license information to project licensing
- **Event Handling**: Improved button event binding for better compatibility in bundled executables

### Distribution
- **GitHub Releases Ready**: Executable can be distributed as release asset
- **No Installation Required**: Users can run the exe directly without Python installation
- **Final Build**: Executable rebuilt with shortcuts.md included (74.7MB standalone exe)

## [1.0.0] - 2025-01-01

### Added
- **Manual Viewer**: Added in-app manual viewing with language selection (English/Turkish)
- **GitHub Publishing Files**: Added README.md, LICENSE, requirements.txt, .gitignore
- **File Filtering**: Improved file dialog to show only supported file types by default
- **README Integration**: Updated to display README.md in-app instead of external viewer

### Changed
- **Code Refactoring**: Split large main.py into modular files:
  - `main_window.py`: Main application window and UI
  - `ai.py`: AI-related functionality
  - `tts.py`: Text-to-speech functions
  - `utils.py`: Helper functions (file reading, shortcuts)
  - `dialogs.py`: Dialog classes (Notepad, Reader)
  - `file_converter.py`: File conversion logic
- **Requirements**: Updated dependencies with proper versions and optional libraries
- **File Paths**: Fixed README path to use correct filename

### Fixed
- **File Dialog Wildcard**: Corrected wildcard format for proper file filtering
- **Manual File Paths**: Updated to match actual file extensions (.md for both languages)
- **Import Errors**: Resolved module import issues after refactoring

### Technical Improvements
- **Modular Architecture**: Improved maintainability with separated concerns
- **Error Handling**: Added try-except blocks for file operations
- **Accessibility**: Maintained keyboard navigation and screen reader support
- **Encoding**: Consistent UTF-8 handling for all text files

### Documentation
- **README.md**: Comprehensive project documentation
- **Manual Files**: Detailed user manuals in Turkish and English (English manual content pending)
- **License**: Added MIT license
- **Requirements**: Clear dependency list with versions

### Notes
- Application remains portable (no installation required)
- All original features preserved
- Backward compatibility maintained