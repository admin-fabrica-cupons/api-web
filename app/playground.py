from __future__ import annotations


PLAYGROUND_HTML = r'''<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Product Scraper API · Playground</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0a0d12;
      --panel: #111722;
      --panel-2: #151d29;
      --line: #263244;
      --text: #eef4ff;
      --muted: #8fa0b8;
      --accent: #70a5ff;
      --accent-2: #8dd7b6;
      --danger: #ff8b91;
      --warning: #ffd27a;
      --shadow: 0 18px 60px rgba(0,0,0,.28);
      --radius: 16px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at 15% -10%, rgba(112,165,255,.16), transparent 32%),
        radial-gradient(circle at 90% 0%, rgba(141,215,182,.09), transparent 28%),
        var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    button, input, select, textarea { font: inherit; }
    a { color: var(--accent); text-decoration: none; }
    .shell { max-width: 1500px; margin: 0 auto; padding: 24px; }
    .topbar {
      display: flex; align-items: center; justify-content: space-between; gap: 16px;
      margin-bottom: 18px;
    }
    .brand { display: flex; gap: 12px; align-items: center; }
    .logo {
      width: 42px; height: 42px; border-radius: 12px;
      display: grid; place-items: center;
      background: linear-gradient(135deg, rgba(112,165,255,.22), rgba(141,215,182,.18));
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
      font-weight: 800;
    }
    h1 { margin: 0; font-size: 20px; letter-spacing: -.02em; }
    .subtitle { color: var(--muted); margin-top: 3px; font-size: 13px; }
    .top-actions { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
    .status {
      display: inline-flex; align-items: center; gap: 8px;
      border: 1px solid var(--line); background: rgba(17,23,34,.72);
      padding: 8px 10px; border-radius: 999px; color: var(--muted); font-size: 12px;
    }
    .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--warning); }
    .dot.ok { background: var(--accent-2); box-shadow: 0 0 16px rgba(141,215,182,.6); }
    .layout { display: grid; grid-template-columns: minmax(360px, 520px) minmax(0, 1fr); gap: 18px; }
    .card {
      border: 1px solid var(--line); border-radius: var(--radius);
      background: rgba(17,23,34,.90); box-shadow: var(--shadow); overflow: hidden;
    }
    .card-head {
      display: flex; align-items: center; justify-content: space-between; gap: 12px;
      padding: 16px 18px; border-bottom: 1px solid var(--line);
      background: rgba(21,29,41,.74);
    }
    .card-head h2 { font-size: 14px; margin: 0; letter-spacing: .01em; }
    .card-body { padding: 18px; }
    .field { margin-bottom: 14px; }
    label { display: flex; justify-content: space-between; gap: 8px; font-size: 12px; color: #c8d4e7; margin-bottom: 7px; }
    label small { color: var(--muted); }
    input, select, textarea {
      width: 100%; border: 1px solid var(--line); border-radius: 10px; color: var(--text);
      background: #0c1119; outline: none; transition: .16s border-color, .16s box-shadow;
    }
    input, select { height: 42px; padding: 0 12px; }
    textarea { min-height: 92px; resize: vertical; padding: 10px 12px; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; line-height: 1.5; }
    input:focus, select:focus, textarea:focus { border-color: rgba(112,165,255,.75); box-shadow: 0 0 0 3px rgba(112,165,255,.10); }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
    details { border: 1px solid var(--line); border-radius: 12px; background: #0d131c; margin-top: 12px; }
    summary { cursor: pointer; padding: 12px 14px; color: #cbd7e8; font-size: 12px; user-select: none; }
    details .inner { padding: 2px 14px 14px; }
    .check-row { display: flex; gap: 16px; flex-wrap: wrap; margin: 6px 0 14px; }
    .check { display: inline-flex; align-items: center; gap: 8px; color: #cbd7e8; font-size: 12px; }
    .check input { width: 16px; height: 16px; accent-color: var(--accent); }
    .btn {
      border: 1px solid var(--line); background: #121a25; color: var(--text);
      border-radius: 10px; padding: 9px 12px; cursor: pointer; transition: .16s transform, .16s background, .16s border-color;
    }
    .btn:hover { transform: translateY(-1px); border-color: #3d4e67; background: #172130; }
    .btn.primary { background: linear-gradient(135deg, #5d91ed, #6f9ef0); border-color: #79a8fa; color: white; font-weight: 700; }
    .btn.primary:hover { background: linear-gradient(135deg, #6a9cf1, #7aa8f4); }
    .btn:disabled { opacity: .55; cursor: wait; transform: none; }
    .actions { display: flex; gap: 10px; flex-wrap: wrap; }
    .hint { color: var(--muted); font-size: 11px; line-height: 1.5; }
    .tabs { display: flex; gap: 5px; overflow-x: auto; }
    .tab { border: 0; border-radius: 8px; background: transparent; color: var(--muted); padding: 8px 10px; cursor: pointer; font-size: 12px; }
    .tab.active { background: #1c2736; color: var(--text); }
    .result-meta { display: flex; gap: 8px; flex-wrap: wrap; padding: 12px 18px; border-bottom: 1px solid var(--line); background: #0e141e; min-height: 49px; align-items: center; }
    .pill { font-size: 11px; padding: 5px 8px; border: 1px solid var(--line); border-radius: 999px; color: var(--muted); }
    .pill.good { color: var(--accent-2); border-color: rgba(141,215,182,.34); }
    .pill.bad { color: var(--danger); border-color: rgba(255,139,145,.34); }
    .output-wrap { position: relative; }
    pre {
      margin: 0; padding: 18px; height: calc(100vh - 220px); min-height: 560px;
      overflow: auto; white-space: pre; tab-size: 2;
      color: #dce8f8; background: #090e15; font-size: 12px; line-height: 1.55;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }
    .empty { color: var(--muted); }
    .error { color: var(--danger); }
    .product { display: none; padding: 18px; height: calc(100vh - 220px); min-height: 560px; overflow: auto; background: #090e15; }
    .product-grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 10px; }
    .kv { border: 1px solid var(--line); border-radius: 10px; background: #0f1620; padding: 12px; overflow: hidden; }
    .kv span { display: block; color: var(--muted); font-size: 10px; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 6px; }
    .kv strong { display: block; color: var(--text); font-size: 13px; overflow-wrap: anywhere; }
    .notice { border: 1px solid rgba(255,210,122,.24); background: rgba(255,210,122,.06); color: #e7d2a3; padding: 10px 12px; border-radius: 10px; font-size: 11px; line-height: 1.55; margin-bottom: 14px; }
    .spinner { display: none; width: 14px; height: 14px; border: 2px solid rgba(255,255,255,.25); border-top-color: white; border-radius: 50%; animation: spin .7s linear infinite; }
    .loading .spinner { display: inline-block; }
    @keyframes spin { to { transform: rotate(360deg); } }
    @media (max-width: 980px) {
      .shell { padding: 14px; }
      .layout { grid-template-columns: 1fr; }
      pre, .product { height: 620px; min-height: 420px; }
      .topbar { align-items: flex-start; flex-direction: column; }
      .top-actions { justify-content: flex-start; }
    }
    @media (max-width: 560px) {
      .grid-2, .grid-3, .product-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <header class="topbar">
      <div class="brand">
        <div class="logo">S</div>
        <div>
          <h1>Product Scraper API</h1>
          <div class="subtitle">Playground para testar HTTP, Chromium, proxies e extração.</div>
        </div>
      </div>
      <div class="top-actions">
        <span class="status"><span id="healthDot" class="dot"></span><span id="healthText">checando API…</span></span>
        <a class="btn" href="/docs" target="_blank" rel="noreferrer">Swagger</a>
        <a class="btn" href="/openapi.json" target="_blank" rel="noreferrer">OpenAPI</a>
      </div>
    </header>

    <section class="layout">
      <form id="scrapeForm" class="card" autocomplete="off">
        <div class="card-head">
          <h2>Requisição</h2>
          <button id="exampleBtn" class="btn" type="button">Carregar exemplo</button>
        </div>
        <div class="card-body">
          <div class="notice">Use o playground apenas em URLs que você está autorizado a acessar. A API não resolve CAPTCHA nem contorna controles de acesso.</div>

          <div class="field">
            <label for="url">URL <small>obrigatório</small></label>
            <input id="url" name="url" type="url" placeholder="https://example.com/produto" required />
          </div>

          <div class="field">
            <label for="apiKey">API Key <small>enviada apenas no header X-API-Key</small></label>
            <input id="apiKey" name="apiKey" type="password" placeholder="Opcional se API_KEY não estiver configurada" />
          </div>

          <div class="grid-3">
            <div class="field">
              <label for="mode">Modo</label>
              <select id="mode">
                <option value="auto">auto</option>
                <option value="http">http</option>
                <option value="browser">browser</option>
              </select>
            </div>
            <div class="field">
              <label for="renderJs">Render JS</label>
              <select id="renderJs">
                <option value="auto">seguir modo</option>
                <option value="true">forçar browser</option>
                <option value="false">forçar HTTP</option>
              </select>
            </div>
            <div class="field">
              <label for="waitUntil">Wait until</label>
              <select id="waitUntil">
                <option value="domcontentloaded">domcontentloaded</option>
                <option value="load">load</option>
                <option value="networkidle">networkidle</option>
                <option value="commit">commit</option>
              </select>
            </div>
          </div>

          <div class="grid-3">
            <div class="field">
              <label for="timeout">Timeout ms</label>
              <input id="timeout" type="number" min="1000" max="90000" placeholder="35000" />
            </div>
            <div class="field">
              <label for="delay">Delay ms</label>
              <input id="delay" type="number" min="0" max="10000" value="0" />
            </div>
            <div class="field">
              <label for="retries">Retries</label>
              <input id="retries" type="number" min="0" max="4" value="2" />
            </div>
          </div>

          <div class="field">
            <label for="selector">Aguardar seletor CSS <small>opcional</small></label>
            <input id="selector" placeholder=".product-title, #price, ..." />
          </div>

          <div class="check-row">
            <label class="check"><input id="extract" type="checkbox" checked /> Extrair metadados</label>
            <label class="check"><input id="includeHtml" type="checkbox" checked /> Incluir HTML</label>
            <label class="check"><input id="blockResources" type="checkbox" checked /> Bloquear mídia/fontes</label>
          </div>

          <details>
            <summary>Proxy</summary>
            <div class="inner">
              <div class="field">
                <label for="proxyServer">Servidor</label>
                <input id="proxyServer" placeholder="http://proxy.exemplo.com:8080" />
              </div>
              <div class="grid-2">
                <div class="field"><label for="proxyUser">Usuário</label><input id="proxyUser" /></div>
                <div class="field"><label for="proxyPass">Senha</label><input id="proxyPass" type="password" /></div>
              </div>
              <div class="field"><label for="proxyBypass">Bypass <small>opcional</small></label><input id="proxyBypass" placeholder="localhost,.dominio.com" /></div>
            </div>
          </details>

          <details>
            <summary>Headers, cookies e navegador</summary>
            <div class="inner">
              <div class="field">
                <label for="headers">Headers JSON</label>
                <textarea id="headers" spellcheck="false" placeholder='{"Referer":"https://example.com/"}'>{}</textarea>
              </div>
              <div class="field">
                <label for="cookies">Cookies JSON</label>
                <textarea id="cookies" spellcheck="false" placeholder='[{"name":"session","value":"...","domain":"example.com"}]'>[]</textarea>
              </div>
              <div class="field"><label for="userAgent">User-Agent <small>vazio = padrão aleatório</small></label><input id="userAgent" /></div>
              <div class="grid-2">
                <div class="field"><label for="locale">Locale</label><input id="locale" value="pt-BR" /></div>
                <div class="field"><label for="timezone">Timezone</label><input id="timezone" value="America/Sao_Paulo" /></div>
              </div>
            </div>
          </details>

          <div class="actions" style="margin-top: 16px">
            <button id="sendBtn" class="btn primary" type="submit"><span class="spinner"></span><span>Executar scrape</span></button>
            <button id="clearBtn" class="btn" type="button">Limpar resultado</button>
          </div>
          <p class="hint">O modo <b>auto</b> tenta HTTP primeiro e usa Chromium quando a página aparenta depender de JavaScript. Em Render gratuito, prefira HTTP quando possível para economizar memória.</p>
        </div>
      </form>

      <section class="card">
        <div class="card-head">
          <div class="tabs" role="tablist">
            <button class="tab active" type="button" data-tab="json">JSON</button>
            <button class="tab" type="button" data-tab="html">HTML</button>
            <button class="tab" type="button" data-tab="product">Produto</button>
            <button class="tab" type="button" data-tab="request">Request</button>
          </div>
          <button id="copyBtn" class="btn" type="button">Copiar</button>
        </div>
        <div id="meta" class="result-meta"><span class="pill">Nenhuma requisição executada</span></div>
        <div class="output-wrap">
          <pre id="output" class="empty">O resultado aparecerá aqui.</pre>
          <div id="productOutput" class="product"></div>
        </div>
      </section>
    </section>
  </main>

  <script>
    (() => {
      const $ = (id) => document.getElementById(id);
      const form = $('scrapeForm');
      const sendBtn = $('sendBtn');
      const output = $('output');
      const productOutput = $('productOutput');
      const meta = $('meta');
      let result = null;
      let lastPayload = null;
      let activeTab = 'json';

      const pretty = (value) => JSON.stringify(value, null, 2);
      const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));

      function parseJsonField(id, fallback) {
        const raw = $(id).value.trim();
        if (!raw) return fallback;
        try { return JSON.parse(raw); }
        catch (e) { throw new Error(`${id === 'headers' ? 'Headers' : 'Cookies'} contém JSON inválido: ${e.message}`); }
      }

      function buildPayload() {
        const payload = {
          url: $('url').value.trim(),
          mode: $('mode').value,
          extract: $('extract').checked,
          include_html: $('includeHtml').checked,
          wait_until: $('waitUntil').value,
          delay_ms: Number($('delay').value || 0),
          max_retries: Number($('retries').value || 0),
          block_resources: $('blockResources').checked,
          locale: $('locale').value.trim() || 'pt-BR',
          timezone_id: $('timezone').value.trim() || 'America/Sao_Paulo',
          headers: parseJsonField('headers', {}),
          cookies: parseJsonField('cookies', []),
        };

        const renderJs = $('renderJs').value;
        if (renderJs !== 'auto') payload.render_js = renderJs === 'true';
        if ($('timeout').value) payload.timeout_ms = Number($('timeout').value);
        if ($('selector').value.trim()) payload.wait_for_selector = $('selector').value.trim();
        if ($('userAgent').value.trim()) payload.user_agent = $('userAgent').value.trim();

        const proxyServer = $('proxyServer').value.trim();
        if (proxyServer) {
          payload.proxy = { server: proxyServer };
          if ($('proxyUser').value) payload.proxy.username = $('proxyUser').value;
          if ($('proxyPass').value) payload.proxy.password = $('proxyPass').value;
          if ($('proxyBypass').value.trim()) payload.proxy.bypass = $('proxyBypass').value.trim();
        }
        return payload;
      }

      function updateMeta(ok, response, elapsedClient) {
        if (!response) {
          meta.innerHTML = '<span class="pill">Nenhuma requisição executada</span>';
          return;
        }
        const code = response.status_code ?? response.status ?? '—';
        const mode = response.mode_used ?? '—';
        const elapsed = response.elapsed_ms ?? elapsedClient ?? '—';
        const finalUrl = response.final_url;
        meta.innerHTML = [
          `<span class="pill ${ok ? 'good' : 'bad'}">HTTP ${esc(code)}</span>`,
          `<span class="pill">modo: ${esc(mode)}</span>`,
          `<span class="pill">${esc(elapsed)} ms</span>`,
          finalUrl ? `<span class="pill" title="${esc(finalUrl)}">${esc(finalUrl.length > 54 ? finalUrl.slice(0, 54) + '…' : finalUrl)}</span>` : ''
        ].join('');
      }

      function renderProduct() {
        const data = result?.data || {};
        const p = data.product || {};
        const fields = [
          ['Nome', p.name || data.title],
          ['Preço', p.price],
          ['Preço anterior', p.oldPrice || p.old_price],
          ['Moeda', p.currency],
          ['Disponibilidade', p.availability],
          ['Imagem', Array.isArray(p.image) ? p.image[0] : (p.image || data.openGraph?.image)],
          ['Canonical', data.canonical],
          ['URL final', result?.final_url],
        ].filter(([,v]) => v !== undefined && v !== null && String(v) !== '');

        if (!fields.length) {
          productOutput.innerHTML = '<div class="empty">Nenhum dado de produto foi detectado.</div>';
          return;
        }
        productOutput.innerHTML = `<div class="product-grid">${fields.map(([k,v]) => `<div class="kv"><span>${esc(k)}</span><strong>${esc(v)}</strong></div>`).join('')}</div>`;
      }

      function renderTab() {
        document.querySelectorAll('.tab').forEach((el) => el.classList.toggle('active', el.dataset.tab === activeTab));
        if (activeTab === 'product') {
          output.style.display = 'none';
          productOutput.style.display = 'block';
          renderProduct();
          return;
        }
        productOutput.style.display = 'none';
        output.style.display = 'block';
        output.classList.remove('error');

        if (!result && activeTab !== 'request') {
          output.textContent = 'O resultado aparecerá aqui.';
          output.classList.add('empty');
          return;
        }
        output.classList.remove('empty');

        if (activeTab === 'json') output.textContent = pretty(result);
        if (activeTab === 'html') output.textContent = result?.html || 'A resposta não contém HTML. Ative “Incluir HTML”.';
        if (activeTab === 'request') output.textContent = lastPayload ? pretty(lastPayload) : 'Execute ou monte uma requisição para visualizar o payload.';
      }

      async function sendRequest(event) {
        event.preventDefault();
        let payload;
        try { payload = buildPayload(); }
        catch (e) {
          result = { error: e.message };
          output.classList.add('error');
          renderTab();
          return;
        }
        lastPayload = payload;
        sendBtn.disabled = true;
        sendBtn.classList.add('loading');
        const started = performance.now();
        try {
          const headers = { 'Content-Type': 'application/json' };
          const key = $('apiKey').value.trim();
          if (key) headers['X-API-Key'] = key;
          const response = await fetch('/v1/scrape', { method: 'POST', headers, body: JSON.stringify(payload) });
          let body;
          try { body = await response.json(); }
          catch { body = { detail: await response.text() }; }
          const clientElapsed = Math.round(performance.now() - started);
          if (!response.ok) {
            result = { status: response.status, ...body };
            updateMeta(false, result, clientElapsed);
          } else {
            result = body;
            updateMeta(true, body, clientElapsed);
          }
          renderTab();
        } catch (e) {
          result = { error: `Falha de rede: ${e.message}` };
          updateMeta(false, { status: 'network-error' }, Math.round(performance.now() - started));
          renderTab();
        } finally {
          sendBtn.disabled = false;
          sendBtn.classList.remove('loading');
        }
      }

      form.addEventListener('submit', sendRequest);
      document.querySelectorAll('.tab').forEach((el) => el.addEventListener('click', () => { activeTab = el.dataset.tab; renderTab(); }));

      $('exampleBtn').addEventListener('click', () => {
        $('url').value = 'https://example.com';
        $('mode').value = 'auto';
        $('renderJs').value = 'auto';
        $('headers').value = '{}';
        $('cookies').value = '[]';
        $('selector').value = '';
        $('delay').value = '0';
        $('retries').value = '2';
      });

      $('clearBtn').addEventListener('click', () => {
        result = null; lastPayload = null; activeTab = 'json'; updateMeta(false, null); renderTab();
      });

      $('copyBtn').addEventListener('click', async () => {
        let text = '';
        if (activeTab === 'json') text = result ? pretty(result) : '';
        if (activeTab === 'html') text = result?.html || '';
        if (activeTab === 'request') text = lastPayload ? pretty(lastPayload) : '';
        if (activeTab === 'product') text = result?.data?.product ? pretty(result.data.product) : '';
        if (!text) return;
        try {
          await navigator.clipboard.writeText(text);
          const old = $('copyBtn').textContent; $('copyBtn').textContent = 'Copiado'; setTimeout(() => $('copyBtn').textContent = old, 900);
        } catch (_) {}
      });

      fetch('/health').then((r) => r.json()).then((d) => {
        if (d.ok) { $('healthDot').classList.add('ok'); $('healthText').textContent = 'API online'; }
        else $('healthText').textContent = 'API indisponível';
      }).catch(() => $('healthText').textContent = 'API indisponível');
    })();
  </script>
</body>
</html>'''
