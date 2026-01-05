import os
import subprocess
import sys
import wx

from utils import open_file

class NotepadDialog(wx.Dialog):
    def __init__(self, save_path, parent=None):
        super().__init__(parent, title="Notepad", size=wx.Size(600, 400))
        self.save_path = save_path

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.text_edit = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.text_edit.SetHint("Type your note here")
        vbox.Add(self.text_edit, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        save_btn = wx.Button(self, label="Save")
        save_btn.Bind(wx.EVT_BUTTON, self.save_note)
        button_sizer.Add(save_btn, 0, wx.ALL, 5)

        close_btn = wx.Button(self, wx.ID_CANCEL, label="Close")
        button_sizer.Add(close_btn, 0, wx.ALL, 5)

        vbox.Add(button_sizer, 0, wx.ALIGN_RIGHT)

        self.SetSizer(vbox)
        self.Bind(wx.EVT_KEY_DOWN, lambda e: self.EndModal(wx.ID_CANCEL) if e.GetKeyCode() == wx.WXK_ESCAPE else e.Skip())
        self.text_edit.SetFocus()

    def save_note(self, event):
        text = self.text_edit.GetValue()
        if not text.strip():
            wx.MessageBox("No text to save.", "Warning", wx.OK | wx.ICON_WARNING)
            return
        with wx.FileDialog(self, "Save Note", self.save_path, wildcard="PDF Files (*.pdf)|*.pdf|Text Files (*.txt)|*.txt|RTF Files (*.rtf)|*.rtf|Word Documents (*.docx)|*.docx", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            ext = ""
            if fileDialog.GetFilterIndex() == 0:
                ext = ".pdf"
            elif fileDialog.GetFilterIndex() == 1:
                ext = ".txt"
            elif fileDialog.GetFilterIndex() == 2:
                ext = ".rtf"
            elif fileDialog.GetFilterIndex() == 3:
                ext = ".docx"
            if not pathname.lower().endswith(ext):
                pathname += ext
            try:
                if ext == ".txt":
                    with open(pathname, 'w', encoding='utf-8') as f:
                        f.write(text)
                elif ext == ".pdf":
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import letter
                    c = canvas.Canvas(pathname, pagesize=letter)
                    width, height = letter
                    lines = text.split('\n')
                    y = height - 50
                    for line in lines:
                        c.drawString(50, y, line)
                        y -= 15
                        if y < 50:
                            c.showPage()
                            y = height - 50
                    c.save()
                elif ext == ".docx":
                    from docx import Document
                    doc = Document()
                    for line in text.split('\n'):
                        doc.add_paragraph(line)
                    doc.save(pathname)
                elif ext == ".rtf":
                    rtf_content = "{\\rtf1\\ansi\\ansicpg1252\\deff0\\deflang1033{\\fonttbl{\\f0\\fnil\\fcharset0 Arial;}}\n\\viewkind4\\uc1\\pard\\f0\\fs20 " + text.replace('\n', '\\par ') + "}"
                    with open(pathname, 'w', encoding='utf-8') as f:
                        f.write(rtf_content)
                wx.MessageBox("Note saved successfully.", "Saved", wx.OK | wx.ICON_INFORMATION)
            except ImportError as e:
                wx.MessageBox(f"Required library not available: {e}", "Error", wx.OK | wx.ICON_ERROR)
            except Exception as e:
                wx.MessageBox(f"Failed to save: {e}", "Error", wx.OK | wx.ICON_ERROR)

class ReaderDialog(wx.Dialog):
    def __init__(self, text, parent=None):
        super().__init__(parent, title="Reader", size=wx.Size(600, 400))

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.text_view = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.text_view.SetValue(text)
        self.text_view.SetFocus()
        vbox.Add(self.text_view, 1, wx.EXPAND | wx.ALL, 5)

        close_btn = wx.Button(self, wx.ID_CANCEL, label="Close")
        vbox.Add(close_btn, 0, wx.ALL, 5)

        self.SetSizer(vbox)
        self.Bind(wx.EVT_KEY_DOWN, lambda e: self.EndModal(wx.ID_CANCEL) if e.GetKeyCode() == wx.WXK_ESCAPE else e.Skip())