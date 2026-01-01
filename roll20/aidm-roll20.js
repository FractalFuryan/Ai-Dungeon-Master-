// ===============================
// AI Dungeon Master — Roll20 API
// Sandbox-safe (NO fetch, NO HTTP)
// ===============================
//
// This script captures !aidm commands and queues them in state.
// The GM uses !aidm_dump to retrieve the queue for relay processing.
// Fully compliant with Roll20 API sandbox restrictions.

state.AIDM = state.AIDM || {
  queue: []
};

// Main command handler - captures all !aidm commands
on('chat:message', function (msg) {
  if (msg.type !== 'api') return;
  if (!msg.content.startsWith('!aidm')) return;

  const text = msg.content.replace('!aidm', '').trim();

  // Handle help command locally
  if (text === 'help') {
    sendChat('AI DM', `/w "${msg.who}" **AI Dungeon Master Commands**\n` +
      `• !aidm [your action] — Narrate player action\n` +
      `• !aidm persona [name] — Change DM persona (classic|gothic|whimsical|etc)\n` +
      `• !aidm roll [skill] — Request Roll20-native skill check\n` +
      `• !aidm myturn — Request next turn in queue\n` +
      `• !aidm help — Show this message\n\n` +
      `*GM Only:*\n` +
      `• !aidm_dump — Export queue for relay processing\n` +
      `• !aidm_clear — Clear pending queue`
    );
    return;
  }

  const payload = {
    ts: Date.now(),
    campaign_id: Campaign().get('_id'),
    player_name: msg.who,
    player_id: msg.playerid,
    text: text,
    selected: msg.selected ? msg.selected.map(s => s._id) : []
  };

  // Push to local queue
  state.AIDM.queue.push(payload);

  sendChat(
    'AI DM',
    `/direct <span style="color:#8B4513; font-style:italic;">[AI DM] Received. Thinking…</span>`
  );
});

// GM command to dump queue (relay reads this)
on('chat:message', function (msg) {
  if (msg.type !== 'api') return;
  if (msg.content !== '!aidm_dump') return;
  if (!playerIsGM(msg.playerid)) {
    sendChat('AI DM', `/w "${msg.who}" Only the GM can dump the queue.`);
    return;
  }

  if (state.AIDM.queue.length === 0) {
    sendChat('AI DM', '/w gm No pending commands.');
    return;
  }

  const dump = JSON.stringify(state.AIDM.queue);
  state.AIDM.queue = [];

  sendChat('AI DM', `/w gm AIDM_QUEUE:${dump}`);
});

// GM command to clear queue (emergency)
on('chat:message', function (msg) {
  if (msg.type !== 'api') return;
  if (msg.content !== '!aidm_clear') return;
  if (!playerIsGM(msg.playerid)) {
    sendChat('AI DM', `/w "${msg.who}" Only the GM can clear the queue.`);
    return;
  }

  const count = state.AIDM.queue.length;
  state.AIDM.queue = [];
  sendChat('AI DM', `/w gm Queue cleared (${count} commands removed).`);
});

log('AI Dungeon Master API script loaded successfully.');
