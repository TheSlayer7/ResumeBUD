async function setProvider(provider) { try { await api('/settings/provider', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ provider }) }); notify(`${provider === 'local' ? 'Local keyless mode' : provider + ' mode'} enabled`); await refreshProviderStatus(); } catch (error) { notify(error.message); } }
function openApiDocs() {
  const tab = window.open('/docs', '_blank', 'noopener,noreferrer');
  if (!tab) notify('Allow pop-ups to open API docs in a new tab.');
}
function openOpenApiSpec() {
  const tab = window.open('/openapi.json', '_blank', 'noopener,noreferrer');
  if (!tab) notify('Allow pop-ups to open OpenAPI JSON in a new tab.');
}
async function refreshProviderStatus() {
  const badge = $('#provider-status');
  if (!badge) return;
  try {
    const data = await api('/settings/provider');
    badge.textContent = `Current provider: ${String(data.provider || 'local').toUpperCase()}`;
  } catch (_) {
    badge.textContent = 'Current provider: unavailable';
  }
}
async function checkBackendStatus() {
  try {
    const [provider, resumes, jobs] = await Promise.all([
      api('/settings/provider'),
      api('/resumes'),
      api('/jobs')
    ]);
    notify(`API online | ${provider.provider} mode | ${resumes.length} resumes | ${jobs.length} jobs`);
  } catch (error) {
    notify(error.message || 'Unable to reach API');
  }
}
function wireResumeBud() {
  const toggle = $('#bud-toggle'); const panel = $('#bud-panel');
  if (!toggle) return;
  toggle.onclick = () => panel.classList.toggle('hidden');
  $('#bud-close').onclick = () => panel.classList.add('hidden');
  document.querySelectorAll('[data-bud-page]').forEach((button) => button.onclick = () => { state.page = button.dataset.budPage; panel.classList.add('hidden'); render(); });
  $('#bud-form').onsubmit = async (event) => { event.preventDefault(); const input = $('#bud-input'); const messages = $('#bud-messages'); const message = input.value.trim(); if (!message) return; input.value = ''; messages.insertAdjacentHTML('beforeend', `<div class="bud-message user">${esc(message)}</div>`); const pending = document.createElement('div'); pending.className = 'bud-message assistant pending'; pending.textContent = 'Thinking...'; messages.appendChild(pending); messages.scrollTop = messages.scrollHeight; try { const response = await api('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message }) }); pending.classList.remove('pending'); pending.innerHTML = `${esc(response.answer)}<small>${esc(response.provider)} mode</small>`; } catch (error) { pending.remove(); notify(error.message || 'Assistant unavailable'); } messages.scrollTop = messages.scrollHeight; };
}
const oldSettings = settings;
function settings() { $('#content').innerHTML = `<div class="top"><div><h2>Workspace settings</h2><p>Hey, what's up? Choose how ResumeBUD evaluates resumes.</p></div></div><section class="panel" style="max-width:760px"><span class="step">EVALUATION PROVIDER</span><h3>Choose your analysis mode</h3><p class="detail">Local mode is private, keyless, and uses the built-in evidence matcher. Gemini uses your configured API key for richer semantic feedback.</p><div id="provider-status" class="provider-status">Current provider: loading...</div><div class="provider-actions"><button class="btn accent" onclick="setProvider('local')">Use local mode</button><button class="btn primary" onclick="setProvider('gemini')">Use Gemini</button></div><div class="provider-actions"><button class="btn" onclick="openApiDocs()">Open API docs ↗</button><button class="btn" onclick="openOpenApiSpec()">Open OpenAPI JSON</button><button class="btn" onclick="checkBackendStatus()">Check backend status</button></div><p class="muted" style="margin-top:16px">Use API docs to test endpoints, and OpenAPI JSON to integrate with tools or generate clients.</p><button class="btn" onclick="loadDemo()">Load demo workspace</button></section>`; refreshProviderStatus(); }
const baseRender = render;
function render() { const titles = { dashboard: 'Dashboard', resumes: 'Resumes', jobs: 'Jobs', screening: 'Screening', candidates: 'Candidates', settings: 'Settings' }; $('#title').textContent = titles[state.page]; document.querySelectorAll('.nav').forEach((x) => x.classList.toggle('active', x.dataset.page === state.page)); ({ dashboard, resumes, jobs, screening, candidates, settings }[state.page])(); const greetings = { dashboard: "Hey, what's up? Ready to find the right signal?", resumes: "Hey, what's up? Looking for feedback on a resume?", jobs: "Hey, what's up? Let's shape the role you're hiring for.", screening: "Hey, what's up? Ready to compare the shortlist?", candidates: "Hey, what's up? Let's explore your candidate pool.", settings: "Hey, what's up? Choose local or cloud analysis." }; let hello = $('#page-greeting'); if (!hello) { hello = document.createElement('p'); hello.id = 'page-greeting'; $('#title').after(hello); } hello.textContent = greetings[state.page]; wireResumeBud(); }
loadData().then(render).catch((error) => notify(error.message));
