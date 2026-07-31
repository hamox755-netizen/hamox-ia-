
"""
============================================================
  MonIA — Site web Streamlit avec connexion Google/Discord
  et assistant IA façon Claude (texte, images, fichiers,
  historique de conversations, réponses en streaming).
============================================================
 
INSTALLATION
------------
    pip install streamlit anthropic requests pillow
 
CONFIGURATION
-------------
Crée un fichier .streamlit/secrets.toml (en local) ou configure les
"Secrets" dans les paramètres de ton app sur Streamlit Community Cloud :
 
    ANTHROPIC_API_KEY = "sk-ant-xxxxxxxx"
 
    [google]
    CLIENT_ID     = "xxxxx.apps.googleusercontent.com"
    CLIENT_SECRET = "xxxxx"
    REDIRECT_URI  = "https://ton-app.streamlit.app"
 
    [discord]
    CLIENT_ID     = "xxxxx"
    CLIENT_SECRET = "xxxxx"
    REDIRECT_URI  = "https://ton-app.streamlit.app"
 
Où créer les identifiants OAuth :
  - Google  : https://console.cloud.google.com/apis/credentials
  - Discord : https://discord.com/developers/applications (onglet OAuth2)
 
⚠️ La REDIRECT_URI doit être EXACTEMENT la même dans le code Google/Discord
   et dans secrets.toml (avec ou sans "/" final, au caractère près).
 
LANCEMENT LOCAL
----------------
    streamlit run app.py
 
DÉPLOIEMENT
-----------
Pousse ce fichier + requirements.txt sur un repo GitHub, puis déploie-le
sur https://share.streamlit.io (Streamlit Community Cloud), ou n'importe
quel hébergeur compatible Streamlit (Render, Railway, etc.).
"""
 
import base64
import uuid
from datetime import datetime
from urllib.parse import urlencode
 
import requests
import streamlit as st
 
try:
    import anthropic
except ImportError:
    anthropic = None
 
 
# ============================================================
# CONFIGURATION GÉNÉRALE
# ============================================================
 
st.set_page_config(
    page_title="MonIA",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# Modèle Claude à utiliser. Vérifie le nom exact disponible sur ton compte
# API ici : https://docs.claude.com/en/docs/about-claude/models
MODEL_NAME = "claude-sonnet-5"
 
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
 
DISCORD_AUTH_URL = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_USERINFO_URL = "https://discord.com/api/users/@me"
 
STYLE_PROMPTS = {
    "Standard": (
        "Tu es un assistant IA utile, clair et bienveillant. Réponds de "
        "façon naturelle et bien structurée."
    ),
    "Concis": (
        "Tu es un assistant IA. Réponds toujours de façon très brève et "
        "directe, sans détails superflus, sauf si on te demande plus de détails."
    ),
    "Créatif": (
        "Tu es un assistant IA imaginatif et expressif. Tu peux prendre des "
        "libertés stylistiques, utiliser des images et des exemples "
        "originaux tout en restant utile et précis."
    ),
}
 
 
# ============================================================
# STYLE CSS
# ============================================================
 
CUSTOM_CSS = """
<style>
#MainMenu, footer, header {visibility: hidden;}
 
.stApp {
    background: radial-gradient(circle at top left, #1c1830 0%, #0e0d18 60%);
}
 
.login-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding-top: 8vh;
}
 
.login-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 48px 40px;
    max-width: 420px;
    width: 100%;
    text-align: center;
    box-shadow: 0 8px 40px rgba(0,0,0,0.35);
}
 
.login-card h1 {
    font-size: 2rem;
    margin-bottom: 4px;
    background: linear-gradient(90deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
 
.login-card p {
    color: #9ca3af;
    margin-bottom: 28px;
}
 
div[data-testid="stSidebar"] {
    background: #14121f;
}
 
.chat-title {
    font-size: 1.3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
 
.conv-btn button {
    text-align: left !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>
"""
 
 
# ============================================================
# OAUTH — GOOGLE
# ============================================================
 
def google_login_url() -> str:
    cfg = st.secrets["google"]
    params = {
        "client_id": cfg["CLIENT_ID"],
        "redirect_uri": cfg["REDIRECT_URI"],
        "response_type": "code",
        "scope": "openid email profile",
        "prompt": "select_account",
        "state": "google",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
 
 
def google_exchange_code(code: str) -> dict:
    cfg = st.secrets["google"]
    data = {
        "code": code,
        "client_id": cfg["CLIENT_ID"],
        "client_secret": cfg["CLIENT_SECRET"],
        "redirect_uri": cfg["REDIRECT_URI"],
        "grant_type": "authorization_code",
    }
    resp = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=15)
    resp.raise_for_status()
    access_token = resp.json()["access_token"]
 
    user = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    ).json()
 
    return {
        "name": user.get("name", "Utilisateur Google"),
        "email": user.get("email"),
        "avatar": user.get("picture"),
        "provider": "Google",
    }
 
 
# ============================================================
# OAUTH — DISCORD
# ============================================================
 
def discord_login_url() -> str:
    cfg = st.secrets["discord"]
    params = {
        "client_id": cfg["CLIENT_ID"],
        "redirect_uri": cfg["REDIRECT_URI"],
        "response_type": "code",
        "scope": "identify email",
        "state": "discord",
    }
    return f"{DISCORD_AUTH_URL}?{urlencode(params)}"
 
 
def discord_exchange_code(code: str) -> dict:
    cfg = st.secrets["discord"]
    data = {
        "client_id": cfg["CLIENT_ID"],
        "client_secret": cfg["CLIENT_SECRET"],
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": cfg["REDIRECT_URI"],
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(DISCORD_TOKEN_URL, data=data, headers=headers, timeout=15)
    resp.raise_for_status()
    access_token = resp.json()["access_token"]
 
    user = requests.get(
        DISCORD_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    ).json()
 
    avatar_url = None
    if user.get("avatar"):
        avatar_url = (
            f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png"
        )
 
    return {
        "name": user.get("username", "Utilisateur Discord"),
        "email": user.get("email"),
        "avatar": avatar_url,
        "provider": "Discord",
    }
 
 
def handle_oauth_redirect():
    """Récupère le code renvoyé par Google/Discord après connexion."""
    query = st.query_params
    if "code" in query and "user" not in st.session_state:
        code = query["code"]
        state = query.get("state", "")
        try:
            if state == "google":
                st.session_state.user = google_exchange_code(code)
            elif state == "discord":
                st.session_state.user = discord_exchange_code(code)
            st.query_params.clear()
            st.rerun()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Erreur lors de la connexion : {exc}")
 
 
# ============================================================
# PAGE DE CONNEXION
# ============================================================
 
def show_login_page():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<h1>✨ MonIA</h1>", unsafe_allow_html=True)
        st.markdown(
            "<p>Connecte-toi pour discuter avec l'assistant</p>",
            unsafe_allow_html=True,
        )
 
        google_ready = "google" in st.secrets
        discord_ready = "discord" in st.secrets
 
        if google_ready:
            st.link_button(
                "🔵  Continuer avec Google",
                google_login_url(),
                use_container_width=True,
            )
        else:
            st.button(
                "🔵  Continuer avec Google (secrets manquants)",
                disabled=True,
                use_container_width=True,
            )
 
        if discord_ready:
            st.link_button(
                "🟣  Continuer avec Discord",
                discord_login_url(),
                use_container_width=True,
            )
        else:
            st.button(
                "🟣  Continuer avec Discord (secrets manquants)",
                disabled=True,
                use_container_width=True,
            )
 
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
 
 
# ============================================================
# GESTION DES CONVERSATIONS
# ============================================================
 
def init_chat_state():
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}
    if "current_conv_id" not in st.session_state:
        new_conversation()
 
 
def new_conversation():
    conv_id = str(uuid.uuid4())
    st.session_state.conversations[conv_id] = {
        "title": "Nouvelle conversation",
        "messages": [],  # [{role, content(str pour affichage), api_content(list pour l'API)}]
        "created_at": datetime.now().isoformat(),
    }
    st.session_state.current_conv_id = conv_id
 
 
def current_conversation():
    return st.session_state.conversations[st.session_state.current_conv_id]
 
 
def delete_conversation(conv_id: str):
    del st.session_state.conversations[conv_id]
    if not st.session_state.conversations:
        new_conversation()
    elif st.session_state.current_conv_id == conv_id:
        st.session_state.current_conv_id = next(iter(st.session_state.conversations))
 
 
# ============================================================
# OUTILS FICHIERS / IMAGES
# ============================================================
 
IMAGE_TYPES = {"png", "jpg", "jpeg", "gif", "webp"}
TEXT_TYPES = {"txt", "md", "csv", "json", "py", "log"}
 
 
def build_attachment_blocks(uploaded_files):
    """Transforme les fichiers uploadés en blocs de contenu pour l'API Claude."""
    blocks = []
    for f in uploaded_files:
        ext = f.name.split(".")[-1].lower()
        raw = f.read()
 
        if ext in IMAGE_TYPES:
            b64 = base64.b64encode(raw).decode()
            media_type = f.type or f"image/{ext}"
            blocks.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": b64,
                    },
                }
            )
        elif ext in TEXT_TYPES:
            try:
                text = raw.decode("utf-8", errors="ignore")
            except Exception:  # noqa: BLE001
                text = "(impossible de lire ce fichier)"
            blocks.append(
                {
                    "type": "text",
                    "text": f"[Contenu du fichier joint « {f.name} »]\n{text[:8000]}",
                }
            )
        else:
            blocks.append(
                {
                    "type": "text",
                    "text": f"[Fichier joint « {f.name} », type non pris en charge pour lecture directe]",
                }
            )
    return blocks
 
 
# ============================================================
# APPEL À L'API CLAUDE (STREAMING)
# ============================================================
 
def get_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("ANTHROPIC_API_KEY manquant dans les secrets.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)
 
 
def stream_assistant_reply(client, api_messages, system_prompt):
    with client.messages.stream(
        model=MODEL_NAME,
        max_tokens=2048,
        system=system_prompt,
        messages=api_messages,
    ) as stream:
        for chunk in stream.text_stream:
            yield chunk
 
 
# ============================================================
# INTERFACE DE CHAT
# ============================================================
 
def show_chat_page():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    init_chat_state()
    user = st.session_state.user
 
    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.markdown("<div class='chat-title'>✨ MonIA</div>", unsafe_allow_html=True)
 
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.write(f"**{user['name']}**")
            st.caption(f"{user['provider']} · {user.get('email') or ''}")
        with col_b:
            if user.get("avatar"):
                st.image(user["avatar"], width=40)
 
        if st.button("🚪 Se déconnecter", use_container_width=True):
            st.session_state.clear()
            st.rerun()
 
        st.divider()
 
        if st.button("➕ Nouvelle conversation", use_container_width=True):
            new_conversation()
            st.rerun()
 
        st.caption("Historique")
        for conv_id, conv in sorted(
            st.session_state.conversations.items(),
            key=lambda kv: kv[1]["created_at"],
            reverse=True,
        ):
            row = st.columns([5, 1])
            label = "💬 " + conv["title"]
            with row[0]:
                st.markdown("<div class='conv-btn'>", unsafe_allow_html=True)
                if st.button(label, key=f"sel_{conv_id}", use_container_width=True):
                    st.session_state.current_conv_id = conv_id
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with row[1]:
                if st.button("🗑️", key=f"del_{conv_id}"):
                    delete_conversation(conv_id)
                    st.rerun()
 
        st.divider()
        st.caption("Réglages")
        style = st.selectbox(
            "Ton des réponses",
            list(STYLE_PROMPTS.keys()),
            key="style_choice",
        )
        uploaded_files = st.file_uploader(
            "📎 Joindre des fichiers / images",
            accept_multiple_files=True,
            key="uploader",
        )
 
    # ---------- ZONE DE CHAT ----------
    conv = current_conversation()
 
    for msg in conv["messages"]:
        avatar = "🧑" if msg["role"] == "user" else "✨"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["display"])
 
    prompt = st.chat_input("Écris ton message...")
 
    if prompt:
        attachment_blocks = (
            build_attachment_blocks(uploaded_files) if uploaded_files else []
        )
 
        display_text = prompt
        if uploaded_files:
            display_text += "\n\n" + ", ".join(f"📎 {f.name}" for f in uploaded_files)
 
        api_content = attachment_blocks + [{"type": "text", "text": prompt}]
 
        conv["messages"].append(
            {"role": "user", "display": display_text, "api_content": api_content}
        )
        if conv["title"] == "Nouvelle conversation":
            conv["title"] = prompt[:40] + ("…" if len(prompt) > 40 else "")
 
        with st.chat_message("user", avatar="🧑"):
            st.markdown(display_text)
 
        api_messages = [
            {"role": m["role"], "content": m["api_content"]} for m in conv["messages"]
        ]
 
        client = get_client()
        system_prompt = STYLE_PROMPTS[style]
 
        with st.chat_message("assistant", avatar="✨"):
            full_reply = st.write_stream(
                stream_assistant_reply(client, api_messages, system_prompt)
            )
 
        conv["messages"].append(
            {
                "role": "assistant",
                "display": full_reply,
                "api_content": [{"type": "text", "text": full_reply}],
            }
        )
        st.rerun()
 
 
# ============================================================
# POINT D'ENTRÉE
# ============================================================
 
def main():
    handle_oauth_redirect()
    if "user" in st.session_state:
        show_chat_page()
    else:
        show_login_page()
 
 
if __name__ == "__main__":
    main()
 
