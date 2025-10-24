// Background script for Chrome extension
import { execute } from './temp/generator.js';

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'generateRandom') {
    // Delegate to the generator module
    execute(sendResponse);
  }
  
  // Return true to indicate we will send a response asynchronously
  return true;
});
