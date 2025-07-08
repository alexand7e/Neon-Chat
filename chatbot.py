import streamlit as st
import requests
import uuid # Importa a biblioteca para gerar IDs únicos

# --- Configuração da Página e Carregamento de Recursos ---

try:
    from streamlit_lottie import st_lottie
    support_lottie = True
except ModuleNotFoundError:
    support_lottie = False

st.set_page_config(page_title="IAI - Inteligencia Artificial para Inovação", layout="wide", page_icon="💡")

# --- Funções Auxiliares ---

@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# ATUALIZAÇÃO 1: A função agora aceita o session_id como argumento
def get_n8n_response(prompt: str, session_id: str):
    """
    Envia o prompt e o session_id do usuário para o webhook do n8n.
    """
    webhook_url = st.secrets.get("N8N_WEBHOOK_URL")

    if not webhook_url:
        st.error("A URL do webhook do n8n não está configurada nos secrets do Streamlit.")
        st.info("Por favor, configure o secret 'N8N_WEBHOOK_URL' para que a IAI funcione.")
        return None

    headers = {
          'Content-Type': 'application/json',
    }
    # ATUALIZAÇÃO 2: O payload agora inclui o prompt e o sessionID
    payload = {
        "message": prompt,
        "sessionId": session_id
    }
    
    try:
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        response_data = response.json()
        return response_data.get("output", "Erro: A resposta do n8n não continha a chave 'output'.")

    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão com o webhook: {e}")
        return None
    except ValueError:
        st.error("Erro: Não foi possível decodificar a resposta JSON do n8n.")
        return None

# --- Interface do Usuário (UI) ---

with st.sidebar:
    # st.title("IAI 💡")
    # st.markdown("##### Inteligencia Artificial para Inovação")
    st.image(".img/logo.jpg")


    if support_lottie:
        lottie_chat = load_lottieurl(
            "https://assets4.lottiefiles.com/packages/lf20_touohxv0.json"
        )
        if lottie_chat:
            st_lottie(lottie_chat, height=200)
    
    st.markdown("---")
    st.markdown("Esta interface se conecta a um fluxo de trabalho de automação (n8n) para gerar respostas inteligentes e contextuais.")
    # st.markdown("A URL do webhook deve ser configurada nos **secrets** da aplicação.")

st.header("Converse com a IAI")

# ATUALIZAÇÃO 3: Inicialização do session_id e do histórico de mensagens
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4()) # Gera um ID único e o armazena

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Eu sou a IAI, sua Inteligência Artificial para Inovação. Como posso ajudar você hoje?"}]

# Exibição do chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Interação do usuário
if prompt := st.chat_input("Digite sua pergunta para a IAI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # ATUALIZAÇÃO 4: Passa o session_id para a função de chamada do webhook
    with st.chat_message("assistant"):
        with st.spinner("A IAI está pensando..."):
            # Pega o ID da sessão atual
            current_session_id = st.session_state.session_id
            response_content = get_n8n_response(prompt, current_session_id)
            
            if response_content:
                st.write(response_content)
                st.session_state.messages.append({"role": "assistant", "content": response_content})