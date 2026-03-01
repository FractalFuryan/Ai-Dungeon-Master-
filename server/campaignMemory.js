export class CampaignMemory {
  constructor() {
    // In-memory storage - could be extended to use a database
    this.campaigns = new Map();
  }
  
  /**
   * Initialize campaign memory for a session
   */
  initCampaign(sessionId) {
    if (!this.campaigns.has(sessionId)) {
      this.campaigns.set(sessionId, {
        sessionId,
        messages: [],
        npcs: [],
        locations: [],
        quests: [],
        inventory: [],
        createdAt: Date.now(),
        updatedAt: Date.now()
      });
    }
    return this.campaigns.get(sessionId);
  }
  
  /**
   * Add a message to campaign history
   */
  addMessage(sessionId, message) {
    const campaign = this.initCampaign(sessionId);
    campaign.messages.push(message);
    campaign.updatedAt = Date.now();
    
    // Keep only last 100 messages to prevent memory issues
    if (campaign.messages.length > 100) {
      campaign.messages = campaign.messages.slice(-100);
    }
    
    return message;
  }
  
  /**
   * Get campaign state for AI context
   */
  getCampaignState(sessionId) {
    const campaign = this.campaigns.get(sessionId);
    if (!campaign) {
      return {
        messages: [],
        summary: 'New campaign - no history yet.'
      };
    }
    
    // Return recent messages for context
    const recentMessages = campaign.messages.slice(-20);
    
    return {
      messages: recentMessages,
      npcs: campaign.npcs,
      locations: campaign.locations,
      quests: campaign.quests,
      summary: this.generateSummary(campaign)
    };
  }
  
  /**
   * Generate a summary of the campaign
   */
  generateSummary(campaign) {
    if (campaign.messages.length === 0) {
      return 'New campaign - no history yet.';
    }
    
    const messageCount = campaign.messages.length;
    const diceRolls = campaign.messages.filter(m => m.type === 'dice').length;
    
    return `Campaign with ${messageCount} events (${diceRolls} dice rolls).`;
  }
  
  /**
   * Add NPC to campaign
   */
  addNPC(sessionId, npc) {
    const campaign = this.initCampaign(sessionId);
    campaign.npcs.push({
      ...npc,
      addedAt: Date.now()
    });
    campaign.updatedAt = Date.now();
  }
  
  /**
   * Add location to campaign
   */
  addLocation(sessionId, location) {
    const campaign = this.initCampaign(sessionId);
    campaign.locations.push({
      ...location,
      addedAt: Date.now()
    });
    campaign.updatedAt = Date.now();
  }
  
  /**
   * Add or update quest
   */
  addQuest(sessionId, quest) {
    const campaign = this.initCampaign(sessionId);
    campaign.quests.push({
      ...quest,
      addedAt: Date.now()
    });
    campaign.updatedAt = Date.now();
  }
  
  /**
   * Clear campaign data
   */
  clearCampaign(sessionId) {
    this.campaigns.delete(sessionId);
  }
  
  /**
   * Get all campaigns (for debugging/admin)
   */
  getAllCampaigns() {
    return Array.from(this.campaigns.values());
  }
}
