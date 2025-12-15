import { useState } from "react";

export default function Home() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  async function speak() {
    setLoading(true);

    const response = await fetch(`/api/tts?text=${encodeURIComponent(text)}`);
    const arrayBuffer = await response.arrayBuffer();

    const audioBlob = new Blob([arrayBuffer], { type: "audio/mpeg" });
    const url = URL.createObjectURL(audioBlob);

    const audio = new Audio(url);
    audio.play();

    setLoading(false);
  }

  return (
    <div style={{ padding: "40px", fontFamily: "sans-serif" }}>
      <h1>ElevenLabs TTS Demo</h1>

      <textarea
        rows="5"
        style={{ width: "100%", padding: "10px", fontSize: "16px" }}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Seslendirmek istediğiniz metni yazın..."
      ></textarea>

      <button
        onClick={speak}
        disabled={loading}
        style={{
          marginTop: "20px",
          padding: "10px 20px",
          fontSize: "16px",
          cursor: "pointer"
        }}
      >
        {loading ? "Ses oluşturuluyor..." : "Konuş"}
      </button>
    </div>
  );
}
