const output = document.getElementById("output");
const scrapeBtn = document.getElementById("scrapeBtn");

scrapeBtn.addEventListener("click", async () => {
  output.textContent = "Scraping in progress...";

  // 1️⃣ Get active tab
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) {
    output.textContent = "No active tab found.";
    return;
  }

  // 2️⃣ Extract page body text
  const [{ result: bodyText }] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => document.body.innerText.trim()
  });

  console.log("Extracted body text, sending to server...");

  // 3️⃣ Request LLM-generated scraper code from backend
  const res = await fetch("http://localhost:8000/generate-scraper", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: bodyText, url: tab.url })
  });

  const { code } = await res.json();
  if (!code) {
    console.log("No code returned from server");
    output.textContent = "Error: no scraper code returned.";
    return;
  }

  console.log("Response from server received successfully");

  // 4️⃣ Create a Web Worker to run LLM-generated code safely
  const blob = new Blob([
    `${code}
    onmessage = e => {
      try {
        const result = extractData(e.data);
        postMessage({ result });
      } catch(err) {
        postMessage({ error: err.message });
      }
    };`
  ], { type: "application/javascript" });

  const worker = new Worker(URL.createObjectURL(blob));

  worker.onmessage = (e) => {
    const { result, error } = e.data;
    output.textContent = error ? "Error: " + error : JSON.stringify(result, null, 2);
    worker.terminate(); // clean up
  };

  // 5️⃣ Send page body text to the worker
  worker.postMessage(bodyText);
});
