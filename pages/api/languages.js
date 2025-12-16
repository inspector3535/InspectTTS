export default function handler(req, res) {
  res.status(200).json({
    languages: [
      { id: "en", name: "English" },
      { id: "tr", name: "Turkish" },
      { id: "de", name: "German" },
      { id: "fr", name: "French" },
      { id: "es", name: "Spanish" }
    ]
  });
}
