import os
import subprocess
import sys
import wx

from utils import read_file, open_file

def show_converter_dialog(self, event):
    dlg = wx.Dialog(self, title="File Converter", size=wx.Size(400, 200))
    vbox = wx.BoxSizer(wx.VERTICAL)

    file_sizer = wx.BoxSizer(wx.HORIZONTAL)
    self.source_file_edit = wx.TextCtrl(dlg)
    self.source_file_edit.Disable()
    file_sizer.Add(self.source_file_edit, 1, wx.EXPAND | wx.ALL, 5)

    select_file_btn = wx.Button(dlg, label="Browse...")
    select_file_btn.Bind(wx.EVT_BUTTON, lambda e: self.select_source_file(dlg))
    file_sizer.Add(select_file_btn, 0, wx.ALL, 5)
    vbox.Add(file_sizer, 0, wx.EXPAND)

    format_sizer = wx.BoxSizer(wx.HORIZONTAL)
    format_label = wx.StaticText(dlg, label="Convert to:")
    format_sizer.Add(format_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

    self.target_format_combo = wx.Choice(dlg, choices=[".txt", ".pdf", ".rtf", ".docx"])
    format_sizer.Add(self.target_format_combo, 0, wx.ALL, 5)
    vbox.Add(format_sizer, 0, wx.EXPAND)

    button_sizer = wx.BoxSizer(wx.HORIZONTAL)
    ok_btn = wx.Button(dlg, wx.ID_OK, label="Convert")
    ok_btn.Bind(wx.EVT_BUTTON, lambda e: self.convert_file(dlg))
    button_sizer.Add(ok_btn, 0, wx.ALL, 5)

    cancel_btn = wx.Button(dlg, wx.ID_CANCEL, label="Cancel")
    button_sizer.Add(cancel_btn, 0, wx.ALL, 5)
    vbox.Add(button_sizer, 0, wx.ALIGN_RIGHT)

    dlg.SetSizer(vbox)
    dlg.Bind(wx.EVT_KEY_DOWN, lambda e: dlg.EndModal(wx.ID_CANCEL) if e.GetKeyCode() == wx.WXK_ESCAPE else e.Skip())
    dlg.ShowModal()
    dlg.Destroy()

def select_source_file(self, dlg):
    with wx.FileDialog(dlg, "Select File to Convert", wildcard="Supported Files (*.txt;*.pdf;*.rtf;*.doc;*.docx)|*.txt;*.pdf;*.rtf;*.doc;*.docx|All Files (*.*)|*.*", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return
        pathname = fileDialog.GetPath()
        self.source_file_edit.SetValue(pathname)

def convert_file(self, dlg):
    source_path = self.source_file_edit.GetValue()
    if not source_path:
        wx.MessageBox("Please select a source file.", "Warning", wx.OK | wx.ICON_WARNING)
        return

    target_ext = self.target_format_combo.GetStringSelection()

    text = read_file(source_path)
    if text is None:
        wx.MessageBox("Unable to read the source file.", "Error", wx.OK | wx.ICON_ERROR)
        return

    dir_name = os.path.dirname(source_path)
    base_name = os.path.splitext(os.path.basename(source_path))[0]
    output_path = os.path.join(dir_name, base_name + target_ext)

    try:
        if target_ext == '.txt':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
        elif target_ext == '.pdf':
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                c = canvas.Canvas(output_path, pagesize=letter)
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
            except ImportError:
                wx.MessageBox("PDF library not available. Please install reportlab.", "Error", wx.OK | wx.ICON_ERROR)
                return
        elif target_ext == '.rtf':
            rtf_content = "{\\rtf1\\ansi\\ansicpg1252\\deff0\\deflang1033{\\fonttbl{\\f0\\fnil\\fcharset0 Arial;}}\n\\viewkind4\\uc1\\pard\\f0\\fs20 " + text.replace('\n', '\\par ') + "}"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rtf_content)
        elif target_ext == '.docx':
            try:
                from docx import Document
                doc = Document()
                for line in text.split('\n'):
                    doc.add_paragraph(line)
                doc.save(output_path)
            except ImportError:
                wx.MessageBox("DOCX library not available. Please install python-docx.", "Error", wx.OK | wx.ICON_ERROR)
                return
        else:
            wx.MessageBox("Unsupported target format.", "Error", wx.OK | wx.ICON_ERROR)
            return

        self.show_conversion_success(output_path, dlg)

    except Exception as e:
        wx.MessageBox(f"Conversion failed: {e}", "Error", wx.OK | wx.ICON_ERROR)

def show_conversion_success(self, file_path, parent_dlg):
    dlg = wx.MessageDialog(parent_dlg, "File converted successfully!", "Conversion Successful", wx.OK)
    dlg.SetOKLabel("Open file")
    if dlg.ShowModal() == wx.ID_OK:
        try:
            open_file(file_path)
        except Exception as e:
            wx.MessageBox(f"Unable to open file: {e}", "Error", wx.OK | wx.ICON_ERROR)
    dlg.Destroy()
    parent_dlg.EndModal(wx.ID_OK)