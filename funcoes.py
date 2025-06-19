import streamlit as st
from firebase_admin import firestore, credentials 
import firebase_admin 
import re
import unicodedata
import time

# Nome da coleção principal de usuários definida como variável global
COLECAO_USUARIOS = "contos-proibidos"

def _criar_id_do_titulo(titulo):
    """
    Cria um ID de documento seguro a partir de um título.
    Remove caracteres especiais, converte para minúsculas e substitui espaços.
    """
    if not titulo or not isinstance(titulo, str):
        # Gera um ID com timestamp se o título for inválido para evitar colisões
        return f"conto_sem_titulo_{int(time.time())}"

    # Normaliza o título para remover acentos (ex: "ação" -> "acao")
    slug = unicodedata.normalize('NFKD', titulo).encode('ascii', 'ignore').decode('utf-8')

    # Converte para minúsculas e remove caracteres que não sejam letras, números ou espaços/hífens
    slug = slug.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    
    # Substitui um ou mais espaços/hífens por um único underscore
    slug = re.sub(r'[\s-]+', '_', slug).strip('_')

    # Caso o título seja composto apenas de caracteres inválidos
    if not slug:
        return f"conto_proibido_{int(time.time())}"
        
    # Trunca o ID para um tamanho seguro para o Firestore (limite é 1500 bytes)
    return slug[:500]

def inicializar_firebase():
    # Verifica se estamos em produção (Streamlit Cloud) ou desenvolvimento local
    if 'firebase' in st.secrets:
        cred = credentials.Certificate({
            "type": st.secrets.firebase.type,
            "project_id": st.secrets.firebase.project_id,
            "private_key_id": st.secrets.firebase.private_key_id,
            "private_key": st.secrets.firebase.private_key,
            "client_email": st.secrets.firebase.client_email,
            "client_id": st.secrets.firebase.client_id,
            "auth_uri": st.secrets.firebase.auth_uri,
            "token_uri": st.secrets.firebase.token_uri,
            "auth_provider_x509_cert_url": st.secrets.firebase.auth_provider_x509_cert_url,
            "client_x509_cert_url": st.secrets.firebase.client_x509_cert_url,
            "universe_domain": st.secrets.firebase.universe_domain
        })
    else:
        # Usa o arquivo local em desenvolvimento
        cred = credentials.Certificate("firebase-key.json")
        
    # Inicializa o Firebase apenas se ainda não foi inicializado
    try:
        firebase_admin.get_app() 
    except ValueError:
        firebase_admin.initialize_app(cred)

def salvar_conto_no_firebase(description, intensity, style, super_putaria, story_markdown, story_title, context_data=None):
    """
    Salva os detalhes de um conto gerado no Firestore, usando o título como ID.
    Retorna o ID do documento criado em caso de sucesso, ou None em caso de erro.
    """
    try:
        inicializar_firebase()
        db = firestore.client()

        # Cria um ID de documento a partir do título do conto
        doc_id = _criar_id_do_titulo(story_title)
        doc_ref = db.collection(COLECAO_USUARIOS).document(doc_id)
        
        # Prepara os dados do conto
        story_data = {
            "tema": description,
            "intensidade": intensity,
            "estilo": style,
            "modo_proibidao": super_putaria,
            "titulo_conto": story_title,
            "conto_markdown": story_markdown,
            "timestamp": firestore.SERVER_TIMESTAMP
        }

        # Adiciona os dados de contexto, se existirem
        if context_data:
            story_data["contexto"] = context_data

        doc_ref.set(story_data)
        
        #st.toast("Conto salvo no banco de dados com sucesso!", icon="💾")
        return doc_id
    except Exception as e:
        st.error(f"Erro ao salvar o conto no Firebase: {e}")
        return None

def atualizar_avaliacao_no_firebase(doc_id, rating):
    """
    Atualiza um conto existente no Firestore com a avaliação do usuário.
    """
    if not doc_id:
        return False
    try:
        inicializar_firebase()
        db = firestore.client()
        doc_ref = db.collection(COLECAO_USUARIOS).document(doc_id)
        
        doc_ref.update({
            "avaliacao": rating,
            "avaliacao_timestamp": firestore.SERVER_TIMESTAMP
        })
        #st.toast("Obrigado pela sua avaliação!", icon="👍")
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar a avaliação no Firebase: {e}")
        return False
