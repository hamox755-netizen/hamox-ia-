import streamlit as st

st.set_page_config(page_title="Mon IA Perso - Complet", page_icon="🤖", layout="wide")

# --- INITIALISATION DE LA BASE DE DONNÉES EN MÉMOIRE ---
if "users_db" not in st.session_state:
    st.session_state.users_db = {"admin@example.com": {"password": "1234", "name": "Admin Test"}}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "chat"

if "messages" not in st.session_state:
    st.session_state.messages = []


# --- PAGE DE CONNEXION / INSCRIPTON ---
def show_auth_page():
    st.title("🔐 Bienvenue sur votre Assistant")
    
    tab1, tab2, tab3 = st.tabs(["Se connecter", "Créer un compte", "Connexion avec Google"])

    with tab1:
        st.subheader("Connexion classique")
        with st.form("login_form"):
            email = st.text_input("Adresse Email")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Connexion")
            
            if submit:
                if email in st.session_state.users_db and st.session_state.users_db[email]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = email
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Email ou mot de passe incorrect.")

    with tab2:
        st.subheader("Créer un nouveau compte")
        with st.form("signup_form"):
            new_name = st.text_input("Nom complet")
            new_email = st.text_input("Adresse Email (pour l'inscription)")
            new_password = st.text_input("Mot de passe", type="password")
            submit_signup = st.form_submit_button("S'inscrire")
            
            if submit_signup:
                if new_email in st.session_state.users_db:
                    st.error("Cet email est déjà utilisé.")
                elif not new_email or not new_password:
                    st.error("Veuillez remplir tous les champs.")
                else:
                    st.session_state.users_db[new_email] = {"password": new_password, "name": new_name}
                    st.success("Compte créé avec succès ! Vous pouvez vous connecter.")

    with tab3:
        st.subheader("Connexion rapide")
        st.write("Simulez une connexion instantanée via un compte tiers.")
        if st.button("Se connecter avec Google 🌐"):
            google_email = "utilisateur.google@gmail.com"
            if google_email not in st.session_state.users_db:
                st.session_state.users_db[google_email] = {"password": "oauth_user", "name": "Utilisateur Google"}
            st.session_state.logged_in = True
            st.session_state.current_user = google_email
            st.success("Connecté avec succès via Google !")
            st.rerun()


# --- PAGE DES PARAMÈTRES ---
def show_settings_page():
    st.title("⚙️ Paramètres du compte")
    st.write(f"Connecté en tant que : **{st.session_state.current_user}**")
    
    user_info = st.session_state.users_db.get(st.session_state.current_user, {})
    
    with st.form("settings_form"):
        st.subheader("Modifier vos informations")
        new_name = st.text_input("Nom affiché", value=user_info.get("name", ""))
        new_pass = st.text_input("Nouveau mot de passe", type="password")
        save_btn = st.form_submit_button("Enregistrer les modifications")
        
        if save_btn:
            if new_name:
                st.session_state.users_db[st.session_state.current_user]["name"] = new_name
            if new_pass:
                st.session_state.users_db[st.session_state.current_user]["password"] = new_pass
            st.success("Paramètres mis à jour avec succès !")

    st.markdown("---")
    if st.button("🔄 Changer de compte (Se déconnecter)"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.current_page = "chat"
        st.rerun()


# --- PAGE PRINCIPALE (LE CHAT) ---
def show_main_app():
    with st.sidebar:
        user_name = st.session_state.users_db.get(st.session_state.current_user, {}).get("name", "Utilisateur")
        st.write(f"👤 **{user_name}**")
        
        if st.button("💬 Nouvelle discussion"):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        
        if st.button("⚙️ Paramètres du compte"):
            st.session_state.current_page = "settings"
            st.rerun()
        if st.button("💬 Retour au Chat"):
            st.session_state.current_page = "chat"
            st.rerun()

        st.markdown("---")
        st.subheader("Réglages de l'IA")
        restrictions_on = st.toggle("Activer les restrictions", value=True)
        web_search_on = st.toggle("Activer la recherche Web", value=True)

        if restrictions_on:
            st.info("🔒 Sécurité : Active")
        else:
            st.warning("⚠️ Sécurité : Désactivée")

        if web_search_on:
            st.success("🌍 Web : Actif")
        else:
            st.info("💻 Web : Inactif")

    if st.session_state.current_page == "settings":
        show_settings_page()
    else:
        st.title("🤖 Assistant Personnel Avancé")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Envoyez un message à votre IA..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            web_tag = "🌍 [Web Actif]" if web_search_on else "🧠 [Mémoire Interne]"
            sec_tag = "🔒 [Sécurisé]" if restrictions_on else "⚠️ [Sans Filtre]"
            
            reponse = f"{web_tag} {sec_tag}

Réponse générée pour : *{prompt}*"

            st.session_state.messages.append({"role": "assistant", "content": reponse})
            with st.chat_message("assistant"):
                st.markdown(reponse)


# --- ROUTEUR PRINCIPAL ---
if not st.session_state.logged_in:
    show_auth_page()
else:
    show_main_app()
