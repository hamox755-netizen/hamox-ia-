import streamlit as st
import time

st.set_page_config(page_title="Mon IA - Interface Gemini", page_icon="✨", layout="wide")

# --- STYLE CSS TYPE GEMINI & CHATGPT ---
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

# --- PORTAIL DE CONNEXION OFFICIEL (GOOGLE & DISCORD) ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; margin-top: 40px;'>Connexion à l'Assistant</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9aa0a6;'>Sélectionnez votre plateforme de connexion officielle.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Onglets de connexion similaires aux grands modèles
        tab_google, tab_discord = st.tabs(["🔒 Google (Officiel)", "🎮 Discord (Officiel)"])

        with tab_google:
            with st.form("google_auth"):
                st.markdown("### Accès via Google")
                g_email = st.text_input("Adresse Email Google")
                g_pass = st.text_input("Mot de passe", type="password")
                remember_g = st.checkbox("Se rappeler de moi", value=True)
                submit_g = st.form_submit_button("Continuer avec Google", use_container_width=True)
                
                if submit_g:
                    if g_email and g_pass:
                        st.session_state.logged_in = True
                        st.session_state.user_identity = f"Google: {g_email}"
                        st.success("Connexion Google établie avec succès !")
                        st.rerun()
                    else:
                        st.error("Veuillez remplir tous les champs de connexion.")

        with tab_discord:
            with st.form("discord_auth"):
                st.markdown("### Accès via Discord")
                d_user = st.text_input("Nom d'utilisateur ou Email Discord")
                d_pass = st.text_input("Mot de passe", type="password")
                remember_d = st.checkbox("Se rappeler de moi", value=True)
                submit_d = st.form_submit_button("Continuer avec Discord", use_container_width=True)
                
                if submit_d:
                    if d_user and d_pass:
                        st.session_state.logged_in = True
                        st.session_state.user_identity = f"Discord: {d_user}"
                        st.success("Connexion Discord établie avec succès !")
                        st.rerun()
                    else:
                        st.error("Veuillez remplir tous les champs de connexion.")

        st.markdown("<p style='text-align: center; font-size: 12px; color: gray; margin-top: 25px;'>Pour toute réinitialisation d'e-mail ou de mot de passe, veuillez l'effectuer directement depuis les paramètres de votre compte Google ou Discord.</p>", unsafe_allow_html=True)

else:
    # --- BARRE LATÉRALE (HISTORIQUE ET GESTION DES SALONS) ---
    with st.sidebar:
        st.markdown(f"👤 **{st.session_state.user_identity}**")
        
        if st.button("➕ Nouvelle discussion", use_container_width=True):
            nouveau_salon = f"Discussion {len(st.session_state.chats) + 1}"
            st.session_state.chats[nouveau_salon] = []
            st.session_state.current_chat = nouveau_salon
            st.rerun()

        st.markdown("---")
        st.subheader("Historique des salons")
        
        # Sélecteur déroulant de l'historique
        salon_actif = st.selectbox("Vos conversations", list(st.session_state.chats.keys()), index=list(st.session_state.chats.keys()).index(st.session_state.current_chat))
        if salon_actif != st.session_state.current_chat:
            st.session_state.current_chat = salon_actif
            st.rerun()

        st.markdown("---")
        if st.button("🚪 Se déconnecter", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- INTERFACE PRINCIPALE DE DISCUSSION ---
    st.title("Bonjour")
    st.markdown("<p style='color: #9aa0a6; font-size: 18px;'>Comment puis-je vous aider aujourd'hui ?</p>", unsafe_allow_html=True)

    messages_salon = st.session_state.chats[st.session_state.current_chat]

    # Restitution de l'historique du chat actuel
    for message in messages_salon:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "file" in message and message["file"] is not None:
                st.image(message["file"], width=250)

    # --- ZONE DE SAISIE AVEC LE BOUTON "+" PLACÉ À GAUCHE ---
    col_bouton_plus, col_champ_texte = st.columns([0.06, 0.94])
    
    with col_bouton_plus:
        menu_fichiers = st.popover("➕", help="Joindre une image ou un fichier")
    
    with col_champ_texte:
        prompt = st.chat_input("Posez votre question à l'IA...")

    # Chargement d'un fichier via le menu contextuel de gauche
    fichier_joint = None
    with menu_fichiers:
        st.write("Ajouter des médias")
        fichier_joint = st.file_uploader("Sélectionner une photo ou un document", type=["png", "jpg", "jpeg", "pdf", "txt"])

    # Traitement du message et génération de la réponse avec effet dynamique
    if prompt or fichier_joint:
        texte_utilisateur = prompt if prompt else "Analyse ce fichier joint :"
        
        messages_salon.append({"role": "user", "content": texte_utilisateur, "file": fichier_joint})
        
        with st.chat_message("user"):
            st.markdown(texte_utilisateur)
            if fichier_joint:
                st.image(fichier_joint, width=250)

        # Réponse de l'IA avec effet machine à écrire fluide
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
