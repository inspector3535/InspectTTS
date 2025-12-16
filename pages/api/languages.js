export default async function handler(req, res) {
  try {
    const response = await fetch("https://api.elevenlabs.io/v1/voices", {
      headers: {
        "xi-api-key": process.env.ElevenLabsAPI
      }
    });

    const data = await response.json();

    if (!data.voices) {
      return res.status(500).json({ error: "Voices data not found" });
    }

    const languagesSet = new Set();

    data.voices.forEach(voice => {
      if (voice.labels) {
        if (voice.labels.language) {
          languagesSet.add(voice.labels.language);
        }
        if (voice.labels.accent) {
          languagesSet.add(voice.labels.accent);
        }
      }
    });

    const languages = Array.from(languagesSet);

    res.status(200).json({
      languages
    });

  } catch (error) {
    res.status(500).json({
      error: "Failed to fetch languages"
    });
  }
}
