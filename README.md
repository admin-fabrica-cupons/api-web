# Product Scraper API

API para buscar HTML de páginas públicas, com fallback opcional para Chromium/Playwright quando a página depende de JavaScript. Também extrai metadados genéricos úteis para páginas de produto, como JSON-LD, Open Graph, título, canonical, preço e imagem quando esses dados existem no HTML.

## Recursos

- `POST /v1/scrape`: retorna JSON com HTML + metadados extraídos.
- `GET /v1/html`: retorna HTML puro.
- Modos `http`, `browser` e `auto`.
- Renderização de JavaScript com Chromium/Playwright.
- Proxy HTTP/HTTPS/SOCKS5 por requisição ou por variável de ambiente.
- Headers, cookies, user-agent, locale, timezone, timeout, retries e espera por seletor.
- Bloqueio opcional de imagens/fonts/mídia para reduzir custo do navegador.
- Fallback automático de HTTP para browser em páginas aparentemente dinâmicas/desafiadas.
- Limite de tamanho de resposta, concorrência do Chromium, rate limit e API key.
- Proteção básica contra SSRF, bloqueando localhost, IPs privados, link-local e reservados.

> Use somente em páginas e dados que você tem autorização para acessar e respeite termos de uso, robots.txt e limites dos sites. O projeto não inclui CAPTCHA solver nem técnicas para contornar controles de acesso.

## Rodar localmente

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
playwright install --with-deps chromium
uvicorn app.main:app --reload
```

Playground: `http://localhost:8000/playground`

Swagger: `http://localhost:8000/docs`


## Playground web

A interface de testes está disponível em `/playground` (e a rota `/` redireciona para ela). Ela permite montar e executar chamadas sem precisar de Postman ou cURL.

Recursos da interface:

- URL e API key.
- Modos `auto`, `http` e `browser`.
- Controle de `render_js`, `wait_until`, timeout, delay e retries.
- Seletor CSS para aguardar conteúdo dinâmico.
- Proxy por requisição, inclusive usuário/senha e bypass.
- Headers e cookies em JSON.
- User-Agent, locale e timezone.
- Abas para JSON completo, HTML bruto, dados de produto e payload enviado.
- Status HTTP, modo realmente usado e tempo da requisição.
- Botão para copiar a saída.

A API key digitada no playground é usada somente no header `X-API-Key` da requisição feita pelo navegador e não é gravada pelo frontend.

## Exemplo simples

```bash
curl -X POST http://localhost:8000/v1/scrape \
  -H "Content-Type: application/json" \
  -H "X-API-Key: troque-por-uma-chave-forte" \
  -d '{
    "url": "https://example.com",
    "mode": "auto",
    "include_html": true,
    "extract": true
  }'
```

## Renderizar JavaScript

```bash
curl -X POST http://localhost:8000/v1/scrape \
  -H "Content-Type: application/json" \
  -H "X-API-Key: troque-por-uma-chave-forte" \
  -d '{
    "url": "https://example.com/produto",
    "mode": "browser",
    "wait_until": "domcontentloaded",
    "wait_for_selector": "body",
    "delay_ms": 1000,
    "block_resources": true
  }'
```

## Proxy

```json
{
  "url": "https://example.com/produto",
  "mode": "browser",
  "proxy": {
    "server": "http://proxy.example.com:8080",
    "username": "usuario",
    "password": "senha"
  }
}
```

Para um proxy fixo no servidor, configure:

```env
DEFAULT_PROXY_URL=http://usuario:senha@proxy.example.com:8080
```

Não exponha credenciais de proxy em logs ou no frontend.

## Exemplo de resposta

```json
{
  "requested_url": "https://example.com/produto",
  "final_url": "https://example.com/produto",
  "status_code": 200,
  "mode_used": "browser",
  "content_type": "text/html; charset=utf-8",
  "elapsed_ms": 1432,
  "html": "<!doctype html>...",
  "data": {
    "title": "Produto X",
    "canonical": "https://example.com/produto",
    "openGraph": {
      "image": "https://cdn.example.com/produto.jpg"
    },
    "product": {
      "name": "Produto X",
      "price": "99.90",
      "currency": "BRL"
    },
    "jsonLd": []
  },
  "warnings": []
}
```

## Endpoint HTML puro

```bash
curl "http://localhost:8000/v1/html?url=https%3A%2F%2Fexample.com&render_js=false" \
  -H "X-API-Key: troque-por-uma-chave-forte"
```

## Deploy no Render

O projeto inclui `Dockerfile` e `render.yaml`.

1. Envie o projeto para um repositório GitHub.
2. No Render, crie um **Web Service** e conecte o repositório.
3. Escolha o runtime **Docker**.
4. O serviço deve usar o `Dockerfile` automaticamente.
5. Configure/guarde o valor de `API_KEY` em Environment.
6. Use `/health` como Health Check Path.

O servidor escuta em `0.0.0.0:${PORT:-10000}`, compatível com o requisito de Web Services do Render.

### Plano e memória

O `render.yaml` começa no plano `free` para evitar criar cobrança automaticamente. O plano gratuito tem 512 MB de RAM e é indicado para testes; Chromium pode ficar apertado nessa memória. Para uso estável/produção, considere `1c-2g` (1 CPU / 2 GB) ou superior e mantenha `MAX_BROWSER_CONCURRENCY` baixo. O modo `auto` ajuda porque usa Chromium apenas quando necessário.

## Parâmetros principais do POST `/v1/scrape`

| Campo | Exemplo | Função |
|---|---|---|
| `url` | `https://...` | Página alvo |
| `mode` | `auto` | `auto`, `http` ou `browser` |
| `render_js` | `true` | Força browser se `true`; HTTP se `false` |
| `extract` | `true` | Extrai JSON-LD/OG/produto |
| `include_html` | `true` | Inclui HTML na resposta JSON |
| `wait_until` | `domcontentloaded` | Evento de navegação do Playwright |
| `wait_for_selector` | `.product-title` | Aguarda elemento específico |
| `delay_ms` | `1000` | Espera adicional depois do carregamento |
| `timeout_ms` | `35000` | Timeout por chamada |
| `max_retries` | `2` | Retries do modo HTTP |
| `block_resources` | `true` | Bloqueia imagem/font/mídia no browser |
| `headers` | `{...}` | Headers extras |
| `cookies` | `[...]` | Cookies da sessão |
| `proxy` | `{...}` | Proxy por chamada |

## Observações para Mercado Livre, Shopee, Magalu etc.

Não existe uma configuração universal que garanta acesso a todos os e-commerces. Eles mudam HTML, carregamento e políticas frequentemente. A melhor estratégia é:

1. Usar APIs oficiais quando disponíveis.
2. Tentar HTTP primeiro.
3. Extrair JSON-LD/Open Graph/estado serializado no HTML.
4. Usar Playwright somente quando o conteúdo realmente depender de JavaScript.
5. Aplicar filas, cache, rate limits e backoff para não sobrecarregar o site.
6. Se usar proxy, usar um provedor legítimo e respeitar as regras do site.

A próxima evolução natural é criar `adapters/amazon.py`, `adapters/mercadolivre.py`, `adapters/shopee.py`, `adapters/magalu.py` etc., mantendo este fetcher como camada genérica.
