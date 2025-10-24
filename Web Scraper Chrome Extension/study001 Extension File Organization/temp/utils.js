// Utility functions for the Chrome extension

/**
 * Generates a random color in hex format
 * @returns {string} A random hex color (e.g., "#FF5733")
 */
function generateRandomColor() {
  // Generate random RGB values
  const r = Math.floor(Math.random() * 256);
  const g = Math.floor(Math.random() * 256);
  const b = Math.floor(Math.random() * 256);
  
  // Return as hex color
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

// Export the function for use in other scripts
export { generateRandomColor };
