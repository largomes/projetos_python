# app_tudo_junto.py - TUDO em um arquivo só
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error

# ============ CONFIGURAÇÃO ============
st.set_page_config(
    page_title="MySQL System",
    layout="wide"
)

# ============ FUNÇÃO DE CONEXÃO ============
def conectar_mysql(database=None):
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Sua senha
            database=database
        )
        return conexao
    except Error as e:
        st.error(f"Erro: {e}")
        return None

# ============ ESTADO DA APLICAÇÃO ============
if "pagina" not in st.session_state:
    st.session_state.pagina = "home"

if "guia_secao" not in st.session_state:
    st.session_state.guia_secao = "basico"

# ============ BARRA LATERAL DE NAVEGAÇÃO ============
with st.sidebar:
    st.title("🧭 Navegação")
    
    # Logo
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #0D47A1;">🗄️</h1>
        <h3>MySQL System</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Menu
    st.subheader("📚 Aprendizado")
    if st.button("🏠 Página Inicial", use_container_width=True):
        st.session_state.pagina = "home"
    
    if st.button("📚 Guia MySQL", use_container_width=True):
        st.session_state.pagina = "guia"
    
    if st.button("🎯 Exercícios", use_container_width=True):
        st.session_state.pagina = "exercicios"
    
    st.subheader("🔧 Ferramentas")
    if st.button("🔍 Query Editor", use_container_width=True, type="primary"):
        st.session_state.pagina = "query_editor"
    
    if st.button("⚙️ MySQL Manager", use_container_width=True):
        st.session_state.pagina = "mysql_manager"
    
    st.markdown("---")
    st.caption(f"📍 Página: {st.session_state.pagina}")

# ============ PÁGINA: HOME ============
def pagina_home():
    st.title("🏠 Sistema MySQL - Continuidade do Sistema Mysql Manager")
    st.subheader(" Mysql Manager - QUERYS ")
    
    # Banner
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
    ">
        <h2 style="color: white;">Tudo para dominar MySQL</h2>
        <p>Teoria • Prática • Projetos Reais</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 📚 Guia Completo")
            st.write("Aprenda do zero ao avançado")
            if st.button("Estudar", key="btn_guia"):
                st.session_state.pagina = "guia"
    
    with col2:
        with st.container(border=True):
            st.markdown("### 🎯 Exercícios")
            st.write("Pratique com desafios")
            if st.button("Praticar", key="btn_exercicios"):
                st.session_state.pagina = "exercicios"
    
    with col3:
        with st.container(border=True):
            st.markdown("### 🔍 Query Editor")
            st.write("Ambiente SQL real")
            if st.button("Usar Editor", key="btn_editor"):
                st.session_state.pagina = "query_editor"

# ============ PÁGINA: QUERY EDITOR (COMPLETO) ============
def pagina_query_editor():
    st.title("🔍 Criar Querys em SQL")
    
    # Seção 1: Seleção do banco
    st.subheader("1. 📁 Selecione um Banco")
    
    conexao = conectar_mysql()
    if not conexao:
        st.error("Não foi possível conectar ao MySQL")
        return
    
    cursor = conexao.cursor()
    cursor.execute("SHOW DATABASES")
    bancos = [db[0] for db in cursor.fetchall() 
             if db[0] not in ['information_schema', 'mysql', 'performance_schema', 'sys']]
    cursor.close()
    conexao.close()
    
    if not bancos:
        st.error("Nenhum banco disponível!")
        return
    
    banco_selecionado = st.selectbox("Banco:", bancos)
    st.success(f"✅ Banco: **{banco_selecionado}**")
    
    # Seção 2: Editor
    st.subheader("2. 📝 Editor SQL")
    # CSS customizado para o text_area
    st.markdown("""
    <style>
        .stTextArea textarea {
            background-color: #001100;  /* Fundo verde muito escuro */
            color: #00FF41;            /* VERDE NEON */
            font-family: 'Monaco', 'Ubuntu Mono', monospace;
            font-size: 15px;
            border: 2px solid #003300;
            text-shadow: 0 0 5px #00FF41;  /* Brilho sutil */
        }
    </style>
    """, unsafe_allow_html=True)
    
    query = st.text_area(
        "Digite sua query:",
        value="SELECT 'Hello MySQL' as teste",
        height=350,
        placeholder="Ex: SELECT * FROM tabela LIMIT 10;"
    )
    
    # Botões
    col1, col2 = st.columns([3, 1])
    with col1:
        executar = st.button("▶️ Executar Query", type="primary", use_container_width=True)
    with col2:
        if st.button("📚 Exemplos", use_container_width=True):
            with st.expander("Exemplos", expanded=True):
                st.code("""
-- Ver tabelas
SHOW TABLES;

-- Ver estrutura
DESCRIBE nome_tabela;

-- Selecionar dados
SELECT * FROM nome_tabela LIMIT 10;

-- Criar tabela
CREATE TABLE teste (
    id INT PRIMARY KEY,
    nome VARCHAR(100)
);
                """, language="sql")
    
    # Seção 3: Execução
    if executar and query.strip():
        st.subheader("3. 📊 Resultados")
        
        conexao = conectar_mysql(banco_selecionado)
        if not conexao:
            return
        
        cursor = conexao.cursor()
        
        try:
            with st.spinner("Executando..."):
                cursor.execute(query)
                
                if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE')):
                    resultados = cursor.fetchall()
                    
                    if cursor.description:
                        colunas = [desc[0] for desc in cursor.description]
                        
                        if resultados:
                            df = pd.DataFrame(resultados, columns=colunas)
                            st.success(f"✅ {len(df)} linha(s) retornada(s)")
                            st.dataframe(df, use_container_width=True)
                            
                            # Download
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                "⬇️ Baixar CSV",
                                csv,
                                f"resultados_{banco_selecionado}.csv",
                                "text/csv"
                            )
                        else:
                            st.info("✅ Query executada, mas sem resultados.")
                    else:
                        st.info("✅ Query executada com sucesso.")
                
                else:
                    linhas = cursor.rowcount
                    conexao.commit()
                    st.success(f"✅ Query executada! Linhas afetadas: {linhas}")
        
        except Error as e:
            st.error(f"❌ Erro: {e}")
            conexao.rollback()
        
        finally:
            cursor.close()
            conexao.close()
    
    # Botão voltar
    st.markdown("---")
    if st.button("🏠 Voltar para Home"):
        st.session_state.pagina = "home"

# ============ PÁGINA: GUIA ============
def pagina_guia():
    st.title("📚 Guia MySQL")
    
    # Menu do guia
    secao = st.session_state.guia_secao
    
    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
    with col_g1:
        if st.button("🗄️ Básico", use_container_width=True):
            st.session_state.guia_secao = "basico"
    with col_g2:
        if st.button("🔍 Consultas", use_container_width=True):
            st.session_state.guia_secao = "consultas"
    with col_g3:
        if st.button("🏗️ Tabelas", use_container_width=True):
            st.session_state.guia_secao = "tabelas"
    with col_g4:
        if st.button("⚡ Avançado", use_container_width=True):
            st.session_state.guia_secao = "avancado"
    
    st.markdown("---")
    
    # Conteúdo baseado na seção
    if secao == "basico":
        st.subheader("🗄️ Conceitos Básicos")
        st.write("""
        **MySQL** é um sistema de gerenciamento de banco de dados relacional.
        
        **Exemplo de criação:**
        """)
        st.code("""
CREATE DATABASE meu_banco;
USE meu_banco;

CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100),
    email VARCHAR(150) UNIQUE
);
        """, language="sql")
    
    elif secao == "consultas":
        st.subheader("🔍 Consultas SQL")
        st.code("""
-- SELECT básico
SELECT * FROM tabela;

-- SELECT com filtro
SELECT nome, email 
FROM usuarios 
WHERE ativo = 1;

-- SELECT com ordenação
SELECT * FROM produtos 
ORDER BY preco DESC;
        """, language="sql")
    
    # Botão voltar
    st.markdown("---")
    if st.button("🏠 Voltar para Home", key="voltar_guia"):
        st.session_state.pagina = "home"

# ============ PÁGINA: EXERCÍCIOS ============
def pagina_exercicios():
    st.title("🎯 Exercícios MySQL")
    
    nivel = st.radio(
        "Nível:",
        ["🥉 Iniciante", "🥈 Intermediário", "🥇 Avançado"],
        horizontal=True
    )
    
    with st.container(border=True):
        st.write("**Exercício:** Selecione todos os produtos com preço maior que 1000")
        
        resposta = st.text_area("Sua query:", height=80)
        
        if st.button("✅ Verificar"):
            if resposta.strip():
                st.info("Verificação: Em uma versão completa, esta query seria executada e avaliada!")
            else:
                st.warning("Digite sua resposta primeiro!")
    
    # Botão voltar
    st.markdown("---")
    if st.button("🏠 Voltar para Home"):
        st.session_state.pagina = "home"

# ============ PÁGINA: MYSQL MANAGER ============
def pagina_mysql_manager():
    st.title("⚙️ MySQL Manager")
    
    st.info("""
    Esta funcionalidade está em desenvolvimento.
    
    **Funcionalidades planejadas:**
    - Gerenciamento de bancos
    - Criação/edição de tabelas
    - Inserção/edição de dados
    - Visualização de relacionamentos
    """)
    
    # Botão voltar
    st.markdown("---")
    if st.button("🏠 Voltar para Home"):
        st.session_state.pagina = "home"

# ============ ROTEADOR PRINCIPAL ============
pagina = st.session_state.pagina

if pagina == "home":
    pagina_home()
elif pagina == "guia":
    pagina_guia()
elif pagina == "exercicios":
    pagina_exercicios()
elif pagina == "query_editor":
    pagina_query_editor()  
elif pagina == "mysql_manager":
    pagina_mysql_manager()

# ============ RODAPÉ ============
st.markdown("---")
st.caption("✨ Sistema MySQL - Tudo em um só lugar | Desenvolvido com Streamlit")