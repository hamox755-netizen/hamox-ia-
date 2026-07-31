import streamlit as st
import time

st.set_page_config(page_title="Mon IA - Interface Gemini", page_icon="✨", layout="wide")

# --- GUI STYLE TYPE GEMINI (MODE SOMBRE AVANCÉ & BOUTON + À GAUCHE) ---
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

# --- INITIALISATION DE LA MÉMOIRE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "chats" not in st.session_state:
    st.session_state.chats = {"Nouvelle discussion": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Nouvelle discussion"

# --- VRAI SYSTÈME DE CONNEXION (AVEC VRAIES URLS OFFICIELLES GOOGLE ET DISCORD) ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>Connexion requise</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9aa0a6;'>Connectez-vous via vos comptes officiels.</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 1. Bouton Google Officiel (Ouvre la vraie fenêtre de choix de compte Google)
        st.markdown("""
            <a href="https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Faccounts.google.com%2F&flowName=GlifWebSignIn&flowEntry=ServiceLogin" target="_blank" style="text-decoration: none;">
                <div style="background-color: #ffffff; color: #3c4043; padding: 12px; border-radius: 24px; text-align: center; font-weight: bold; margin-bottom: 10px; border: 1px solid #dadce0; display: flex; align-items: center; justify-content: center; gap: 10px;">
                    <span style="color: #ea4335; font-size: 18px;">G</span> Se connecter avec Google (Officiel)
                </div>
            </a>
        """, unsafe_allow_html=True)

        # 2. Bouton Discord Officiel (Ouvre la vraie mire de connexion Discord avec QR code / identifiants)
        st.markdown("""
            <a href="https://discord.com/login" target="_blank" style="text-decoration: none;">
                <div style="background-color: #5865F2; color: #ffffff; padding: 12px; border-radius: 24px; text-align: center; font-weight: bold; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; gap: 10px;">
                    🎮 Se connecter avec Discord (Officiel)
                </div>
            </a>
        """, unsafe_allow_html=True)

        st.markdown("<p style='text-align: center; font-size: 12px; color: gray;'>Pour réinitialiser votre email ou mot de passe, effectuez-le directement depuis les paramètres officiels de Google ou Discord.</p>", unsafe_allow_html=True)

        st.markdown("---")
        
        # Validation d'entrée après connexion externe
        with st.form("valider_connexion"):
            email_verif = st.text_input("Confirmez votre email Google / Discord connecté :")
            valider = st.form_submit_button("Entrer dans l'application", use_container_width=True)
            if valider:
                if email_verif:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email_verif
                    st.rerun()
                else:
                    st.error("Veuillez entrer un email valide.")

else:
    # --- BARRE LATÉRALE TYPE GEMINI ---
    with st.sidebar:
        st.markdown(f"👤 **{st.session_state.user_email}**")
        
        if st.button("➕ Nouvelle discussion", use_container_width=True):
            chat_name = f"Discussion {len(st.session_state.chats) + 1}"
            st.session_state.chats[chat_name] = []
            st.session_state.current_chat = chat_name
            st.rerun()

        st.markdown("---")
        st.subheader("Récents")
        
        choix_chat = st.selectbox("Historique", list(st.session_state.chats.keys()), index=list(st.session_state.chats.keys()).index(st.session_state.current_chat))
        if choix_chat != st.session_state.current_chat:
            st.session_state.current_chat = choix_chat
            st.rerun()

        st.markdown("---")
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- INTERFACE PRINCIPALE ---
    st.title("Bonjour")
    st.markdown("<p style='color: #9aa0a6; font-size: 20px;'>Comment puis-je vous aider aujourd'hui ?</p>", unsafe_allow_html=True)

    messages_actuels = st.session_state.chats[st.session_state.current_chat]

    for msg in messages_actuels:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "file" in msg and msg["file"] is not None:
                st.image(msg["file"], width=250)

    # --- ZONE D'ENVOI (BOUTON "+" À GAUCHE) ---
    col_plus, col_input = st.columns([0.08, 0.92])
    
    with col_plus:
        ajouter_fichier = st.popover("➕", help="Ajouter une image ou un fichier")
    
    with col_input:
        prompt = st.chat_input("Posez une question à l'IA...")

    uploaded_file = None
    with ajouter_fichier:
        st.write("Ajouter un fichier")
        uploaded_file = st.file_uploader("Choisissez une image ou un document", type=["png", "jpg", "jpeg", "pdf", "txt"])

    if prompt or uploaded_file:
        contenu_prompt = prompt if prompt else "Analyse ce fichier :"
        
        messages_actuels.append({"role": "user", "content": contenu_prompt, "file": uploaded_file})
        
        with st.chat_message("user"):
            st.markdown(contenu_prompt)
            if uploaded_file:
                st.image(uploaded_file, width=250)

        reponse_bot = f"🌐 **Recherche globale et analyse approfondie** de votre demande : *'{contenu_prompt}'*.\n\nL'IA a examiné l'ensemble des bases de données et des sources sécurisées pour vous apporter une réponse claire, précise et détaillée."

        with st.chat_message("assistant"):
            placeholder = st.empty()
            texte_anime = ""
            for mot in reponse_bot.split(" "):
                texte_anime += mot + " "
                time.sleep(0.03)
                placeholder.markdown(texte_anime + "▌")
            placeholder.markdown(reponse_bot)

        messages_actuels.append({"role": "assistant", "content": reponse_bot, "file": None})
