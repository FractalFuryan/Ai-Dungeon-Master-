# 🎲 AI Dungeon Master

A voice-driven AI Dungeon Master that players join via QR code. Supports multiplayer sessions, server-side dice rolls, campaign memory, and real-time narration over WebSockets. Designed for phones and tablets with push-to-talk voice input and spoken DM responses.

## Features

- 🎤 **Voice Input**: Push-to-talk voice commands for players and DM
- 🔊 **Spoken Narration**: Text-to-speech DM responses
- 📱 **Mobile Optimized**: Designed for phones and tablets
- 🔗 **QR Code Joining**: Players scan QR code to join sessions
- 🎲 **Server-Side Dice Rolls**: Fair dice rolling with multiple dice types
- 💾 **Campaign Memory**: Persistent campaign state and history
- 👥 **Multiplayer Support**: Multiple players in real-time
- ⚡ **Real-Time Communication**: WebSocket-based instant updates
- 🤖 **AI Integration**: Optional OpenAI integration for dynamic narratives

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/FractalFuryan/Ai-Dungeon-Master-.git
cd Ai-Dungeon-Master-

# Install dependencies
npm install

# (Optional) Set up OpenAI API key
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Running the Server

```bash
# Start the server
npm start

# Or use development mode with auto-reload
npm run dev
```

The server will start on `http://localhost:3000`

## How to Play

### For the Dungeon Master (DM)

1. Open `http://localhost:3000` in your browser
2. Click "Create Session"
3. Share the QR code or URL with players
4. Wait for players to join
5. Click "Start Campaign" to begin
6. Use voice input (hold button) or text to narrate the story
7. View player actions and dice rolls in the campaign log

### For Players

1. Scan the QR code shown by the DM (or open the join URL)
2. Enter your character name
3. Click "Join Campaign"
4. Use voice input (hold button) to speak your actions
5. Use quick dice roll buttons or custom notation (e.g., "2d6+3")
6. Listen to the DM's narration (spoken automatically)

## Game Controls

### Voice Input
- **DM**: Hold the "Hold to Narrate" button to speak
- **Players**: Hold the "Hold to Speak" button to describe actions

### Dice Rolling
Common dice notations:
- `1d20` - Roll one 20-sided die
- `2d6` - Roll two 6-sided dice
- `1d20+5` - Roll d20 and add 5
- `3d8-2` - Roll three 8-sided dice and subtract 2

Available quick-roll buttons: d20, d12, d10, d8, d6, d4

## Technology Stack

- **Backend**: Node.js, Express, Socket.io
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Real-Time**: WebSocket (Socket.io)
- **QR Codes**: qrcode library
- **Voice**: Web Speech API (built into modern browsers)
- **AI**: OpenAI API (optional)

## Browser Compatibility

### Required Features
- WebSocket support
- Web Speech API (for voice input/output)
- Modern ES6+ JavaScript support

### Recommended Browsers
- **Mobile**: Chrome/Safari on iOS, Chrome on Android
- **Desktop**: Chrome, Edge, Safari (latest versions)

**Note**: Voice input works best on Chrome. Safari has limited Web Speech API support.

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Optional: OpenAI API key for AI-powered narration
OPENAI_API_KEY=your_api_key_here

# Optional: Server port (default: 3000)
PORT=3000
```

### Without OpenAI

The system works without OpenAI API by using rule-based responses. Players can still:
- Use voice input for actions
- Receive text-to-speech responses
- Roll dice
- Join via QR code

The DM will get simple contextual responses instead of AI-generated narration.

## Project Structure

```
Ai-Dungeon-Master-/
├── server/
│   ├── index.js           # Main server and WebSocket handlers
│   ├── sessionManager.js  # Session management
│   ├── diceRoller.js      # Dice rolling logic
│   ├── campaignMemory.js  # Campaign state and history
│   └── aiService.js       # AI integration (OpenAI)
├── public/
│   ├── index.html         # DM console interface
│   ├── player.html        # Player interface
│   ├── styles.css         # Responsive styles
│   ├── dm.js              # DM client logic
│   └── player.js          # Player client logic
├── package.json
├── .env.example
└── README.md
```

## API Endpoints

### HTTP Endpoints

- `POST /api/session/create` - Create a new session (returns QR code)
- `GET /api/session/:sessionId` - Get session information
- `GET /join/:sessionId` - Player join page

### WebSocket Events

#### From Client to Server
- `dm:join` - DM joins session
- `player:join` - Player joins session
- `player:voice` - Player voice input
- `dm:narrate` - DM narration
- `dice:roll` - Roll dice
- `session:start` - Start the campaign

#### From Server to Client
- `dm:joined` - DM successfully joined
- `player:welcome` - Player successfully joined
- `player:joined` - New player joined (broadcast)
- `player:left` - Player disconnected (broadcast)
- `player:spoke` - Player action (broadcast)
- `dm:narration` - DM/AI narration (broadcast)
- `dice:result` - Dice roll result (broadcast)
- `session:started` - Campaign started (broadcast)
- `error` - Error message

## Troubleshooting

### Voice Input Not Working
- **Mobile Safari**: Limited support - try Chrome instead
- **HTTPS Required**: Voice API requires HTTPS in production (works on localhost)
- **Microphone Permission**: Grant microphone access when prompted

### QR Code Not Scanning
- Ensure good lighting and camera focus
- Try manually entering the URL instead
- Verify the server is accessible on the network

### Players Can't Connect
- Check firewall settings
- Ensure server is running and accessible
- Verify the correct port is being used
- For remote access, use ngrok or similar tunneling service

### No AI Responses
- Verify `OPENAI_API_KEY` is set in `.env`
- Check API key is valid and has credits
- System falls back to rule-based responses if AI unavailable

## Development

```bash
# Install dependencies
npm install

# Run in development mode (auto-reload)
npm run dev

# Run in production mode
npm start
```

## Future Enhancements

- [ ] Character sheet management
- [ ] Persistent database storage
- [ ] Combat tracker
- [ ] Map/grid integration
- [ ] Custom campaign templates
- [ ] Voice commands for dice rolls
- [ ] Mobile app versions

## License

ISC

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

Created for tabletop RPG enthusiasts who want to blend technology with traditional gaming.