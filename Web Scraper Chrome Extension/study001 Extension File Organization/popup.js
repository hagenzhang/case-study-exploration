document.addEventListener('DOMContentLoaded', function() {
  const generateBtn = document.getElementById('generateBtn');
  const resultText = document.getElementById('resultText');
  const body = document.body;

  // Handle button click
  generateBtn.addEventListener('click', function() {
    // Send message to background script
    chrome.runtime.sendMessage({action: 'generateRandom'}, function(response) {
      if (response && response.success) {
        // Update the text box with the random values
        resultText.value = `Color: ${response.color}\nNumber: ${response.number}`;
        
        // Update the background color
        body.style.backgroundColor = response.color;
      } else {
        // Handle error case
        resultText.value = 'Error generating random values';
        console.error('Error:', response ? response.error : 'No response');
      }
    });
  });

  // Listen for messages from background script (if needed for future enhancements)
  chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'updateValues') {
      resultText.value = `Color: ${request.color}\nNumber: ${request.number}`;
      body.style.backgroundColor = request.color;
    }
  });
});
