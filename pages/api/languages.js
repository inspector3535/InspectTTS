let cachedLanguages = null
let cachedAt = 0

const CACHE_TTL = 6 * 60 * 60 * 1000 // 6 saat

const FALLBACK_LANGUAGES = [
  {
    code: "en",
    name: "English",
    description: "Default fallback language"
  }
]

export default async function handler(req, res) {
  const now = Date.now()

  // 1️⃣ CACHE
  if (cachedLanguages && (now - cachedAt) < CACHE_TTL) {
    return res.status(200).json({
      source: "cache",
      languages: cachedLanguages
    })
  }

  // 2️⃣ LIVE
  try {
    const response = await fetch("https://api.elevenlabs.io/v1/languages", {
      headers: {
        "xi-api-key": process.env.ElevenLabsAPI
      }
    })

    if (!response.ok) {
      throw new Error(`ElevenLabs error ${response.status}`)
    }

    const data = await response.json()
    const languages = data.languages || data || []

    cachedLanguages = languages
    cachedAt = now

    return res.status(200).json({
      source: "live",
      languages
    })

  } catch (error) {

    // 3️⃣ FALLBACK
    if (cachedLanguages) {
      return res.status(200).json({
        source: "cache",
        languages: cachedLanguages,
        warning: "Live fetch failed, serving cached data"
      })
    }

    return res.status(200).json({
      source: "fallback",
      languages: FALLBACK_LANGUAGES,
      error: "Live and cache unavailable"
    })
  }
}
