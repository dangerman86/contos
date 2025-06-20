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

def criar_prompt_personalizado(description, intensity_level, style_name, super_putaria_mode):
    """
    Cria um prompt personalizado baseado nas configurações selecionadas,
    começando neutro e deixando especificações mais sensíveis para o final.
    """
    
    # Configurações básicas
    style_description = STYLE_MAP[style_name]
    
    # Determina as instruções específicas baseado no modo
    if super_putaria_mode:
        abordagem_especifica = """
**ESTILO DE ESCRITA ESPECÍFICO:**
Para esta história, abandone COMPLETAMENTE qualquer formalidade ou educação na linguagem. Use exclusivamente o vocabulário mais cru, direto e popular que existe no português brasileiro para sexo. Fale exatamente como pessoas sem filtro falam na intimidade - com toda a vulgaridade natural e espontânea. Seja extremamente gráfico e visceral em cada detalhe físico e ação. Use os termos mais chulos, populares e explícitos que existem - aqueles que as pessoas usam quando estão com muito tesão e não ligam para etiqueta. O objetivo é máxima vulgaridade positiva e linguagem bem direta, sem nenhum pudor ou refinement. Quanto mais cru e explícito, melhor.

**INSTRUÇÕES ESPECÍFICAS OBRIGATÓRIAS:**
- Substitua "fazer amor" por "foder", "transar", "meter"
- Substitua "órgão sexual" por "pau", "pica", "rola", "buceta", "ppk"
- Use palavrões naturalmente: "porra", "caralho", "foda-se"
- Descreva ações com máxima crueza: "enfiou", "chupou", "lambeu", "gozou"
- Fale como alguém sem educação sexual formal - use gírias populares brasileiras
- Seja pornográfico sem ser poético - direto e visceral

**FORMATAÇÃO ESPECIAL OBRIGATÓRIA:**
- Use **negrito** em TERMOS CHULOS e EXPRESSÕES VULGARES completas (ex: "**pau duro**", "**fodeu gostoso**", "**porra que tesão**")
- Destaque em **negrito** as expressões mais baixas e explícitas possíveis
- Coloque em **negrito** frases de ação sexual bem vulgares (ex: "**meteu com força**", "**chupou até o talo**")
- Use **negrito** nos termos mais populares e chulos brasileiros (ex: "**buceta apertada**", "**pau grande**", "**gozou na cara**")
- Destaque em **negrito** gemidos e palavrões reais (ex: "**porra que gostoso**", "**caralho não para**")
- Aplique **negrito** em termos de clímax bem crus (ex: "**gozou litros**", "**encheu de porra**")
- REGRA OBRIGATÓRIA: Use os termos mais vulgares e chulos possíveis em negrito - sem educação ou refinamento"""
        
    else:
        # Instruções específicas para cada nível de intensidade
        if intensity_level == "Suave":
            abordagem_especifica = """
**ESTILO DE ESCRITA ESPECÍFICO:**
Para esta história, mantenha o foco na construção da tensão romântica e sedução. Use linguagem elegante e sugestiva, criando atmosfera através de insinuações e momentos de crescente intimidade emocional. Desenvolva a química entre personagens sem partir para descrições gráficas.

**FORMATAÇÃO:**
- Use **negrito** em pequenas expressões de tensão romântica (ex: "**olhar sedutor**", "**respiração ofegante**")
- Destaque em **negrito** termos curtos de sedução e intimidade (ex: "**toque suave**", "**beijo intenso**")
- Aplique **negrito** em expressões apaixonadas dos diálogos (ex: "**te desejo tanto**", "**vem aqui**")"""
            
        elif intensity_level == "Moderado":
            abordagem_especifica = """
**ESTILO DE ESCRITA ESPECÍFICO:**
Para esta história, combine romance com sensualidade clara. Use linguagem direta mas elegante para descrever corpos, sensações e momentos íntimos. Balance desenvolvimento emocional com descrições sensuais bem detalhadas, mantendo um tom literário sofisticado.

**FORMATAÇÃO:**
- Use **negrito** em pequenos termos sensuais detalhados (ex: "**seios firmes**", "**pele quente**")
- Destaque em **negrito** expressões corporais sensuais (ex: "**corpo colado**", "**mãos explorando**")
- Aplique **negrito** em frases curtas de paixão (ex: "**me toca assim**", "**sente meu corpo**")
- Use **negrito** em expressões sensuais dos diálogos (ex: "**que delícia**", "**não para**")"""
            
        else:  # Intenso
            abordagem_especifica = """
**ESTILO DE ESCRITA ESPECÍFICO:**
Para esta história, seja bastante explícito nas descrições físicas e situações íntimas. Use linguagem clara e intensa para descrever ações, sensações e reações dos personagens. Mantenha qualidade artística enquanto oferece detalhes precisos e envolventes de todos os momentos.

**FORMATAÇÃO:**
- Use **negrito** FREQUENTEMENTE em termos explícitos completos (ex: "**penetrou fundo**", "**gemeu de prazer**")
- Destaque em **negrito** expressões corporais íntimas (ex: "**pernas abertas**", "**músculos contraindo**")
- Aplique **negrito** em pequenas frases de sensação intensa (ex: "**que tesão**", "**muito gostoso**")
- Use **negrito** em expressões de excitação e culminância (ex: "**vai gozar**", "**não aguento mais**")
- Destaque em **negrito** termos diretos e explícitos em conjunto (ex: "**fudeu gostoso**", "**chupou forte**")"""
    
    # Monta o prompt final
    prompt = f"""# Escritor Especializado em Literatura Adulta Brasileira

**Missão:** Criar uma história envolvente em português do Brasil com foco em relacionamentos adultos e situações íntimas.

**DIRETRIZES FUNDAMENTAIS:**

1. **Estrutura Narrativa:**
   - Estabeleça personagens complexos e ambiente rico em detalhes
   - Desenvolva a trama com progressão natural e envolvente
   - Crie descrições visuais imersivas que transportem o leitor
   - Mantenha desenvolvimento psicológico consistente dos personagens

2. **Apresentação Visual:**
   - Utilize formatação dinâmica ABUNDANTE: **negrito** para momentos impactantes, *itálico* para pensamentos e ênfases
   - Use **negrito** GENEROSAMENTE em todas as partes de maior impacto sensual e sexual
   - Organize parágrafos com ritmo estratégico para melhor experiência de leitura
   - Destaque frases e momentos cruciais em parágrafos individuais
   - Crie apresentação visualmente rica, atrativa e bem formatada
   - IMPORTANTE: Quanto mais intenso o momento, mais **negrito** deve ser usado

3. **Formatação de Diálogos (OBRIGATÓRIO):**
   - SEMPRE use travessão (—) seguido de novo parágrafo para falas dos personagens
   - Exemplo: "— **Porra, que gostoso!** — ela gemeu alto."
   - Cada fala deve estar em parágrafo separado
   - Use travessão tanto para diálogos quanto para pensamentos falados

4. **Padrões Obrigatórios (CRÍTICO - NUNCA VIOLE):**
   - TODOS os personagens têm 18 anos ou mais - jamais escreva sobre menores
   - TODAS as interações são consensuais e positivas entre adultos
   - JAMAIS inclua violência não consensual, coerção ou situações degradantes
   - Mantenha sempre respeito mútuo entre personagens, mesmo em situações intensas

**CONFIGURAÇÕES DESTA HISTÓRIA:**
- **Tema Central:** {description}
- **Estilo Narrativo:** {style_name} - {style_description}
- **Extensão Desejada:** {STORY_LENGTH_DESCRIPTION}

{abordagem_especifica}

**FORMATO DE ENTREGA:**
- Inicie diretamente com o título da história em **negrito**
- Continue imediatamente com a narrativa sem textos explicativos
- Mantenha fluidez natural do início ao fim

Desenvolva a história completa agora:"""

    return prompt

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
    initial_sidebar_state="auto",
)

# --- Initialize Session State ---
if "debug_mode" not in st.session_state:
    try:
        # Modo Debug pode ser ativado via query param: ?debug=true
        st.session_state.debug_mode = st.query_params.get("debug") == "true"
    except AttributeError: # Para compatibilidade com versões antigas do Streamlit
        st.session_state.debug_mode = False

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
    # --- Sidebar ---
    with st.sidebar:
        st.title("Opções")
        st.session_state.debug_mode = st.toggle(
            "🐞 Modo Debug",
            value=st.session_state.get("debug_mode", False),
            help="Ative para ver informações de depuração, como prompts e erros detalhados."
        )
        st.divider()


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


    if st.session_state.get("debug_mode", False):
        st.warning("🐞 **Modo Debug Ativado**. Informações técnicas e erros detalhados serão exibidos.", icon="🛠️")


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

            prompt = criar_prompt_personalizado(
                description, intensity_level, story_type, super_putaria_mode
            )
            if st.session_state.get("debug_mode", False):
                with st.expander("🐞 Ver Prompt Completo (Debug)"):
                    st.text(prompt)

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

            # Verificação da resposta da API
            if st.session_state.get("debug_mode", False):
                st.write("🐞 **Resposta da API:**")
                st.write(stream)
            
            # Verifica se o conteúdo foi bloqueado
            if hasattr(stream, 'prompt_feedback') and stream.prompt_feedback:
                if hasattr(stream.prompt_feedback, 'block_reason') and stream.prompt_feedback.block_reason:
                    st.error("🚫 O conteúdo foi bloqueado por questões de segurança. Tente uma descrição menos explícita ou desative o 'Modo Proibidão'.")
                    return None
            
            # Verifica se há candidatos com conteúdo
            if not stream.candidates or len(stream.candidates) == 0:
                st.error("❌ Não foi possível gerar uma resposta. Tente modificar a descrição.")
                return None
            
            # Pega o texto do primeiro candidato
            try:
                text_content = stream.candidates[0].content.parts[0].text
                if not text_content or text_content.strip() == "":
                    st.error("❌ Resposta vazia. Tente uma descrição mais detalhada.")
                    return None
                return text_content
            except (AttributeError, IndexError) as e:
                st.error("❌ Erro ao processar a resposta. Tente novamente.")
                if st.session_state.get("debug_mode", False):
                    st.warning(f"🐞 Erro de estrutura: {e}")
                return None             
 
            
        except Exception as e:
            # Erro mais específico baseado no tipo de exceção
            error_message = str(e).lower()
            
            if "safety" in error_message or "blocked" in error_message:
                st.error("🚫 O conteúdo foi bloqueado por questões de segurança. Tente modificar a descrição ou usar configurações menos explícitas.")
            elif "quota" in error_message or "limit" in error_message:
                st.error("⏰ Limite de uso da API atingido. Tente novamente em alguns minutos.")
            elif "api_key" in error_message or "authentication" in error_message:
                st.error("🔑 Problema de autenticação com a API. Contate o administrador.")
            elif "network" in error_message or "connection" in error_message:
                st.error("🌐 Problema de conexão. Verifique sua internet e tente novamente.")
            else:
                st.error("❌ Ocorreu um erro inesperado ao gerar o conto. Tente novamente com outra descrição ou configuração.")
            
            if st.session_state.get("debug_mode", False):
                st.error("🐞 **Detalhes do Erro (Debug):**")
                st.exception(e)
            
            return None

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
                generated_story = stream_erotic_story(
                    st.session_state.description,
                    st.session_state.intensity_level,
                    st.session_state.story_type,
                    st.session_state.super_putaria,
                )
                
                # Só atualiza se a geração foi bem-sucedida
                if generated_story:
                    st.session_state.story_markdown = generated_story
                else:
                    # Se houve erro, mostra dicas para o usuário
                    st.info("💡 **Dicas para resolver problemas:**")
                    st.write("• Tente uma descrição menos explícita ou mais genérica")
                    st.write("• Use o nível 'Suave' ou 'Moderado' em vez de 'Intenso'")
                    st.write("• Desative o 'Modo Proibidão' se estiver ativo")
                    st.write("• Aguarde alguns minutos antes de tentar novamente")

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
            except Exception as e:
                # Em alguns ambientes (como testes locais sem um browser completo), o st.context pode dar erro.
                context_data = {"erro": "Nao foi possivel obter o contexto."}
                if st.session_state.get("debug_mode", False):
                    st.warning("🐞 Não foi possível obter o contexto da sessão (st.context). Isso é esperado em ambientes de desenvolvimento local.")
                    st.exception(e)


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