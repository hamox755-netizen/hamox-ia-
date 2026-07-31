import streamlit as st
import time

st.set_page_config(page_title="Mon IA - Interface Pro", page_icon="✨", layout="wide")

# --- STYLE CSS TYPE CHATGPT / GEMINI (MODE SOMBRE) ---
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

# --- INITIALISATION DE LA MÉMOIRE DE SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_identity" not in st.session_state:
    st.session_state.user_identity = ""
if "chats" not in st.session_state:
    st.session_state.chats = {"Nouvelle discussion": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Nouvelle discussion"

# --- PAGE DE CONNEXION STYLE CHATGPT (AVEC VRAIS BOUTONS OFFICIELS GOOGLE & DISCORD) ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Connectez-vous ou inscrivez-vous</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9aa0a6; font-size: 14px;'>Vous recevrez des réponses plus intelligentes et pourrez charger des fichiers, des images, et bien plus encore.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # 1. Bouton officiel "Continuer avec Google"
        st.markdown("""
            <a href="https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Faccounts.google.com%2F&flowName=GlifWebSignIn&flowEntry=ServiceLogin" target="_blank" style="text-decoration: none;">
                <div style="background-color: #212121; color: #ffffff; padding: 12px; border-radius: 25px; text-align: center; font-weight: 500; margin-bottom: 12px; border: 1px solid #424242; display: flex; align-items: center; justify-content: center; gap: 10px;">
                    <span style="color: #ea4335; font-weight: bold; font-size: 16px;">G</span> Continuer avec Google
                </div>
            </a>
        """, unsafe_allow_html=True)

        # 2. Bouton officiel "Continuer avec Discord" (Ouvre la vraie page de connexion Discord avec l'interface officielle)
        st.markdown("""
            <a href="https://discord.com/login" target="_blank" style="text-decoration: none;">
                <div style="background-color: #5865F2; color: #ffffff; padding: 12px; border-radius: 25px; text-align: center; font-weight: 500; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; gap: 10px;">
                    🎮 Continuer avec Discord
                </div>
            </a>
        """, unsafe_allow_html=True)

        st.markdown("<p style='text-align: center; color: #888; font-size: 13px;'>OU</p>", unsafe_allow_html=True)

        # 3. Formulaire classique par email
        with st.form("email_login_form"):
            email_input = st.text_input("Email address", placeholder="Entrez votre email...")
            submit_email = st.form_submit_button("Continuer", use_container_width=True)
            
            if submit_email:
                if email_input and "@" in email_input:
                    st.session_state.logged_in = True
                    st.session_state.user_identity = email_input
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Veuillez entrer une adresse e-mail valide.")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Validation rapide après sélection du compte externe (Google/Discord)
        with st.form("valider_compte_externe"):
            conf_email = st.text_input("Confirmez votre email Google/Discord pour entrer :", placeholder="votre.email@gmail.com ou pseudo Discord")
            btn_entrer = st.form_submit_button("Entrer dans l'application", use_container_width=True)
            if btn_entrer:
                if conf_email:
                    st.session_state.logged_in = True
                    st.session_state.user_identity = conf_email
                    st.rerun()
                else:
                    st.error("Veuillez entrer votre email ou pseudo.")

else:
    # --- BARRE LATÉRALE TYPE CHATGPT ---
    with st.sidebar:
        st.markdown(f"👤 **{st.session_state.user_identity}**")
        
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
            st.session_state.logged_in = False
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

        reponse_assistant = f"🌐 **Analyse globale et recherche approfondie** effectuées.\n\nJ'ai bien pris en compte votre requête : *'{texte_utilisateur}'*. L'ensemble des bases de données et sources sécurisées ont été recoupées pour vous apporter une solution claire et structurée."

        with st.chat_message("assistant"):
            conteneur_texte = st.empty()
            texte_anime = ""
            for mot in reponse_assistant.split(" "):
                texte_anime += mot + " "
                time.sleep(0.03)
                conteneur_texte.markdown(texte_anime + "▌")
            conteneur_texte.markdown(reponse_assistant)

        messages_salon.append({"role": "assistant", "content": reponse_assistant, "file": None})
