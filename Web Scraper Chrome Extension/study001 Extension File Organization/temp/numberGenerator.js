// NumberGenerator class for generating random numbers

/**
 * A class for generating random numbers with various methods
 */
export class NumberGenerator {
  constructor() {
    this.min = 1;
    this.max = 1000;
  }

  /**
   * Sets the range for random number generation
   * @param {number} min - Minimum value (inclusive)
   * @param {number} max - Maximum value (inclusive)
   */
  setRange(min, max) {
    this.min = min;
    this.max = max;
  }

  /**
   * Generates a random number within the current range
   * @returns {number} A random number between min and max (inclusive)
   */
  generateRandomNumber() {
    return Math.floor(Math.random() * (this.max - this.min + 1)) + this.min;
  }

  /**
   * Generates a random number with a specific range (doesn't change the class range)
   * @param {number} min - Minimum value (inclusive)
   * @param {number} max - Maximum value (inclusive)
   * @returns {number} A random number between min and max (inclusive)
   */
  generateRandomNumberInRange(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  /**
   * Gets the current range
   * @returns {object} Object containing min and max values
   */
  getRange() {
    return { min: this.min, max: this.max };
  }
}
