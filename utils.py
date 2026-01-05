import os
import re
import subprocess
import sys
import wx

def parse_shortcut(shortcut):
    flags = 0
    parts = shortcut.split('+')
    key_part = parts[-1]
    for part in parts[:-1]:
        if part.lower() == 'ctrl':
            flags |= wx.ACCEL_CTRL
        elif part.lower() == 'alt':
            flags |= wx.ACCEL_ALT
        elif part.lower() == 'shift':
            flags |= wx.ACCEL_SHIFT
    if len(key_part) == 1:
        key = ord(key_part.upper())
    elif key_part.lower() == 'escape':
        key = wx.WXK_ESCAPE
    elif key_part.lower() == 'enter':
        key = wx.WXK_RETURN
    else:
        key = None
    return flags, key

def read_file(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == '.txt':
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.rtf':
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            content = re.sub(r'\\[a-z]+\d* ?', '', content)
            content = re.sub(r'[{}]', '', content)
            return content
        elif ext == '.pdf':
            try:
                from pdfminer.high_level import extract_text
                return extract_text(path)
            except ImportError:
                return None
        elif ext in ['.doc', '.docx']:
            try:
                from docx import Document
                doc = Document(path)
                return '\n'.join([para.text for para in doc.paragraphs])
            except ImportError:
                return None
        elif ext == '.epub':
            try:
                from ebooklib import epub
                book = epub.read_epub(path)
                text = ''
                for item in book.get_items():
                    if item.get_type() == 9:  # ITEM_DOCUMENT
                        text += item.get_content().decode('utf-8') + '\n'
                text = re.sub(r'<[^>]+>', '', text)
                return text
            except ImportError:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return None

def open_file(path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        print(f"Unable to open file: {e}")