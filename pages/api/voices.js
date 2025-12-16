let cachedVoices = null
let cachedAt = 0

const CACHE_TTL = 6 * 60 * 60 * 1000 // 6 saat

const FALLBACK_VOICES = [
  {
    voice_id: "fallback-1",
    name: "Default Voice",
    description: "Fallback voice used when ElevenLabs is unavailable",
    labels: { accent: "neutral", gender: "neutral" }
  }
]

export default async function handler(req, res) {
  const now = Date.now()

  // 1️⃣ CACHE
  if (cachedVoices && (now - cachedAt) < CACHE_TTL) {
    return res.status(200).json({
      source: "cache",
      voices: cachedVoices
    })
  }

  // 2️⃣ LIVE
  try {
    const response = await fetch("https://api.elevenlabs.io/v1/voices", {
      headers: {
        "xi-api-key": process.env.ElevenLabsAPI
      }
    })

    if (!response.ok) {
      throw new Error(`ElevenLabs error ${response.status}`)
    }

    const data = await response.json()
    const voices = data.voices || []

    cachedVoices = voices
    cachedAt = now

    return res.status(200).json({
      source: "live",
      voices
    })

  } catch (error) {

    // 3️⃣ FALLBACK
    if (cachedVoices) {
      return res.status(200).json({
        source: "cache",
        voices: cachedVoices,
        warning: "Live fetch failed, serving cached data"
      })
    }

    return res.status(200).json({
      source: "fallback",
      voices: FALLBACK_VOICES,
      error: "Live and cache unavailable"
    })
  }
}
