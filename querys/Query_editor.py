# pages/3_query_editor.py - EDITOR DE QUERIES
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error

st.set_page_config(
    page_title="Editor de Queries",
    page_icon="🔍"
)

st.title("🔍 Criar Queries em SQL")
st.markdown("---")
# Link para página 1
if st.button("⬅️ Ir para Página de Manual   "):
    st.switch_page("pages/Manual.py")
    # Link para página 1
if st.button("⬅️ Ir para Página de exercicios"):
    st.switch_page("pages/exercicios.py")

if st.button("🏠 Página Principal            "):
    st.switch_page("app.py")
st.markdown("---")

# ============ FUNÇÃO DE CONEXÃO ============
def conectar_mysql(database=None):
    """Conecta ao MySQL"""
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",      # ALTERE AQUI
            password="",      # SUA SENHA AQUI
            database=database
        )
        return conexao
    except Error as e:
        st.error(f"❌ Erro de conexão: {e}")
        return None

# ============ SELEÇÃO DO BANCO ============
st.subheader("1. 📁 Selecione um Banco")

# Listar bancos
conexao = conectar_mysql()
if not conexao:
    st.stop()

cursor = conexao.cursor()
cursor.execute("SHOW DATABASES")
bancos = [db[0] for db in cursor.fetchall() 
         if db[0] not in ['information_schema', 'mysql', 'performance_schema', 'sys']]
cursor.close()
conexao.close()

if not bancos:
    st.error("❌ Nenhum banco disponível!")
    st.stop()

banco_selecionado = st.selectbox("Escolha:", bancos)
st.success(f"✅ Banco selecionado: **{banco_selecionado}**")

# ============ EDITOR SQL ============
st.subheader("2. 📝 Digite sua Query SQL")

query = st.text_area(
    "Query:",
    value="SELECT * FROM sua_tabela LIMIT 10",
    height=120,
    placeholder="Ex: SELECT * FROM tabela LIMIT 5",
    key="query_input"
)

col1, col2 = st.columns(2)
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

-- Contar registros
SELECT COUNT(*) FROM nome_tabela;
            """, language="sql")

# ============ EXECUTAR ============
if executar and query.strip():
    st.subheader("3. 📊 Resultados")
    
    conexao = conectar_mysql(banco_selecionado)
    if not conexao:
        st.stop()
    
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

# ============ TABELAS DO BANCO ============
st.markdown("---")
if st.button("🗃️ Listar Tabelas deste Banco", use_container_width=True):
    conexao = conectar_mysql(banco_selecionado)
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("SHOW TABLES")
        tabelas = cursor.fetchall()
        cursor.close()
        conexao.close()
        
        if tabelas:
            st.write(f"**Tabelas ({len(tabelas)}):**")
            for tabela in tabelas:
                st.code(tabela[0])
        else:
            st.info("📭 Nenhuma tabela encontrada.")