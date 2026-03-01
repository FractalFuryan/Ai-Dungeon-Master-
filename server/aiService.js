import OpenAI from 'openai';

export class AIService {
  constructor() {
    this.openai = null;
    
    // Initialize OpenAI if API key is available
    if (process.env.OPENAI_API_KEY) {
      this.openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY
      });
    }
  }
  
  /**
   * Get DM response based on player input and campaign context
   */
  async getDMResponse(playerInput, campaignContext) {
    // If no OpenAI key, return a simple rule-based response
    if (!this.openai) {
      return this.getRuleBasedResponse(playerInput, campaignContext);
    }
    
    try {
      const messages = this.buildContextMessages(playerInput, campaignContext);
      
      const completion = await this.openai.chat.completions.create({
        model: 'gpt-4-turbo-preview',
        messages,
        max_tokens: 300,
        temperature: 0.9
      });
      
      return completion.choices[0].message.content.trim();
    } catch (error) {
      console.error('OpenAI API error:', error);
      // Fallback to rule-based response
      return this.getRuleBasedResponse(playerInput, campaignContext);
    }
  }
  
  /**
   * Build context messages for OpenAI
   */
  buildContextMessages(playerInput, campaignContext) {
    const messages = [
      {
        role: 'system',
        content: `You are an expert Dungeon Master for a fantasy tabletop RPG. 
You create immersive, engaging narratives that respond to player actions.
Keep responses concise (2-4 sentences) but vivid and atmospheric.
Describe outcomes of actions, introduce challenges, and advance the story.
If players attempt risky actions, suggest appropriate dice rolls.`
      }
    ];
    
    // Add recent campaign history for context
    if (campaignContext.messages && campaignContext.messages.length > 0) {
      const history = campaignContext.messages
        .slice(-10)
        .map(m => `${m.speaker}: ${m.text}`)
        .join('\n');
      
      messages.push({
        role: 'system',
        content: `Recent campaign events:\n${history}`
      });
    }
    
    // Add current player input
    messages.push({
      role: 'user',
      content: playerInput
    });
    
    return messages;
  }
  
  /**
   * Simple rule-based response when AI is not available
   */
  getRuleBasedResponse(playerInput, campaignContext) {
    const input = playerInput.toLowerCase();
    
    // Check for common actions
    if (input.includes('attack') || input.includes('fight')) {
      return "You engage in combat! Roll for initiative (1d20). What's your attack strategy?";
    }
    
    if (input.includes('search') || input.includes('look')) {
      return "You carefully examine your surroundings. The dimly lit chamber reveals ancient markings on the walls and a faint draft coming from the north.";
    }
    
    if (input.includes('door') || input.includes('open')) {
      return "The door creaks ominously as you approach. Do you want to check for traps first, or push it open?";
    }
    
    if (input.includes('talk') || input.includes('speak')) {
      return "The mysterious figure regards you cautiously, waiting to hear what you have to say.";
    }
    
    if (input.includes('heal') || input.includes('rest')) {
      return "You take a moment to tend to your wounds. Roll a medicine check (1d20) if you want to use healing supplies.";
    }
    
    // Default response
    return `Interesting choice. As you ${playerInput}, you notice the atmosphere growing tense. What do you do next?`;
  }
  
  /**
   * Generate campaign introduction
   */
  async generateIntroduction(setting = 'fantasy') {
    if (!this.openai) {
      return this.getDefaultIntroduction(setting);
    }
    
    try {
      const completion = await this.openai.chat.completions.create({
        model: 'gpt-4-turbo-preview',
        messages: [
          {
            role: 'system',
            content: 'You are a Dungeon Master starting a new campaign. Create a brief, exciting introduction.'
          },
          {
            role: 'user',
            content: `Create a campaign introduction for a ${setting} setting (3-4 sentences).`
          }
        ],
        max_tokens: 200,
        temperature: 0.9
      });
      
      return completion.choices[0].message.content.trim();
    } catch (error) {
      console.error('OpenAI API error:', error);
      return this.getDefaultIntroduction(setting);
    }
  }
  
  /**
   * Default introduction when AI is not available
   */
  getDefaultIntroduction(setting) {
    return `Welcome, brave adventurers! You find yourselves at the edge of a mysterious realm, where danger and glory await in equal measure. The air crackles with magic and possibility. Your journey begins now...`;
  }
}
