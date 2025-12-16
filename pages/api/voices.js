let cachedVoices = null;
let cacheTimestamp = 0;

const CACHE_DURATION = 1000 * 60 * 60 * 6;

export default async function handler(req, res) {
  try {
    const now = Date.now();

    if (cachedVoices && now - cacheTimestamp < CACHE_DURATION) {
      return res.status(200).json({
        source: "cache",
        voices: cachedVoices
      });
    }

    const response = await fetch("https://api.elevenlabs.io/v1/voices", {
      headers: {
        "xi-api-key": process.env.ElevenLabsAPI,
        "Accept": "application/json"
      }
    });

    if (!response.ok) {
      const text = await response.text();
      return res.status(response.status).json({
        error: "ElevenLabs API error",
        status: response.status,
        details: text
      });
    }

    const data = await response.json();
    const voices = data.voices || [];

    cachedVoices = voices;
    cacheTimestamp = now;

    res.status(200).json({
      source: "live",
      voices
    });

  } catch (err) {
    res.status(500).json({
      error: "Unexpected server error",
      message: err.message
    });
  }
}
