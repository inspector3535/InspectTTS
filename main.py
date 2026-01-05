import os
import sys

# Configure ffmpeg path for bundled executable
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg', 'ffmpeg.exe')
    if os.path.exists(ffmpeg_path):
        # Set ffmpeg path for pydub
        import pydub
        pydub.AudioSegment.ffmpeg = ffmpeg_path
else:
    # Running in development - use system ffmpeg if available
    pass

from main_window import MainWindow
import wx

if __name__ == "__main__":
    app = wx.App()
    window = MainWindow()
    window.Show()
    app.MainLoop()