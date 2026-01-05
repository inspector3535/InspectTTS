InspectTTS manual.
In this file, you will find answers to all your questions about my experimental project InspectTTS and API. Please read carefully.
first of all I want to start with a question: What features do you think a TTS (Text-to-Speech app) should have?
Hello, I am Mert Anlar. I previously brought Turkish language support to the TeamTalk Classic app and provided technical support to visually impaired communities.
I have been working on accessibility in the background for a long time. A message I received from a Telegram group inspired me, and I launched the Inspect TTS (EXPERIMENTAL) project.
So, what was that message? A tiny API.
Yes, this minuscule structure, which we use in every area of technology and is indispensable, led me to develop my own app.
So, what is an API? (For those who don't know)
An API is an intermediary bridge that fulfills your requests. With a symple example, when you go to a restaurant, instead of going to the kitchen yourself to get your food, you order from the waiter. The waiter ensures it's prepared inside and brought to your table.
in terms of technology, the API logic works as follows:
When you want to listen to music from platforms like YouTube or Spotify, you type the song's name in the search box and press the search button. Your request is first transmitted and processed by the platform via an API server.
Then, the platform brings you your search results via the API, and you can listen to your request.
Of course, your ability to play the song also depends on this API. When you give the command "play," the request communicates with the API server again and returns to you as music.
So, what is Inspect TTS? Inspect TTS is essentially a text-to-speech app. It relies on a 3rd party Google TTS service and allows you to download the converted text as an MP3 to your computer and listen to it with your favorite player.
For those who don't want to download, it also offers a listen-only option.
Inspect TTS is not just a TTS app; it is an experimental project that combines text processing and productivity features.
Thanks to its portable structure, no installation is required, and it leaves no trace in the registry or folders like Program Files.
In addition, it allows you to determine the speed and pitch. It also enables you to easily convert your text files into audio files with its file attachment feature.
When you select your file, you can read a preview of it in a text box to ensure you haven't selected the wrong file.
It is crucial to specify the language of your file or typed text from the language selection box; otherwise, the conversion process will fail.
Supported languages: Arabic (ar), Bulgarian (BG), German (de), English en, Hindi (hi), Japanese (ja), Chinese (zh), and Turkish (tr).
After setting the speed and pitch in the respective fields, you can press the "Convert to Audio" button and choose "Download" or "Listen only" to either download or just listen. So, what distinguishes this app from others on the market? You'll find out below.
Notepad. Another feature!
Why should this TTS app be just a simple text-to-speech app? I'm sure a small but useful notepad would adorn this app.
Moreover, unlike classic notepad apps that save as .txt, this one can also save in PDF, RTF, TXT, and DOCX formats.
Ask AI:
The presence of artificial intelligence has exploded today. It's in our computers, phones, and even our favorite social media apps, so why shouldn't it be in this app?
With the AI feature within Inspect TTS, you can:
• Ask questions about your text files, summarize them, analyze them,
• Consult the AI assistant on any topic you're curious about,
• Save AI outputs to a file,
• And copy them directly to the clipboard!
Reader (document reader):
Wouldn't it be great to be able to read your documents within Inspect TTS, without leaving the app, in a sweet and accessible interface?
This reader is just perfect for that! You can open any text file within the app and read it in a plain text box.
File converter:
Wouldn't you like to convert your text files to each other?
Why waste hours searching for file conversion apps online and watching countless ads? With Inspect TTS's built-in file converter, your valuable time will be yours. The file converter supports popular document formats and allows easy conversion between them.
Fetch a page:
Do you have an article or news piece?
Thanks to this feature of the Inspect TTS, you can easily read it without being exposed to links, graphics, and clickable elements on the page!
Additionally, you can share the article you're reading with your AI assistant and ask it questions!
All you need to do is press the "Analyze with AI" button, and the rest is up to the app! The app shares the content of the page you are currently reading with the Ask AI feature, and all you have to do is tell it what you want to do.
*** Settings ***
Now we come to the settings section. Every change you make here is saved to a tiny file called Settings.ini, and your settings are preserved as long as this file exists. Let's get acquainted with our settings window...
General page:
Here you can connect your existing Gemini API key to access AI-powered features (currently only Gemini is supported). There is also a "Show API key" checkbox to ensure you've entered your API key correctly.
When you check this, you can compare it with the key in the box and on your clipboard. When you press the "Save" button, the app sends a request to ensure the key is working correctly.
If everything is fine, it displays a success and saved message; otherwise, it is not saved. Furthermore, I am continuing my work to enable the key to be saved secretly in the settings file, in a format that only the app can read.
This would be a great advantage for those who want to share the app with their own key and allow others to benefit, but as a developer, I definitely do not recommend this.
I want to implement this feature purely for security reasons.
"Actually, it would be better to integrate a 3rd party AI; who wants to bother getting an API key and all that?" I hear you say. You are absolutely right, very much so.
Rest assured, this was what I wanted to do most, but due to 3rd party AI services sometimes working one day and taking a break the next, I had to integrate Gemini. This way, the data you share with AI and the quota you use are under your control.
• "Choose..." button for the notes folder:
InspectTTS is designed to save your notes to the Documents folder by default, but you can also specify a different location to have your notes saved there.
Shortcuts: Yes, I've added shortcuts to easily access the buttons within the app, so instead of tabbing through, you can reach the desired function via a shortcut.
Enable Shortcuts: It is off by default.
More info... Here, the shortcuts are listed in a text viewer, and you can reach the desired function using the arrow keys.
About page:
Here you can read the thank you message to 3rd party API providers, view the readme, English and Turkish Manual files of the app and copy my Telegram address to contact me.
*** Notes***:
• This concept, which is still in the experimental stage, was developed in English so that it can be tested on a global scale. My work continues to add different languages.
• Please remember that the app relies on a 3rd party Google TTS service, and this service may be temporarily or permanently shut down. For the continuation of my project, I am researching different TTS services.
Those who wish to assist me in this regard can contact me via the Telegram username I will provide in this document and in the About section of my app.
• My work continues to preserve special characters such as (┘ ² ←) in text files during conversion.
• To access AI features, you can use a Gemini API key obtained from the Google Cloud platform; API keys obtained from platforms like Google AI Studio may considered invalid.
• For my experimental project, I prefer not to share the source code until a period of time that I will determine. I kindly ask my valued users to explore the application, enjoy using it in their daily lives, and provide me with feedback only.
• For secure distribution, the project will be shared via the GitHub platform. Users who are familiar with GitHub may also use the Issues page (which will be provided in the contact section) to submit feedback, feature requests, and bug reports.
• This decision has been made with security, sustainability, and the project’s maturation process in mind.
*** Disclaimer ***
Please keep in mind that this app is currently a concept, and I (Mert Anlar, also known as Inspector or Robert Smith) cannot be held responsible for any potential issues that may arise during use.
This project has been developed solely for API testing and educational purposes. Please use it at your own risk.
*** Contact ***
How did you find my app? For bug reports, feedback, or feature requests, you can contact me using the channels below:
Telegram: @ms35last
Github: https://github.com/inspector3535/Inspect-TTS-issues
This experimental project may grow or disappear over time based on your feedback, but whatever the outcome, I thoroughly enjoyed developing it.
A small step I took for an API test returned to me as such an experimental project. I hope you use it with happiness and health and benefit from the effort I put in.