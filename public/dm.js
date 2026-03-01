// DM Console JavaScript
const socket = io();

let currentSessionId = null;
let recognition = null;
let isRecording = false;

// Initialize speech recognition
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-US';
  
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    sendNarration(transcript);
  };
  
  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    updateVoiceButton(false);
  };
  
  recognition.onend = () => {
    updateVoiceButton(false);
  };
}

// Screen management
function showScreen(screenId) {
  document.querySelectorAll('.screen').forEach(screen => {
    screen.classList.remove('active');
  });
  document.getElementById(screenId).classList.add('active');
}

// Create session
document.getElementById('create-session-btn').addEventListener('click', async () => {
  try {
    const response = await fetch('/api/session/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    
    const data = await response.json();
    currentSessionId = data.sessionId;
    
    // Display QR code and session info
    document.getElementById('qr-code').src = data.qrCode;
    document.getElementById('session-id').textContent = data.sessionId;
    document.getElementById('join-url').value = data.joinUrl;
    
    // Connect to session as DM
    socket.emit('dm:join', { sessionId: currentSessionId });
    
    showScreen('qr-screen');
  } catch (error) {
    console.error('Error creating session:', error);
    alert('Failed to create session');
  }
});

// Copy URL
document.getElementById('copy-url-btn').addEventListener('click', () => {
  const urlInput = document.getElementById('join-url');
  urlInput.select();
  document.execCommand('copy');
  
  const btn = document.getElementById('copy-url-btn');
  const originalText = btn.textContent;
  btn.textContent = 'Copied!';
  setTimeout(() => {
    btn.textContent = originalText;
  }, 2000);
});

// Start session
document.getElementById('start-session-btn').addEventListener('click', () => {
  socket.emit('session:start', { sessionId: currentSessionId });
  showScreen('campaign-screen');
  
  // Add welcome message to log
  addLogEntry({
    speaker: 'System',
    text: 'Campaign started! Welcome, adventurers!',
    type: 'system'
  });
});

// Voice narration button
const voiceBtn = document.getElementById('dm-voice-btn');
if (voiceBtn && recognition) {
  voiceBtn.addEventListener('mousedown', startRecording);
  voiceBtn.addEventListener('mouseup', stopRecording);
  voiceBtn.addEventListener('touchstart', (e) => {
    e.preventDefault();
    startRecording();
  });
  voiceBtn.addEventListener('touchend', (e) => {
    e.preventDefault();
    stopRecording();
  });
}

function startRecording() {
  if (!recognition || isRecording) return;
  
  isRecording = true;
  updateVoiceButton(true);
  
  try {
    recognition.start();
  } catch (error) {
    console.error('Failed to start recording:', error);
    updateVoiceButton(false);
  }
}

function stopRecording() {
  if (!recognition || !isRecording) return;
  
  isRecording = false;
  
  try {
    recognition.stop();
  } catch (error) {
    console.error('Failed to stop recording:', error);
  }
  
  updateVoiceButton(false);
}

function updateVoiceButton(recording) {
  isRecording = recording;
  const btn = document.getElementById('dm-voice-btn');
  const text = btn.querySelector('.voice-text');
  
  if (recording) {
    btn.classList.add('recording');
    text.textContent = 'Listening...';
  } else {
    btn.classList.remove('recording');
    text.textContent = 'Hold to Narrate';
  }
}

// Text narration
document.getElementById('send-narration-btn').addEventListener('click', () => {
  const input = document.getElementById('dm-text-input');
  const text = input.value.trim();
  
  if (text) {
    sendNarration(text);
    input.value = '';
  }
});

function sendNarration(text) {
  socket.emit('dm:narrate', {
    sessionId: currentSessionId,
    text
  });
  
  addLogEntry({
    speaker: 'DM',
    text,
    type: 'dm'
  });
  
  // Speak the narration
  speakText(text);
}

// Text-to-speech
function speakText(text) {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;
    speechSynthesis.speak(utterance);
  }
}

// Dice rolling
function rollDice(notation) {
  socket.emit('dice:roll', {
    sessionId: currentSessionId,
    diceNotation: notation,
    playerName: 'DM'
  });
}

// Socket event handlers
socket.on('dm:joined', (data) => {
  console.log('DM joined session:', data);
  updatePlayersList(data.players);
});

socket.on('player:joined', (data) => {
  updatePlayersList(data.players);
  document.getElementById('player-count').textContent = data.players.length;
  
  addLogEntry({
    speaker: 'System',
    text: `${data.player.name} joined the party!`,
    type: 'system'
  });
});

socket.on('player:left', (data) => {
  updatePlayersList(data.players);
  document.getElementById('player-count').textContent = data.players.length;
  
  addLogEntry({
    speaker: 'System',
    text: `${data.playerName} left the party.`,
    type: 'system'
  });
});

socket.on('player:spoke', (data) => {
  addLogEntry({
    speaker: data.playerName,
    text: data.text,
    type: 'player'
  });
});

socket.on('dice:result', (data) => {
  const resultText = `${data.playerName} rolled ${data.notation}: ${data.result.total}`;
  const details = data.result.rolls ? ` (${data.result.rolls.join(', ')})` : '';
  
  addLogEntry({
    speaker: 'Dice',
    text: resultText + details,
    type: 'dice'
  });
});

socket.on('dm:narration', (data) => {
  // AI-generated narration will appear here
  if (data.text && !data.text.startsWith('DM:')) {
    addLogEntry({
      speaker: 'DM (AI)',
      text: data.text,
      type: 'dm'
    });
    speakText(data.text);
  }
});

socket.on('error', (data) => {
  console.error('Socket error:', data);
  alert(data.message);
});

// Update players list
function updatePlayersList(players) {
  const list = document.getElementById('players-list');
  
  if (players.length === 0) {
    list.innerHTML = '<p style="color: #888;">No players yet</p>';
    return;
  }
  
  list.innerHTML = players.map(player => `
    <div class="player-item">
      <strong>${player.name}</strong>
      <div style="font-size: 0.9rem; color: #d4a574;">
        HP: ${player.hp} | AC: ${player.ac} | Level: ${player.level}
      </div>
    </div>
  `).join('');
}

// Add log entry
function addLogEntry(entry) {
  const log = document.getElementById('campaign-log');
  const div = document.createElement('div');
  div.className = `log-entry ${entry.type}-message`;
  
  const time = new Date().toLocaleTimeString();
  
  div.innerHTML = `
    <div class="log-speaker">${entry.speaker}</div>
    <div class="log-text">${entry.text}</div>
    <div class="log-timestamp">${time}</div>
  `;
  
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

// Allow Enter key in textarea with Shift
document.getElementById('dm-text-input').addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    document.getElementById('send-narration-btn').click();
  }
});
