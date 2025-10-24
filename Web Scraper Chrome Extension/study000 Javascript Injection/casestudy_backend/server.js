import express from "express";
import fetch from "node-fetch";
import 'dotenv/config';

import cors from "cors";




const app = express();
app.use(express.json());
app.use(cors());

app.post("/generate-scraper", async (req, res) => {
  const { text, url } = req.body;

  console.log("Received request to generate scraper for URL:", url);

  // Build prompt for the LLM
  const prompt = `
You are a JavaScript expert. Generate a function named extractData(text) 
that parses the given page text and returns an array of JSON objects for events.
Each event should include: name, date, location. 
Do not include any other explanation or code outside the function.

Only use the following text from the page:
---
${text.slice(0, 8000)}
---

Return the function as valid JavaScript code. Example:

function extractData(text) {
  return [
    { name: "Concert", date: "2025-10-25", location: "Dallas" }
  ];
}
`;

  try {
    // Call DeepSeek API
    const response = await fetch(`${process.env.DEEPSEEK_URL}`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.DEEPSEEK_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: `${process.env.DEEPSEEK_MODEL}`,
        messages: [
          { role: "system", content: "You are a JavaScript data extraction assistant." },
          { role: "user", content: prompt },
        ],
        temperature: 0.2,
      }),
    });

    const data = await response.json();
    console.log("Full DeepSeek response:", JSON.stringify(data, null, 2));

    // Check for errors
    if (data.error) {
      console.error("DeepSeek API error:", data.error);
      return res.status(500).json({ error: data.error });
    }

    const code = data.choices?.[0]?.message?.content?.trim() || "";

    if (!code) {
      console.error("No code returned from DeepSeek.");
      return res.status(500).json({ error: "No code returned from DeepSeek." });
    }

    console.log("Scraper code generated successfully.");
    res.json({ code });

  } catch (err) {
    console.error("Error generating scraper:", err);
    res.status(500).json({ error: err.message });
  }
});

app.listen(8000, () => console.log("Backend listening on port 8000"));
