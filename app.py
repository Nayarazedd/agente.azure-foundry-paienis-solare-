import os
import sqlite3
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv(override=True)

# Configuração do Cliente Azure OpenAI usando os nomes do .env que deu certo
client = AzureOpenAI(
    azure_endpoint=os.getenv("ENDPOINT"),
    api_key=os.getenv("API_KEY"),
    api_version=os.getenv("API_VERSION", "2024-08-07-preview")
)

DEPLOYMENT_NAME = os.getenv("GPT5_MODEL")
DB_NAME = "painel_solar.db"

# --- BANCO DE DADOS E FUNÇÕES ---
def inicializar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_usuario TEXT NOT NULL,
            resposta_ia TEXT NOT NULL,
            data_hora TEXT NOT NULL,
            status TEXT DEFAULT 'Pendente'
        )
    """)
    conn.commit()
    conn.close()

def consultar_prompt(item_id: int):
    """Consulta os detalhes de um registro de prompt/serviço no banco SQLite."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, prompt_usuario, resposta_ia, data_hora, status FROM produtos WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "prompt": row[1], "resposta": row[2], "data_hora": row[3], "status": row[4]}
    return None

def verificar_prompt(item_id: int):
    """Atualiza o status de verificação/conclusão de um registro no banco SQLite."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE produtos SET status = 'Verificado/Concluído' WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao atualizar: {e}")
        return False

def salvar_historico(prompt: str, resposta: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO produtos (prompt_usuario, resposta_ia, data_hora, status) VALUES (?, ?, ?, 'Ativo')", (prompt, resposta, data_hora))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id

# Inicializa o banco ao iniciar a aplicação
inicializar_banco()

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Agente Solar AI - Limpeza de Painéis", layout="centered")

st.title("☀️ Agente de IA - Limpeza e Manutenção de Painéis Solares")
st.markdown("Sistema inteligente integrado ao Azure Foundry para diagnóstico, agendamento e controle de limpeza de usinas solares.")

# Entrada do usuário
pergunta = st.text_area("Descreva a necessidade de limpeza ou faça sua pergunta sobre os painéis:")

if st.button("Enviar para o Agente"):
    if not pergunta.strip():
        st.warning("Por favor, digite uma pergunta válida.")
    elif not DEPLOYMENT_NAME or not os.getenv("ENDPOINT") or not os.getenv("API_KEY"):
        st.error(f"Erro de configuração: Variáveis da Azure não definidas no ambiente. (Endpoint: {bool(os.getenv('ENDPOINT'))}, Key: {bool(os.getenv('API_KEY'))}, Model: {bool(DEPLOYMENT_NAME)})")
    else:
        try:
            with st.spinner("O agente está analisando os dados..."):
                response = client.chat.completions.create(
                    model=DEPLOYMENT_NAME,
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é um engenheiro especialista em manutenção e otimização de painéis solares fotovoltaicos. Responda de forma técnica e prática."
                        },
                        {
                            "role": "user",
                            "content": pergunta
                        }
                    ]
                )
                resposta_texto = response.choices[0].message.content
                
                # Salva no banco SQLite
                item_id = salvar_historico(pergunta, resposta_texto)
                
                st.success(f"Resposta gerada e salva com sucesso! (ID do Registro: {item_id})")
                st.markdown("### Resposta do Agente:")
                st.write(resposta_texto)
                
        except Exception as e:
            st.error(f"Erro na comunicação com a API da Azure: {e}")

# Seção de consulta rápida via banco de dados
st.markdown("---")
st.subheader("🔍 Consulta Rápida de Registros (Banco SQLite)")
consulta_id = st.number_input("Digite o ID do registro para consultar:", min_value=1, step=1)
if st.button("Consultar ID"):
    resultado = consultar_prompt(int(consulta_id))
    if resultado:
        st.json(resultado)
    else:
        st.info("Nenhum registro encontrado com esse ID.")
        