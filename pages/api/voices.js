let cachedVoices = null;
let cacheTimestamp = 0;

const CACHE_DURATION = 1000 * 60 * 60 * 6; // 6 saat

export default async function handler(req, res) {
  try {
    const now = Date.now();

    // ✅ Cache varsa ve süresi dolmadıysa
    if (cachedVoices && now - cacheTimestamp < CACHE_DURATION) {
      return res.status(200).json({
        source: "cache",
        voices: cachedVoices
      });
    }

    // 🔁 Cache yoksa ElevenLabs'a git
    const response = await fetch("https://api.elevenlabs.io/v1/voices", {
      headers: {
        "xi-api-key": process.env.ElevenLabsAPI
      }
    });

    if (!response.ok) {
      throw new Error("ElevenLabs API error");
    }

    const data = await response.json();
    const voices = data.voices || [];

    // 💾 Cache'e yaz
    cachedVoices = voices;
    cacheTimestamp = now;

    res.status(200).json({
      source: "live",
      voices
    });

  } catch (error) {
    // 🚑 API patladıysa cache varsa onu dön
    if (cachedVoices) {
      return res.status(200).json({
        source: "cache-fallback",
        voices: cachedVoices
      });
    }

    res.status(500).json({
      error: "Failed to fetch voices"
    });
  }
}
