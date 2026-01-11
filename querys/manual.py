 # pages/1_guia_mysql.py
import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

st.set_page_config(
    page_title="📚 Guia MySQL",
    page_icon="📖",
    layout="wide"
)

st.title("📄 Manual MYSQL")
st.write("Esta é a 1ª página ")

# Link para página 2
if st.button("➡️ Ir para Página de Exercicios"):
    st.switch_page("pages/exercicios.py")

st.markdown("---")
st.write("Voltar para:")
if st.button("🏠 Página Principal"):
    st.switch_page("app.py")
    
   

# CSS para melhorar visualização
st.markdown("""
<style>
.guia-card {
    background: white;
    padding: 25px;
    border-radius: 15px;
    border-left: 5px solid #4CAF50;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.code-block {
    background: #2d2d2d;
    color: #f8f8f2;
    padding: 15px;
    border-radius: 8px;
    font-family: 'Courier New', monospace;
    margin: 10px 0;
}
.topic-title {
    color: #0D47A1;
    border-bottom: 2px solid #0D47A1;
    padding-bottom: 5px;
}
</style>
""", unsafe_allow_html=True)

st.title("📚 Guia Completo MySQL")
st.markdown("---")

# ============ MENU RÁPIDO ============
st.subheader("🎯 Navegação Rápida")
col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)

with col_nav1:
    if st.button("🗄️ Básico", use_container_width=True):
        st.session_state.guia_secao = "basico"
        st.rerun()

with col_nav2:
    if st.button("🔍 Consultas", use_container_width=True):
        st.session_state.guia_secao = "consultas"
        st.rerun()

with col_nav3:
    if st.button("🏗️ Tabelas", use_container_width=True):
        st.session_state.guia_secao = "tabelas"
        st.rerun()

with col_nav4:
    if st.button("⚡ Avançado", use_container_width=True):
        st.session_state.guia_secao = "avancado"
        st.rerun()

# Seção atual
secao = st.session_state.get("guia_secao", "basico")

# ============ SEÇÃO: BÁSICO ============
if secao == "basico":
    st.markdown('<h2 class="topic-title">🗄️ Fundamentos do MySQL</h2>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="guia-card">', unsafe_allow_html=True)
        
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown("### 📝 O que é MySQL?")
            st.write("""
            MySQL é um sistema de gerenciamento de banco de dados relacional (RDBMS) open-source.
            
            **Principais características:**
            - ✅ Gratuito e open-source
            - ⚡ Rápido e confiável
            - 🔒 Seguro
            - 📊 Suporte a grandes volumes de dados
            - 🔗 Suporte a transações ACID
            """)
            
            st.markdown("### 🎯 Conceitos Básicos")
            st.write("""
            **Banco de Dados:** Coleção de dados organizados  
            **Tabela:** Estrutura com linhas e colunas  
            **Linha/Registro:** Um item na tabela  
            **Coluna/Campo:** Um atributo dos dados  
            **Chave Primária:** Identificador único  
            **Chave Estrangeira:** Relacionamento entre tabelas
            """)
        
        with col_info2:
            st.markdown("### 📊 Tipos de Dados Comuns")
            
            tipos = {
                "INT": "Números inteiros",
                "VARCHAR(n)": "Texto (até n caracteres)",
                "TEXT": "Texto longo",
                "DATE": "Data (YYYY-MM-DD)",
                "DATETIME": "Data e hora",
                "DECIMAL(m,n)": "Números decimais",
                "BOOLEAN": "Verdadeiro/Falso"
            }
            
            for tipo, desc in tipos.items():
                st.write(f"**`{tipo}`** - {desc}")
            
            st.markdown("### 🔑 Tipos de Chaves")
            st.write("""
            **PRIMARY KEY:** Identificador único obrigatório  
            **FOREIGN KEY:** Referência a outra tabela  
            **UNIQUE KEY:** Valor único (pode ser nulo)  
            **INDEX:** Acelera buscas (não único)
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Exemplos básicos
    st.markdown("### 💻 Exemplos Práticos")
    
    tab_ex1, tab_ex2, tab_ex3 = st.tabs(["Criar Banco", "Usar Banco", "Mostrar Bancos"])
    
    with tab_ex1:
        st.markdown('<div class="code-block">', unsafe_allow_html=True)
        st.code("""
-- Criar um novo banco de dados
CREATE DATABASE meu_banco;

-- Criar com codificação específica
CREATE DATABASE meu_banco 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
        """, language="sql")
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("**Explicação:** Cria um novo banco vazio.")
    
    with tab_ex2:
        st.markdown('<div class="code-block">', unsafe_allow_html=True)
        st.code("""
-- Selecionar banco para usar
USE meu_banco;

-- Verificar banco atual
SELECT DATABASE();
        """, language="sql")
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("**Explicação:** Define qual banco será usado pelos próximos comandos.")
    
    with tab_ex3:
        st.markdown('<div class="code-block">', unsafe_allow_html=True)
        st.code("""
-- Ver todos os bancos
SHOW DATABASES;

-- Ver bancos com filtro
SHOW DATABASES LIKE '%test%';
        """, language="sql")
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("**Explicação:** Lista todos os bancos disponíveis.")

# ============ SEÇÃO: CONSULTAS ============
elif secao == "consultas":
    st.markdown('<h2 class="topic-title">🔍 Consultas SQL</h2>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="guia-card">', unsafe_allow_html=True)
        
        st.markdown("### 🎯 SELECT - Consultar dados")
        
        col_select1, col_select2 = st.columns(2)
        
        with col_select1:
            st.markdown("**Sintaxe Básica:**")
            st.markdown('<div class="code-block">', unsafe_allow_html=True)
            st.code("""
SELECT coluna1, coluna2, ...
FROM tabela
WHERE condição
ORDER BY coluna
LIMIT n;
            """, language="sql")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_select2:
            st.markdown("**Exemplo Prático:**")
            st.markdown('<div class="code-block">', unsafe_allow_html=True)
            st.code("""
SELECT nome, email, data_nascimento
FROM usuarios
WHERE ativo = 1
ORDER BY nome ASC
LIMIT 10;
            """, language="sql")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### 🎲 Funções de Agregação")
        
        funcoes = [
            ("COUNT()", "Contar registros"),
            ("SUM()", "Somar valores"),
            ("AVG()", "Média dos valores"),
            ("MIN()", "Valor mínimo"),
            ("MAX()", "Valor máximo"),
            ("GROUP_CONCAT()", "Concatenar valores")
        ]
        
        cols = st.columns(3)
        for i, (funcao, desc) in enumerate(funcoes):
            with cols[i % 3]:
                st.metric(funcao, desc)
        
        st.markdown("### 🔗 JOIN - Unir tabelas")
        
        tab_join1, tab_join2, tab_join3, tab_join4 = st.tabs(["INNER", "LEFT", "RIGHT", "FULL"])
        
        with tab_join1:
            st.write("**INNER JOIN:** Apenas registros com correspondência")
            st.code("""
SELECT u.nome, p.titulo
FROM usuarios u
INNER JOIN posts p ON u.id = p.usuario_id;
            """, language="sql")
        
        with tab_join2:
            st.write("**LEFT JOIN:** Todos da esquerda + correspondências")
            st.code("""
SELECT u.nome, p.titulo
FROM usuarios u
LEFT JOIN posts p ON u.id = p.usuario_id;
            """, language="sql")
        
        with tab_join3:
            st.write("**RIGHT JOIN:** Todos da direita + correspondências")
            st.code("""
SELECT u.nome, p.titulo
FROM usuarios u
RIGHT JOIN posts p ON u.id = p.usuario_id;
            """, language="sql")
        
        with tab_join4:
            st.write("**FULL JOIN:** Todos os registros (MySQL não tem nativo)")
            st.code("""
SELECT u.nome, p.titulo
FROM usuarios u
LEFT JOIN posts p ON u.id = p.usuario_id
UNION
SELECT u.nome, p.titulo
FROM usuarios u
RIGHT JOIN posts p ON u.id = p.usuario_id;
            """, language="sql")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============ SEÇÃO: TABELAS ============
elif secao == "tabelas":
    st.markdown('<h2 class="topic-title">🏗️ Gerenciamento de Tabelas</h2>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="guia-card">', unsafe_allow_html=True)
        
        st.markdown("### 📋 Criar Tabela")
        
        col_create1, col_create2 = st.columns(2)
        
        with col_create1:
            st.markdown("**Exemplo Completo:**")
            st.markdown('<div class="code-block">', unsafe_allow_html=True)
            st.code("""
CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    data_nascimento DATE,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nome (nome),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """, language="sql")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_create2:
            st.markdown("**Modificadores Comuns:**")
            
            modificadores = [
                ("NOT NULL", "Campo obrigatório"),
                ("DEFAULT valor", "Valor padrão"),
                ("AUTO_INCREMENT", "Auto incremento"),
                ("UNIQUE", "Valor único"),
                ("PRIMARY KEY", "Chave primária"),
                ("CHECK (condição)", "Validação")
            ]
            
            for mod, desc in modificadores:
                st.write(f"**`{mod}`** - {desc}")
        
        st.markdown("### 🔧 Alterar Tabela")
        
        tab_alter1, tab_alter2, tab_alter3, tab_alter4 = st.tabs(["Add", "Modify", "Drop", "Rename"])
        
        with tab_alter1:
            st.write("**Adicionar coluna:**")
            st.code("ALTER TABLE usuarios ADD COLUMN telefone VARCHAR(20);", language="sql")
        
        with tab_alter2:
            st.write("**Modificar coluna:**")
            st.code("ALTER TABLE usuarios MODIFY COLUMN nome VARCHAR(150);", language="sql")
        
        with tab_alter3:
            st.write("**Remover coluna:**")
            st.code("ALTER TABLE usuarios DROP COLUMN telefone;", language="sql")
        
        with tab_alter4:
            st.write("**Renomear tabela:**")
            st.code("ALTER TABLE usuarios RENAME TO clientes;", language="sql")
        
        st.markdown("### 📊 Ver Estrutura")
        
        col_struct1, col_struct2 = st.columns(2)
        
        with col_struct1:
            st.write("**Ver colunas:**")
            st.code("DESCRIBE usuarios;", language="sql")
            st.code("SHOW COLUMNS FROM usuarios;", language="sql")
        
        with col_struct2:
            st.write("**Ver índices:**")
            st.code("SHOW INDEX FROM usuarios;", language="sql")
            st.write("**Ver SQL de criação:**")
            st.code("SHOW CREATE TABLE usuarios;", language="sql")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============ SEÇÃO: AVANÇADO ============
elif secao == "avancado":
    st.markdown('<h2 class="topic-title">⚡ Tópicos Avançados</h2>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="guia-card">', unsafe_allow_html=True)
        
        st.markdown("### 🔒 Transações ACID")
        
        st.write("""
        **Atomicidade:** Todas as operações são executadas ou nenhuma  
        **Consistência:** Dados sempre em estado válido  
        **Isolamento:** Transações não interferem entre si  
        **Durabilidade:** Alterações persistem após commit
        """)
        
        st.markdown('<div class="code-block">', unsafe_allow_html=True)
        st.code("""
START TRANSACTION;

-- Operações
INSERT INTO conta (cliente_id, saldo) VALUES (1, 1000);
UPDATE conta SET saldo = saldo - 100 WHERE cliente_id = 1;
UPDATE conta SET saldo = saldo + 100 WHERE cliente_id = 2;

-- Confirmar
COMMIT;

-- Ou cancelar em caso de erro
ROLLBACK;
        """, language="sql")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### 🎭 Stored Procedures")
        
        col_sp1, col_sp2 = st.columns(2)
        
        with col_sp1:
            st.write("**Criar Procedure:**")
            st.code("""
DELIMITER //
CREATE PROCEDURE sp_usuarios_ativos()
BEGIN
    SELECT * FROM usuarios WHERE ativo = 1;
END //
DELIMITER ;
            """, language="sql")
        
        with col_sp2:
            st.write("**Chamar Procedure:**")
            st.code("CALL sp_usuarios_ativos();", language="sql")
            st.write("**Remover Procedure:**")
            st.code("DROP PROCEDURE sp_usuarios_ativos;", language="sql")
        
        st.markdown("### 🔍 Views")
        
        st.write("**Criar View:**")
        st.code("""
CREATE VIEW vw_usuarios_ativos AS
SELECT id, nome, email 
FROM usuarios 
WHERE ativo = 1;
        """, language="sql")
        
        st.write("**Usar como tabela:**")
        st.code("SELECT * FROM vw_usuarios_ativos;", language="sql")
        
        st.markdown("### ⚡ Triggers")
        
        st.code("""
CREATE TRIGGER tr_log_usuario_insert
AFTER INSERT ON usuarios
FOR EACH ROW
BEGIN
    INSERT INTO log_usuarios (acao, usuario_id, data)
    VALUES ('INSERT', NEW.id, NOW());
END;
        """, language="sql")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============ RECURSOS ADICIONAIS ============
st.markdown("---")
st.subheader("📚 Recursos para Aprender Mais")

col_rec1, col_rec2, col_rec3 = st.columns(3)

with col_rec1:
    st.markdown("**🎓 Cursos Online**")
    st.write("- MySQL Tutorial (w3schools)")
    st.write("- MySQL for Beginners (Udemy)")
    st.write("- Database Foundations (Coursera)")

with col_rec2:
    st.markdown("**📖 Documentação**")
    st.write("- [MySQL Official Docs](https://dev.mysql.com/doc/)")
    st.write("- [MySQL Cheat Sheet](https://devhints.io/mysql)")
    st.write("- [SQL Style Guide](https://www.sqlstyle.guide/)")

with col_rec3:
    st.markdown("**💡 Prática**")
    st.write("- SQLZoo (exercícios interativos)")
    st.write("- LeetCode (problemas SQL)")
    st.write("- HackerRank (desafios SQL)")

# ============ BOTÃO PARA PRATICAR ============
st.markdown("---")
col_practice1, col_practice2 = st.columns([3, 1])

with col_practice1:
    st.info("💡 **Aprenda fazendo!** A teoria é importante, mas a prática consolida o conhecimento.")

with col_practice2:
    if st.button("🎯 Ir para Exercícios", type="primary", use_container_width=True):
        st.switch_page("pages/2_exercicios.py")

st.caption("✨ Guia criado para o MySQL Manager Pro")