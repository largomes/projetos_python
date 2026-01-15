# app.py - Página principal com navegação
import streamlit as st

# ============ CONFIGURAÇÃO ============
st.set_page_config(
    page_title="MySQL System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ ESTADO DA APLICAÇÃO ============
if "pagina" not in st.session_state:
    st.session_state.pagina = "home"

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
    
    # Menu Principal
    st.subheader("📚 Aprendizado")
    
    # Botões de navegação
    if st.button("🏠 Página Inicial", use_container_width=True):
        st.session_state.pagina = "home"
        st.rerun()
    
    if st.button("📚 Guia MySQL", use_container_width=True):
        st.session_state.pagina = "manual"
        st.rerun()
    
    if st.button("🎯 Exercícios", use_container_width=True):
        st.session_state.pagina = "exercicios"
        st.rerun()
    
    st.subheader("🔧 Ferramentas")
    
    if st.button("🔍 Query Editor", use_container_width=True, type="primary"):
        st.session_state.pagina = "query_editor"
        st.rerun()
    
    if st.button("⚙️ MySQL Manager", use_container_width=True):
        st.session_state.pagina = "mysql_manager"
        st.rerun()
        
    if st.button("🤖 NLP to SQL", use_container_width=True):
       st.session_state.pagina = "nlp_sql"
       st.rerun()    
    
    st.markdown("---")
    st.caption(f"📍 Página atual: {st.session_state.pagina}")

# ============ PÁGINA: HOME ============
def pagina_home():
    st.title("🏠 Sistema MySQL - Continuidade do Sistema Mysql Manager")
    st.subheader("Mysql Manager - QUERYS")
    
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
            if st.button("Estudar", key="btn_guia_home"):
                st.session_state.pagina = "manual"
                st.rerun()
    
    with col2:
        with st.container(border=True):
            st.markdown("### 🎯 Exercícios")
            st.write("Pratique com desafios")
            if st.button("Praticar", key="btn_exercicios_home"):
                st.session_state.pagina = "exercicios"
                st.rerun()
    
    with col3:
        with st.container(border=True):
            st.markdown("### 🔍 Query Editor")
            st.write("Ambiente SQL real")
            if st.button("Usar Editor", key="btn_editor_home"):
                st.session_state.pagina = "query_editor"
                st.rerun()
    
    # Explicação do sistema
    with st.expander("ℹ️ Como usar este sistema", expanded=True):
        st.markdown("""
        ### Estrutura do Sistema:
        
        1. **Página Inicial** (esta) - Visão geral do sistema
        2. **Guia MySQL** (`manual.py`) - Material de estudo completo
        3. **Exercícios** (`exercicios.py`) - Prática com desafios
        4. **Query Editor** (`query_editor.py`) - Ambiente de execução SQL
        5. **MySQL Manager** - Gerenciamento de bancos (em desenvolvimento)
        
        ### 📁 Arquivos do projeto:
        ```
        seu_projeto/
        ├── app.py              ← Este arquivo (navegação principal)
        ├── manual.py           ← Guia de estudo MySQL
        ├── exercicios.py       ← Exercícios práticos
        ├── query_editor.py     ← Editor SQL completo
        └── requirements.txt    ← Dependências
        ```
        """)

# ============ ROTEADOR PRINCIPAL ============
def main():
    pagina = st.session_state.pagina
    
    # Verificar qual página mostrar
    if pagina == "home":
        pagina_home()
    
    elif pagina == "manual":
        # Importar e executar a página manual.py
        try:
            import manual
            manual.pagina_guia()
        except Exception as e:
            st.error(f"Erro ao carregar a página manual: {e}")
            st.info("Crie o arquivo `manual.py` com a função `pagina_guia()`")
            if st.button("Voltar para Home"):
                st.session_state.pagina = "home"
                st.rerun()
    
    elif pagina == "exercicios":
        # Importar e executar a página exercicios.py
        try:
            import exercicios
            exercicios.pagina_exercicios()
        except Exception as e:
            st.error(f"Erro ao carregar a página exercicios: {e}")
            st.info("Crie o arquivo `exercicios.py` com a função `pagina_exercicios()`")
            if st.button("Voltar para Home"):
                st.session_state.pagina = "home"
                st.rerun()
    
    elif pagina == "query_editor":
        # Importar e executar a página query_editor.py
        try:
            import query_editor
            query_editor.pagina_query_editor()
        except Exception as e:
            st.error(f"Erro ao carregar a página query_editor: {e}")
            st.info("Crie o arquivo `query_editor.py` com a função `pagina_query_editor()`")
            if st.button("Voltar para Home"):
                st.session_state.pagina = "home"
                st.rerun()
    
    elif pagina == "mysql_manager":
        st.title("⚙️ MySQL Manager")
        st.info("Esta funcionalidade está em desenvolvimento.")
        if st.button("🏠 Voltar para Home"):
            st.session_state.pagina = "home"
            st.rerun()
            
    elif pagina == "nlp_sql":
        try:
            import nlp_sql  # seu novo arquivo
            nlp_sql.pagina_nlp_sql()
        except:
            st.error("Módulo não encontrado")       
    
    # Rodapé
    st.markdown("---")
    st.caption("✨ Sistema MySQL - Página Principal | Desenvolvido com Streamlit")

if __name__ == "__main__":
    main()