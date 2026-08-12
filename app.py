
import streamlit as st
from groq import Groq

# 1. Configuração da página do Streamlit
st.set_page_config(
    page_title="Maestro Professor de Música",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Título e descrição da aplicação
st.title("🎵 Maestro Professor de Música")
st.markdown(
    "Olá! Sou seu assistente especialista em **bateria, guitarra, baixo e canto**. "
    "Podemos conversar sobre tipos de notas musicais, estilos musicais, partituras, tablaturas, "
    "leitura avançada, técnica e som de instrumentos da orquestra, além de ritmo!"
)

# 2. Configuração do cliente Groq utilizando os segredos do Streamlit
# Certifique-se de configurar 'GROQ_API_KEY' no st.secrets (ou secrets.toml)
try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    groq_api_key = None

if not groq_api_key:
    st.error("A chave de API do Groq (GROQ_API_KEY) não foi encontrada nos segredos do Streamlit.")
    st.stop()

client = Groq(api_key=groq_api_key)

# 3. Inicialização do histórico de mensagens no estado da sessão do Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "Você é um maestro e professor de música especialista em bateria, guitarra, baixo e canto. "
                "Seu foco é conversar sobre tipos de notas musicais, estilos de música, partituras, tablaturas, "
                "leitura avançada de partituras, conhecimento técnico e sonoro dos instrumentos da orquestra, "
                "e desenvolvimento de um excelente senso de ritmo. Mantenha um tom didático, acolhedor e profissional, "
                "adequado para públicos de 10 a 55 anos."
            )
        }
    ]

# Exibição do histórico de mensagens anteriores (excluindo a system message)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 4. Captura da entrada do usuário via chat input do Streamlit
if prompt := st.chat_input("Digite sua dúvida sobre música, instrumentos ou partituras..."):
    # Adiciona a mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Exibe a mensagem do usuário na interface
    with st.chat_message("user"):
        st.markdown(prompt)

    # 5. Comunicação com a API do Groq e exibição da resposta em tempo real
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Requisição para o modelo Llama 3 via Groq
            stream = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                temperature=0.7,
                max_tokens=1024
            )
            
            # Processamento do fluxo de resposta (streaming)
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            full_response = f"Desculpe, ocorreu um erro ao se comunicar com o agente: {e}"
            message_placeholder.markdown(full_response)

    # Adiciona a resposta do assistente ao histórico da sessão
    st.session_state.messages.append({"role": "assistant", "content": full_response})