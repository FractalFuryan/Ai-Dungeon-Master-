export class SessionManager {
  constructor() {
    this.sessions = new Map();
  }
  
  createSession(sessionId) {
    const session = {
      id: sessionId,
      players: [],
      dmSocketId: null,
      isActive: false,
      createdAt: Date.now()
    };
    
    this.sessions.set(sessionId, session);
    return session;
  }
  
  getSession(sessionId) {
    return this.sessions.get(sessionId);
  }
  
  deleteSession(sessionId) {
    return this.sessions.delete(sessionId);
  }
  
  getAllSessions() {
    return Array.from(this.sessions.values());
  }
}
