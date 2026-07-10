#!/usr/bin/env python3
"""
Sintegra Story Engine — serveur local
Run:  python3 story-server.py
Open: http://localhost:5680
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, quote
import json, os, urllib.request

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "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")
PORT = int(os.environ.get("PORT", 5680))

SYSTEM_PROMPT = (
    "Tu es un directeur creatif expert en branding pour un Startup Studio africain. "
    "Reponds UNIQUEMENT avec du JSON valide, aucun texte autour, aucun markdown."
)

EXISTING = (
    "- Sintegra Institute : education et transformation professionnelle des talents africains\n"
    "- LinkHR : connexion entre talents et opportunites internationales\n"
    "- Residia : accompagnement humain vers une nouvelle vie en France\n"
    "- Big Tech Africa : celebration et visibilite de l'innovation africaine"
)

JSON_SCHEMA = '''{
  "nom": "nom court du projet",
  "tagline": "une phrase accrocheuse de 8-12 mots",
  "vision": "ou le projet veut aller dans 5-10 ans (2-3 phrases)",
  "mission": "le probleme qu il resout et pour qui (2-3 phrases)",
  "histoire_de_marque": "pourquoi ce projet existe, l emotion derriere (3-4 phrases)",
  "slogans": ["slogan public large", "slogan decideurs", "slogan communaute"],
  "personas": [
    {"nom": "prenom", "age": "25-35 ans", "profil": "description courte", "douleur": "probleme principal", "desir": "ce qu il veut vraiment"},
    {"nom": "prenom", "age": "35-45 ans", "profil": "description courte", "douleur": "probleme principal", "desir": "ce qu il veut vraiment"}
  ],
  "ton_communication": "style, registre, ce qu on evite (2-3 phrases)",
  "campagnes": ["idee 1", "idee 2", "idee 3", "idee 4", "idee 5"],
  "mots_cles_visuels": ["mot1", "mot2", "mot3", "mot4", "mot5"],
  "differenciateur": "en quoi ce projet se distingue des 4 projets existants (2-3 phrases)"
}'''

HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sintegra Story Engine</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f0f13; color: #e8e8f0; min-height: 100vh; }
.header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  padding: 40px 32px 32px; border-bottom: 1px solid #2a2a4a; }
.header h1 { font-size: 28px; font-weight: 700; color: #fff; letter-spacing: -0.5px; }
.header h1 span { color: #7c6af7; }
.header p { color: #8888aa; margin-top: 8px; font-size: 14px; }
.container { max-width: 900px; margin: 0 auto; padding: 32px 24px; }
.existing { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 12px;
  padding: 20px; margin-bottom: 28px; }
.existing h3 { font-size: 13px; text-transform: uppercase; letter-spacing: 1px;
  color: #7c6af7; margin-bottom: 14px; }
.project-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.tag { background: #12122a; border: 1px solid #2a2a4a; border-radius: 20px;
  padding: 5px 14px; font-size: 13px; color: #aaaacc; }
.input-section { margin-bottom: 24px; }
label { display: block; font-size: 14px; color: #aaaacc; margin-bottom: 8px; font-weight: 500; }
textarea { width: 100%; background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 10px;
  color: #e8e8f0; font-size: 15px; padding: 16px; resize: vertical; min-height: 120px;
  outline: none; transition: border-color 0.2s; font-family: inherit; line-height: 1.6; }
textarea:focus { border-color: #7c6af7; }
.key-row { display: flex; gap: 12px; margin-bottom: 24px; }
input[type=text] { flex: 1; background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 10px;
  color: #e8e8f0; font-size: 14px; padding: 12px 16px; outline: none;
  font-family: monospace; transition: border-color 0.2s; }
input[type=text]:focus { border-color: #7c6af7; }
button { background: #7c6af7; color: #fff; border: none; border-radius: 10px;
  padding: 13px 32px; font-size: 15px; font-weight: 600; cursor: pointer;
  transition: background 0.2s, transform 0.1s; white-space: nowrap; }
button:hover { background: #6a5be0; }
button:active { transform: scale(0.98); }
button:disabled { background: #3a3a5a; color: #666; cursor: default; }
.loader { display: none; text-align: center; padding: 48px; }
.spinner { width: 40px; height: 40px; border: 3px solid #2a2a4a;
  border-top-color: #7c6af7; border-radius: 50%; animation: spin 0.8s linear infinite;
  margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.loader p { color: #8888aa; font-size: 14px; }
#output { display: none; }
.card { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 14px;
  padding: 24px; margin-bottom: 20px; }
.card-title { font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px;
  color: #7c6af7; margin-bottom: 14px; font-weight: 600; }
.hero { background: linear-gradient(135deg, #1a1a3e, #12122a);
  border: 1px solid #3a3a6a; border-radius: 14px; padding: 28px;
  margin-bottom: 20px; text-align: center; }
.hero h2 { font-size: 26px; font-weight: 700; color: #fff; margin-bottom: 10px; }
.hero .tagline { font-size: 16px; color: #aaaadd; font-style: italic; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media(max-width:600px) { .two-col { grid-template-columns: 1fr; } }
.story-text { font-size: 15px; line-height: 1.75; color: #ccccee; }
.slogan-list { list-style: none; }
.slogan-list li { padding: 10px 16px; margin-bottom: 8px; background: #12122a;
  border-left: 3px solid #7c6af7; border-radius: 0 8px 8px 0;
  font-size: 14px; color: #ccccee; }
.persona { background: #12122a; border-radius: 10px; padding: 16px; margin-bottom: 12px; }
.persona-name { font-weight: 700; color: #fff; margin-bottom: 6px; font-size: 15px; }
.persona-row { font-size: 13px; color: #8888aa; margin-top: 4px; }
.persona-row span { color: #ccccee; }
.campagne-list { list-style: none; counter-reset: camp; }
.campagne-list li { counter-increment: camp; padding: 10px 16px 10px 44px;
  margin-bottom: 8px; background: #12122a; border-radius: 8px;
  font-size: 14px; color: #ccccee; position: relative; }
.campagne-list li::before { content: counter(camp); position: absolute; left: 14px;
  top: 50%; transform: translateY(-50%); width: 20px; height: 20px;
  background: #7c6af7; border-radius: 50%; font-size: 11px; font-weight: 700;
  color: #fff; text-align: center; line-height: 20px; }
.visual-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.vtag { background: #12122a; border: 1px solid #3a3a5a; border-radius: 6px;
  padding: 6px 14px; font-size: 13px; color: #aaaacc; }
.diff-box { background: #0a1a0a; border: 1px solid #2a4a2a; border-radius: 10px;
  padding: 16px; font-size: 14px; color: #88cc88; line-height: 1.6; }
.ton-box { background: #12122a; border-radius: 10px; padding: 16px;
  font-size: 14px; color: #ccccee; line-height: 1.6; }
.img-section { margin-bottom: 20px; }
.img-wrap { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 14px;
  overflow: hidden; position: relative; min-height: 200px; }
.img-wrap img { width: 100%; display: block; border-radius: 14px; }
.img-skeleton { width: 100%; height: 400px; background: linear-gradient(90deg,
  #1a1a2e 25%, #2a2a4a 50%, #1a1a2e 75%);
  background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 14px; }
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
.img-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px;
  color: #7c6af7; margin-bottom: 12px; font-weight: 600; }
.img-prompt-box { background: #12122a; border-radius: 8px; padding: 12px 16px;
  font-size: 12px; color: #6666aa; font-family: monospace; margin-top: 12px;
  word-break: break-all; line-height: 1.5; }
.img-actions { display: flex; gap: 10px; margin-top: 12px; }
.img-btn { background: #2a2a4a; color: #ccccee; border: none; border-radius: 8px;
  padding: 8px 18px; font-size: 13px; cursor: pointer; }
.img-btn:hover { background: #3a3a5a; }
.actions { display: flex; gap: 12px; margin-bottom: 32px; }
.btn-sec { background: #2a2a4a; color: #ccccee; }
.btn-sec:hover { background: #3a3a5a; }
.error { background: #2a1a1a; border: 1px solid #6a2a2a; border-radius: 10px;
  padding: 16px; color: #ff8888; font-size: 14px; display: none; margin-bottom: 20px; }
@media print {
  body { background: #fff; color: #000; }
  .header { background: #1a1a2e; }
  .key-row, .actions, .existing, .input-section { display: none; }
  #output { display: block !important; }
  .card, .hero { border: 1px solid #ddd; background: #f9f9f9; }
  .card-title { color: #5544cc; }
}
</style>
</head>
<body>
<div class="header">
  <h1>Sintegra <span>Story Engine</span></h1>
  <p>Genere l'identite narrative complete d'un projet en 30 secondes &middot; Propulse par NVIDIA NIM</p>
</div>
<div class="container">
  <div class="existing">
    <h3>Projets existants dans le studio</h3>
    <div class="project-tags">
      <span class="tag">Sintegra Institute &mdash; education</span>
      <span class="tag">LinkHR &mdash; talents &amp; opportunites</span>
      <span class="tag">Residia &mdash; installation en France</span>
      <span class="tag">Big Tech Africa &mdash; innovation africaine</span>
    </div>
  </div>
  <div class="input-section">
    <label>Description du nouveau projet</label>
    <textarea id="desc" placeholder="Ex: Sintegra Pay est une solution de paiement mobile pensee pour les entrepreneurs africains de la diaspora qui veulent envoyer de l'argent et payer leurs fournisseurs en Afrique sans frais bancaires excessifs..."></textarea>
  </div>
  <div class="key-row">
    <input type="hidden" id="apikey" value="" />
    <button id="btn" onclick="generate()" style="width:100%">Generer l'identite &#10022;</button>
  </div>
  <div class="error" id="error"></div>
  <div class="loader" id="loader"><div class="spinner"></div><p>Generation en cours...</p></div>
  <div id="output">
    <div class="actions">
      <button class="btn-sec" onclick="window.print()">Imprimer / PDF</button>
      <button class="btn-sec" onclick="copyJSON()">Copier JSON</button>
    </div>
    <div class="hero">
      <h2 id="o-nom"></h2>
      <div class="tagline" id="o-tagline"></div>
    </div>
    <div class="img-section">
      <div class="img-label">Visuel IA genere (FLUX)</div>
      <div class="img-wrap">
        <div class="img-skeleton" id="img-skeleton"></div>
        <img id="o-image" src="" alt="" style="display:none" />
      </div>
      <div class="img-prompt-box" id="o-img-prompt"></div>
      <div class="img-actions">
        <button class="img-btn" onclick="downloadImg()">Telecharger l'image</button>
        <button class="img-btn" onclick="regenImg()">Regenerer</button>
      </div>
    </div>
    <div class="two-col">
      <div class="card"><div class="card-title">Vision</div><p class="story-text" id="o-vision"></p></div>
      <div class="card"><div class="card-title">Mission</div><p class="story-text" id="o-mission"></p></div>
    </div>
    <div class="card"><div class="card-title">Histoire de marque</div><p class="story-text" id="o-histoire"></p></div>
    <div class="two-col">
      <div class="card"><div class="card-title">Slogans</div><ul class="slogan-list" id="o-slogans"></ul></div>
      <div class="card"><div class="card-title">Ton de communication</div><div class="ton-box" id="o-ton"></div></div>
    </div>
    <div class="card"><div class="card-title">Personas cibles</div><div id="o-personas"></div></div>
    <div class="card"><div class="card-title">Idees de campagnes</div><ul class="campagne-list" id="o-campagnes"></ul></div>
    <div class="two-col">
      <div class="card"><div class="card-title">Mots-cles visuels</div><div class="visual-tags" id="o-visuels"></div></div>
      <div class="card"><div class="card-title">Differenciateur vs projets existants</div><div class="diff-box" id="o-diff"></div></div>
    </div>
  </div>
</div>
<script>
var lastJSON = null;
function generate() {
  var desc = document.getElementById('desc').value.trim();
  var key  = document.getElementById('apikey').value.trim();
  if (!desc) { showError('Ecris une description de projet.'); return; }
  if (!key)  { showError('Entre ta cle NVIDIA NIM (nvapi-...).'); return; }
  document.getElementById('btn').disabled = true;
  document.getElementById('loader').style.display = 'block';
  document.getElementById('output').style.display = 'none';
  document.getElementById('error').style.display = 'none';
  fetch('/generate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({description: desc, key: key})
  })
  .then(function(r) { return r.json().then(function(d) { return {ok: r.ok, d: d}; }); })
  .then(function(res) {
    if (!res.ok) throw new Error(res.d.error || 'Erreur serveur');
    displayResult(res.d);
  })
  .catch(function(e) { showError('Erreur : ' + e.message); })
  .finally(function() {
    document.getElementById('btn').disabled = false;
    document.getElementById('loader').style.display = 'none';
  });
}
function displayResult(d) {
  lastJSON = d;
  document.getElementById('o-nom').textContent    = d.nom || '';
  document.getElementById('o-tagline').textContent = d.tagline || '';
  document.getElementById('o-vision').textContent  = d.vision || '';
  document.getElementById('o-mission').textContent = d.mission || '';
  document.getElementById('o-histoire').textContent = d.histoire_de_marque || '';
  document.getElementById('o-ton').textContent     = d.ton_communication || '';
  document.getElementById('o-diff').textContent    = d.differenciateur || '';
  var sl = document.getElementById('o-slogans');
  sl.innerHTML = (d.slogans||[]).map(function(s){return '<li>'+s+'</li>';}).join('');
  var pe = document.getElementById('o-personas');
  pe.innerHTML = (d.personas||[]).map(function(p){
    return '<div class="persona"><div class="persona-name">'+p.nom+' &middot; '+p.age+'</div>'
      +'<div class="persona-row">Profil : <span>'+p.profil+'</span></div>'
      +'<div class="persona-row">Douleur : <span>'+p.douleur+'</span></div>'
      +'<div class="persona-row">Desir : <span>'+p.desir+'</span></div></div>';
  }).join('');
  var ca = document.getElementById('o-campagnes');
  ca.innerHTML = (d.campagnes||[]).map(function(c){return '<li>'+c+'</li>';}).join('');
  var vi = document.getElementById('o-visuels');
  vi.innerHTML = (d.mots_cles_visuels||[]).map(function(v){return '<span class="vtag">'+v+'</span>';}).join('');
  // Image
  if (d.image_url) {
    document.getElementById('img-skeleton').style.display = 'block';
    document.getElementById('o-img-prompt').textContent = d.image_prompt || '';
    var img = document.getElementById('o-image');
    img.style.display = 'none';
    img.onload = function() {
      document.getElementById('img-skeleton').style.display = 'none';
      img.style.display = 'block';
    };
    img.onerror = function() {
      document.getElementById('img-skeleton').style.display = 'none';
      document.getElementById('o-img-prompt').textContent = 'Image non disponible — reessaie dans 30s';
    };
    img.src = d.image_url;
  }
  document.getElementById('output').style.display = 'block';
  document.getElementById('output').scrollIntoView({behavior:'smooth'});
}
function downloadImg() {
  var img = document.getElementById('o-image');
  if (!img.src) return;
  var a = document.createElement('a');
  a.href = img.src;
  a.download = (lastJSON && lastJSON.nom ? lastJSON.nom : 'sintegra') + '-visual.jpg';
  a.target = '_blank';
  a.click();
}
function regenImg() {
  if (!lastJSON || !lastJSON.image_url) return;
  var seed = Math.floor(Math.random() * 99999);
  var newUrl = lastJSON.image_url.replace(/&seed=\d+/, '') + '&seed=' + seed;
  document.getElementById('img-skeleton').style.display = 'block';
  var img = document.getElementById('o-image');
  img.style.display = 'none';
  img.onload = function() {
    document.getElementById('img-skeleton').style.display = 'none';
    img.style.display = 'block';
  };
  img.src = newUrl;
}
function showError(msg) {
  var el = document.getElementById('error');
  el.textContent = msg;
  el.style.display = 'block';
}
function copyJSON() {
  navigator.clipboard.writeText(JSON.stringify(lastJSON, null, 2));
}
</script>
</body>
</html>"""


def build_prompt(description):
    return (
        "Projets existants dans le studio :\n"
        + EXISTING
        + "\n\nNouveau projet a positionner :\n"
        + description
        + "\n\nGenere UNIQUEMENT un objet JSON valide avec cette structure :\n"
        + JSON_SCHEMA
    )


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))

    def do_POST(self):
        if urlparse(self.path).path != "/generate":
            self._json(404, {"error": "Not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        description = body.get("description", "").strip()
        key = body.get("key", "").strip() or NVIDIA_API_KEY

        if not key:
            self._json(400, {"error": "Cle NVIDIA manquante."})
            return
        if not description:
            self._json(400, {"error": "Description vide."})
            return

        payload = json.dumps({
            "model": "meta/llama-3.1-8b-instruct",
            "max_tokens": 1200,
            "temperature": 0.7,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": build_prompt(description)}
            ]
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": "Bearer " + key,
                "Content-Type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
            raw = result["choices"][0]["message"]["content"].strip()
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            parsed = json.loads(raw.strip())
            # Build image prompt from narrative output
            keywords = ", ".join(parsed.get("mots_cles_visuels", []))
            nom = parsed.get("nom", "project")
            tagline = parsed.get("tagline", "")
            img_prompt = (
                "chibi anime illustration, " + nom + " brand, "
                "african professional superhero characters, diverse team, "
                + keywords + ", "
                "colorful vibrant background, Africa and France connected, "
                "floating documents and symbols, Eiffel Tower silhouette, "
                "globe at base, vibrant blue yellow purple palette, "
                "clean white outlines, professional cartoon style, 4k"
            )
            parsed["image_url"] = (
                "https://image.pollinations.ai/prompt/"
                + quote(img_prompt)
                + "?width=1024&height=1024&model=flux&nologo=true"
            )
            parsed["image_prompt"] = img_prompt
            self._json(200, parsed)
        except urllib.error.HTTPError as e:
            self._json(e.code, {"error": e.read().decode()})
        except Exception as e:
            self._json(500, {"error": str(e)})

    def _json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("[story-engine] " + fmt % args)


if __name__ == "__main__":
    if not NVIDIA_API_KEY:
        print("Conseil : exporte ta cle pour ne pas la retaper :")
        print("  export NVIDIA_API_KEY=nvapi-...\n")
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print("Story Engine -> http://localhost:" + str(PORT))
    print("Ctrl+C pour arreter.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArrete.")
