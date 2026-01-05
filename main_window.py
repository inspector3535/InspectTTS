import configparser
import io
import logging
import os
import re
import requests
import subprocess
import sys
import tempfile
import urllib.parse
import wx

from ai import AccessibleTextCtrl, AIThread, AIInput
from dialogs import NotepadDialog, ReaderDialog
from file_converter import show_converter_dialog, select_source_file, convert_file, show_conversion_success
from tts import show_success_dialog, download_audio, listen_audio, download_last_audio, on_conversion_finished, show_api_error_popup
from utils import parse_shortcut, read_file, open_file
from tts_api import TTSAPIThread

class MainWindow(wx.Frame):
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            filename='inspecttts.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("InspectTTS application started")

        super().__init__(None, title="InspectTTS v1.0", size=wx.Size(600, 400))
        self.last_audio_data = None
        self.attached_file_content = None
        self.fetched_content = None

        # Load settings
        self.config = configparser.ConfigParser()
        self.config_file = 'settings.ini'
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        if not self.config.has_section('Settings'):
            self.config.add_section('Settings')
        self.gemini_api_key = self.config.get('Settings', 'gemini_api_key', fallback='')
        self.save_path = self.config.get('Settings', 'save_path', fallback=os.path.join(os.path.expanduser("~"), "Documents"))
        self.enable_shortcuts = self.config.getboolean('Settings', 'enable_shortcuts', fallback=False)

        self.init_ui()
        self.load_shortcuts()
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Text Edit
        self.text_edit = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.text_edit.SetHint("Type text here to convert")
        vbox.Add(self.text_edit, 1, wx.EXPAND | wx.ALL, 5)

        # Controls Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Add File Button
        self.add_file_btn = wx.Button(panel, label="Add File")
        self.add_file_btn.Bind(wx.EVT_BUTTON, self.add_file)
        hbox.Add(self.add_file_btn, 0, wx.ALL, 5)

        # Voice Settings Group
        voice_box = wx.StaticBoxSizer(wx.StaticBox(panel, label="text language"), wx.HORIZONTAL)

        # Language ComboBox
        self.lang_combo = wx.Choice(panel, choices=["Select one...", "ar", "bg", "en", "fr", "hi", "ja", "tr", "zh"])
        self.lang_combo.SetSelection(0)
        voice_box.Add(self.lang_combo, 0, wx.ALL, 5)

        # Speed
        speed_box = wx.BoxSizer(wx.HORIZONTAL)
        speed_label = wx.StaticText(panel, label="Speed:")
        self.speed_spin = wx.SpinCtrlDouble(panel, min=0.5, max=2.0, initial=1.0, inc=0.1)
        speed_box.Add(speed_label, 0, wx.ALIGN_CENTER_VERTICAL)
        speed_box.Add(self.speed_spin, 0, wx.ALL, 5)
        voice_box.Add(speed_box, 0, wx.ALL, 5)

        # Pitch
        pitch_box = wx.BoxSizer(wx.HORIZONTAL)
        pitch_label = wx.StaticText(panel, label="Pitch:")
        self.pitch_spin = wx.SpinCtrlDouble(panel, min=0.5, max=2.0, initial=1.0, inc=0.1)
        pitch_box.Add(pitch_label, 0, wx.ALIGN_CENTER_VERTICAL)
        pitch_box.Add(self.pitch_spin, 0, wx.ALL, 5)
        voice_box.Add(pitch_box, 0, wx.ALL, 5)

        hbox.Add(voice_box, 0, wx.ALL, 5)

        # Convert Button
        self.convert_btn = wx.Button(panel, label="Convert to audio")
        self.convert_btn.Bind(wx.EVT_BUTTON, self.convert_audio)
        hbox.Add(self.convert_btn, 0, wx.ALL, 5)

        # Notepad Button
        self.notepad_btn = wx.Button(panel, label="Notepad")
        self.notepad_btn.Bind(wx.EVT_BUTTON, self.show_notepad)
        hbox.Add(self.notepad_btn, 0, wx.ALL, 5)

        # Talk to AI Button
        self.talk_to_ai_btn = wx.Button(panel, label="Ask AI")
        self.talk_to_ai_btn.Bind(wx.EVT_BUTTON, self.check_api_and_open_ai)
        hbox.Add(self.talk_to_ai_btn, 0, wx.ALL, 5)

        # Reader Button
        self.reader_btn = wx.Button(panel, label="Reader")
        self.reader_btn.Bind(wx.EVT_BUTTON, self.show_reader)
        hbox.Add(self.reader_btn, 0, wx.ALL, 5)

        # File Converter Button
        self.converter_btn = wx.Button(panel, label="File converter")
        self.converter_btn.Bind(wx.EVT_BUTTON, self.show_converter_dialog)
        hbox.Add(self.converter_btn, 0, wx.ALL, 5)

        # Fetch Page Button
        self.fetch_page_btn = wx.Button(panel, label="Fetch Page")
        self.fetch_page_btn.Bind(wx.EVT_BUTTON, self.show_fetch_page_dialog)
        hbox.Add(self.fetch_page_btn, 0, wx.ALL, 5)

        # Settings Button
        self.settings_btn = wx.Button(panel, label="Settings")
        self.settings_btn.Bind(wx.EVT_BUTTON, self.show_settings)
        hbox.Add(self.settings_btn, 0, wx.ALL, 5)

        vbox.Add(hbox, 0, wx.EXPAND)

        # Progress Bar
        self.progress_bar = wx.Gauge(panel, range=100)
        self.progress_bar.Hide()
        vbox.Add(self.progress_bar, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(vbox)

        # Tab order
        self.text_edit.SetFocus()

    def load_shortcuts(self):
        # Get shortcuts file path (same logic as README/manual files)
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            shortcuts_file = os.path.join(bundle_dir, "docs", "shortcuts.md")
        else:
            # Running in development
            shortcuts_file = os.path.join(os.getcwd(), "docs", "shortcuts.md")

        if not os.path.exists(shortcuts_file):
            return
        self.buttons = {
            "Add File": self.add_file_btn,
            "Notepad": self.notepad_btn,
            "Ask AI": self.talk_to_ai_btn,
            "Reader": self.reader_btn,
            "File converter": self.converter_btn,
            "Fetch Page": self.fetch_page_btn,
            "Settings": self.settings_btn,
            "Convert to audio": self.convert_btn,
        }
        self.shortcuts = {
            "Convert to audio": lambda e: self.convert_audio(e),
            "Download": lambda e: self.download_last_audio(e),
            "Escape": lambda e: self.Close()
        }
        self.shortcut_ids = {}
        entries = []
        with open(shortcuts_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    name, shortcut = line.split(':', 1)
                    name = name.strip()
                    shortcut = shortcut.strip()
                    if name in self.buttons:
                        button = self.buttons[name]
                        if self.enable_shortcuts:
                            flags, key = parse_shortcut(shortcut)
                            if key:
                                id_ = wx.NewId()
                                self.shortcut_ids[name] = id_
                                self.Bind(wx.EVT_MENU, lambda e, btn=button: btn.Command(wx.CommandEvent(wx.EVT_BUTTON.typeId, btn.GetId())), id=id_)
                                entries.append((flags, key, id_))
                    elif name in self.shortcuts:
                        if self.enable_shortcuts:
                            flags, key = parse_shortcut(shortcut)
                            if key:
                                id_ = wx.NewId()
                                self.shortcut_ids[name] = id_
                                self.Bind(wx.EVT_MENU, self.shortcuts[name], id=id_)
                                entries.append((flags, key, id_))
        # Always bind escape key regardless of shortcut settings
        esc_id = wx.NewId()
        self.Bind(wx.EVT_MENU, lambda e: self.Close(), id=esc_id)
        entries.append((wx.ACCEL_NORMAL, wx.WXK_ESCAPE, esc_id))

        if entries:
            accel_tbl = wx.AcceleratorTable(entries)
            self.SetAcceleratorTable(accel_tbl)

    def convert_audio(self, event):
        text = self.text_edit.GetValue().strip()
        if not text:
            wx.MessageBox("Please enter some text to convert", "Warning", wx.OK | wx.ICON_WARNING)
            return

        lang = self.lang_combo.GetStringSelection()
        if lang == "Select one...":
            wx.MessageBox("Please select a language.", "Warning", wx.OK | wx.ICON_WARNING)
            return

        self.convert_btn.Disable()
        self.add_file_btn.Disable()
        self.lang_combo.Disable()
        self.speed_spin.Disable()
        self.pitch_spin.Disable()
        self.text_edit.Disable()
        self.progress_bar.Show()

        self.tts_thread = TTSAPIThread(text, lang, self.speed_spin.GetValue(), self.pitch_spin.GetValue(), self.progress_bar.SetValue, self.on_conversion_finished)

    def on_conversion_finished(self, data, success):
        if success and data:
            logging.info("TTS conversion successful")
            # Apply speed and pitch modifications
            speed = self.speed_spin.GetValue()
            pitch = self.pitch_spin.GetValue()
            if speed != 1.0 or pitch != 1.0:
                try:
                    from pydub import AudioSegment
                    audio = AudioSegment.from_mp3(io.BytesIO(data))
                    if speed != 1.0:
                        audio = audio.speedup(playback_speed=speed)
                    if pitch != 1.0:
                        new_frame_rate = int(audio.frame_rate * pitch)
                        audio = audio.set_frame_rate(new_frame_rate)
                    output = io.BytesIO()
                    audio.export(output, format='mp3')
                    data = output.getvalue()
                except ImportError:
                    wx.MessageBox("Audio processing requires ffmpeg. Please install ffmpeg to enable speed/pitch adjustments.", "FFmpeg Required", wx.OK | wx.ICON_INFORMATION)
                except Exception as e:
                    logging.warning(f"Could not apply speed/pitch modifications: {e}")
                    wx.MessageBox(f"Could not apply speed/pitch modifications: {e}. Using original audio.", "Warning", wx.OK | wx.ICON_WARNING)
            self.last_audio_data = data
            show_success_dialog(self)
        else:
            logging.error("TTS conversion failed")
            show_api_error_popup(self)

    def show_success_dialog(self):
        show_success_dialog(self)

    def download_audio(self):
        download_audio(self)

    def listen_audio(self):
        listen_audio(self)

    def download_last_audio(self):
        download_last_audio(self)

    def add_file(self, event):
        with wx.FileDialog(self, "Open File", wildcard="Supported Files (*.rtf;*.pdf;*.txt;*.doc;*.docx)|*.rtf;*.pdf;*.txt;*.doc;*.docx|All Files (*.*)|*.*", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            text = read_file(pathname)
            if text is not None:
                self.text_edit.SetValue(text)
                self.text_edit.SetFocus()
            else:
                wx.MessageBox("Unable to open file! Please make sure that your file isn't corrupted and supported.", "Error", wx.OK | wx.ICON_ERROR)

    def show_api_error_popup(self):
        show_api_error_popup(self)

    def show_settings(self, event):
        dlg = wx.Dialog(self, title="Settings", size=wx.Size(400, 300))
        notebook = wx.Notebook(dlg)

        # General Tab
        self.general_panel = wx.Panel(notebook)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        gemini_label = wx.StaticText(self.general_panel, label="Gemini API Key:")
        self.vbox.Add(gemini_label, 0, wx.ALL, 5)

        self.gemini_key_edit = wx.TextCtrl(self.general_panel, style=wx.TE_PASSWORD)
        self.gemini_key_edit.SetValue(self.gemini_api_key)
        self.vbox.Add(self.gemini_key_edit, 0, wx.EXPAND | wx.ALL, 5)

        self.show_key_checkbox = wx.CheckBox(self.general_panel, label="Show API key")
        self.show_key_checkbox.Bind(wx.EVT_CHECKBOX, self.toggle_key_visibility)
        self.vbox.Add(self.show_key_checkbox, 0, wx.ALL, 5)

        save_key_btn = wx.Button(self.general_panel, label="Save")
        save_key_btn.Bind(wx.EVT_BUTTON, self.save_gemini_key)
        self.vbox.Add(save_key_btn, 0, wx.ALL, 5)

        save_path_label = wx.StaticText(self.general_panel, label="Default Save Path:")
        self.vbox.Add(save_path_label, 0, wx.ALL, 5)

        self.save_path_edit = wx.TextCtrl(self.general_panel)
        self.save_path_edit.SetValue(self.save_path)
        self.save_path_edit.Disable()
        self.vbox.Add(self.save_path_edit, 0, wx.EXPAND | wx.ALL, 5)

        choose_btn = wx.Button(self.general_panel, label="Choose...")
        choose_btn.Bind(wx.EVT_BUTTON, self.choose_save_path)
        self.vbox.Add(choose_btn, 0, wx.ALL, 5)

        self.general_panel.SetSizer(self.vbox)
        notebook.AddPage(self.general_panel, "General")

        # Shortcuts Tab
        shortcuts_panel = wx.Panel(notebook)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.enable_shortcuts_cb = wx.CheckBox(shortcuts_panel, label="Enable Shortcuts")
        self.enable_shortcuts_cb.SetValue(self.enable_shortcuts)
        vbox.Add(self.enable_shortcuts_cb, 0, wx.ALL, 5)

        more_info_btn = wx.Button(shortcuts_panel, label="More info...")
        more_info_btn.Bind(wx.EVT_BUTTON, self.show_shortcuts_info)
        vbox.Add(more_info_btn, 0, wx.ALL, 5)

        shortcuts_panel.SetSizer(vbox)
        notebook.AddPage(shortcuts_panel, "Shortcuts")

        # About Tab
        about_panel = wx.Panel(notebook)
        vbox = wx.BoxSizer(wx.VERTICAL)

        about_label = wx.StaticText(about_panel, label="InspectTTS v1.0\n\nCopyright 2025 Inspector\n\nPlease read the readme section for more info.\n\nAPI Provider: Sujan Rai - credits and big thanks to him!\n\nIf you're enjoying this app, feel free to contact me for feature requests via Telegram:\n\n@ms35last")
        vbox.Add(about_label, 0, wx.ALL, 5)

        copy_btn = wx.Button(about_panel, label="Copy Telegram ID")
        copy_btn.Bind(wx.EVT_BUTTON, self.copy_telegram_id)
        vbox.Add(copy_btn, 0, wx.ALL, 5)

        view_readme_btn = wx.Button(about_panel, label="View Readme")
        view_readme_btn.Bind(wx.EVT_BUTTON, self.view_readme)
        vbox.Add(view_readme_btn, 0, wx.ALL, 5)

        view_manual_btn = wx.Button(about_panel, label="View Manual")
        view_manual_btn.Bind(wx.EVT_BUTTON, self.show_manual_choice)
        vbox.Add(view_manual_btn, 0, wx.ALL, 5)

        contact_github_btn = wx.Button(about_panel, label="Contact me on GitHub")
        contact_github_btn.Bind(wx.EVT_BUTTON, self.contact_github)
        vbox.Add(contact_github_btn, 0, wx.ALL, 5)

        about_panel.SetSizer(vbox)
        notebook.AddPage(about_panel, "About")

        dlg_sizer = wx.BoxSizer(wx.VERTICAL)
        dlg_sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(dlg, wx.ID_OK, label="OK")
        ok_btn.Bind(wx.EVT_BUTTON, lambda e: self.save_settings(dlg))
        cancel_btn = wx.Button(dlg, wx.ID_CANCEL, label="Cancel")
        button_sizer.Add(ok_btn, 0, wx.ALL, 5)
        button_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        dlg_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT)

        dlg.SetSizer(dlg_sizer)
        dlg.Bind(wx.EVT_KEY_DOWN, lambda e: dlg.EndModal(wx.ID_CANCEL) if e.GetKeyCode() == wx.WXK_ESCAPE else e.Skip())
        dlg.ShowModal()
        dlg.Destroy()

    def save_settings(self, dlg):
        old_enable = self.enable_shortcuts
        self.config.set('Settings', 'save_path', self.save_path)
        self.enable_shortcuts = self.enable_shortcuts_cb.GetValue()
        self.config.set('Settings', 'enable_shortcuts', str(self.enable_shortcuts))
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
        if old_enable != self.enable_shortcuts:
            wx.MessageBox("Please restart for changes to take effect.", "Warning", wx.OK | wx.ICON_WARNING)
        dlg.EndModal(wx.ID_OK)

    def choose_save_path(self, event):
        with wx.DirDialog(self, "Choose Save Directory", self.save_path, style=wx.DD_DEFAULT_STYLE) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_OK:
                self.save_path = dirDialog.GetPath()
                self.save_path_edit.SetValue(self.save_path)

    def toggle_key_visibility(self, event):
        show = self.show_key_checkbox.GetValue()
        current_value = self.gemini_key_edit.GetValue()
        # Destroy old
        self.vbox.Detach(self.gemini_key_edit)
        self.gemini_key_edit.Destroy()
        # Create new
        style = 0 if show else wx.TE_PASSWORD
        self.gemini_key_edit = wx.TextCtrl(self.general_panel, value=current_value, style=style)
        self.vbox.Insert(1, self.gemini_key_edit, 0, wx.EXPAND | wx.ALL, 5)  # position after label
        self.vbox.Layout()

    def show_shortcuts_info(self, event):
        # Get shortcuts file path (same logic as README/manual files)
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            shortcuts_path = os.path.join(bundle_dir, "docs", "shortcuts.md")
        else:
            # Running in development
            shortcuts_path = os.path.join(os.getcwd(), "docs", "shortcuts.md")

        dlg = wx.Dialog(self, title="Shortcuts", size=wx.Size(400, 300))
        text = "Application Shortcuts:\n\n"
        try:
            with open(shortcuts_path, 'r', encoding='utf-8') as f:
                text += f.read()
        except Exception as e:
            text += f"shortcuts.md not found or error: {e}"
        text_ctrl = wx.TextCtrl(dlg, value=text, style=wx.TE_MULTILINE | wx.TE_READONLY)
        text_ctrl.SetFocus()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        ok_btn = wx.Button(dlg, wx.ID_OK, label="OK")
        sizer.Add(ok_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        dlg.SetSizer(sizer)
        dlg.Bind(wx.EVT_KEY_DOWN, lambda e: dlg.EndModal(wx.ID_CANCEL) if e.GetKeyCode() == wx.WXK_ESCAPE else e.Skip())
        dlg.ShowModal()
        dlg.Destroy()

    def save_gemini_key(self, event):
        key = self.gemini_key_edit.GetValue().strip()
        if not key:
            wx.MessageBox("Please enter a Gemini API key.", "Warning", wx.OK | wx.ICON_WARNING)
            return
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={key}"
            payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and data['candidates']:
                    self.gemini_api_key = key
                    self.config.set('Settings', 'gemini_api_key', key)
                    with open(self.config_file, 'w') as configfile:
                        self.config.write(configfile)
                    wx.MessageBox("API saved successfully! The API key you have provided is working and saved, you can now talk to AI using this API!", "Success", wx.OK | wx.ICON_INFORMATION)
                else:
                    wx.MessageBox("API key is invalid or not working.", "Error", wx.OK | wx.ICON_ERROR)
            else:
                wx.MessageBox("API error: Please make sure that the API key you have entered is correct and working.", "Error", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"Failed to test API: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    def copy_telegram_id(self, event):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject("@ms35last"))
            wx.TheClipboard.Close()

    def contact_github(self, event):
        import webbrowser
        github_url = "https://github.com/inspector3535/Inspect-TTS-issues"
        webbrowser.open(github_url)

    def view_readme(self, event):
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            readme_path = os.path.join(bundle_dir, "docs", "README.md")
        else:
            # Running in development
            readme_path = os.path.join(os.getcwd(), "docs", "README.md")
        if os.path.exists(readme_path):
            dlg = wx.Dialog(self, title="README", size=wx.Size(800, 600))
            text = ""
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except Exception as e:
                text = f"Error reading README.md: {e}"
            text_ctrl = wx.TextCtrl(dlg, value=text, style=wx.TE_MULTILINE | wx.TE_READONLY)
            text_ctrl.SetFocus()
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 5)
            ok_btn = wx.Button(dlg, wx.ID_OK, label="OK")
            sizer.Add(ok_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
            dlg.SetSizer(sizer)
            dlg.Bind(wx.EVT_KEY_DOWN, lambda e: dlg.EndModal(wx.ID_CANCEL) if e.GetKeyCode() == wx.WXK_ESCAPE else e.Skip())
            dlg.ShowModal()
            dlg.Destroy()
        else:
            wx.MessageBox("README.md not found in the application directory.", "File not found", wx.OK | wx.ICON_ERROR)

    def show_manual_choice(self, event):
        dlg = wx.Dialog(self, title="Choose Manual Language", size=wx.Size(300, 150))
        vbox = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(dlg, label="Please choose which manual to view:")
        vbox.Add(label, 0, wx.ALL, 10)

        self.manual_lang_combo = wx.Choice(dlg, choices=["English", "Turkish"])
        self.manual_lang_combo.SetSelection(0)  # Default to English
        vbox.Add(self.manual_lang_combo, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(dlg, wx.ID_OK, label="OK")
        ok_btn.Bind(wx.EVT_BUTTON, lambda e: self.on_manual_ok(dlg))
        hbox.Add(ok_btn, 0, wx.ALL, 5)

        cancel_btn = wx.Button(dlg, wx.ID_CANCEL, label="Cancel")
        hbox.Add(cancel_btn, 0, wx.ALL, 5)
        vbox.Add(hbox, 0, wx.ALIGN_CENTER)

        dlg.SetSizer(vbox)
        dlg.Bind(wx.EVT_KEY_DOWN, lambda e: dlg.EndModal(wx.ID_CANCEL) if e.GetKeyCode() == wx.WXK_ESCAPE else e.Skip())

        # Tab order: combo first, then OK, Cancel
        self.manual_lang_combo.SetFocus()

        dlg.ShowModal()
        dlg.Destroy()

    def on_manual_ok(self, dlg):
        selection = self.manual_lang_combo.GetStringSelection()
        if selection == "English":
            manual_file = "Manual-EN.md"
        elif selection == "Turkish":
            manual_file = "Manual-TR.md"
        else:
            wx.MessageBox("Invalid selection.", "Error", wx.OK | wx.ICON_ERROR)
            return

        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            manual_path = os.path.join(bundle_dir, "docs", manual_file)
        else:
            # Running in development
            manual_path = os.path.join(os.getcwd(), "docs", manual_file)
        if os.path.exists(manual_path):
            self.view_manual(manual_path, selection)
        else:
            wx.MessageBox(f"{manual_file} not found in the application directory.", "File not found", wx.OK | wx.ICON_ERROR)
        dlg.EndModal(wx.ID_OK)

    def view_manual(self, path, lang):
        dlg = wx.Dialog(self, title=f"Manual ({lang})", size=wx.Size(800, 600))
        text = ""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            text = f"Error reading {os.path.basename(path)}: {e}"
        text_ctrl = wx.TextCtrl(dlg, value=text, style=wx.TE_MULTILINE | wx.TE_READONLY)
        text_ctrl.SetFocus()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        ok_btn = wx.Button(dlg, wx.ID_OK, label="OK")
        sizer.Add(ok_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        dlg.SetSizer(sizer)
        dlg.Bind(wx.EVT_KEY_DOWN, lambda e: dlg.EndModal(wx.ID_CANCEL) if e.GetKeyCode() == wx.WXK_ESCAPE else e.Skip())
        dlg.ShowModal()
        dlg.Destroy()

    def open_ai_window(self):
        self.ai_dialog = wx.Dialog(self, title="Ask AI", size=wx.Size(600, 400))
        self.conversation_history = []

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.ai_response = AccessibleTextCtrl(self.ai_dialog, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.ai_response.SetMinSize(wx.Size(-1, 200))
        vbox.Add(self.ai_response, 1, wx.EXPAND | wx.ALL, 5)

        # Add status label for better UX during AI generation
        self.ai_status = wx.StaticText(self.ai_dialog, label="")
        vbox.Add(self.ai_status, 0, wx.EXPAND | wx.ALL, 5)

        self.ai_progress = wx.Gauge(self.ai_dialog, range=100)
        self.ai_progress.Hide()
        vbox.Add(self.ai_progress, 0, wx.EXPAND | wx.ALL, 5)

        copy_btn = wx.Button(self.ai_dialog, label="Copy Response")
        copy_btn.Bind(wx.EVT_BUTTON, self.copy_response)
        vbox.Add(copy_btn, 0, wx.ALL, 5)

        export_btn = wx.Button(self.ai_dialog, label="Export results to a file")
        export_btn.Bind(wx.EVT_BUTTON, self.export_results)
        vbox.Add(export_btn, 0, wx.ALL, 5)

        input_sizer = wx.BoxSizer(wx.HORIZONTAL)

        attach_btn = wx.Button(self.ai_dialog, label="Attach a file")
        attach_btn.Bind(wx.EVT_BUTTON, self.attach_file)
        input_sizer.Add(attach_btn, 0, wx.ALL, 5)

        self.ai_input = AIInput(self.ai_dialog, self.send_ai_query)
        self.ai_input.SetMinSize(wx.Size(-1, 180))
        input_sizer.Add(self.ai_input, 1, wx.EXPAND | wx.ALL, 5)

        send_btn = wx.Button(self.ai_dialog, label="Send")
        send_btn.Bind(wx.EVT_BUTTON, self.send_ai_query)
        input_sizer.Add(send_btn, 0, wx.ALL, 5)

        vbox.Add(input_sizer, 0, wx.EXPAND)

        self.ai_dialog.SetSizer(vbox)

        # Escape key handler for modal dialog
        self.ai_dialog.Bind(wx.EVT_CHAR_HOOK, lambda e: self.ai_dialog.EndModal(wx.ID_CANCEL) if e.GetKeyCode() == wx.WXK_ESCAPE else e.Skip())

        # Tab order
        self.ai_input.SetFocus()

        self.ai_dialog.ShowModal()
        self.ai_dialog.Destroy()



    def attach_file(self, event):
        with wx.FileDialog(self.ai_dialog, "Attach File", wildcard="Supported Files (*.txt *.pdf *.doc *.docx *.rtf)", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            text = read_file(pathname)
            if text is not None:
                self.attached_file_content = text
                wx.MessageBox("File attached successfully. You can now type your query.", "File Attached", wx.OK | wx.ICON_INFORMATION)
                self.ai_input.SetFocus()
            else:
                wx.MessageBox("Unable to read the selected file.", "Error", wx.OK | wx.ICON_ERROR)

    def send_ai_query(self):
        query = self.ai_input.GetValue().strip()
        if not query:
            wx.MessageBox("Please enter a query.", "Warning", wx.OK | wx.ICON_WARNING)
            return

        full_query = query
        if self.fetched_content:
            full_query = f"Analyze this content:\n{self.fetched_content}\n\nQuery: {query}"
            self.fetched_content = None
        elif self.attached_file_content:
            full_query = f"Analyze this file:\n{self.attached_file_content}\n\nQuery: {query}"

        send_btn = self.ai_dialog.FindWindowByName("Send")
        if send_btn:
            send_btn.Disable()
        self.ai_input.Disable()
        self.ai_progress.Show()

        # Show waiting message and disable interaction until completion
        self.ai_response.SetValue("Generating result, please wait...")
        self.ai_response.Disable()  # Prevent user interaction during generation
        # Disable buttons during generation
        copy_btn = self.ai_dialog.FindWindowByName("Copy Response")
        if copy_btn:
            copy_btn.Disable()
        export_btn = self.ai_dialog.FindWindowByName("Export results to a file")
        if export_btn:
            export_btn.Disable()

        self.conversation_history.append({"role": "user", "parts": [{"text": full_query}]})

        self.ai_thread = AIThread(full_query, self.gemini_api_key, self.conversation_history, self.on_ai_response, lambda p: self.ai_progress.SetValue(p))

    def on_ai_response(self, ai_text, success):
        if success:
            logging.info("AI query successful")
            self.conversation_history.append({"role": "model", "parts": [{"text": ai_text}]})
            conversation_text = ""
            for msg in self.conversation_history:
                role = msg["role"]
                text = msg["parts"][0]["text"]
                conversation_text += f"{role.capitalize()}: {text}\n\n"
            self.ai_status.SetLabel("")  # Clear status message
            self.ai_response.SetValue(conversation_text)
            self.ai_response.SetFocus()  # Move focus to results
        else:
            logging.error(f"AI query failed: {ai_text}")
            self.ai_status.SetLabel("")  # Clear status message
            self.ai_response.SetValue(ai_text)
            self.ai_response.SetFocus()  # Focus on error message

        self.ai_progress.Hide()
        self.ai_response.Enable()  # Re-enable response area after generation
        # Re-enable buttons after generation
        copy_btn = self.ai_dialog.FindWindowByName("Copy Response")
        if copy_btn:
            copy_btn.Enable()
        export_btn = self.ai_dialog.FindWindowByName("Export results to a file")
        if export_btn:
            export_btn.Enable()
        send_btn = self.ai_dialog.FindWindowByName("Send")
        if send_btn:
            send_btn.Enable()
        self.ai_input.Enable()
        self.ai_input.Clear()
        self.ai_input.SetFocus()

    def copy_response(self, event):
        text = self.ai_response.GetValue()
        if text:
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(text))
                wx.TheClipboard.Close()
                # Removed notification message as per suggestion
        else:
            wx.MessageBox("No response to copy.", "No Response", wx.OK | wx.ICON_WARNING)

    def export_results(self, event):
        text = self.ai_response.GetValue()
        if not text:
            wx.MessageBox("No response to export.", "No Response", wx.OK | wx.ICON_WARNING)
            return

        with wx.FileDialog(self.ai_dialog, "Export Results", wildcard="Text Files (*.txt)|*.txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w', encoding='utf-8') as f:
                    f.write(text)
                # Removed notification message as per suggestion
            except Exception as e:
                wx.MessageBox(f"Failed to export: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def show_notepad(self, event):
        dlg = NotepadDialog(self.save_path, self)
        dlg.ShowModal()
        dlg.Destroy()

    def show_reader(self, event):
        with wx.FileDialog(self, "Open Document", self.save_path, wildcard="Supported Files (*.txt *.pdf *.epub *.rtf *.doc *.docx)|*.txt;*.pdf;*.epub;*.rtf;*.doc;*.docx", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            text = read_file(pathname)
            if text is not None:
                reader_dlg = ReaderDialog(text, self)
                reader_dlg.ShowModal()
                reader_dlg.Destroy()
            else:
                wx.MessageBox("Unable to read the selected file. Please ensure it is a supported format and not corrupted.", "Error", wx.OK | wx.ICON_ERROR)

    def show_fetch_page_dialog(self, event):
        dlg = wx.Dialog(self, title="Fetch Page", size=wx.Size(400, 150))
        vbox = wx.BoxSizer(wx.VERTICAL)

        url_label = wx.StaticText(dlg, label="Please enter the desired URL to fetch")
        vbox.Add(url_label, 0, wx.ALL, 5)

        self.url_edit = wx.TextCtrl(dlg)
        vbox.Add(self.url_edit, 0, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fetch_btn = wx.Button(dlg, label="Fetch")
        fetch_btn.Bind(wx.EVT_BUTTON, lambda e: self.fetch_page(dlg))
        button_sizer.Add(fetch_btn, 0, wx.ALL, 5)

        cancel_btn = wx.Button(dlg, wx.ID_CANCEL, label="Cancel")
        button_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        vbox.Add(button_sizer, 0, wx.ALIGN_RIGHT)

        dlg.SetSizer(vbox)
        dlg.Bind(wx.EVT_KEY_DOWN, lambda e: dlg.EndModal(wx.ID_CANCEL) if e.GetKeyCode() == wx.WXK_ESCAPE else e.Skip())
        dlg.ShowModal()
        dlg.Destroy()

    def fetch_page(self, dlg):
        url = self.url_edit.GetValue().strip()
        if not url:
            wx.MessageBox("Please enter a URL.", "Warning", wx.OK | wx.ICON_WARNING)
            return

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                html_content = response.text
                html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
                html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
                html_content = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', html_content, flags=re.IGNORECASE)
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html_content, 'html.parser')
                    content = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    text_content = '\n'.join([elem.get_text() for elem in content])
                except ImportError:
                    text_content = re.sub(r'<[^>]+>', '', html_content)
                    text_content = re.sub(r'\s+', ' ', text_content).strip()

                self.show_page_content(text_content)
                dlg.EndModal(wx.ID_OK)
            else:
                wx.MessageBox(f"Failed to fetch page: HTTP {response.status_code}", "Error", wx.OK | wx.ICON_ERROR)
        except requests.exceptions.RequestException as e:
            wx.MessageBox(f"Network error: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    def show_page_content(self, content):
        dlg = wx.Dialog(self, title="Page Content", size=wx.Size(800, 600))
        vbox = wx.BoxSizer(wx.VERTICAL)

        text_view = wx.TextCtrl(dlg, style=wx.TE_MULTILINE | wx.TE_READONLY)
        text_view.SetValue(content)
        # Add page navigation for better content browsing
        def on_text_key_down(event):
            key = event.GetKeyCode()
            current_pos = text_view.GetInsertionPoint()
            text_length = len(text_view.GetValue())

            if key == wx.WXK_PAGEUP:
                # Page up functionality - jump back ~2000 characters
                new_pos = max(0, current_pos - 2000)
                text_view.SetInsertionPoint(new_pos)
                text_view.ShowPosition(new_pos)
            elif key == wx.WXK_PAGEDOWN:
                # Page down functionality - jump forward ~2000 characters
                new_pos = min(text_length, current_pos + 2000)
                text_view.SetInsertionPoint(new_pos)
                text_view.ShowPosition(new_pos)
            else:
                # Let default arrow key behavior work normally
                event.Skip()
        text_view.Bind(wx.EVT_KEY_DOWN, on_text_key_down)
        vbox.Add(text_view, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        def on_summarize(event):
            self.summarize_with_ai(content)

        def on_copy(event):
            self.copy_content(content)

        summarize_btn = wx.Button(dlg, label="Summarize with AI")
        summarize_btn.Bind(wx.EVT_BUTTON, on_summarize)
        button_sizer.Add(summarize_btn, 0, wx.ALL, 5)

        copy_btn = wx.Button(dlg, label="Copy article to clipboard")
        copy_btn.Bind(wx.EVT_BUTTON, on_copy)
        button_sizer.Add(copy_btn, 0, wx.ALL, 5)

        cancel_btn = wx.Button(dlg, wx.ID_CANCEL, label="Cancel")
        button_sizer.Add(cancel_btn, 0, wx.ALL, 5)

        vbox.Add(button_sizer, 0, wx.ALIGN_RIGHT)

        dlg.SetSizer(vbox)
        dlg.Bind(wx.EVT_KEY_DOWN, lambda e: dlg.EndModal(wx.ID_CANCEL) if e.GetKeyCode() == wx.WXK_ESCAPE else e.Skip())
        text_view.SetFocus()
        dlg.ShowModal()
        dlg.Destroy()

    def copy_content(self, content):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(content))
            wx.TheClipboard.Close()
            wx.MessageBox("Content copied to clipboard.", "Copied", wx.OK | wx.ICON_INFORMATION)

    def show_converter_dialog(self, event):
        show_converter_dialog(self, event)

    def select_source_file(self, dlg):
        select_source_file(self, dlg)

    def convert_file(self, dlg):
        convert_file(self, dlg)

    def show_conversion_success(self, file_path, parent_dlg):
        show_conversion_success(self, file_path, parent_dlg)

    def summarize_with_ai(self, content):
        if not self.gemini_api_key:
            wx.MessageBox("Please provide a valid API first.", "Error", wx.OK | wx.ICON_ERROR)
            return
        self.fetched_content = content
        if not hasattr(self, 'ai_dialog') or not self.ai_dialog.IsShown():
            self.open_ai_window()

    def check_api_and_open_ai(self, event):
        if not self.gemini_api_key:
            wx.MessageBox("Please configure a Gemini API to use the AI related features.", "Error", wx.OK | wx.ICON_ERROR)
            return
        self.open_ai_window()

    def on_close(self, event):
        logging.info("InspectTTS application closed")
        self.Destroy()

    def on_key_down(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.Close()
        else:
            event.Skip()