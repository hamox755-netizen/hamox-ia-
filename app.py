import streamlit as st
import time

st.set_page_config(page_title="Assistant IA - Mode Pro", page_icon="✨", layout="wide")

# --- DESIGN GUI STYLE CHATGPT / GEMINI ---
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

# --- INITIALISATION DE LA SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_identity" not in st.session_state:
    st.session_state.user_identity = ""
if "chats" not in st.session_state:
    st.session_state.chats = {"Nouvelle discussion": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Nouvelle discussion"

# --- VRAI PORTAIL DE CONNEXION TYPE PLATEFORME PRO ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>Bienvenue</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9aa0a6;'>Connectez-vous pour accéder à votre espace IA.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Choix de la méthode de connexion sous forme d'onglets propres
        auth_tab_google, auth_tab_discord = st.tabs(["🔒 Connexion Google", "🎮 Connexion Discord"])

        with auth_tab_google:
            with st.form("form_google"):
                st.markdown("### Compte Google")
                g_email = st.text_input("Adresse Email Google")
                g_pass = st.text_input("Mot de passe", type="password")
                submit_g = st.form_submit_button("Se connecter avec Google", use_container_width=True)
                
                if submit_g:
                    if g_email and g_pass:
                        st.session_state.logged_in = True
                        st.session_state.user_identity = f"Google: {g_email}"
                        st.success("Connexion Google réussie !")
                        st.rerun()
                    else:
                        st.error("Veuillez remplir tous les champs.")

        with auth_tab_discord:
            with st.form("form_discord"):
                st.markdown("### Compte Discord")
                d_user = st.text_input("Nom d'utilisateur ou Email Discord")
                d_pass = st.text_input("Mot de passe", type="password")
                submit_d = st.form_submit_button("Se connecter avec Discord", use_container_width=True)
                
                if submit_d:
                    if d_user and d_pass:
                        st.session_state.logged_in = True
                        st.session_state.user_identity = f"Discord: {d_user}"
                        st.success("Connexion Discord réussie !")
                        st.rerun()
                    else:
                        st.error("Veuillez remplir tous les champs.")

        st.markdown("<p style='text-align: center; font-size: 12px; color: gray; margin-top: 20px;'>En cas d'oubli, la réinitialisation de votre mot de passe se fait directement depuis les portails officiels respectifs.</p>", unsafe_allow_html=True)

else:
    # --- BARRE LATÉRALE TYPE CHATGPT / GEMINI ---
    with st.sidebar:
        st.markdown(f"👤 **{st.session_state.user_identity}**")
        
        if st.button("➕ Nouvelle discussion", use_container_width=True):
            chat_name = f"Discussion {len(st.session_state.chats) + 1}"
            st.session_state.chats[chat_name] = []
            st.session_state.current_chat = chat_name
            st.rerun()

        st.markdown("---")
        st.subheader("Historique des chats")
        
        # Liste déroulante ou sélecteur des salons
        choix_chat = st.selectbox("Vos salons", list(st.session_state.chats.keys()), index=list(st.session_state.chats.keys()).index(st.session_state.current_chat))
        if choix_chat != st.session_state.current_chat:
            st.session_state.current_chat = choix_chat
            st.rerun()

        st.markdown("---")
        if st.button("🚪 Se déconnecter", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- INTERFACE PRINCIPALE DE DISCUSSION ---
    st.title("Bonjour")
    st.markdown("<p style='color: #9aa0a6; font-size: 18px;'>Comment puis-je vous aider aujourd'hui ?</p>", unsafe_allow_html=True)

    messages_actuels = st.session_state.chats[st.session_state.current_chat]

    # Affichage de l'historique de la conversation en cours
    for msg in messages_actuels:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "file" in msg and msg["file"] is not None:
                st.image(msg["file"], width=250)

    # --- ZONE DE SAISIE AVEC LE BOUTON "+" À GAUCHE POUR LES FICHIERS ---
    col_plus, col_input = st.columns([0.06, 0.94])
    
    with col_plus:
        # Menu déroulant popover positionné à gauche de l'input
        ajouter_fichier = st.popover("➕", help="Joindre une image ou un fichier")
    
    with col_input:
        prompt = st.chat_input("Envoyez un message à votre IA...")

    uploaded_file = None
    with ajouter_fichier:
        st.write("Importer un fichier")
        uploaded_file = st.file_uploader("Sélectionner une photo ou un document", type=["png", "jpg", "jpeg", "pdf", "txt"])

    # Traitement du message utilisateur et de la réponse de l'IA
    if prompt or uploaded_file:
        contenu_prompt = prompt if prompt else "Analyse ce fichier joint :"
        
        messages_actuels.append({"role": "user", "content": contenu_prompt, "file": uploaded_file})
        
        with st.chat_message("user"):
            st.markdown(contenu_prompt)
            if uploaded_file:
                st.image(uploaded_file, width=250)

        # Réponse simulée de l'IA avec un effet "machine à écrire" stylé (le texte apparaît progressivement)
        reponse_bot = f"🌐 **Recherche globale et traitement validé**.\n\nJ'ai bien analysé votre demande : *'{contenu_prompt}'*. Toutes les données sécurisées et sources web ont été recoupées pour vous apporter une solution claire et précise."

        with st.chat_message("assistant"):
            placeholder = st.empty()
            texte_anime = ""
            for mot in reponse_bot.split(" "):
                texte_anime += mot + " "
                time.sleep(0.03)  # Vitesse d'écriture fluide
                placeholder.markdown(texte_anime + "▌")
            placeholder.markdown(reponse_bot)

        messages_actuels.append({"role": "assistant", "content": reponse_bot, "file": None})
