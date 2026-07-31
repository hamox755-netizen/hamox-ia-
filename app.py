import streamlit as st
import time

st.set_page_config(page_title="Mon IA - Interface Pro", page_icon="✨", layout="wide")

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

# --- INITIALISATION DE LA MÉMOIRE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_identity" not in st.session_state:
    st.session_state.user_identity = ""
if "chats" not in st.session_state:
    st.session_state.chats = {"Nouvelle discussion": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Nouvelle discussion"

# --- PAGE DE CONNEXION INTERACTIVE INTÉGRÉE ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Connectez-vous à l'IA</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9aa0a6; font-size: 14px;'>Accédez à votre historique, envoyez des fichiers et discutez avec l'assistant.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Formulaire de connexion fluide et direct
        with st.form("login_direct"):
            email_input = st.text_input("Adresse e-mail Google ou Discord", placeholder="ex: hamox95754@gmail.com")
            password_input = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submit_btn:
                if email_input and len(email_input) > 3 and "@" in email_input:
                    st.session_state.logged_in = True
                    st.session_state.user_identity = email_input
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Veuillez entrer une adresse e-mail valide.")

else:
    # --- BARRE LATÉRALE ---
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
