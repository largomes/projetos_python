# nlp_sql.py - Conectado aos SEUS bancos reais
import streamlit as st
import re
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# ============ CONEXÃO COM SEUS BANCOS ============
def conectar_mysql(database=None):
    """CONECTA AOS SEUS BANCOS REAIS"""
    try:
        conexao = mysql.connector.connect(
            host="localhost",      # SEU host
            user="root",           # SEU usuário
            password="",           # SUA senha (a mesma que usa no query_editor)
            database=database      # Banco específico ou None para listar
        )
        return conexao
    except Error as e:
        st.error(f"Erro de conexão: {e}")
        return None

def obter_tabelas(banco):
    """OBTÉM TABELAS REAIS DO SEU BANCO"""
    try:
        conexao = conectar_mysql(banco)
        if not conexao:
            return []
        
        cursor = conexao.cursor()
        cursor.execute("SHOW TABLES")
        tabelas = [t[0] for t in cursor.fetchall()]
        cursor.close()
        conexao.close()
        return tabelas
    except Exception as e:
        st.error(f"Erro ao obter tabelas: {e}")
        return []

def obter_colunas(banco, tabela):
    """OBTÉM COLUNAS REAIS DA SUA TABELA"""
    try:
        conexao = conectar_mysql(banco)
        if not conexao:
            return []
        
        cursor = conexao.cursor()
        cursor.execute(f"DESCRIBE {tabela}")
        colunas_info = cursor.fetchall()
        
        # Extrair nomes das colunas e tipos
        colunas = []
        tipos_colunas = {}
        
        for col in colunas_info:
            nome_coluna = col[0]
            tipo_coluna = col[1]
            colunas.append(nome_coluna)
            tipos_colunas[nome_coluna] = tipo_coluna
        
        cursor.close()
        conexao.close()
        return colunas, tipos_colunas
    except Exception as e:
        st.warning(f"Não foi possível obter colunas de {tabela}: {e}")
        return [], {}

def obter_dados_amostra(banco, tabela, limite=3):
    """OBTÉM DADOS REAIS PARA ANÁLISE"""
    try:
        conexao = conectar_mysql(banco)
        if not conexao:
            return []
        
        cursor = conexao.cursor()
        cursor.execute(f"SELECT * FROM {tabela} LIMIT {limite}")
        dados = cursor.fetchall()
        
        if cursor.description:
            colunas = [desc[0] for desc in cursor.description]
            cursor.close()
            conexao.close()
            return dados, colunas
        else:
            cursor.close()
            conexao.close()
            return [], []
    except:
        return [], []

# ============ GERADOR INTELIGENTE (ANALISA SEUS DADOS REAIS) ============
class GeradorSQLInteligente:
    def __init__(self, banco):
        self.banco = banco
        self.analisar_banco()
    
    def analisar_banco(self):
        """ANALISA SEU BANCO REAL para entender a estrutura"""
        self.tabelas = obter_tabelas(self.banco)
        self.estrutura = {}
        
        for tabela in self.tabelas[:5]:  # Analisa as primeiras 5 tabelas
            colunas, tipos = obter_colunas(self.banco, tabela)
            dados_amostra, _ = obter_dados_amostra(self.banco, tabela, 2)
            
            self.estrutura[tabela] = {
                'colunas': colunas,
                'tipos': tipos,
                'tem_dados': len(dados_amostra) > 0,
                'colunas_texto': [c for c in colunas if any(kw in tipos.get(c, '').lower() for kw in ['char', 'text', 'varchar'])],
                'colunas_numericas': [c for c in colunas if any(kw in tipos.get(c, '').lower() for kw in ['int', 'decimal', 'float', 'double'])],
                'colunas_data': [c for c in colunas if any(kw in tipos.get(c, '').lower() for kw in ['date', 'time', 'timestamp'])],
            }
    
    def detectar_tabela_relevante(self, texto):
        """DETECTA qual tabela do SEU banco é mais relevante para o texto"""
        texto = texto.lower()
        
        # Primeiro, ver se o texto menciona alguma tabela existente
        for tabela in self.tabelas:
            if tabela.lower() in texto:
                return tabela
        
        # Se não mencionou, analisar contexto
        palavras_chave_tabela = {
            'cliente': ['cliente', 'clientes', 'usuário', 'usuarios', 'user', 'users', 'pessoa', 'pessoas'],
            'produto': ['produto', 'produtos', 'item', 'items', 'mercadoria', 'artigo'],
            'pedido': ['pedido', 'pedidos', 'venda', 'vendas', 'compra', 'compras', 'ordem', 'ordens'],
            'funcionario': ['funcionário', 'funcionarios', 'empregado', 'colaborador', 'staff'],
        }
        
        for tabela_padrao, palavras in palavras_chave_tabela.items():
            if any(palavra in texto for palavra in palavras):
                # Ver se existe tabela similar
                for tabela_real in self.tabelas:
                    if tabela_padrao in tabela_real.lower():
                        return tabela_real
        
        # Se não encontrou, usar a primeira tabela com dados
        for tabela in self.tabelas:
            if self.estrutura.get(tabela, {}).get('tem_dados', False):
                return tabela
        
        return self.tabelas[0] if self.tabelas else "tabela"
    
    def detectar_colunas_relevantes(self, tabela, texto):
        """DETECTA quais colunas da SUA tabela são relevantes"""
        if tabela not in self.estrutura:
            return ["*"]
        
        colunas_disponiveis = self.estrutura[tabela]['colunas']
        texto = texto.lower()
        colunas_detectadas = []
        
        # Verificar menções diretas a colunas
        for coluna in colunas_disponiveis:
            if coluna.lower() in texto:
                colunas_detectadas.append(coluna)
        
        # Se encontrou colunas específicas
        if colunas_detectadas:
            return colunas_detectadas[:5]  # Limita a 5 colunas
        
        # Se não, analisar por contexto
        palavras_chave = {
            'nome': ['nome', 'chamar', 'identificar'],
            'email': ['email', 'e-mail', 'correio'],
            'telefone': ['telefone', 'fone', 'contato', 'celular'],
            'data': ['data', 'dia', 'mês', 'ano', 'tempo', 'hora'],
            'valor': ['valor', 'preço', 'custo', 'dinheiro', 'total', 'soma'],
            'quantidade': ['quantidade', 'qtd', 'numero', 'número', 'contar'],
            'status': ['status', 'estado', 'situação', 'ativo'],
            'cidade': ['cidade', 'local', 'endereço', 'morada'],
        }
        
        for coluna_padrao, palavras in palavras_chave.items():
            if any(palavra in texto for palavra in palavras):
                # Ver se existe coluna similar na tabela real
                for coluna_real in colunas_disponiveis:
                    if coluna_padrao in coluna_real.lower():
                        colunas_detectadas.append(coluna_real)
                        break
        
        return colunas_detectadas if colunas_detectadas else ["*"]
    
    def gerar_condicoes(self, tabela, texto):
        """Gera condições WHERE baseadas nos SEUS dados"""
        if tabela not in self.estrutura:
            return ""
        
        condicoes = []
        texto = texto.lower()
        
        # 1. Condições por valores específicos (extrai do texto)
        # Padrão: "de lisboa", "com status ativo"
        padroes_valores = [
            (r'de\s+(\w+)', 'cidade'),  # "de lisboa"
            (r'com\s+(\w+)\s+(\w+)', None),  # "com status ativo"
            (r'(\w+)\s*=\s*[\'"]([^\'"]+)[\'"]', None),  # cidade='Lisboa'
        ]
        
        for padrao, tipo_default in padroes_valores:
            matches = re.finditer(padrao, texto)
            for match in matches:
                if tipo_default == 'cidade':
                    valor = match.group(1)
                    # Procurar coluna de cidade na tabela real
                    colunas_texto = self.estrutura[tabela]['colunas_texto']
                    coluna_cidade = next((c for c in colunas_texto if any(kw in c.lower() for kw in ['cidade', 'city', 'local'])), None)
                    if coluna_cidade:
                        condicoes.append(f"{coluna_cidade} = '{valor.capitalize()}'")
        
        # 2. Condições numéricas
        colunas_numericas = self.estrutura[tabela]['colunas_numericas']
        if colunas_numericas:
            coluna_valor = colunas_numericas[0]  # Primeira coluna numérica
            
            # Extrair comparações numéricas
            comparacoes = [
                (r'maior\s+(?:que|do\s+que)?\s*(\d+)', '>'),
                (r'menor\s+(?:que|do\s+que)?\s*(\d+)', '<'),
                (r'igual\s+a\s*(\d+)', '='),
                (r'entre\s+(\d+)\s+e\s+(\d+)', 'BETWEEN'),
            ]
            
            for padrao, operador in comparacoes:
                match = re.search(padrao, texto)
                if match:
                    if operador == 'BETWEEN':
                        condicoes.append(f"{coluna_valor} BETWEEN {match.group(1)} AND {match.group(2)}")
                    else:
                        condicoes.append(f"{coluna_valor} {operador} {match.group(1)}")
                    break
        
        # 3. Condições de data
        colunas_data = self.estrutura[tabela]['colunas_data']
        if colunas_data:
            coluna_data = colunas_data[0]
            
            periodos = [
                ('hoje', "= CURDATE()"),
                ('ontem', "= DATE_SUB(CURDATE(), INTERVAL 1 DAY)"),
                ('esta semana', ">= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"),
                ('este mês', "MONTH({}) = MONTH(CURDATE())"),
                ('este ano', "YEAR({}) = YEAR(CURDATE())"),
                ('último mês', "{} BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND CURDATE()"),
            ]
            
            for periodo, condicao in periodos:
                if periodo in texto:
                    if '{}' in condicao:
                        condicoes.append(condicao.format(coluna_data))
                    else:
                        condicoes.append(f"{coluna_data} {condicao}")
                    break
        
        return " AND ".join(condicoes) if condicoes else ""
    
    def gerar_query(self, texto):
        """Gera SQL ANALISANDO SEU BANCO REAL"""
        # 1. Detectar tabela mais relevante
        tabela = self.detectar_tabela_relevante(texto)
        
        # 2. Detectar colunas
        colunas = self.detectar_colunas_relevantes(tabela, texto)
        
        # 3. Detectar função de agregação
        query_select = "SELECT "
        
        if any(palavra in texto.lower() for palavra in ['contar', 'quantos', 'total de']):
            query_select += "COUNT(*) as total"
            colunas = ["*"]  # Para COUNT, não precisa de colunas específicas
        elif any(palavra in texto.lower() for palavra in ['somar', 'total']):
            if self.estrutura.get(tabela, {}).get('colunas_numericas'):
                coluna_num = self.estrutura[tabela]['colunas_numericas'][0]
                query_select += f"SUM({coluna_num}) as total"
                colunas = [coluna_num]
            else:
                query_select += "*"
        elif any(palavra in texto.lower() for palavra in ['média', 'media', 'avg']):
            if self.estrutura.get(tabela, {}).get('colunas_numericas'):
                coluna_num = self.estrutura[tabela]['colunas_numericas'][0]
                query_select += f"AVG({coluna_num}) as media"
                colunas = [coluna_num]
            else:
                query_select += "*"
        else:
            if colunas == ["*"]:
                query_select += "*"
            else:
                query_select += ", ".join(colunas)
        
        # 4. Construir query
        query = f"{query_select} FROM {tabela}"
        
        # 5. Adicionar condições
        condicoes = self.gerar_condicoes(tabela, texto)
        if condicoes:
            query += f" WHERE {condicoes}"
        
        # 6. Ordenação
        if any(palavra in texto.lower() for palavra in ['ordenar', 'ordem', 'ordenado']):
            colunas_disponiveis = self.estrutura.get(tabela, {}).get('colunas', ['id'])
            coluna_ordem = colunas_disponiveis[0]
            
            if 'decrescente' in texto.lower() or 'maior' in texto.lower():
                query += f" ORDER BY {coluna_ordem} DESC"
            else:
                query += f" ORDER BY {coluna_ordem} ASC"
        
        # 7. Limite
        limite = 10  # Default
        match = re.search(r'(\d+)\s*(?:primeiros?|últimos?|resultados?)', texto.lower())
        if match:
            limite = int(match.group(1))
        elif 'todos' in texto.lower():
            limite = 1000
        
        query += f" LIMIT {limite};"
        
        return query, tabela, colunas

# ============ PÁGINA PRINCIPAL ============
def pagina_nlp_sql():
    st.title("🤖 Gerador de SQL por Texto (Conectado aos SEUS Bancos)")
    
    # Primeiro, conectar para listar bancos
    conexao = conectar_mysql()
    if not conexao:
        st.error("Não foi possível conectar ao MySQL. Verifique se o MySQL está rodando.")
        return
    
    cursor = conexao.cursor()
    cursor.execute("SHOW DATABASES")
    bancos_disponiveis = [db[0] for db in cursor.fetchall() 
                         if db[0] not in ['information_schema', 'mysql', 'performance_schema', 'sys']]
    cursor.close()
    conexao.close()
    
    if not bancos_disponiveis:
        st.error("Nenhum banco de dados encontrado no seu MySQL!")
        st.info("Crie um banco primeiro ou use o Query Editor para criar tabelas.")
        return
    
    st.success(f"✅ Conectado ao MySQL. {len(bancos_disponiveis)} banco(s) disponível(is).")
    
    # Seção 1: Seleção do banco
    st.subheader("1. 📁 Selecione SEU Banco")
    
    banco_selecionado = st.selectbox(
        "Banco de dados:",
        bancos_disponiveis,
        help="Selecione o banco onde quer fazer a consulta"
    )
    
    # Analisar o banco selecionado
    with st.spinner(f"Analisando estrutura do banco '{banco_selecionado}'..."):
        gerador = GeradorSQLInteligente(banco_selecionado)
    
    # Mostrar informações do banco
    with st.expander(f"📊 Estrutura do banco '{banco_selecionado}'", expanded=False):
        if gerador.tabelas:
            st.write(f"**Tabelas encontradas:** {len(gerador.tabelas)}")
            
            for tabela in gerador.tabelas[:10]:  # Mostra até 10 tabelas
                if tabela in gerador.estrutura:
                    info = gerador.estrutura[tabela]
                    st.write(f"- **{tabela}**: {len(info['colunas'])} colunas")
                    
                    # Mostrar algumas colunas como exemplo
                    colunas_exemplo = info['colunas'][:5]
                    if colunas_exemplo:
                        st.caption(f"  Ex: {', '.join(colunas_exemplo)}")
            
            if len(gerador.tabelas) > 10:
                st.caption(f"... e mais {len(gerador.tabelas) - 10} tabelas")
        else:
            st.warning("Nenhuma tabela encontrada neste banco.")
    
    # Seção 2: Entrada de texto
    st.subheader("2. 📝 Descreva o que precisa")
    
    texto_usuario = st.text_area(
        "Digite em português o que quer consultar:",
        height=120,
        placeholder=f"Ex: Mostrar os clientes de Lisboa que fizeram compras este mês...",
        key="texto_consulta"
    )
    
    # Exemplos baseados nas tabelas reais
    with st.expander("💡 Exemplos baseados no SEU banco", expanded=True):
        if gerador.tabelas:
            tabela_exemplo = gerador.tabelas[0]
            colunas_exemplo = gerador.estrutura.get(tabela_exemplo, {}).get('colunas', [])[:3]
            
            st.write(f"**Para a tabela `{tabela_exemplo}`**:")
            st.write(f"- `Mostrar {', '.join(colunas_exemplo[:2]) if colunas_exemplo else 'dados'} de {tabela_exemplo}`")
            st.write(f"- `Contar registros em {tabela_exemplo}`")
            
            if gerador.estrutura.get(tabela_exemplo, {}).get('colunas_numericas'):
                coluna_num = gerador.estrutura[tabela_exemplo]['colunas_numericas'][0]
                st.write(f"- `Somar {coluna_num} de {tabela_exemplo}`")
        
        st.write("\n**Padrões genéricos:**")
        st.write("- `clientes com data recente`")
        st.write("- `produtos com preço maior que 100`")
        st.write("- `últimos 10 registros`")
    
    # Botões
    col1, col2 = st.columns([1, 3])
    with col1:
        btn_gerar = st.button("🔮 Gerar SQL", type="primary", use_container_width=True)
    
    with col2:
        if st.button("🔄 Limpar", use_container_width=True):
            st.session_state.texto_consulta = ""
            st.rerun()
    
    # Seção 3: Resultado
    if btn_gerar and texto_usuario.strip():
        st.subheader("3. ⚡ Query Gerada (Baseada nos SEUS Dados)")
        
        try:
            with st.spinner("Analisando seu texto e gerando SQL..."):
                query_gerada, tabela_detectada, colunas_detectadas = gerador.gerar_query(texto_usuario)
            
            # Mostrar análise
            st.info(f"**Tabela detectada:** `{tabela_detectada}`")
            if colunas_detectadas != ["*"]:
                st.info(f"**Colunas detectadas:** {', '.join(colunas_detectadas)}")
            
            # Mostrar query
            st.code(query_gerada, language="sql")
            
            # Botões de ação
            col_a1, col_a2, col_a3 = st.columns(3)
            
            with col_a1:
                st.download_button(
                    "📋 Copiar Query",
                    query_gerada,
                    f"query_gerada_{banco_selecionado}.sql",
                    "text/plain",
                    use_container_width=True
                )
            
            with col_a2:
                if st.button("✏️ Abrir no Editor SQL", use_container_width=True):
                    st.session_state.pagina = "query_editor"
                    st.session_state.texto_query = query_gerada
                    st.session_state.banco_selecionado = banco_selecionado
                    st.rerun()
            
            with col_a3:
                # Testar a query
                if st.button("🧪 Testar Query", use_container_width=True):
                    try:
                        conexao = conectar_mysql(banco_selecionado)
                        if conexao:
                            cursor = conexao.cursor()
                            cursor.execute(query_gerada)
                            
                            if cursor.description:
                                resultados = cursor.fetchall()
                                colunas = [desc[0] for desc in cursor.description]
                                
                                if resultados:
                                    import pandas as pd
                                    df = pd.DataFrame(resultados, columns=colunas)
                                    st.success(f"✅ Query executada! {len(df)} resultado(s).")
                                    st.dataframe(df, use_container_width=True)
                                else:
                                    st.info("✅ Query executada, mas sem resultados.")
                            else:
                                st.success("✅ Query executada com sucesso (não retorna dados).")
                            
                            cursor.close()
                            conexao.close()
                    except Error as e:
                        st.error(f"❌ Erro ao executar: {e}")
            
            # Explicação
            with st.expander("🔍 Como funcionou?", expanded=False):
                st.write(f"**Texto analisado:** \"{texto_usuario}\"")
                st.write(f"**Banco usado:** {banco_selecionado}")
                st.write(f"**Tabela escolhida:** {tabela_detectada} (de {len(gerador.tabelas)} disponíveis)")
                
                if tabela_detectada in gerador.estrutura:
                    st.write(f"**Colunas disponíveis nesta tabela:** {len(gerador.estrutura[tabela_detectada]['colunas'])}")
                
                st.write("\n**Próximos passos:**")
                st.write("1. Copie a query para o Editor SQL para ajustes finos")
                st.write("2. Teste a query com o botão 'Testar Query'")
                st.write("3. Se não ficou bom, reformule o texto")
        
        except Exception as e:
            st.error(f"Erro ao gerar query: {e}")
            st.info("Tente ser mais específico ou use palavras mais comuns.")
    
    # Seção 4: Dicas avançadas
    with st.expander("🎓 Dicas para melhor resultado", expanded=False):
        st.markdown("""
        **Para melhores resultados:**
        
        1. **Mencione nomes de tabelas** que existem no seu banco
        2. **Use palavras das colunas** (veja na estrutura acima)
        3. **Para números**, seja específico: "maior que 100"
        4. **Para datas**, use: "hoje", "este mês", "2024"
        5. **Para textos**, use: "de Lisboa", "com nome João"
        
        **Exemplos que funcionam bem:**
        - `clientes de Lisboa`
        - `produtos com preço maior que 50`
        - `últimos 10 pedidos`
        - `contar usuários ativos`
        
        **Limitações atuais:**
        - Não faz JOINs automáticos entre tabelas
        - Funciona melhor com 1 tabela por vez
        - Para consultas complexas, use o Editor SQL tradicional
        """)
    
    # Botão voltar
    st.markdown("---")
    if st.button("🏠 Voltar para Página Inicial"):
        st.session_state.pagina = "home"
        st.rerun()

# Teste local
if __name__ == "__main__":
    st.set_page_config(page_title="NLP to SQL", layout="wide")
    pagina_nlp_sql()