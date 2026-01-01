// === Codespaces-safe dynamic URLs ===
const isHttps = window.location.protocol === "https:";
const wsProto = isHttps ? "wss" : "ws";
const API_BASE = `${window.location.protocol}//${window.location.host}`;

let sessionId = null;
let ws = null;
let myName = null;
let isHost = false;

// Auto-join if QR-scanned URL has session_id
const params = new URLSearchParams(window.location.search);
if (params.has("session_id")) {
    sessionId = params.get("session_id");
    document.getElementById("status").innerText = `Joined session: ${sessionId}`;
    connectWebSocket();
}

document.getElementById('create-session').addEventListener('click', async () => {
    const res = await fetch(`${API_BASE}/session/create`, { method: 'POST' });
    const data = await res.json();
    sessionId = data.session_id;
    isHost = true;
    
    const joinUrl = `${window.location.origin}?session_id=${sessionId}`;
    document.getElementById("qr-code").innerHTML = ""; // clear old
    new QRCode(document.getElementById('qr-code'), {
        text: joinUrl,
        width: 256,
        height: 256
    });
    
    // Show host controls
    document.getElementById("persona-controls").style.display = "block";
    document.getElementById("pass-turn").style.display = "inline-block";
    
    document.getElementById("status").innerText = `Session created: ${sessionId} — Share QR!`;
    connectWebSocket();
    
    // Persona selection
    document.getElementById("persona-select").addEventListener("change", async (e) => {
        const persona = e.target.value;
        await fetch(`${API_BASE}/session/set_persona`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({session_id: sessionId, persona})
        });
    });
    
    // Pass turn button
    document.getElementById("pass-turn").addEventListener("click", async () => {
        await fetch(`${API_BASE}/session/next_turn`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({session_id: sessionId})
        });
    });
    
    // Show campaign controls
    document.getElementById("campaign-controls").style.display = "block";
    
    // Save campaign
    document.getElementById("save-campaign").addEventListener("click", async () => {
        const name = document.getElementById("campaign-name").value.trim() || "My Adventure";
        const res = await fetch(`${API_BASE}/campaign/save`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({session_id: sessionId, campaign_name: name})
        });
        const data = await res.json();
        if (data.success) {
            addLog(`📜 Campaign "${name}" saved!`, "system");
            document.getElementById("campaign-name").value = "";
        } else {
            addLog(`Error saving: ${data.error}`, "system");
        }
    });
    
    // Load campaign
    document.getElementById("load-campaign").addEventListener("click", async () => {
        const listRes = await fetch(`${API_BASE}/campaign/list`);
        const listData = await listRes.json();
        const campaigns = listData.campaigns;
        
        if (campaigns.length === 0) {
            alert("No saved campaigns yet!");
            return;
        }
        
        let options = "Choose a campaign to load:\n\n";
        campaigns.forEach((c, i) => {
            const updatedDate = new Date(c.updated).toLocaleDateString();
            options += `${i+1}. ${c.name} (${updatedDate})\n`;
        });
        const choice = prompt(options + "\nEnter number:");
        const idx = parseInt(choice) - 1;
        
        if (idx >= 0 && idx < campaigns.length) {
            const selected = campaigns[idx];
            const res = await fetch(`${API_BASE}/campaign/load`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({campaign_id: selected.id})
            });
            const data = await res.json();
            if (data.session_id) {
                // Close old WebSocket before switching
                if (ws) ws.close();
                
                sessionId = data.session_id;
                const joinUrl = `${window.location.origin}?session_id=${sessionId}`;
                document.getElementById("qr-code").innerHTML = "";
                new QRCode(document.getElementById('qr-code'), joinUrl);
                addLog(`📜 Loaded campaign: ${selected.name}`, "system");
                connectWebSocket();
            } else {
                addLog(`Error loading: ${data.error}`, "system");
            }
        }
    });
});

function connectWebSocket() {
    if (!sessionId) return;
    
    ws = new WebSocket(`${wsProto}://${window.location.host}/ws/${sessionId}`);
    
    ws.onopen = () => {
        // Announce join
        myName = prompt("Your name?") || "Hero";
        ws.send(JSON.stringify({ type: "join", player_name: myName }));
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === "persona_update") {
            document.getElementById("persona-select").value = data.persona;
            addLog(`DM voice changed to: ${data.persona}`, "system");
        }
        
        if (data.type === "turn_update") {
            document.getElementById("active-player").innerText = 
                data.active_player ? data.active_player : "Free — anyone can speak";
            document.getElementById("turn-queue").innerText = 
                data.queue && data.queue.length ? data.queue.join(" → ") : "none";
            
            if (data.text) addLog(data.text, "system");
        }
        
        if (data.type === "whisper") {
            addLog(data.text, "whisper");
        }
        
        if (data.type === "system") {
            addLog(data.text, "system");
        }
        
        if (data.type === "narration") {
            addLog(`DM: ${data.text}`, "narration");
            
            // Play audio from base64
            if (data.audio_base64) {
                const audio = new Audio(`data:audio/mp3;base64,${data.audio_base64}`);
                audio.play().catch(e => console.log("Audio playback:", e));
            } else {
                // Fallback to browser TTS
                const utter = new SpeechSynthesisUtterance(data.text);
                utter.rate = 0.95;
                speechSynthesis.speak(utter);
            }
            
            if (isHost) {
                document.getElementById("persona-select").value = data.persona;
            }
        }
    };
    
    ws.onerror = (error) => console.error('WebSocket error:', error);
}

function addLog(text, type = "narration") {
    const div = document.createElement("div");
    div.className = type;
    div.innerText = text;
    document.getElementById("log").prepend(div);
}

// === Voice Input ===
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.continuous = false;
recognition.interimResults = false;

document.getElementById('push-to-talk').addEventListener('mousedown', () => {
    document.getElementById('push-to-talk').style.background = "#f44";
    recognition.start();
});
document.getElementById('push-to-talk').addEventListener('mouseup', () => {
    document.getElementById('push-to-talk').style.background = "";
});

recognition.onresult = (event) => {
    const text = event.results[0][0].transcript;
    document.getElementById("status").innerText = `You said: "${text}"`;
    
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ 
            type: "voice_input", 
            text: text,
            player_name: myName
        }));
    }
};

recognition.onerror = (e) => console.error(e);
