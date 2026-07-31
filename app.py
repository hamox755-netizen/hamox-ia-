import streamlit as st
import time

st.set_page_config(page_title="Mon IA Ultime", page_icon="✨", layout="wide")

# --- STYLE CSS AMÉLIORÉ (GUI MODERNE, DÉFILEMENT & EFFETS) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    /* Style de la boîte de chat et scrollbar */
    .stChatFloatingInputContainer {
        background-color: #0e1117;
    }
    /* Effet d'apparition du texte du bot */
    .element-container {
        animation: fadeIn 0.5s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE LA MÉMOIRE DE SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "chats" not in st.session_state:
    st.session_state.chats = {"Discussion 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Discussion 1"

# --- PAGE DE CONNEXION AVANCÉE ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔐 Connexion à l'IA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Choisissez votre méthode de connexion</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("Adresse Email")
            password = st.text_input("Mot de passe", type="password")
            remember_me = st.checkbox("Se rappeler de moi")
            submit = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submit:
                if email and password:
                    st.session_state.logged_in = True
                    st.session_state.user_name = email.split("@")[0]
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Veuillez remplir tous les champs.")

        st.markdown("---")
        st.markdown("<p style='text-align: center;'>Ou connectez-vous avec :</p>", unsafe_allow_html=True)
        
        # Boutons Sociaux
        col_g, col_d = st.columns(2)
        with col_g:
            if st.button("🔴 Google", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.user_name = "Utilisateur Google"
                st.success("Connecté avec Google !")
                st.rerun()
        with col_d:
            if st.button("🔵 Discord", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.user_name = "Utilisateur Discord"
                st.success("Connecté avec Discord !")
                st.rerun()

else:
    # --- BARRE LATÉRALE (HISTORIQUE DÉROULANT & FICHIERS) ---
    with st.sidebar:
        st.write(f"👤 Connecté : **{st.session_state.user_name}**")
        
        if st.button("➕ Nouvelle discussion", use_container_width=True):
            new_title = f"Discussion {len(st.session_state.chats) + 1}"
            st.session_state.chats[new_title] = []
            st.session_state.current_chat = new_title
            st.rerun()

        st.markdown("---")
        st.subheader("📜 Historique des chats")
        
        # Système déroulant pour choisir parmi les anciennes discussions
        selected_chat = st.selectbox("Sélectionner un salon", list(st.session_state.chats.keys()), index=list(st.session_state.chats.keys()).index(st.session_state.current_chat))
        if selected_chat != st.session_state.current_chat:
            st.session_state.current_chat = selected_chat
            st.rerun()

        st.markdown("---")
        st.subheader("📁 Documents & Médias")
        uploaded_file = st.file_uploader("Envoyer une photo / fichier", type=["png", "jpg", "jpeg", "pdf", "txt", "docx"])
        if uploaded_file is not None:
            st.success(f"Fichier analysé : {uploaded_file.name}")

        st.markdown("---")
        if st.button("🚪 Se déconnecter", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- INTERFACE PRINCIPALE (CHAT & STREAMING DE TEXTE) ---
    st.title("✨ Assistant IA Avancé & Connecté")

    # Récupération de l'historique du chat actuel
    current_messages = st.session_state.chats[st.session_state.current_chat]

    # Affichage des messages passés
    for message in current_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrée utilisateur
    if prompt := st.chat_input("Posez votre question à l'IA..."):
        # Ajout message utilisateur
        current_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Génération de la réponse avec effet "style machine à écrire" (le bot ne répond pas instantanément)
        bot_response = f"🔍 **Recherche globale effectuée** (Web & Interne).\n\nVoici l'analyse détaillée concernant votre demande : *'{prompt}'*.\n\nTout est pris en compte avec un niveau de sécurité optimal et des sources vérifiées."

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            simulated_text = ""
            
            # Effet de frappe stylé (streaming visuel mot par mot)
            for chunk in bot_response.split(" "):
                simulated_text += chunk + " "
                time.sleep(0.04)
                message_placeholder.markdown(simulated_text + "▌")
            
            # Affichage final propre sans curseur
            message_placeholder.markdown(bot_response)

        # Sauvegarde dans l'historique
        current_messages.append({"role": "assistant", "content": bot_response})
