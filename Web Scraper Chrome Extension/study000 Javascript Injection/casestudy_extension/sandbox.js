window.addEventListener("message", (event) => {
  const { code, text } = event.data;

  if (!code || !text) return;

  try {
    // Wrap code and extractData function
    const fn = new Function(`${code}; return extractData;`);
    const extractData = fn();

    const result = extractData(text);

    // Send result back to popup
    window.parent.postMessage({ result }, "*");
  } catch (err) {
    window.parent.postMessage({ error: err.message }, "*");
  }
});
