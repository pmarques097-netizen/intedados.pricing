"""INTEDADOS PRICING — tela de entrada única.
Faz o login e leva cada usuário ao Pricing da rede dele (cada cliente roda separado, com os seus dados).
Local: http://localhost:8510   ·   Nuvem: app principal do repositório intedados.pricing
"""
import base64
import hashlib
import hmac
import json
import time
from pathlib import Path

import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parent
NUVEM = "/mount/src" in str(Path.cwd())
MASTERS = {"diretoria", "master", "administrador", "admin"}

st.set_page_config(page_title="intedados · Pricing", layout="centered",
                   page_icon=next((str(p) for p in RAIZ.glob("clientes/*/assets_marca/icone_intedados.png")), None))


@st.cache_data(ttl=60, show_spinner=False)
def clientes():
    try:
        return json.loads((RAIZ / "clientes.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def url_cliente(info):
    return str((info.get("nuvem") if NUVEM else None) or info.get("url") or "")


@st.cache_data(ttl=60, show_spinner=False)
def usuarios(cod):
    try:
        b = pd.read_csv(RAIZ / "clientes" / cod / "USUARIOS_INTEDADOS.csv", sep=";", encoding="utf-8-sig", dtype=str).fillna("")
        b["Usuario"] = b["Usuario"].astype(str).str.strip().str.lower()
        return b
    except Exception:
        return pd.DataFrame(columns=["Usuario", "Nome", "Perfil", "Senha_Hash", "Ativo"])


def base_chave():
    try:
        b = str(st.secrets.get("intedados_chave", "")).strip()
        if b:
            return b
    except Exception:
        pass
    f = RAIZ / "app" / ".chave_sessao"
    try:
        if not f.exists() and not NUVEM:
            import secrets
            f.write_text(secrets.token_hex(32), encoding="utf-8")
        return f.read_text(encoding="utf-8").strip() if f.exists() else ""
    except Exception:
        return ""


def passe(usuario, destino, senha_hash, validade=1800):
    chave = (base_chave() + "|" + senha_hash).encode()
    msg = f"{usuario}|{destino.upper()}|{int(time.time()) + validade}"
    sig = hmac.new(chave, msg.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(msg.encode()).decode().rstrip("=") + "." + sig


def acessos(usuario, senha):
    """Clientes em que o usuário está ativo e com esta senha: [(cod, info, nome, hash, admin)]."""
    h = hashlib.sha256(str(senha).encode()).hexdigest()
    r = []
    for cod, info in clientes().items():
        if NUVEM and not (info.get("nuvem") or info.get("na_nuvem")):
            continue
        b = usuarios(cod)
        l = b[b["Usuario"].eq(usuario)]
        if l.empty:
            continue
        l = l.iloc[0]
        if str(l.get("Ativo", "Sim")).strip().lower() == "não" or str(l.get("Senha_Hash", "")) != h:
            continue
        r.append((cod, info, l.get("Nome", usuario), h, str(l.get("Perfil", "")).strip().lower() in MASTERS))
    return r


def ir(url):
    """Abre o Pricing da rede na mesma aba (com botão de reserva)."""
    import streamlit.components.v1 as components
    components.html(f"""<script>
      (function(){{ try {{ const a = window.parent.document.createElement('a'); a.href = {json.dumps(url)}; a.target = '_self';
        window.parent.document.body.appendChild(a); a.click(); }} catch(e) {{ window.top.location.href = {json.dumps(url)}; }} }})();
    </script>""", height=0)


st.markdown("""<style>
[data-testid="stHeader"]{height:0;background:transparent}
[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none}
.stApp{background:radial-gradient(1200px 600px at 50% -10%,#16305a 0%,#0a1628 55%,#070f1d 100%)}
.block-container{padding-top:6vh;max-width:520px}
.ip-marca{text-align:center;margin-bottom:14px}
.ip-marca h1{font-size:1.9rem;margin:6px 0 2px 0;color:#eaf1ff;letter-spacing:-.01em}
.ip-marca h1 b{background:linear-gradient(90deg,#4f8cff,#9b6bff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.ip-marca p{color:#9fb3cc;margin:0}
div[data-testid="stForm"]{border:1px solid rgba(91,151,211,.30);border-radius:16px;background:linear-gradient(180deg,#0b2036,#08192a);
  box-shadow:0 18px 44px rgba(0,0,0,.3);padding:20px 22px}
button[kind="primaryFormSubmit"],button[kind="primary"],a[data-testid="stBaseLinkButton-primary"]{background:linear-gradient(135deg,#2f6bff,#7b4dff)!important;
  border:0!important;color:#fff!important;font-weight:700!important}
.ip-cli{border:1px solid rgba(120,160,220,.25);border-radius:14px;padding:12px 14px;margin:8px 0;background:rgba(255,255,255,.03)}
.ip-cli b{color:#eaf1ff}.ip-cli span{color:#8fa3bd;font-size:.85rem}
</style>""", unsafe_allow_html=True)

logo = next(iter(sorted(RAIZ.glob("clientes/*/assets_marca/logo_intedados_marca.png"))), None)
if logo:
    c = st.columns([1, 1.6, 1])
    c[1].image(str(logo), use_container_width=True)
st.markdown('<div class="ip-marca"><h1>intedados<b>.pricing</b></h1><p>Inteligência de Pricing para Drogarias</p></div>',
            unsafe_allow_html=True)

ss = st.session_state
if not ss.get("ip_acessos"):
    with st.form("ip_login"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        ok = st.form_submit_button("Entrar", type="primary", use_container_width=True)
    if ok:
        usuario = str(u).strip().lower()
        acs = acessos(usuario, p) if usuario and p else []
        if not acs:
            st.error("Usuário ou senha inválidos.")
        else:
            ss["ip_usuario"] = usuario
            ss["ip_acessos"] = [(cod, info, nome, h, adm) for cod, info, nome, h, adm in acs]
            st.rerun()
    st.stop()

usuario, acs = ss["ip_usuario"], ss["ip_acessos"]
links = []
for cod, info, nome, h, adm in acs:
    url = url_cliente(info)
    if url:
        links.append((cod, info, f"{url.rstrip('/')}/?passe={passe(usuario, cod, h)}"))

if not links:
    st.warning("Seu usuário ainda não tem um Pricing publicado. Fale com a Intedados.")
elif len(links) == 1 and not acs[0][4]:
    cod, info, url = links[0]
    st.success(f"Abrindo o {info.get('nome', cod)}…")
    st.link_button(f"Entrar no {info.get('nome', cod)}", url, type="primary", use_container_width=True)
    ir(url)
else:
    st.markdown(f"**Olá, {acs[0][2]}.** Escolha o cliente:")
    for cod, info, url in links:
        st.markdown(f'<div class="ip-cli"><b>{info.get("nome", cod)}</b><br><span>{info.get("rede", "")}'
                    f'{" · " + info["regiao"] if info.get("regiao") else ""}</span></div>', unsafe_allow_html=True)
        st.link_button(f"Entrar no {info.get('nome', cod)}", url, use_container_width=True)
if st.button("Sair", use_container_width=False):
    ss.pop("ip_acessos", None)
    ss.pop("ip_usuario", None)
    st.rerun()
