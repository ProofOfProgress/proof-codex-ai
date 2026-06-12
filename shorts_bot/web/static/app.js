function apiHeaders(extra = {}) {
  const h = { ...extra };
  if (window.__API_TOKEN__) {
    h.Authorization = `Bearer ${window.__API_TOKEN__}`;
  }
  return h;
}

function toast(msg, ok = true) {
  const el = document.createElement('div');
  el.textContent = msg;
  el.style.cssText = `position:fixed;bottom:20px;right:20px;padding:12px 18px;border-radius:10px;font-size:.9rem;z-index:9999;color:#fff;background:${ok ? '#166534' : '#991b1b'};box-shadow:0 8px 24px rgba(0,0,0,.4);`;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3200);
}

const messages = document.getElementById('messages');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');

function addMsg(text, who) {
  const el = document.createElement('div');
  el.className = 'msg ' + who;
  el.textContent = text;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
}

if (chatForm) {
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;
    chatInput.value = '';
    addMsg(text, 'user');
    addMsg('Thinking...', 'bot');
    const pending = messages.lastChild;
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: apiHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      pending.textContent = res.ok ? (data.reply || 'No reply') : (data.detail || data.message || 'Error');
    } catch {
      pending.textContent = 'Connection error.';
    }
  });
}

function showPanel(name) {
  document.querySelectorAll('.panel').forEach((p) => p.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach((b) => b.classList.remove('active'));
  const panel = document.getElementById('panel-' + name);
  const btn = document.querySelector(`[data-panel="${name}"]`);
  if (panel) panel.classList.add('active');
  if (btn) btn.classList.add('active');
}

document.querySelectorAll('.nav-btn').forEach((btn) => {
  btn.addEventListener('click', () => showPanel(btn.dataset.panel));
});

async function decideImprovement(id, yes) {
  const path = yes ? 'yes' : 'no';
  await fetch(`/api/improvements/${id}/${path}`, {
    method: 'POST',
    headers: apiHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ note: yes ? 'Approved.' : 'Skipped.' }),
  });
  document.querySelector(`.imp-card[data-id="${id}"]`)?.remove();
}

async function decideDraft(id, yes) {
  const note = yes ? 'Approved.' : (prompt('Why reject? (optional)') || 'Rejected.');
  const path = yes ? 'yes' : 'no';
  await fetch(`/api/drafts/${id}/${path}`, {
    method: 'POST',
    headers: apiHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ note }),
  });
  document.querySelector(`.draft-card[data-draft="${id}"]`)?.remove();
}

async function decideDev(id, yes) {
  const path = yes ? 'yes' : 'no';
  await fetch(`/api/dev/${id}/${path}`, {
    method: 'POST',
    headers: apiHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ note: yes ? 'Approved.' : 'Skipped.' }),
  });
  document.querySelector(`.dev-card[data-id="${id}"]`)?.remove();
}

const applyBrandBtn = document.getElementById('apply-brand-btn');
const brandMsg = document.getElementById('brand-msg');
if (applyBrandBtn) {
  applyBrandBtn.addEventListener('click', async () => {
    applyBrandBtn.disabled = true;
    brandMsg.className = 'sync-msg';
    brandMsg.textContent = 'Opening browser — updating channel name and description…';
    try {
      const res = await fetch('/api/youtube/apply-brand', { method: 'POST', headers: apiHeaders() });
      const data = await res.json();
      brandMsg.className = 'sync-msg ' + (data.ok ? 'ok' : 'err');
      let text = data.message || 'Done';
      if (data.name_updated) text += ' · Name updated';
      if (data.description_updated) text += ' · Description updated';
      brandMsg.textContent = text;
    } catch {
      brandMsg.className = 'sync-msg err';
      brandMsg.textContent = 'Apply failed — sign into YouTube in the browser profile first.';
    } finally {
      applyBrandBtn.disabled = false;
    }
  });
}

const produceMsg = document.getElementById('produce-msg');
const produceAutoBtn = document.getElementById('produce-auto-btn');
if (produceAutoBtn && produceMsg) {
  produceAutoBtn.addEventListener('click', async () => {
    const draftId = parseInt(document.getElementById('produce-draft-id')?.value, 10);
    if (!draftId) {
      produceMsg.className = 'sync-msg err';
      produceMsg.textContent = 'Enter draft ID first.';
      return;
    }
    produceAutoBtn.disabled = true;
    produceMsg.className = 'sync-msg';
    produceMsg.textContent = 'Auto-building still images from script…';
    try {
      const res = await fetch(`/api/production/auto/${draftId}`, { method: 'POST', headers: apiHeaders() });
      const data = await res.json();
      produceMsg.className = 'sync-msg ' + (data.ok ? 'ok' : 'err');
      produceMsg.textContent = data.message || 'Done';
    } catch {
      produceMsg.className = 'sync-msg err';
      produceMsg.textContent = 'Auto production failed.';
    } finally {
      produceAutoBtn.disabled = false;
    }
  });
}

const produceBtn = document.getElementById('produce-btn');
if (produceBtn && produceMsg) {
  produceBtn.addEventListener('click', async () => {
    const draftId = parseInt(document.getElementById('produce-draft-id')?.value, 10);
    const text = document.getElementById('produce-transcript')?.value?.trim();
    if (!draftId || !text) {
      produceMsg.className = 'sync-msg err';
      produceMsg.textContent = 'Enter draft ID and TurboScribe transcript.';
      return;
    }
    produceBtn.disabled = true;
    produceMsg.className = 'sync-msg';
    produceMsg.textContent = 'Building image prompts and CapCut timeline…';
    try {
      const res = await fetch('/api/production', {
        method: 'POST',
        headers: apiHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ draft_id: draftId, turboscribe_text: text }),
      });
      const data = await res.json();
      produceMsg.className = 'sync-msg ' + (data.ok ? 'ok' : 'err');
      produceMsg.textContent = data.message || (data.detail || 'Done');
    } catch {
      produceMsg.className = 'sync-msg err';
      produceMsg.textContent = 'Production pack failed.';
    } finally {
      produceBtn.disabled = false;
    }
  });
}

const syncBtn = document.getElementById('sync-btn');
const syncMsg = document.getElementById('sync-msg');
if (syncBtn) {
  syncBtn.addEventListener('click', async () => {
    syncBtn.disabled = true;
    syncMsg.className = 'sync-msg';
    syncMsg.textContent = 'Syncing...';
    try {
      const res = await fetch('/api/youtube/sync', { method: 'POST', headers: apiHeaders() });
      const data = await res.json();
      syncMsg.className = 'sync-msg ' + (data.ok ? 'ok' : 'err');
      syncMsg.textContent = data.message || 'Done';
      if (data.ok) location.reload();
    } catch {
      syncMsg.className = 'sync-msg err';
      syncMsg.textContent = 'Sync failed';
    } finally {
      syncBtn.disabled = false;
    }
  });
}

const devForm = document.getElementById('dev-form');
if (devForm) {
  devForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('dev-title').value.trim();
    const desc = document.getElementById('dev-desc').value.trim();
    if (!title || !desc) return;
    const res = await fetch('/api/dev', {
      method: 'POST',
      headers: apiHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ title, description: desc }),
    });
    const data = await res.json();
    toast(data.message || 'Queued');
    setTimeout(() => location.reload(), 800);
  });
}

const copyLearned = document.getElementById('copy-learned');
const learnedBox = document.getElementById('learned-box');
if (copyLearned && learnedBox) {
  copyLearned.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(learnedBox.textContent || '');
      toast('Copied learned rules');
    } catch {
      toast('Copy failed — select text manually', false);
    }
  });
}

async function refreshStats() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    document.querySelectorAll('.stat .value').forEach((el, i) => {
      const vals = [data.pending_improvements, data.pending_drafts ?? 0, data.pending_dev];
      if (vals[i] !== undefined) el.textContent = vals[i];
    });
  } catch { /* ignore */ }
}
setInterval(refreshStats, 45000);

const titles = {
  chat: 'Strategist chat',
  rewards: 'Rewards & analytics',
  learning: 'Learning journal',
  dev: 'Dev queue',
  slack: 'Slack setup',
};

async function loadSlackPanel() {
  const stepsEl = document.getElementById('slack-steps');
  const progressEl = document.getElementById('slack-progress');
  const promptEl = document.getElementById('slack-test-prompt');
  if (!stepsEl) return;
  try {
    const res = await fetch('/api/slack/status');
    const data = await res.json();
    if (progressEl) progressEl.textContent = data.progress || '—';
    if (promptEl && data.test_prompt) promptEl.value = data.test_prompt;
    const steps = data.steps || [];
    stepsEl.innerHTML = steps
      .map(
        (s) => `
      <div class="setup-row ${s.done ? 'done' : ''}" style="margin:6px 0;">
        <span class="setup-dot">${s.done ? '✓' : '○'}</span>
        <span><strong>${s.label}</strong>
        ${s.url ? ` — <a href="${s.url}" target="_blank" rel="noopener" style="color:var(--accent);">open</a>` : ''}
        <br><span style="color:var(--muted);font-size:.78rem;">${s.detail || ''}</span></span>
      </div>`
      )
      .join('');
  } catch {
    stepsEl.textContent = 'Could not load Slack status.';
  }
}

const slackTestBtn = document.getElementById('slack-test-btn');
const slackTestMsg = document.getElementById('slack-test-msg');
if (slackTestBtn && slackTestMsg) {
  slackTestBtn.addEventListener('click', async () => {
    slackTestBtn.disabled = true;
    slackTestMsg.className = 'sync-msg';
    slackTestMsg.textContent = 'Sending…';
    try {
      const res = await fetch('/api/slack/test', { method: 'POST', headers: apiHeaders() });
      const data = await res.json();
      slackTestMsg.className = 'sync-msg ' + (res.ok ? 'ok' : 'err');
      slackTestMsg.textContent = res.ok ? data.message : (data.detail || 'Failed');
      if (res.ok) loadSlackPanel();
    } catch {
      slackTestMsg.className = 'sync-msg err';
      slackTestMsg.textContent = 'Request failed — check SLACK_CHANNEL_EMAIL + Gmail or SLACK_WEBHOOK_URL in .env';
    } finally {
      slackTestBtn.disabled = false;
    }
  });
}

document.querySelectorAll('.nav-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    const t = document.getElementById('panel-title');
    if (t) t.textContent = titles[btn.dataset.panel] || 'Shorts Bot';
    if (btn.dataset.panel === 'slack') loadSlackPanel();
  });
});

loadSlackPanel();

window.decideImprovement = decideImprovement;
window.decideDraft = decideDraft;
window.decideDev = decideDev;
window.showPanel = showPanel;
