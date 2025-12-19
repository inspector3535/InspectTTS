export const runtime = "nodejs";

let cachedVoices = null;
let cachedAt = 0;

const CACHE_TTL = 6 * 60 * 60 * 1000;

const FALLBACK_VOICES = [
  {
    voice_id: "fallback-1",
    name: "Default Voice",
    description: "Fallback voice used when ElevenLabs is unavailable",
    labels: { accent: "neutral", gender: "neutral" }
  }
];

export default async function handler(req, res) {
  const now = Date.now();

  if (cachedVoices && (now - cachedAt) < CACHE_TTL) {
    return res.status(200).json({
      source: "cache",
      voices: cachedVoices
    });
  }

  try {
    const response = await fetch("https://api.elevenlabs.io/v1/voices", {
      headers: {
        "xi-api-key": process.env.ELEVENLABS_API_KEY,
        "Accept": "application/json"
      }
    });

    if (!response.ok) {
      const t = await response.text();
      throw new Error(`ElevenLabs ${response.status}: ${t}`);
    }

    const data = await response.json();
    const voices = data.voices || [];

    cachedVoices = voices;
    cachedAt = now;

    return res.status(200).json({
      source: "live",
      voices
    });

  } catch (error) {
    if (cachedVoices) {
      return res.status(200).json({
        source: "cache",
        voices: cachedVoices,
        warning: error.message
      });
    }

    return res.status(200).json({
      source: "fallback",
      voices: FALLBACK_VOICES,
      error: error.message
    });
  }
}
