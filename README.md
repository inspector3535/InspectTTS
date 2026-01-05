# InspectTTS (Experimental)

InspectTTS is a desktop application for text-to-speech conversion, file reading, AI chat, and file conversion. Built with wxPython, it supports multiple languages and formats.

## Features

- **Text-to-Speech**: Convert text to audio with adjustable speed and pitch.
- **File Support**: Read from TXT, PDF, RTF, DOC, DOCX, and EPUB files.
- **AI Integration**: Chat with Gemini AI for text analysis.
- **File Conversion**: Convert between TXT, PDF, RTF, and DOCX formats.
- **Notepad**: Simple text editor with export options.
- **Reader**: Display file contents.
- **Web Page Fetching**: Extract text from web pages.

## Requirements

- Python 3.7+
- wxPython
- requests
- pydub (for audio processing)
- pdfminer.six (for PDF reading)
- python-docx (for DOCX handling)
- ebooklib (for EPUB reading)
- beautifulsoup4 (for HTML parsing)
- reportlab (for PDF generation)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/inspecttts.git
   cd inspecttts
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

## Usage

- Launch the app and enter text to convert to speech.
- Use "Add File" to load text from supported files.
- Configure API keys in Settings for AI features.
- Adjust language, speed, and pitch for TTS.

## Configuration

- API keys are stored in `settings.ini`.

## Status: Experimental / Educational Project

## Audience: Accessibility-focused users and developers

## Contact:

Telegram: @ms35last

## Contributing

Feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- TTS API by Sujan Rai
- Built with wxPython