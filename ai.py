import logging
import requests
import threading
import time
import wx

from utils import read_file

class AccessibleTextCtrl(wx.TextCtrl):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def on_key_down(self, event):
        key = event.GetKeyCode()
        if key in (wx.WXK_UP, wx.WXK_DOWN, wx.WXK_LEFT, wx.WXK_RIGHT):
            # Notify accessibility for cursor movement
            # wxPython has limited accessibility support, but we can try
            pass
        event.Skip()

class AIThread:
    def __init__(self, query, api_key, conversation_history, callback, progress_callback=None):
        self.query = query
        self.api_key = api_key
        self.conversation_history = conversation_history
        self.callback = callback
        self.progress_callback = progress_callback
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        for attempt in range(3):
            try:
                if self.progress_callback:
                    wx.CallAfter(self.progress_callback, 10)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={self.api_key}"
                payload = {"contents": self.conversation_history}
                if self.progress_callback:
                    wx.CallAfter(self.progress_callback, 50)
                response = requests.post(url, json=payload, timeout=15)
                if self.progress_callback:
                    wx.CallAfter(self.progress_callback, 90)
                if response.status_code == 200:
                    data = response.json()
                    if 'candidates' in data and data['candidates'] and 'content' in data['candidates'][0] and 'parts' in data['candidates'][0]['content'] and data['candidates'][0]['content']['parts']:
                        ai_text = data['candidates'][0]['content']['parts'][0]['text']
                        if self.progress_callback:
                            wx.CallAfter(self.progress_callback, 100)
                        wx.CallAfter(self.callback, ai_text, True)
                        return
                    else:
                        wx.CallAfter(self.callback, "No response from AI or invalid response format", False)
                        return
                elif response.status_code == 429:  # Quota exceeded
                    wx.CallAfter(self.callback, "API Quota exceeded. Please try again later.", False)
                    return
                else:
                    if attempt == 2:
                        wx.CallAfter(self.callback, f"API Error: HTTP {response.status_code} - {response.reason}", False)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
                if attempt < 2:
                    time.sleep(1)
                    continue
                else:
                    wx.CallAfter(self.callback, "Error: Network issue. Please check your internet connection.", False)
            except Exception as e:
                logging.error(f"Unexpected AI API Error: {str(e)}")
                wx.CallAfter(self.callback, f"Unexpected error: {str(e)}", False)
                return

class AIInput(wx.TextCtrl):
    def __init__(self, parent, send_callback):
        super().__init__(parent, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        self.send_callback = send_callback
        self.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def on_enter(self, event):
        self.send_callback()

    def on_key_down(self, event):
        if event.ControlDown() and event.GetKeyCode() == ord('\n'):  # Shift+Enter for new line
            self.WriteText('\n')
        else:
            event.Skip()