export const runtime = "nodejs";

import crypto from "crypto";

const rateLimitMap = new Map();
const ttsCache = new Map();

function isRateLimited(ip, limit = 10, windowMs = 60_000) {
  const now = Date.now();
  const record = rateLimitMap.get(ip) || { count: 0, time: now };

  if (now - record.time > windowMs) {
    rateLimitMap.set(ip, { count: 1, time: now });
    return false;
  }

  record.count++;
  rateLimitMap.set(ip, record);
  return record.count > limit;
}

function makeCacheKey(text, voice, settings = {}) {
  const raw = JSON.stringify({ text, voice, settings });
  return crypto.createHash("sha1").update(raw).digest("hex");
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const ip =
    req.headers["x-forwarded-for"]?.split(",")[0] ||
    req.socket.remoteAddress;

  if (isRateLimited(ip)) {
    return res.status(429).json({ error: "Rate limit exceeded" });
  }

  const { text, voice, voice_settings = {} } = req.body || {};

  if (!text) {
    return res.status(400).json({ error: "Text parameter missing." });
  }

  if (!voice) {
    return res.status(400).json({ error: "Voice parameter missing." });
  }

  const cacheKey = makeCacheKey(text, voice, voice_settings);
  const cached = ttsCache.get(cacheKey);

  if (cached && cached.expires > Date.now()) {
    res.setHeader("Content-Type", "audio/mpeg");
    res.setHeader("X-Source", "cache");
    return res.send(cached.audio);
  }

  try {
    const elevenRes = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${voice}`,
      {
        method: "POST",
        headers: {
          "xi-api-key": process.env.ELEVENLABS_API_KEY,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          text,
          model_id: "eleven_multilingual_v2",
          voice_settings
        })
      }
    );

    if (!elevenRes.ok) {
      const t = await elevenRes.text();
      throw new Error(`ElevenLabs ${elevenRes.status}: ${t}`);
    }

    const audioBuffer = Buffer.from(await elevenRes.arrayBuffer());

    ttsCache.set(cacheKey, {
      audio: audioBuffer,
      expires: Date.now() + 1000 * 60 * 60
    });

    res.setHeader("Content-Type", "audio/mpeg");
    res.setHeader("X-Source", "live");
    return res.send(audioBuffer);

  } catch (err) {
    if (cached) {
      res.setHeader("Content-Type", "audio/mpeg");
      res.setHeader("X-Source", "fallback-cache");
      return res.send(cached.audio);
    }

    return res.status(502).json({
      error: "TTS service unavailable",
      details: err.message
    });
  }
}
