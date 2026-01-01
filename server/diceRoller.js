export class DiceRoller {
  /**
   * Roll dice using standard notation (e.g., "2d6", "1d20+5", "3d8-2")
   * @param {string} notation - Dice notation string
   * @returns {object} Result with total, rolls, and modifier
   */
  roll(notation) {
    // Parse notation like "2d6+3" or "1d20-1" or "3d8"
    const regex = /^(\d+)d(\d+)([+-]\d+)?$/i;
    const match = notation.toLowerCase().trim().match(regex);
    
    if (!match) {
      throw new Error('Invalid dice notation. Use format like "2d6" or "1d20+5"');
    }
    
    const numDice = parseInt(match[1], 10);
    const sides = parseInt(match[2], 10);
    const modifier = match[3] ? parseInt(match[3], 10) : 0;
    
    if (numDice < 1 || numDice > 100) {
      throw new Error('Number of dice must be between 1 and 100');
    }
    
    if (sides < 2 || sides > 1000) {
      throw new Error('Dice sides must be between 2 and 1000');
    }
    
    const rolls = [];
    for (let i = 0; i < numDice; i++) {
      rolls.push(Math.floor(Math.random() * sides) + 1);
    }
    
    const sum = rolls.reduce((a, b) => a + b, 0);
    const total = sum + modifier;
    
    return {
      notation,
      numDice,
      sides,
      modifier,
      rolls,
      sum,
      total
    };
  }
  
  /**
   * Roll with advantage (roll twice, take higher)
   */
  rollAdvantage(notation) {
    const roll1 = this.roll(notation);
    const roll2 = this.roll(notation);
    
    return {
      type: 'advantage',
      roll1,
      roll2,
      result: roll1.total >= roll2.total ? roll1 : roll2
    };
  }
  
  /**
   * Roll with disadvantage (roll twice, take lower)
   */
  rollDisadvantage(notation) {
    const roll1 = this.roll(notation);
    const roll2 = this.roll(notation);
    
    return {
      type: 'disadvantage',
      roll1,
      roll2,
      result: roll1.total <= roll2.total ? roll1 : roll2
    };
  }
}
