import streamlit as st
from google import genai
from google.genai import types
import markdown2
from funcoes import salvar_conto_no_firebase, atualizar_avaliacao_no_firebase

import time

# --- Constants ---
MODEL_NAME = "gemini-2.5-flash"
INTENSITY_OPTIONS = ["Suave", "Moderado", "Intenso"]
STYLE_OPTIONS = ["Romântico", "Aventura", "Fantasia", "Realista", "Popular"]
STORY_LENGTH_DESCRIPTION = "aproximadamente 700 palavras. Uma história com bom tempo para desenvolvimento."

INTENSITY_DESCRIPTIONS = {
    "Suave": "Insinuante e romântico",
    "Moderado": "Sensualidade detalhada",
    "Intenso": "Cenas explícitas e diretas",
}

STYLE_MAP = {
    "Romântico": "foco em romance e conexão emocional",
    "Aventura": "uma trama com elementos de aventura e descoberta sexual",
    "Fantasia": "elementos fantásticos e seres imaginativos",
    "Realista": "uma situação do cotidiano",
    "Popular": "linguagem direta e coloquial, sem palavras complexas ou rebuscadas.",
}

STYLE_DESCRIPTIONS = {
    "Romântico": "Foco nos sentimentos",
    "Aventura": "Jornada e descoberta",
    "Fantasia": "Mundos mágicos",
    "Realista": "Situações cotidianas",
    "Popular": "Linguagem direta",
}

PROMPT_TEMPLATE = """
# Ordem de Missão: Escritor de Contos Eróticos Mestre

**Sua Identidade:** Você é um escritor mestre de contos eróticos, aclamado por sua versatilidade, criatividade e capacidade de seguir instruções com precisão absoluta.

**Sua Tarefa:** Escrever um conto erótico excepcional em português do Brasil, baseado estritamente nas configurações fornecidas pelo usuário.

---

## DIRETRIZES DE EXECUÇÃO (LEIA E SIGA OBRIGATORIAMENTE)

### 1. Análise do Modo de Linguagem:

**SE o "Modo Proibidão" estiver "ATIVADO":**
- **Prioridade Máxima:** A linguagem deve ser EXTREMAMENTE explícita, vulgar e de baixo calão. Use o vocabulário sexual mais pesado e direto que conhecer.
- **Objetivo:** A crueza total é o alvo. Sem filtros, sem eufemismos, sem linguagem poética.
- **Ação:** Descreva todas as cenas com detalhes gráficos e viscerais. IGNORE COMPLETAMENTE o "Nível de Paixão" (Suave, Moderado, Intenso), pois este modo sobrepõe tudo.
- **Tom:** O tom deve ser extremamente lascivo e vulgar, mas positivo. não seja degradante

**SE o "Modo Proibidão" estiver "DESATIVADO":**
- **Prioridade Máxima:** Siga RIGOROSAMENTE o "Nível de Paixão" selecionado.
- **Ação por Nível:**
  - **Se "Suave":** Foco total em romance, sedução e tensão. A linguagem deve ser elegante e sugestiva. É PROIBIDO descrever atos sexuais de forma gráfica.
  - **Se "Moderado":** Foco na paixão e entrega. A linguagem pode ser mais direta, com descrições sensuais dos corpos e das ações, mas mantendo um tom literário e evitando vulgaridade gratuita.
  - **Se "Intenso":** Foco na paixão ardente e luxúria. A linguagem deve ser explícita e detalhada, descrevendo os atos sexuais com clareza e intensidade, mas ainda assim com um toque de arte, evitando a crueza do "Modo Proibidão".

### 2. Análise do Estilo Narrativo:
- Adapte a trama, o cenário e os personagens para se alinharem perfeitamente ao estilo escolhido.
- Comece sempre criando uma ambientação detalhada dos personagens e do cenário. 
- A descricao deve servir para que o leitor visualize o que esta lendo. 
- Descreva fisicamente os personagens quando necessario.
- Seja detalhista o suficiente para que o leitor visualize o que esta lendo.

### 3. Análise do Comprimento da História:
- Siga a diretriz de comprimento para controlar o tamanho final do conto.

## 4. Formatação  
- Use BASTANTE formatação para deixar a história mais interessante, como negrito, italico, paragrafos separados, etc
- italicos em partes importantes ou de conteudo inesperado.
- use negrito em partes importantes ou de grande impacto
- frases em paragrafo unico para destaques
- Tudo de forma a deixar a historia mais visual para o usuario. 

## 5. Output: 
- Sua saida deve ser diretamanete o conto erotico, não é necessario nenhum outro texto antes ou depois. 
- Inicie com o Título do conto escrito em negrito e depois a historia
---

## CONFIGURAÇÕES PARA ESTE CONTO:

- **Tema Principal:** {description}
- **Estilo Narrativo:** {style_name} ({style_description})
- **Comprimento Desejado:** {length_description}
- **Nível de Paixão (Ignorado se o Modo Proibidão estiver ATIVADO):** {intensity_level}
- **Modo Proibidão:** {super_putaria_status}

---

**Ordem Final:** Execute a missão. Comece a escrever o conto agora. Use bastante formatacao em italico e negrito para destacar partes importantes.
"""

# --- Dialog for Putaria Mode ---
@st.dialog("Aviso de Conteúdo Explícito")
def show_putaria_warning():
    """Mostra um aviso sobre o conteúdo explícito e pede confirmação."""
    st.warning("🔞 **Atenção: Modo Proibidão Ativado!**")
    st.write(
        "Você está prestes a ativar um modo que gera conteúdo extremamente explícito, vulgar e sem censura."
    )
    st.write("As histórias serão diretas e sem filtros. Tem certeza que quer continuar?")
    if st.button("Sim, é isso que eu quero!", use_container_width=True, type="primary"):
        st.session_state.super_putaria = True
        st.rerun()


# --- Dialog for Age Gate ---
@st.dialog("Aviso de Conteúdo")
def show_age_gate():
    """Mostra um aviso de idade e pede confirmação."""
    st.image("capa.jpg")
    st.write(
        "Este aplicativo contém material que pode ser considerado explícito e é destinado apenas para adultos. Ao continuar, você confirma que tem 18 anos de idade ou mais.")
    if st.button("Eu confirmo que sou maior de 18 anos", use_container_width=True, type="primary"):
        st.session_state.age_verified = True
        st.rerun()


# --- Page Config ---
st.set_page_config(
    page_title="Contos Proibidos",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Initialize Session State ---
if "age_verified" not in st.session_state:
    st.session_state.age_verified = False
if "story_markdown" not in st.session_state:
    st.session_state.story_markdown = None
if "super_putaria" not in st.session_state:
    st.session_state.super_putaria = False
if "saved_to_firebase" not in st.session_state:
    st.session_state.saved_to_firebase = False
if "current_story_id" not in st.session_state:
    st.session_state.current_story_id = None
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False


# --- Age Gate Logic ---
if not st.session_state.age_verified:
    show_age_gate()
else:
    # --- App Header ---
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;0,700;1,400&family=Lato:wght@400;700&display=swap');

    .app-title {
        font-family: 'Merriweather', serif;
        font-size: 3.8em;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.1em;
        color: #c0392b; /* Fallback */
        background: linear-gradient(to right, #a03022, #e74c3c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-fill-color: transparent;
    }

    .app-caption {
        font-family: 'Lato', sans-serif;
        font-size: 1.1em;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 1em;
    }
    .app-caption2 {
        font-family: 'Lato', sans-serif;
        font-size: 0.9em;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 1em;
    }
    </style>
    """, unsafe_allow_html=True)




    st.html('<p class="app-title">❤ Contos Proibidos ❤</p>')
    st.html('<p class="app-caption">Histórias românticas e sensuais para adultos 🔥 <br>Só utilize se for maior de 18 anos 🔞</p>')
    st.divider()




    # --- Helper Function for HTML Export ---
    def create_styled_html(markdown_text):
        """Converts markdown text to a styled HTML string and extracts a title."""
        # Tenta extrair o título da primeira linha e remove do corpo do markdown
        lines = markdown_text.strip().split("\n")
        story_title = "Conto Proibido"
        body_markdown = markdown_text
        if lines and lines[0].strip().startswith("**") and lines[0].strip().endswith("**"):
            story_title = lines[0].strip().replace("**", "")
            body_markdown = "\n".join(lines[1:])

        html_body = markdown2.markdown(
            body_markdown,
            extras=[
                "cuddled-lists",
                "fenced-code-blocks",
                "footnotes",
                "header-ids",
                "markdown-in-html",
                "smarty-pants",
                "spoiler",
                "tables",
                "tag-friendly",
            ],
        )

        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{story_title}</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;0,700;1,400&family=Lato:wght@400;700&display=swap');
                body {{
                    font-family: 'Merriweather', serif;
                    line-height: 1.7;
                    color: #2c3e50;
                    background-color: #fdfcfb;
                    margin: 0;
                    padding: 1.5rem;
                    display: flex;
                    justify-content: center;
                    font-size: 0.95rem;
                }}
                .container {{
                    max-width: 750px;
                    width: 100%;
                    background-color: #ffffff;
                    padding: 2.5rem 3rem;
                    border-radius: 8px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                }}
                .story-header {{
                    text-align: center;
                    margin-bottom: 2.5rem;
                }}
                .story-header .subtitle {{
                    font-family: 'Lato', sans-serif;
                    font-size: 1em;
                    color: #7f8c8d;
                    text-transform: uppercase;
                    letter-spacing: 3px;
                }}
                .story-header .main-title {{
                    font-family: 'Merriweather', serif;
                    font-size: 2.5em;
                    font-weight: 700;
                    margin: 0.2em 0 0 0;
                    color: #c0392b; /* Fallback */
                    background: linear-gradient(to right, #a03022, #e74c3c);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    text-fill-color: transparent;
                }}
                h1, h2, h3 {{
                    font-family: 'Lato', sans-serif;
                    font-weight: 700;
                    color: #c0392b;
                    text-align: center;
                    margin-bottom: 2rem;
                    line-height: 1.3;
                }}
                p {{
                    margin-bottom: 1.2rem;
                    text-align: justify;
                }}
                strong {{
                    font-weight: 700;
                    color: #a03022;
                }}
                em {{
                    font-style: italic;
                    color: #34495e;
                }}
                 hr {{
                    border: 0;
                    height: 1px;
                    background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(192, 57, 43, 0.75), rgba(0, 0, 0, 0));
                    margin: 2rem 0;
                }}
                footer {{
                    text-align: center;
                    margin-top: 3rem;
                    padding-top: 1.5rem;
                    border-top: 1px solid #eee;
                    font-family: 'Lato', sans-serif;
                    font-size: 0.8em;
                    color: #95a5a6;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header class="story-header">
                    <div class="subtitle">Seu Conto Proibido</div>
                    <h1 class="main-title">{story_title}</h1>
                </header>
                
                {html_body}

                <footer>
                    Gerado por contosproibidos.streamlit.app
                </footer>
            </div>
        </body>
        </html>
        """
        return html_content, story_title


    # --- Gemini Streaming Function ---
    def stream_erotic_story(
        description, intensity_level, story_type, super_putaria_mode
    ):
        try:
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

            prompt = PROMPT_TEMPLATE.format(
                description=description,
                style_name=story_type,
                style_description=STYLE_MAP[story_type],
                length_description=STORY_LENGTH_DESCRIPTION,
                intensity_level=intensity_level,
                super_putaria_status="ATIVADO" if super_putaria_mode else "DESATIVADO",
            )

            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=-1,
                ),
                response_mime_type="text/plain",
            )

            stream = client.models.generate_content(   
                model=MODEL_NAME,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=prompt),
                        ],
                    ),
                ],
                config=generate_content_config,
            )

            return stream.candidates[0].content.parts[0].text
        except Exception as e:
            st.error(
                "Ocorreu um erro ao gerar o conto. Tente novamente com outra descrição ou configuração."
            )
            st.info(e)

    # --- Controls ---
    st.text_area(
        "Descreva o tema da história:",
        key="description",
        placeholder="Coloque os detalhes que você quer na história, como pessoas, locais, etc",
        height=100,
    )

    col1, col2, col3 = st.columns([2, 2, 1.4])
    with col1:
        st.selectbox(
            "📚 Estilo:",
            STYLE_OPTIONS,
            key="story_type",
            format_func=lambda style: f"{style} - {STYLE_DESCRIPTIONS.get(style, '')}",
        )

    with col2:
        st.selectbox(
            "❤️ Nível de Paixão:",
            INTENSITY_OPTIONS,
            key="intensity_level",
            disabled=st.session_state.get("super_putaria", False),
            format_func=lambda intensity: f"{intensity} - {INTENSITY_DESCRIPTIONS.get(intensity, '')}",
        )
    with col3:
        st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
        putaria_toggled = st.toggle(
            "🌶️ Modo Proibidão",
            value=st.session_state.super_putaria,
        )

    # Lógica para abrir o diálogo de confirmação
    if putaria_toggled and not st.session_state.super_putaria:
        # O usuário tentou ligar o modo. Mostre o diálogo.
        show_putaria_warning()
    elif not putaria_toggled and st.session_state.super_putaria:
        # O usuário desligou o modo. Apenas atualize o estado.
        st.session_state.super_putaria = False
        st.rerun()


    generate_button = st.button(
        "🚀 Gerar Conto",
        use_container_width=True,
        type="primary",
        disabled=not st.session_state.get("description"),
    )
    st.divider()
    # --- Story Generation ---
    if generate_button:
        if not st.session_state.description:
            st.warning("⚠️ Por favor, descreva um tema para a história.")
        else:
            st.session_state.saved_to_firebase = False  # Reseta o status antes de gerar
            st.session_state.current_story_id = None # Reseta o ID do conto
            st.session_state.feedback_submitted = False # Reseta o status do feedback
            if "user_rating" in st.session_state:
                st.session_state.user_rating = None # Reseta a avaliação
            st.divider()

            spinner_message = (
                "Ahhh, você quer putaria, né? Deixa comigo, vou caprichar na safadeza... 🔥😈"
                if st.session_state.super_putaria
                else "Agora é só relaxar, estamos preparando uma historia bem gostosa para você... 🖋️🔥"
            )
            with st.spinner(spinner_message, show_time=True):
                st.session_state.story_markdown = stream_erotic_story(
                    st.session_state.description,
                    st.session_state.intensity_level,
                    st.session_state.story_type,
                    st.session_state.super_putaria,
                )

    # --- Display Story and Actions ---
    if st.session_state.story_markdown:
        # Criar e fornecer o botão de download para o HTML
        html_content, story_title = create_styled_html(st.session_state.story_markdown)

        # Exibir o HTML gerado na tela
        st.html(html_content)
        st.divider()

        # Gera um nome de arquivo seguro a partir do título
        safe_title = "".join(
            c for c in story_title if c.isalnum() or c in (" ", "-")
        ).rstrip()
        file_name = f"{safe_title.replace(' ', '_') or 'conto_proibido'}.html"

        # Salva o conto no Firebase quando ele é exibido
        if not st.session_state.saved_to_firebase:
            # Coleta os dados de contexto
            try:
                context_data = {
                    "ip_address": st.context.ip_address,
                    "is_embedded": st.context.is_embedded,
                    "locale": st.context.locale,
                    "theme": st.context.theme.type,
                    "timezone": st.context.timezone,
                    "url": st.context.url,
                    "user_agent": st.context.headers.get("user-agent", "N/A")
                }
            except Exception:
                # Em alguns ambientes (como testes locais sem um browser completo), o st.context pode dar erro.
                context_data = {"erro": "Nao foi possivel obter o contexto."}


            doc_id = salvar_conto_no_firebase(
                description=st.session_state.description,
                intensity=st.session_state.intensity_level,
                style=st.session_state.story_type,
                super_putaria=st.session_state.super_putaria,
                story_markdown=st.session_state.story_markdown,
                story_title=story_title,
                context_data=context_data # Passa os dados de contexto
            )
            if doc_id:
                st.session_state.saved_to_firebase = True
                st.session_state.current_story_id = doc_id


        # Primeiro, pedir avaliação centralizada
        st.markdown(
            """
            <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 1.5em;">
                <span style="font-size: 1.1em; font-weight: 500;">Avalie esse conto:</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Centralizando o st.feedback usando st.columns
        col_feedback = st.columns(5)
        with col_feedback[2]:
            rating = st.feedback("stars", key="user_rating")

        # Se o feedback foi enviado e ainda não foi processado, atualize o Firebase
        if rating is not None and not st.session_state.feedback_submitted:
            sucesso = atualizar_avaliacao_no_firebase(st.session_state.current_story_id, rating)
            if sucesso:
                st.session_state.feedback_submitted = True # Marca como enviado para não repetir

        st.divider()

        # Depois, duas colunas para os botões
        col1, col2 = st.columns(2, gap="small")
        with col1:
            @st.fragment
            def download_button():
                st.download_button(
                    label="📥 Baixar Conto em HTML",
                    data=html_content,
                    file_name=file_name,
                    mime="text/html",
                    use_container_width=True,
                    type="primary",
                )
            download_button()
        with col2:
            if st.button("🗑️ Apagar conto", use_container_width=True, type="secondary"):
                st.session_state.story_markdown = None
                st.rerun()
