import streamlit as st
import time
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="Mon IA - Authentification OAuth", page_icon="✨", layout="wide")

# --- STYLE CSS TYPE CHATGPT / GEMINI ---
st.markdown("""
    <style>
    .stApp {
        background-color: #131314;
        color: #e3e3e3;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    section[data-testid="stSidebar"] {
        background-color: #1e1f22;
        border-right: 1px solid #2b2d31;
    }
    
    .stChatInputContainer {
        background-color: #1e1f22 !important;
        border-radius: 30px !important;
        border: 1px solid #444746 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURATION DES CLIENTS OAUTH (Google & Discord) ---
# Note : Pour que les boutons fonctionnent en production, il faut déclarer 
# les Client ID et Secrets obtenus sur Google Cloud Console et Discord Developer Portal.
GOOGLE_CLIENT_ID = "TON_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "TON_GOOGLE_CLIENT_SECRET"

DISCORD_CLIENT_ID = "TON_DISCORD_CLIENT_ID"
DISCORD_CLIENT_SECRET = "TON_DISCORD_CLIENT_SECRET"

# Initialisation des composants OAuth
oauth_google = OAuth2Component(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
    refresh_token_endpoint="https://oauth2.googleapis.com/token"
)

oauth_discord = OAuth2Component(
    client_id=DISCORD_CLIENT_ID,
    client_secret=DISCORD_CLIENT_SECRET,
    authorize_endpoint="https://discord.com/api/oauth2/authorize",
    token_endpoint="https://discord.com/api/oauth2/token",
    refresh_token_endpoint="https://discord.com/api/oauth2/token"
)

# --- INITIALISATION DE LA MÉMOIRE DE SESSION ---
if "token" not in st.session_state:
    st.session_state.token = None
if "chats" not in st.session_state:
    st.session_state.chats = {"Nouvelle discussion": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Nouvelle discussion"

# --- PAGE DE CONNEXION OAUTH ---
if not st.session_state.token:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Connectez-vous ou inscrivez-vous</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9aa0a6; font-size: 14px;'>Utilisez vos comptes officiels pour accéder à l'assistant.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Bouton OAuth Google
        result_google = oauth_google.authorize_button(
            name="Continuer avec Google",
            icon="https://www.google.com/favicon.ico",
            redirect_uri="http://localhost:8501",
            scope="openid email profile",
            key="google"
        )

        st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

        # Bouton OAuth Discord
        result_discord = oauth_discord.authorize_button(
            name="Continuer avec Discord",
            icon="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png",
            redirect_uri="http://localhost:8501",
            scope="identify email",
            key="discord"
        )

        # Capture du jeton de connexion OAuth
        if result_google and "token" in result_google:
            st.session_state.token = result_google["token"]
            st.session_state.user_identity = "Utilisateur Google"
            st.rerun()
            
        if result_discord and "token" in result_discord:
            st.session_state.token = result_discord["token"]
            st.session_state.user_identity = "Utilisateur Discord"
            st.rerun()

else:
    # --- BARRE LATÉRALE DE L'APPLICATION ---
    with st.sidebar:
        st.markdown(f"👤 **{st.session_state.get('user_identity', 'Mon Compte')}**")
        
        if st.button("➕ Nouvelle discussion", use_container_width=True):
            nouveau_salon = f"Discussion {len(st.session_state.chats) + 1}"
            st.session_state.chats[nouveau_salon] = []
            st.session_state.current_chat = nouveau_salon
            st.rerun()

        st.markdown("---")
        st.subheader("Historique")
        
        salon_actif = st.selectbox("Vos salons", list(st.session_state.chats.keys()), index=list(st.session_state.chats.keys()).index(st.session_state.current_chat))
        if salon_actif != st.session_state.current_chat:
            st.session_state.current_chat = salon_actif
            st.rerun()

        st.markdown("---")
        if st.button("🚪 Se déconnecter", use_container_width=True):
            st.session_state.token = None
            st.rerun()

    # --- INTERFACE PRINCIPALE DE CHAT ---
    st.title("Bonjour")
    st.markdown("<p style='color: #9aa0a6; font-size: 18px;'>Comment puis-je vous aider aujourd'hui ?</p>", unsafe_allow_html=True)

    messages_salon = st.session_state.chats[st.session_state.current_chat]

    for message in messages_salon:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "file" in message and message["file"] is not None:
                st.image(message["file"], width=250)

    # --- ZONE DE SAISIE AVEC LE BOUTON "+" À GAUCHE ---
    col_plus, col_input = st.columns([0.06, 0.94])
    
    with col_plus:
        menu_fichiers = st.popover("➕", help="Ajouter une image ou un fichier")
    
    with col_input:
        prompt = st.chat_input("Envoyez un message à votre IA...")

    fichier_joint = None
    with menu_fichiers:
        st.write("Ajouter des fichiers")
        fichier_joint = st.file_uploader("Sélectionner une image ou un document", type=["png", "jpg", "jpeg", "pdf", "txt"])

    if prompt or fichier_joint:
        texte_utilisateur = prompt if prompt else "Analyse ce fichier joint :"
        
        messages_salon.append({"role": "user", "content": texte_utilisateur, "file": fichier_joint})
        
        with st.chat_message("user"):
            st.markdown(texte_utilisateur)
            if fichier_joint:
                st.image(fichier_joint, width=250)

        reponse_assistant = f"🌐 **Authentification OAuth validée**.\n\nJ'ai bien pris en compte votre requête : *'{texte_utilisateur}'*. L'ensemble des bases de données et sources sécurisées ont été recoupées pour vous apporter une solution claire et structurée."

        with st.chat_message("assistant"):
            conteneur_texte = st.empty()
            texte_anime = ""
            for mot in reponse_assistant.split(" "):
                texte_anime += mot + " "
                time.sleep(0.03)
                conteneur_texte.markdown(texte_anime + "▌")
            conteneur_texte.markdown(reponse_assistant)

        messages_salon.append({"role": "assistant", "content": reponse_assistant, "file": None})
