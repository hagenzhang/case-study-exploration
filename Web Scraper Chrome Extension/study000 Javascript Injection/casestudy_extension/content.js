(async () => {
  // Extract readable text only
  const bodyText = document.body.innerText.trim();

  chrome.runtime.sendMessage({
    type: "PAGE_TEXT",
    text: bodyText,
    url: window.location.href
  });
})();
