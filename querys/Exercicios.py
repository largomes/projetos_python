# pages/2_exercicios.py
import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

st.set_page_config(
    page_title="🎯 Exercícios MySQL",
    page_icon="💪",
    layout="wide"
)

st.title("📄 Página de Exercicios praticos")
st.write("Esta é a página 2")

# Link para página 1
if st.button("⬅️ Ir para Página de Manual"):
    st.switch_page("pages/manual.py")
    # Link para página 1
if st.button("⬅️ Ir para Página de querys"):
    st.switch_page("pages/Query_editor.py")

if st.button("🏠 Página Principal"):
    st.switch_page("app.py")
st.markdown("---")
# Estilo
st.markdown("""
<style>
.exercicio-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.solucao-card {
    background: #E8F5E9;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #4CAF50;
    margin: 10px 0;
}
.dica-card {
    background: #FFF3E0;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #FF9800;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

st.title("🎯 Playground de Exercícios MySQL")
st.markdown("---")

# ============ BANCO DE DADOS EXEMPLO ============
st.subheader("📋 Banco de Dados de Exemplo")

col_db1, col_db2, col_db3 = st.columns(3)

with col_db1:
    st.markdown("**🗃️ Tabela: `clientes`**")
    st.code("""
id | nome      | email               | cidade       | saldo
---|-----------|---------------------|--------------|------
1  | João      | joao@email.com      | São Paulo    | 1500
2  | Maria     | maria@email.com     | Rio de Janeiro | 2300
3  | Pedro     | pedro@email.com     | Belo Horizonte| 1800
4  | Ana       | ana@email.com       | São Paulo    | 3200
5  | Carlos    | carlos@email.com    | Curitiba     | 950
    """, language="text")

with col_db2:
    st.markdown("**📦 Tabela: `produtos`**")
    st.code("""
id | nome          | categoria   | preco | estoque
---|---------------|-------------|-------|--------
1  | Notebook      | Eletrônicos | 3500  | 15
2  | Smartphone    | Eletrônicos | 2200  | 30
3  | Mesa          | Móveis      | 800   | 8
4  | Cadeira       | Móveis      | 450   | 25
5  | Livro SQL     | Livros      | 120   | 50
    """, language="text")

with col_db3:
    st.markdown("**🛒 Tabela: `vendas`**")
    st.code("""
id | cliente_id | produto_id | quantidade | data
---|------------|------------|------------|-----------
1  | 1          | 1          | 1          | 2024-01-15
2  | 2          | 2          | 2          | 2024-01-16
3  | 1          | 5          | 3          | 2024-01-17
4  | 3          | 3          | 1          | 2024-01-18
5  | 4          | 4          | 4          | 2024-01-19
    """, language="text")

st.markdown("---")

# ============ EXERCÍCIOS ============
st.subheader("💪 Escolha um Nível de Dificuldade")

nivel = st.radio(
    "Selecione:",
    ["🥉 Iniciante", "🥈 Intermediário", "🥇 Avançado"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

# Exercícios por nível
if "🥉 Iniciante" in nivel:
    st.markdown('<div class="exercicio-card">', unsafe_allow_html=True)
    st.markdown("### 🥉 Nível Iniciante")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Exercício 1
    with st.expander("📝 Exercício 1: SELECT Básico", expanded=True):
        st.write("**Enunciado:** Selecione todos os clientes da cidade de 'São Paulo'")
        
        col_ex1_1, col_ex1_2 = st.columns([3, 1])
        
        with col_ex1_1:
            resposta = st.text_area(
                "Digite sua query:",
                placeholder="SELECT ... FROM ... WHERE ...",
                height=80,
                key="ex1"
            )
        
        with col_ex1_2:
            st.write("")  # Espaço
            st.write("")  # Espaço
            if st.button("✅ Verificar", key="btn_ex1"):
                if "SELECT" in resposta.upper() and "FROM" in resposta.upper() and "WHERE" in resposta.upper() and "SÃO PAULO" in resposta.upper().replace("'", "").replace('"', ""):
                    st.success("✅ Correto!")
                    st.balloons()
                else:
                    st.error("❌ Tente novamente!")
        
        if st.button("💡 Ver Dica", key="dica_ex1"):
            with st.container():
                st.markdown('<div class="dica-card">', unsafe_allow_html=True)
                st.write("**Dica:** Use `SELECT * FROM clientes WHERE cidade = 'São Paulo'`")
                st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("👁️ Ver Solução", key="sol_ex1"):
            with st.container():
                st.markdown('<div class="solucao-card">', unsafe_allow_html=True)
                st.code("SELECT * FROM clientes WHERE cidade = 'São Paulo';", language="sql")
                st.write("**Explicação:** Seleciona todas as colunas (`*`) da tabela `clientes` onde a cidade é 'São Paulo'.")
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Exercício 2
    with st.expander("📝 Exercício 2: ORDER BY", expanded=False):
        st.write("**Enunciado:** Liste os produtos do mais caro para o mais barato")
        
        col_ex2_1, col_ex2_2 = st.columns([3, 1])
        
        with col_ex2_1:
            resposta = st.text_area(
                "Digite sua query:",
                placeholder="SELECT ... FROM ... ORDER BY ...",
                height=80,
                key="ex2"
            )
        
        with col_ex2_2:
            st.write("")
            st.write("")
            if st.button("✅ Verificar", key="btn_ex2"):
                if "SELECT" in resposta.upper() and "FROM" in resposta.upper() and "ORDER BY" in resposta.upper() and "DESC" in resposta.upper():
                    st.success("✅ Correto!")
                else:
                    st.error("❌ Lembre-se de ordenar em ordem decrescente!")
        
        if st.button("💡 Ver Dica", key="dica_ex2"):
            with st.container():
                st.markdown('<div class="dica-card">', unsafe_allow_html=True)
                st.write("**Dica:** Use `ORDER BY preco DESC` para ordenar do maior para o menor")
                st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("👁️ Ver Solução", key="sol_ex2"):
            with st.container():
                st.markdown('<div class="solucao-card">', unsafe_allow_html=True)
                st.code("SELECT * FROM produtos ORDER BY preco DESC;", language="sql")
                st.write("**Explicação:** `ORDER BY` ordena os resultados. `DESC` significa decrescente.")
                st.markdown('</div>', unsafe_allow_html=True)

elif "🥈 Intermediário" in nivel:
    st.markdown('<div class="exercicio-card">', unsafe_allow_html=True)
    st.markdown("### 🥈 Nível Intermediário")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Exercício 3
    with st.expander("📝 Exercício 3: JOIN entre Tabelas", expanded=True):
        st.write("**Enunciado:** Mostre o nome do cliente e o produto que ele comprou")
        
        col_ex3_1, col_ex3_2 = st.columns([3, 1])
        
        with col_ex3_1:
            resposta = st.text_area(
                "Digite sua query:",
                placeholder="SELECT ... FROM ... JOIN ... ON ...",
                height=100,
                key="ex3"
            )
        
        with col_ex3_2:
            st.write("")
            st.write("")
            if st.button("✅ Verificar", key="btn_ex3"):
                if "JOIN" in resposta.upper() and "CLIENTES" in resposta.upper() and "PRODUTOS" in resposta.upper():
                    st.success("✅ Correto!")
                    st.balloons()
                else:
                    st.error("❌ Você precisa unir 3 tabelas!")
        
        if st.button("💡 Ver Dica", key="dica_ex3"):
            with st.container():
                st.markdown('<div class="dica-card">', unsafe_allow_html=True)
                st.write("**Dica:** Você precisa de dois JOINs: `vendas JOIN clientes` e `vendas JOIN produtos`")
                st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("👁️ Ver Solução", key="sol_ex3"):
            with st.container():
                st.markdown('<div class="solucao-card">', unsafe_allow_html=True)
                st.code("""
SELECT 
    c.nome AS cliente,
    p.nome AS produto,
    v.quantidade,
    v.data
FROM vendas v
JOIN clientes c ON v.cliente_id = c.id
JOIN produtos p ON v.produto_id = p.id;
                """, language="sql")
                st.write("**Explicação:** Unimos 3 tabelas através de chaves estrangeiras.")
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Exercício 4
    with st.expander("📝 Exercício 4: GROUP BY e Agregação", expanded=False):
        st.write("**Enunciado:** Calcule o total de vendas por cliente")
        
        col_ex4_1, col_ex4_2 = st.columns([3, 1])
        
        with col_ex4_1:
            resposta = st.text_area(
                "Digite sua query:",
                placeholder="SELECT ... SUM(...) ... GROUP BY ...",
                height=100,
                key="ex4"
            )
        
        with col_ex4_2:
            st.write("")
            st.write("")
            if st.button("✅ Verificar", key="btn_ex4"):
                if "SUM" in resposta.upper() and "GROUP BY" in resposta.upper():
                    st.success("✅ Correto!")
                else:
                    st.error("❌ Use SUM() para somar e GROUP BY para agrupar!")
        
        if st.button("💡 Ver Dica", key="dica_ex4"):
            with st.container():
                st.markdown('<div class="dica-card">', unsafe_allow_html=True)
                st.write("**Dica:** Você precisa somar `quantidade * preco`")
                st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("👁️ Ver Solução", key="sol_ex4"):
            with st.container():
                st.markdown('<div class="solucao-card">', unsafe_allow_html=True)
                st.code("""
SELECT 
    c.nome AS cliente,
    SUM(v.quantidade * p.preco) AS total_gasto
FROM vendas v
JOIN clientes c ON v.cliente_id = c.id
JOIN produtos p ON v.produto_id = p.id
GROUP BY c.id, c.nome
ORDER BY total_gasto DESC;
                """, language="sql")
                st.write("**Explicação:** Agrupamos por cliente e calculamos o total gasto.")
                st.markdown('</div>', unsafe_allow_html=True)

else:  # Avançado
    st.markdown('<div class="exercicio-card">', unsafe_allow_html=True)
    st.markdown("### 🥇 Nível Avançado")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Exercício 5
    with st.expander("📝 Exercício 5: Subquery", expanded=True):
        st.write("**Enunciado:** Encontre clientes que gastaram mais que a média geral")
        
        col_ex5_1, col_ex5_2 = st.columns([3, 1])
        
        with col_ex5_1:
            resposta = st.text_area(
                "Digite sua query:",
                placeholder="SELECT ... WHERE ... > (SELECT AVG(...) ...)",
                height=120,
                key="ex5"
            )
        
        with col_ex5_2:
            st.write("")
            st.write("")
            if st.button("✅ Verificar", key="btn_ex5"):
                if "SELECT" in resposta.upper() and "WHERE" in resposta.upper() and "SELECT" in resposta.upper()[resposta.upper().find("WHERE"):]:
                    st.success("✅ Correto!")
                    st.balloons()
                else:
                    st.error("❌ Você precisa de uma subquery!")
        
        if st.button("💡 Ver Dica", key="dica_ex5"):
            with st.container():
                st.markdown('<div class="dica-card">', unsafe_allow_html=True)
                st.write("**Dica:** A subquery calcula a média: `(SELECT AVG(...) FROM ...)`")
                st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("👁️ Ver Solução", key="sol_ex5"):
            with st.container():
                st.markdown('<div class="solucao-card">', unsafe_allow_html=True)
                st.code("""
SELECT 
    c.nome,
    SUM(v.quantidade * p.preco) AS total_gasto
FROM clientes c
JOIN vendas v ON c.id = v.cliente_id
JOIN produtos p ON v.produto_id = p.id
GROUP BY c.id, c.nome
HAVING total_gasto > (
    SELECT AVG(v2.quantidade * p2.preco)
    FROM vendas v2
    JOIN produtos p2 ON v2.produto_id = p2.id
);
                """, language="sql")
                st.write("**Explicação:** Subquery calcula média geral, HAVING filtra clientes acima dela.")
                st.markdown('</div>', unsafe_allow_html=True)

# ============ DESAFIO EXTRA ============
st.markdown("---")
with st.container():
    st.markdown('<div class="exercicio-card">', unsafe_allow_html=True)
    st.markdown("### 🏆 Desafio Bônus")
    
    st.write("**Crie uma query que:**")
    st.write("1. Mostre o cliente que mais gastou")
    st.write("2. Mostre o produto mais vendido")
    st.write("3. Calcule o faturamento total por mês")
    
    resposta_desafio = st.text_area(
        "Sua query completa:",
        height=150,
        placeholder="-- Sua solução aqui\nSELECT ...",
        key="desafio"
    )
    
    if st.button("🎯 Submeter Desafio", type="primary"):
        if resposta_desafio.strip():
            st.success("📤 Submetido! (Simulação)")
            st.info("Em uma versão real, esta query seria executada e avaliada automaticamente!")
        else:
            st.warning("Digite sua solução primeiro!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============ PRATICAR NO EDITOR ============
st.markdown("---")
col_practice1, col_practice2 = st.columns([3, 1])

with col_practice1:
    st.write("**💡 Aprendeu com os exercícios? Agora pratique no editor real!**")

with col_practice2:
    if st.button("🔍 Ir para Query Editor", type="secondary", use_container_width=True):
        st.switch_page("pages/3_query_editor.py")

# ============ ESTATÍSTICAS ============
st.markdown("---")
st.subheader("📊 Seu Progresso")

col_stats1, col_stats2, col_stats3 = st.columns(3)

with col_stats1:
    st.metric("🎯 Exercícios Completos", "0/8", "+0")

with col_stats2:
    st.metric("⏱️ Tempo Praticando", "0 min", "+0")

with col_stats3:
    st.metric("📈 Nível Atual", "Iniciante", "0%")

# ============ CERTIFICADO SIMULADO ============
st.markdown("---")
with st.expander("🏅 Gerar Certificado de Conclusão", expanded=False):
    nome = st.text_input("Seu nome para o certificado:")
    
    if nome and st.button("🎖️ Gerar Certificado"):
        st.success(f"🎉 Parabéns, {nome}!")
        
        st.markdown(f"""
        <div style="
            border: 5px solid gold;
            padding: 40px;
            text-align: center;
            background: white;
            border-radius: 20px;
            margin: 20px 0;
        ">
            <h1 style="color: #0D47A1;">🏆 Certificado de Conclusão</h1>
            <h2>MySQL Practice Challenge</h2>
            <h3>Concedido à</h3>
            <h1 style="color: #D32F2F;">{nome}</h1>
            <p>Por completar com sucesso os exercícios de prática SQL</p>
            <p><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y')}</p>
            <p>MySQL Manager Pro</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 Em uma versão completa, este certificado seria baixável em PDF!")

st.caption("✨ Exercícios criados para o MySQL Manager Pro - Aprenda fazendo!")    