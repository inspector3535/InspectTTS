export default async function handler(req, res) {
  try {
    const response = await fetch("https://api.elevenlabs.io/v1/voices", {
      headers: {
        "xi-api-key": process.env.ElevenLabsAPI
      }
    });

    const data = await response.json();

    const voices = Array.isArray(data)
      ? data
      : Array.isArray(data.voices)
      ? data.voices
      : [];

    if (voices.length === 0) {
      return res.status(200).json({ languages: [] });
    }

    const languagesSet = new Set();

    voices.forEach(voice => {
      if (voice.labels) {
        Object.values(voice.labels).forEach(value => {
          if (typeof value === "string") {
            languagesSet.add(value);
          }
        });
      }
    });

    res.status(200).json({
      languages: Array.from(languagesSet)
    });

  } catch (error) {
    res.status(500).json({
      error: "Failed to fetch languages"
    });
  }
}
