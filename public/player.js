// Player JavaScript
const socket = io();

let currentSessionId = null;
let playerName = null;
let recognition = null;
let isRecording = false;

// Get session ID from URL
const pathParts = window.location.pathname.split('/');
if (pathParts[1] === 'join' && pathParts[2]) {
  currentSessionId = pathParts[2];
}

// Initialize speech recognition
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-US';
  
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    sendVoiceMessage(transcript);
    updateVoiceStatus(`You said: "${transcript}"`);
  };
  
  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    updateVoiceButton(false);
    updateVoiceStatus('Error: ' + event.error);
  };
  
  recognition.onend = () => {
    updateVoiceButton(false);
  };
} else {
  // Fallback message if speech recognition not available
  setTimeout(() => {
    const status = document.getElementById('voice-status');
    if (status) {
      status.textContent = 'Voice input not supported on this device. Type your dice rolls instead.';
    }
  }, 1000);
}

// Screen management
function showScreen(screenId) {
  document.querySelectorAll('.screen').forEach(screen => {
    screen.classList.remove('active');
  });
  document.getElementById(screenId).classList.add('active');
}

// Join session
document.getElementById('join-session-btn').addEventListener('click', () => {
  const nameInput = document.getElementById('player-name-input');
  playerName = nameInput.value.trim() || `Player ${Math.floor(Math.random() * 1000)}`;
  
  if (!currentSessionId) {
    alert('Invalid session ID');
    return;
  }
  
  socket.emit('player:join', {
    sessionId: currentSessionId,
    name: playerName
  });
});

// Voice input button
const voiceBtn = document.getElementById('player-voice-btn');
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
  updateVoiceStatus('Listening...');
  
  try {
    recognition.start();
  } catch (error) {
    console.error('Failed to start recording:', error);
    updateVoiceButton(false);
    updateVoiceStatus('Failed to start recording');
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
  updateVoiceStatus('Processing...');
}

function updateVoiceButton(recording) {
  isRecording = recording;
  const btn = document.getElementById('player-voice-btn');
  const text = btn.querySelector('.voice-text');
  
  if (recording) {
    btn.classList.add('recording');
    text.textContent = 'Listening...';
  } else {
    btn.classList.remove('recording');
    text.textContent = 'Hold to Speak';
  }
}

function updateVoiceStatus(message) {
  const status = document.getElementById('voice-status');
  if (status) {
    status.textContent = message;
    
    // Clear status after 5 seconds
    setTimeout(() => {
      if (status.textContent === message) {
        status.textContent = '';
      }
    }, 5000);
  }
}

function sendVoiceMessage(text) {
  socket.emit('player:voice', {
    sessionId: currentSessionId,
    text
  });
}

// Dice rolling functions
function playerRollDice(notation) {
  socket.emit('dice:roll', {
    sessionId: currentSessionId,
    diceNotation: notation,
    playerName
  });
}

function playerRollCustomDice() {
  const input = document.getElementById('custom-dice-input');
  const notation = input.value.trim();
  
  if (notation) {
    playerRollDice(notation);
    input.value = '';
  }
}

// Allow Enter key in custom dice input
document.getElementById('custom-dice-input').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    playerRollCustomDice();
  }
});

// Socket event handlers
socket.on('player:welcome', (data) => {
  console.log('Welcomed to session:', data);
  
  // Update player stats
  document.getElementById('player-hp').textContent = data.playerInfo.hp;
  document.getElementById('player-ac').textContent = data.playerInfo.ac;
  document.getElementById('player-level').textContent = data.playerInfo.level;
  
  showScreen('game-screen');
  
  addNarrationEntry({
    speaker: 'System',
    text: `Welcome, ${playerName}! The adventure begins...`,
    type: 'system'
  });
});

socket.on('player:joined', (data) => {
  updatePartyList(data.players);
  
  addNarrationEntry({
    speaker: 'System',
    text: `${data.player.name} joined the party!`,
    type: 'system'
  });
});

socket.on('player:left', (data) => {
  updatePartyList(data.players);
  
  addNarrationEntry({
    speaker: 'System',
    text: `${data.playerName} left the party.`,
    type: 'system'
  });
});

socket.on('player:spoke', (data) => {
  addNarrationEntry({
    speaker: data.playerName,
    text: data.text,
    type: 'player'
  });
});

socket.on('dm:narration', (data) => {
  addNarrationEntry({
    speaker: 'Dungeon Master',
    text: data.text,
    type: 'dm'
  });
  
  // Speak the DM's narration
  speakText(data.text);
});

socket.on('dice:result', (data) => {
  const resultText = `${data.playerName} rolled ${data.notation}: ${data.result.total}`;
  const details = data.result.rolls ? ` (${data.result.rolls.join(', ')})` : '';
  
  addNarrationEntry({
    speaker: 'Dice',
    text: resultText + details,
    type: 'dice'
  });
});

socket.on('session:started', () => {
  addNarrationEntry({
    speaker: 'System',
    text: 'The Dungeon Master has started the campaign!',
    type: 'system'
  });
});

socket.on('session:paused', (data) => {
  addNarrationEntry({
    speaker: 'System',
    text: data.message || 'Session paused',
    type: 'system'
  });
});

socket.on('error', (data) => {
  console.error('Socket error:', data);
  alert(data.message);
});

// Update party list
function updatePartyList(players) {
  const list = document.getElementById('party-list');
  
  if (!players || players.length === 0) {
    list.innerHTML = '<p style="color: #888;">No other players</p>';
    return;
  }
  
  list.innerHTML = players
    .filter(p => p.name !== playerName)
    .map(player => `
      <div class="party-member">
        <span>${player.name}</span>
        <span style="font-size: 0.9rem; color: #d4a574;">Level ${player.level}</span>
      </div>
    `).join('');
  
  if (list.innerHTML === '') {
    list.innerHTML = '<p style="color: #888;">No other players</p>';
  }
}

// Add narration entry
function addNarrationEntry(entry) {
  const log = document.getElementById('narration-log');
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

// Text-to-speech
function speakText(text) {
  if ('speechSynthesis' in window) {
    // Cancel any ongoing speech
    speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;
    
    // Try to use a more dramatic voice if available
    const voices = speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => 
      v.name.includes('Daniel') || 
      v.name.includes('Male') ||
      v.lang.startsWith('en')
    );
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }
    
    speechSynthesis.speak(utterance);
  }
}

// Load voices when available
if ('speechSynthesis' in window) {
  speechSynthesis.onvoiceschanged = () => {
    speechSynthesis.getVoices();
  };
}
