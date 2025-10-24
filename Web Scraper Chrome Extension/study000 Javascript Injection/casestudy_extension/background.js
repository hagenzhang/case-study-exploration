chrome.runtime.onMessage.addListener(async (msg, sender) => {
  if (msg.type === "START_SCRAPE") {
    const { tabId } = msg;

    // Step 1: extract body text from tab
    const [{ result: bodyText }] = await chrome.scripting.executeScript({
      target: { tabId },
      func: () => document.body.innerText.trim(),
    });

    const urlData = await chrome.tabs.get(tabId);

    // Step 2: send to backend for scraper generation
    const res = await fetch("http://localhost:8000/generate-scraper", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: bodyText, url: urlData.url }),
    });

    const { code } = await res.json();
    console.log("Generated scraper code:", code);

    // Step 3: open sandbox
    const sandboxUrl = chrome.runtime.getURL("sandbox.html");
    const sandboxTab = await chrome.tabs.create({ url: sandboxUrl, active: false });


    // Step 4: run scraper code in sandbox
    // Wait for the sandbox tab to finish loading
    chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
      if (tabId === sandboxTab.id && info.status === "complete") {
        chrome.tabs.onUpdated.removeListener(listener);

        // Post the code and bodyText to sandbox.html
        chrome.scripting.executeScript({
          target: { tabId: sandboxTab.id },
          func: (code, text) => {
            window.postMessage({ code, text }, "*");
          },
          args: [code, bodyText],
        });
      }
    });

    // Step 5: receive scraper result
    if (msg.type === "SCRAPER_RESULT") {
      console.log("Received scraper result:", msg.result || msg.error);

      chrome.runtime.sendMessage({
        type: "SCRAPE_DONE",
        result: msg.result,
        error: msg.error,
      });

      await chrome.storage.local.set({ lastResult: msg.result || msg.error });
    }
  }
});
