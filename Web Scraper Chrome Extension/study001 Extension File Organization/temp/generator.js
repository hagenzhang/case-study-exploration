// Generator module for handling random value generation
import { generateRandomColor } from './utils.js';
import { NumberGenerator } from './numberGenerator.js';

// Create a number generator instance
const numberGenerator = new NumberGenerator();

/**
 * Executes the random generation process and sends the response
 * @param {Function} sendResponse - The Chrome extension sendResponse callback
 */
export function execute(sendResponse) {
  try {
    // Generate random color using the utility function
    const randomColor = generateRandomColor();
    
    // Generate random number using the NumberGenerator class
    const randomNumber = numberGenerator.generateRandomNumber();
    
    // Send response back to popup
    sendResponse({
      success: true,
      color: randomColor,
      number: randomNumber
    });
  } catch (error) {
    console.error('Error generating random values:', error);
    sendResponse({
      success: false,
      error: error.message
    });
  }
}
