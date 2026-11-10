import streamlit as st
from google import genai

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Fortezza Content Engineer AI",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Bot de Ingeniería de Contenido & Guiones — Fortezza Perfums")
st.subheader("Ingeniería inversa de videos virales + Plantillas de guiones por demanda")

# ---------------------------------------------------------
# API KEY FIJA
# ---------------------------------------------------------
gemini_key = "AQ.Ab8RN6IgRY9SYPAeKuG6mbhGO_gMMb0IziI6FrTGdt3ZyBsnFQ"

# ---------------------------------------------------------
# BARRA LATERAL (HISTORIAL DE IDEAS Y GESTIÓN)
# ---------------------------------------------------------
with st.sidebar:
    st.header("🔑 Estado de la API")
    st.success("API Key configurada ✅")
    
    st.divider()
    st.header("📁 Historial de Ideas")
    
    # Mostrar las ideas/preguntas anteriores en el panel izquierdo
    if "messages" in st.session_state and st.session_state.messages:
        user_queries = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        if user_queries:
            for idx, query in enumerate(user_queries):
                st.markdown(f"**{idx+1}.** {query[:35]}...")
        else:
            st.info("Aún no hay ideas registradas.")
    else:
        st.info("El historial aparecerá aquí.")

    st.divider()
    st.header("🕒 Gestión de Sesión")
    if st.button("➕ Nueva Conversación", use_container_width=True):
        st.session_state.messages = []
        if "chat_session" in st.session_state:
            del st.session_state.chat_session
        st.rerun()
        
    st.markdown("---")
    st.markdown("### 💡 ¿Cómo usar este Bot?")
    st.markdown("""
    * **Modo Reingeniería:** Pásale la transcripción o estructura de un video para adaptarlo a tus perfumes.
    * **Modo Banco de Ideas:** Pide lotes de ideas con estructuras virales listas.
    """)

# Verificar API Key
if not gemini_key or gemini_key == "PEGA_AQUÍ_TU_API_KEY_DE_GEMINI":
    st.warning("⚠️ Por favor ingresa tu API Key real dentro del código en la variable `gemini_key`.")
    st.stop()

# ---------------------------------------------------------
# INICIALIZAR CLIENTE Y CHAT CON CACHÉ
# ---------------------------------------------------------
@st.cache_resource
def get_gemini_client(api_key):
    return genai.Client(api_key=api_key)

client_ai = get_gemini_client(gemini_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = client_ai.chats.create(model="gemini-3.8-flash")

# Renderizar el historial de mensajes y agregar botón de descarga ultraligero a cada respuesta
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            st.download_button(
                label="📥 Descargar Guion (Exportar a PDF / TXT)",
                data=message["content"],
                file_name=f"guion_fortezza_{i}.txt",
                mime="text/plain",
                key=f"download_hist_{i}"
            )

# ---------------------------------------------------------
# ENTRADA DE TEXTO (TIPO CHAT ABAJO)
# ---------------------------------------------------------
if prompt := st.chat_input("Ej: 'Analiza la estructura de este video...' o 'Dame 5 ideas de Reels para perfumes'"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analizando ingeniería de video y estructurando guiones..."):
            
            system_instruction = """
            Eres un Director experto en Ingeniería de Contenido, Neuro-copywriting y Retención para marcas de comercio electrónico de alta gama (específicamente perfumería como Fortezza Perfums).
            Tu especialidad es diseccionar por qué los videos en Instagram funcionan (su estructura psicológica, ganchos de curiosidad/autoridad, ritmo y CTA) y replicar esas fórmulas de dos formas cuando el usuario te lo pida:
            
            1. **Ingeniería Inversa:** A partir de la descripción, transcripción o referencia que te dé el usuario de un Reel, extraes la anatomía exacta del éxito y creas un guion adaptado para sus perfumes.
            2. **Estructuras Modulares (Plantillas Virales):** Cuando el usuario pida ideas masivas, entregas estructuras probadas de retención donde los espacios del producto queden como variables listas (ej: [NOMBRE_DEL_PERFUME_AQUÍ]) para que él solo los rellene en segundos.
            
            Estructura siempre tus salidas en tablas o pasos limpios manteniendo un tono ultra profesional y estratégico.
            """
            
            full_prompt = f"{system_instruction}\n\nSolicitud del usuario: {prompt}"
            
            response = st.session_state.chat_session.send_message(full_prompt)
            bot_response = response.text
            
            st.markdown(bot_response)
            
            st.download_button(
                label="📥 Descargar Guion (Exportar a PDF / TXT)",
                data=bot_response,
                file_name="guion_fortezza_nuevo.txt",
                mime="text/plain",
                key="download_new"
            )
            
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
