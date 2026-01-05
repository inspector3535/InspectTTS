import io
import logging
import os
import subprocess
import sys
import tempfile
import wx

from tts_api import TTSAPIThread

def show_success_dialog(self):
    dlg = wx.Dialog(self, title="Conversion Successful!", size=wx.Size(300, 120))
    vbox = wx.BoxSizer(wx.VERTICAL)

    label = wx.StaticText(dlg, label="What would you like to do?")
    vbox.Add(label, 0, wx.ALL | wx.CENTER, 10)

    hbox = wx.BoxSizer(wx.HORIZONTAL)
    download_btn = wx.Button(dlg, wx.ID_OK, label="Download audio")
    listen_btn = wx.Button(dlg, wx.ID_CANCEL, label="Listen to audio only")
    hbox.Add(download_btn, 0, wx.ALL, 5)
    hbox.Add(listen_btn, 0, wx.ALL, 5)
    vbox.Add(hbox, 0, wx.ALIGN_CENTER)

    dlg.SetSizer(vbox)
    dlg.Bind(wx.EVT_KEY_DOWN, lambda e: dlg.EndModal(wx.ID_CANCEL) if e.GetKeyCode() == wx.WXK_ESCAPE else e.Skip())

    result = dlg.ShowModal()
    if result == wx.ID_OK:
        self.download_audio()
    elif result == wx.ID_CANCEL:
        self.listen_audio()
    dlg.Destroy()

def download_audio(self):
    if self.last_audio_data:
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", "speech.mp3")
        try:
            with open(downloads_path, 'wb') as f:
                f.write(self.last_audio_data)
            wx.MessageBox("Audio file saved to Downloads folder.", "Download complete", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"Download failed: {e}", "Error", wx.OK | wx.ICON_ERROR)

def listen_audio(self):
    if self.last_audio_data:
        try:
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "inspecttts_temp.mp3")
            with open(temp_path, "wb") as f:
                f.write(self.last_audio_data)
            try:
                subprocess.Popen(["vlc", "--play-and-exit", temp_path])
            except FileNotFoundError:
                if sys.platform.startswith("win"):
                    os.startfile(temp_path)
                elif sys.platform.startswith("darwin"):
                    subprocess.Popen(["open", temp_path])
                else:
                    subprocess.Popen(["xdg-open", temp_path])
        except Exception as e:
            wx.MessageBox(f"Unable to play audio: {e}", "Listen failed", wx.OK | wx.ICON_ERROR)

def download_last_audio(self):
    if self.last_audio_data:
        self.download_audio()
    else:
        wx.MessageBox("No audio available.", "Warning", wx.OK | wx.ICON_WARNING)

def on_conversion_finished(self, data, success):
    self.convert_btn.Enable()
    self.add_file_btn.Enable()
    self.lang_combo.Enable()
    self.speed_spin.Enable()
    self.pitch_spin.Enable()
    self.text_edit.Enable()
    self.progress_bar.Hide()
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
            except Exception as e:
                logging.warning(f"Could not apply speed/pitch modifications: {e}")
                wx.MessageBox(f"Could not apply speed/pitch modifications: {e}. Using original audio.", "Warning", wx.OK | wx.ICON_WARNING)
        self.last_audio_data = data
        self.show_success_dialog()
    else:
        logging.error("TTS conversion failed")
        self.show_api_error_popup()

def show_api_error_popup(self):
    wx.MessageBox("API Error! Please make sure that the API server is running and check quota.", "API Error", wx.OK | wx.ICON_ERROR)