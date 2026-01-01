import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import QRCode from 'qrcode';
import { v4 as uuidv4 } from 'uuid';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { SessionManager } from './sessionManager.js';
import { DiceRoller } from './diceRoller.js';
import { CampaignMemory } from './campaignMemory.js';
import { AIService } from './aiService.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3000;
const sessionManager = new SessionManager();
const diceRoller = new DiceRoller();
const campaignMemory = new CampaignMemory();
const aiService = new AIService();

// Middleware
app.use(express.json());
app.use(express.static(join(__dirname, '../public')));

// Routes
app.get('/', (req, res) => {
  res.sendFile(join(__dirname, '../public/index.html'));
});

// Create new session (DM only)
app.post('/api/session/create', async (req, res) => {
  try {
    const sessionId = uuidv4();
    const session = sessionManager.createSession(sessionId);
    
    // Generate QR code for session
    const joinUrl = `${req.protocol}://${req.get('host')}/join/${sessionId}`;
    const qrCode = await QRCode.toDataURL(joinUrl);
    
    res.json({
      sessionId,
      joinUrl,
      qrCode
    });
  } catch (error) {
    console.error('Error creating session:', error);
    res.status(500).json({ error: 'Failed to create session' });
  }
});

// Join session page
app.get('/join/:sessionId', (req, res) => {
  res.sendFile(join(__dirname, '../public/player.html'));
});

// Get session info
app.get('/api/session/:sessionId', (req, res) => {
  const session = sessionManager.getSession(req.params.sessionId);
  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }
  res.json({
    sessionId: session.id,
    playerCount: session.players.length,
    isActive: session.isActive
  });
});

// WebSocket connection handling
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  let currentSession = null;
  let playerName = null;
  
  // DM creates/joins session
  socket.on('dm:join', ({ sessionId }) => {
    const session = sessionManager.getSession(sessionId);
    if (!session) {
      socket.emit('error', { message: 'Session not found' });
      return;
    }
    
    socket.join(`session:${sessionId}`);
    session.dmSocketId = socket.id;
    currentSession = sessionId;
    
    socket.emit('dm:joined', {
      sessionId,
      players: session.players,
      campaignState: campaignMemory.getCampaignState(sessionId)
    });
  });
  
  // Player joins session
  socket.on('player:join', ({ sessionId, name }) => {
    const session = sessionManager.getSession(sessionId);
    if (!session) {
      socket.emit('error', { message: 'Session not found' });
      return;
    }
    
    if (!session.isActive) {
      socket.emit('error', { message: 'Session is not active' });
      return;
    }
    
    playerName = name || `Player ${session.players.length + 1}`;
    const player = {
      id: socket.id,
      name: playerName,
      hp: 20,
      ac: 15,
      level: 1
    };
    
    session.players.push(player);
    socket.join(`session:${sessionId}`);
    currentSession = sessionId;
    
    // Notify everyone
    io.to(`session:${sessionId}`).emit('player:joined', {
      player,
      players: session.players
    });
    
    socket.emit('player:welcome', {
      sessionId,
      playerInfo: player,
      campaignState: campaignMemory.getCampaignState(sessionId)
    });
  });
  
  // Voice transcription from player
  socket.on('player:voice', async ({ sessionId, text }) => {
    const session = sessionManager.getSession(sessionId);
    if (!session) return;
    
    // Store in campaign memory
    campaignMemory.addMessage(sessionId, {
      speaker: playerName,
      text,
      timestamp: Date.now()
    });
    
    // Broadcast to all players
    io.to(`session:${sessionId}`).emit('player:spoke', {
      playerName,
      text
    });
    
    // Get AI response
    try {
      const context = campaignMemory.getCampaignState(sessionId);
      const response = await aiService.getDMResponse(text, context);
      
      // Store DM response
      campaignMemory.addMessage(sessionId, {
        speaker: 'DM',
        text: response,
        timestamp: Date.now()
      });
      
      // Send to all players
      io.to(`session:${sessionId}`).emit('dm:narration', {
        text: response
      });
    } catch (error) {
      console.error('AI response error:', error);
      socket.emit('error', { message: 'Failed to get DM response' });
    }
  });
  
  // Dice roll request
  socket.on('dice:roll', ({ sessionId, diceNotation, playerName: roller }) => {
    const session = sessionManager.getSession(sessionId);
    if (!session) return;
    
    try {
      const result = diceRoller.roll(diceNotation);
      
      // Store in campaign memory
      campaignMemory.addMessage(sessionId, {
        speaker: 'System',
        text: `${roller || playerName} rolled ${diceNotation}: ${result.total}`,
        type: 'dice',
        details: result,
        timestamp: Date.now()
      });
      
      // Broadcast to all
      io.to(`session:${sessionId}`).emit('dice:result', {
        playerName: roller || playerName,
        notation: diceNotation,
        result
      });
    } catch (error) {
      socket.emit('error', { message: 'Invalid dice notation' });
    }
  });
  
  // DM direct narration
  socket.on('dm:narrate', ({ sessionId, text }) => {
    const session = sessionManager.getSession(sessionId);
    if (!session || session.dmSocketId !== socket.id) return;
    
    campaignMemory.addMessage(sessionId, {
      speaker: 'DM',
      text,
      timestamp: Date.now()
    });
    
    io.to(`session:${sessionId}`).emit('dm:narration', { text });
  });
  
  // Start session
  socket.on('session:start', ({ sessionId }) => {
    const session = sessionManager.getSession(sessionId);
    if (!session || session.dmSocketId !== socket.id) return;
    
    session.isActive = true;
    io.to(`session:${sessionId}`).emit('session:started');
  });
  
  // Disconnect handling
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
    
    if (currentSession) {
      const session = sessionManager.getSession(currentSession);
      if (session) {
        // Remove player
        const playerIndex = session.players.findIndex(p => p.id === socket.id);
        if (playerIndex !== -1) {
          const player = session.players.splice(playerIndex, 1)[0];
          io.to(`session:${currentSession}`).emit('player:left', {
            playerName: player.name,
            players: session.players
          });
        }
        
        // If DM disconnects, pause session
        if (session.dmSocketId === socket.id) {
          session.isActive = false;
          io.to(`session:${currentSession}`).emit('session:paused', {
            message: 'DM disconnected'
          });
        }
      }
    }
  });
});

httpServer.listen(PORT, () => {
  console.log(`AI Dungeon Master server running on port ${PORT}`);
  console.log(`Visit http://localhost:${PORT} to start`);
});
