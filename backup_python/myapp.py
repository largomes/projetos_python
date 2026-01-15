"""
SISTEMA COMPLETO DE GERENCIAMENTO MYSQL - VERSÃO FINAL COMPLETA
CRUD completo com criação ilimitada de campos, FOREIGN KEYS e todas as funcionalidades
Interface web profissional com Streamlit
"""
# ================================= IMPORTES ===================

import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime, date, time 
import warnings
import io


warnings.filterwarnings('ignore')

# ==================== CONFIGURAÇÃO ====================
DEFAULT_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'autocommit': False
}
# ==========================================================================
# ==================== FUNÇÃO QUE DEFINE OS ESTILOS CSS ====================
# ==========================================================================

def aplicar_estilos():
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E88E5;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
        }
        .card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            width: 100%;
        }
        .coluna-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin: 5px 0;
            border-left: 4px solid #1E88E5;
        }
        .primary-key {
            border-left-color: #FF5722;
            background: #fff3e0;
        }
        .foreign-key {
            border-left-color: #4CAF50;
            background: #e8f5e8;
        }
        .tabela-row {
            background: white;
            padding: 10px;
            border-radius: 8px;
            margin: 8px 0;
            border-left: 5px solid #4CAF50;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .dataframe {
            font-size: 0.9em;
        }
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 5px solid #28a745;
        }
        .warning-message {
            background: #fff3cd;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 5px solid #ffc107;
        }
        .info-message {
            background: #d1ecf1;
            color: #0c5460;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 5px solid #17a2b8;
        }
        .fk-relation {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
            border-left: 4px solid #4CAF50;
            font-size: 0.9em;
        }
    </style>
    """, unsafe_allow_html=True)
# ========================================================================================
# ============================== FUNÇÕES DE CONEXÃO ======================================
# ========================================================================================

def conectar_mysql(database=None):
    """Conecta ao MySQL com ou sem banco específico"""
    config = st.session_state.get('db_config', DEFAULT_CONFIG).copy()
    if database:
        config['database'] = database
    
    try:
        conexao = mysql.connector.connect(**config)
        return conexao
    except Error as e:
        st.error(f"❌ Erro de conexão: {e}")
        return None
# ========================================================================================    
# ==================== FUNÇÃO PARA  VERIFICAÇÃO DE CONEXÃO COM MYSQL  ====================   
# ========================================================================================
def verificar_conexao_mysql():
    """Verifica se o MySQL está conectado e acessível"""
    
    # Se não tem configuração, não está conectado
    if 'db_config' not in st.session_state:
        return False, "Nenhuma configuração encontrada"
    
    try:
        # Tenta conectar SEM banco específico
        config = st.session_state.db_config.copy()
        
        # Remove o database se existir (para testar conexão geral)
        if 'database' in config:
            del config['database']
        
        # Tenta conexão
        test_conn = mysql.connector.connect(**config)
        
        # Testa ping
        if test_conn.is_connected():
            test_conn.close()
            return True, f"🟢 Conectado ao MySQL em {config.get('host', 'localhost')}"
        else:
            return False, "❌ Conexão estabelecida mas não ativa"
            
    except mysql.connector.Error as e:
        # Códigos de erro comuns
        if e.errno == 2003:  # Can't connect to MySQL server
            return False, "❌ Não foi possível conectar ao servidor MySQL"
        elif e.errno == 1045:  # Access denied
            return False, "❌ Acesso negado. Verifique usuário/senha"
        elif e.errno == 2005:  # Unknown MySQL server host
            return False, "❌ Servidor MySQL não encontrado"
        else:
            return False, f"❌ Erro {e.errno}: {e.msg}"
    
    except Exception as e:
        return False, f"❌ Erro inesperado: {str(e)}"
    
# ========================================================================================
# ==================== FUNÇÃO PARA  CONEXÃO COM BANCO NO MYSQL  ==========================
# ========================================================================================

def obter_tabelas_banco(nome_banco):
    """Obtém lista de tabelas do banco"""
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return []
    
    cursor = conexao.cursor()
    cursor.execute("SHOW TABLES")
    tabelas = [t[0] for t in cursor.fetchall()]
    cursor.close()
    conexao.close()
    return tabelas
# ==================== FUNÇÃO PARA OBTER ESTRUTURA DA(S) TABELA(S) ====================

def obter_estrutura_tabela(nome_banco, nome_tabela):
    """Obtém estrutura completa de uma tabela"""
    st.subheader("🏚️ ESTRUTURA DE TABELAS")

    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return []
    
    cursor = conexao.cursor()
    cursor.execute(f"DESCRIBE `{nome_tabela}`")
    estrutura = cursor.fetchall()
    cursor.close()
    conexao.close()
    return estrutura
# ==================== FUNÇÃO PARA OBTER A FK ====================

# Primeiro, atualize a função obter_foreign_keys
def obter_foreign_keys(nome_banco, nome_tabela):
    """Obtém foreign keys de uma tabela com informações completas"""
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return []
    
    cursor = conexao.cursor()
    
    # Consulta mais completa para obter foreign keys
    query = """
    SELECT 
        kcu.COLUMN_NAME,
        kcu.REFERENCED_TABLE_NAME,
        kcu.REFERENCED_COLUMN_NAME,
        rc.DELETE_RULE,
        rc.UPDATE_RULE,
        kcu.CONSTRAINT_NAME
    FROM 
        INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
    LEFT JOIN 
        INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
        ON kcu.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
        AND kcu.CONSTRAINT_SCHEMA = rc.CONSTRAINT_SCHEMA
    WHERE 
        kcu.TABLE_SCHEMA = %s
        AND kcu.TABLE_NAME = %s
        AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
    ORDER BY kcu.CONSTRAINT_NAME
    """
    
    cursor.execute(query, (nome_banco, nome_tabela))
    fks = cursor.fetchall()
    cursor.close()
    conexao.close()
    
    return fks  # Retorna: (coluna, tabela_ref, coluna_ref, on_delete, on_update, constraint_name)

# ==================== FUNÇÃO PARA OBTER A CHAVE PRIMARIA ====================

def obter_chave_primaria(nome_banco, nome_tabela):
    """Obtém a chave primária de uma tabela"""
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return None
    
    cursor = conexao.cursor()
    cursor.execute(f"SHOW KEYS FROM `{nome_tabela}` WHERE Key_name = 'PRIMARY'")
    pk_info = cursor.fetchone()
    cursor.close()
    conexao.close()
    
    if pk_info:
        return pk_info[4]  # Nome da coluna
    return None

# ==================== FUNÇÕES DE CRUD (PARA REGISTOS) COMPLETAS ====================

# ==================== FUNÇÃO DE EDITAR REGISTO ====================

def editar_registro(nome_banco, nome_tabela):
    """Edita um registro existente"""
    st.subheader("✏️ Editar Registro")
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Obter estrutura da tabela
        cursor.execute(f"DESCRIBE `{nome_tabela}`")
        colunas_info = cursor.fetchall()
        
        # Obter dados da tabela
        cursor.execute(f"SELECT * FROM `{nome_tabela}` LIMIT 100")
        dados = cursor.fetchall()
        
        if not dados:
            st.info("📭 Nenhum registro para editar.")
            return
        
        # Converter para DataFrame
        nomes_colunas = [col[0] for col in colunas_info]
        df = pd.DataFrame(dados, columns=nomes_colunas)
        
        st.write("**Selecione o registro para editar:**")
        st.dataframe(df, use_container_width=True)
        
        # Encontrar chave primária
        chave_primaria = None
        for col in colunas_info:
            if col[3] == 'PRI':
                chave_primaria = col[0]
                break
        
        if not chave_primaria:
            st.error("❌ Esta tabela não tem uma chave primária definida.")
            st.info("Para editar registros, a tabela precisa de uma PRIMARY KEY.")
            return
        
        # Selecionar registro por chave primária
        st.markdown("---")
        st.write(f"**Selecione o {chave_primaria} do registro que deseja editar:**")
        
        valores_chave = df[chave_primaria].astype(str).tolist()
        chave_selecionada = st.selectbox(f"Valor de {chave_primaria}:", valores_chave)
        
        if chave_selecionada:
            # Buscar o registro específico
            cursor.execute(f"SELECT * FROM `{nome_tabela}` WHERE `{chave_primaria}` = %s", (chave_selecionada,))
            registro = cursor.fetchone()
            
            if registro:
                # Converter para dicionário
                registro_dict = {nomes_colunas[i]: registro[i] for i in range(len(nomes_colunas))}
                
                st.success(f"📋 Editando registro: {chave_primaria} = {chave_selecionada}")
                
                # Formulário de edição
                novos_valores = {}
                
                for col in colunas_info:
                    col_name = col[0]
                    col_type = col[1].upper()
                    valor_atual = registro_dict[col_name]
                    
                    # Se for chave primária, mostrar como texto (não editável)
                    if col[3] == 'PRI':
                        st.text_input(f"{col_name} (chave primária)", value=str(valor_atual), disabled=True)
                        novos_valores[col_name] = valor_atual
                        continue
                    
                    # Campo editável
                    label = f"{col_name}"
                    
                    # Verificar se é FOREIGN KEY
                    fks = obter_foreign_keys(nome_banco, nome_tabela)
                    is_fk = any(fk[0] == col_name for fk in fks)
                    
                    if is_fk:
                        # Para FK, mostrar dropdown com valores válidos
                        for fk in fks:
                            if fk[0] == col_name:
                                tabela_ref, coluna_ref = fk[1], fk[2]
                                
                        cursor_ref = conexao.cursor()
                        cursor_ref.execute(f"SELECT `{coluna_ref}` FROM `{tabela_ref}` ORDER BY `{coluna_ref}`")
                        valores_validos = [str(v[0]) for v in cursor_ref.fetchall()]
                        cursor_ref.close()
                        
                        if valores_validos:
                            label += f" 🔗→ {tabela_ref}.{coluna_ref}"
                            index_valor_atual = 0
                            if str(valor_atual) in valores_validos:
                                index_valor_atual = valores_validos.index(str(valor_atual))
                            novos_valores[col_name] = st.selectbox(label, valores_validos, index=index_valor_atual)
                        else:
                            st.warning(f"Tabela `{tabela_ref}` está vazia")
                            novos_valores[col_name] = st.text_input(label, value=str(valor_atual) if valor_atual else "")
                    
                    elif 'INT' in col_type:
                        novos_valores[col_name] = st.number_input(
                            label, 
                            value=int(valor_atual) if valor_atual is not None else 0,
                            step=1
                        )
                    elif 'DECIMAL' in col_type or 'FLOAT' in col_type or 'DOUBLE' in col_type:
                        novos_valores[col_name] = st.number_input(
                            label,
                            value=float(valor_atual) if valor_atual is not None else 0.0,
                            step=0.01,
                            format="%.2f"
                        )
                    elif 'DATE' in col_type:
                        if valor_atual:
                            try:
                                if isinstance(valor_atual, datetime) or hasattr(valor_atual, 'date'):
                                    data_val = valor_atual.date() if hasattr(valor_atual, 'date') else valor_atual
                                else:
                                    data_val = valor_atual
                                novos_valores[col_name] = st.date_input(label, value=data_val)
                            except:
                                novos_valores[col_name] = st.date_input(label)
                        else:
                            novos_valores[col_name] = st.date_input(label)
                    elif 'TEXT' in col_type or 'LONGTEXT' in col_type:
                        novos_valores[col_name] = st.text_area(
                            label, 
                            value=str(valor_atual) if valor_atual is not None else "",
                            height=100
                        )
                    elif 'VARCHAR' in col_type or 'CHAR' in col_type:
                        novos_valores[col_name] = st.text_input(
                            label,
                            value=str(valor_atual) if valor_atual is not None else ""
                        )
                    elif 'BOOL' in col_type:
                        novos_valores[col_name] = st.checkbox(
                            label,
                            value=bool(valor_atual) if valor_atual is not None else False
                        )
                    else:
                        novos_valores[col_name] = st.text_input(
                            label,
                            value=str(valor_atual) if valor_atual is not None else ""
                        )
                
                # Botão para salvar
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
                        try:
                            # Construir UPDATE
                            set_clause = []
                            valores_update = []
                            
                            for campo, valor in novos_valores.items():
                                if campo != chave_primaria:
                                    set_clause.append(f"`{campo}` = %s")
                                    valores_update.append(valor)
                            
                            # Adicionar WHERE clause
                            valores_update.append(chave_selecionada)
                            
                            sql = f"UPDATE `{nome_tabela}` SET {', '.join(set_clause)} WHERE `{chave_primaria}` = %s"
                            
                            cursor.execute(sql, valores_update)
                            conexao.commit()
                            
                            st.success("✅ Registro atualizado com sucesso!")
                            st.balloons()
                            st.rerun()
                            
                        except Error as e:
                            if "foreign key constraint fails" in str(e).lower():
                                st.error(f"❌ Erro de FOREIGN KEY: Valor inválido na tabela de referência!")
                            else:
                                st.error(f"❌ Erro ao atualizar: {e}")
                            conexao.rollback()
                
                with col2:
                    if st.button("❌ Cancelar Edição", use_container_width=True):
                        st.rerun()
    
    except Error as e:
        st.error(f"Erro: {e}")
    
    finally:
        cursor.close()
        conexao.close()

# ==================== FUNÇÃO DE EXCLUIR REGISTO ====================

def excluir_registro(nome_banco, nome_tabela):
    """Exclui um registro específico"""
    st.subheader("🗑️ Excluir Registro")
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Obter estrutura da tabela
        cursor.execute(f"DESCRIBE `{nome_tabela}`")
        colunas_info = cursor.fetchall()
        
        # Obter dados da tabela
        cursor.execute(f"SELECT * FROM `{nome_tabela}` LIMIT 100")
        dados = cursor.fetchall()
        
        if not dados:
            st.info("📭 Nenhum registro para excluir.")
            return
        
        # Converter para DataFrame
        nomes_colunas = [col[0] for col in colunas_info]
        df = pd.DataFrame(dados, columns=nomes_colunas)
        
        st.write("**Selecione o registro para excluir:**")
        st.dataframe(df, use_container_width=True)
        
        # Encontrar chave primária
        chave_primaria = None
        for col in colunas_info:
            if col[3] == 'PRI':
                chave_primaria = col[0]
                break
        
        if not chave_primaria:
            st.error("❌ Esta tabela não tem uma chave primária definida.")
            return
        
        # Selecionar registro por chave primária
        st.markdown("---")
        st.write(f"**Selecione o {chave_primaria} do registro que deseja excluir:**")
        
        valores_chave = df[chave_primaria].astype(str).tolist()
        chave_selecionada = st.selectbox(f"Valor de {chave_primaria}:", valores_chave, key="excluir_select")
        
        if chave_selecionada:
            # Buscar o registro específico
            cursor.execute(f"SELECT * FROM `{nome_tabela}` WHERE `{chave_primaria}` = %s", (chave_selecionada,))
            registro = cursor.fetchone()
            
            if registro:
                # Converter para dicionário
                registro_dict = {nomes_colunas[i]: registro[i] for i in range(len(nomes_colunas))}
                
                st.warning(f"⚠️ **Registro selecionado para exclusão:**")
                
                # Mostrar em formato de tabela
                col_info, col_valor = st.columns([2, 3])
                with col_info:
                    for chave in registro_dict.keys():
                        st.write(f"**{chave}:**")
                with col_valor:
                    for valor in registro_dict.values():
                        st.write(f"{valor}")
                
                st.markdown("---")
                
                # Verificar se há FOREIGN KEYs que referenciam este registro
                st.write("🔍 **Verificando dependências...**")
                
                # Obter todas as tabelas do banco
                cursor.execute("SHOW TABLES")
                todas_tabelas = [t[0] for t in cursor.fetchall()]
                
                dependencias = []
                for tabela in todas_tabelas:
                    if tabela != nome_tabela:
                        fks = obter_foreign_keys(nome_banco, tabela)
                        for fk in fks:
                            if fk[1] == nome_tabela and fk[2] == chave_primaria:
                                # Verificar se há registros que referenciam este
                                cursor_ref = conexao.cursor()
                                cursor_ref.execute(f"SELECT COUNT(*) FROM `{tabela}` WHERE `{fk[0]}` = %s", (chave_selecionada,))
                                count = cursor_ref.fetchone()[0]
                                cursor_ref.close()
                                
                                if count > 0:
                                    dependencias.append({
                                        'tabela': tabela,
                                        'coluna': fk[0],
                                        'quantidade': count
                                    })
                
                if dependencias:
                    st.error("❌ **Não é possível excluir este registro!**")
                    st.write("**Motivo:** Existem outros registros que dependem deste:")
                    for dep in dependencias:
                        st.write(f"- `{dep['tabela']}.{dep['coluna']}`: {dep['quantidade']} registro(s)")
                    
                    st.info("💡 **Soluções:**")
                    st.write("1. Exclua primeiro os registros dependentes")
                    st.write("2. Altere os registros dependentes para outra referência")
                    st.write("3. Use ON DELETE CASCADE na criação da FOREIGN KEY")
                else:
                    # Confirmação
                    confirm = st.checkbox("⚠️ Confirmar exclusão PERMANENTE deste registro?", key="confirm_exclusao")
                    
                    if confirm:
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("🗑️ EXCLUIR PERMANENTEMENTE", type="primary", use_container_width=True):
                                try:
                                    cursor.execute(f"DELETE FROM `{nome_tabela}` WHERE `{chave_primaria}` = %s", (chave_selecionada,))
                                    conexao.commit()
                                    st.success(f"✅ Registro {chave_selecionada} excluído com sucesso!")
                                    st.balloons()
                                    st.rerun()
                                except Error as e:
                                    st.error(f"❌ Erro ao excluir: {e}")
                                    conexao.rollback()
                        
                        with col_btn2:
                            if st.button("❌ Cancelar", use_container_width=True):
                                st.rerun()
    
    except Error as e:
        st.error(f"Erro: {e}")
    
    finally:
        cursor.close()
        conexao.close()
        
# ==================== FUNÇÃO PARA EXPORTAÇÃO DE DADOS  ====================

def exportar_tabela(nome_banco, nome_tabela):
    """Exporta dados da tabela para CSV"""
    st.subheader("📥 Exportar Dados")
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Obter dados
        cursor.execute(f"SELECT * FROM `{nome_tabela}`")
        dados = cursor.fetchall()
        
        if not dados:
            st.warning("📭 Nenhum dado para exportar. A tabela está vazia.")
            return
        
        # Obter nomes das colunas
        cursor.execute(f"DESCRIBE `{nome_tabela}`")
        colunas_info = cursor.fetchall()
        nomes_colunas = [col[0] for col in colunas_info]
        
        # Criar DataFrame
        df = pd.DataFrame(dados, columns=nomes_colunas)
        
        # Estatísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Registros", len(df))
        with col2:
            st.metric("🏗️ Colunas", len(df.columns))
        with col3:
            tamanho_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
            st.metric("💾 Tamanho", f"{tamanho_mb:.2f} MB")
        
        # Mostrar preview
        st.write("**Preview dos dados (primeiras 10 linhas):**")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Opções de exportação
        st.markdown("---")
        st.write("**Escolha o formato de exportação:**")
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            # Exportar para CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📊 CSV",
                data=csv,
                file_name=f"{nome_tabela}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_exp2:
            # Exportar para Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Dados')
            
            st.download_button(
                label="📈 Excel",
                data=output.getvalue(),
                file_name=f"{nome_tabela}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col_exp3:
            # Exportar para JSON
            json_str = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📋 JSON",
                data=json_str,
                file_name=f"{nome_tabela}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Opções de filtro para exportação
        with st.expander("🔍 Filtrar antes de exportar", expanded=False):
            if not df.empty:
                col_filtro = st.selectbox("Filtrar por coluna:", nomes_colunas)
                valor_filtro = st.text_input("Valor do filtro:")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Aplicar Filtro", use_container_width=True):
                        if valor_filtro:
                            try:
                                df_filtrado = df[df[col_filtro].astype(str).str.contains(valor_filtro, case=False, na=False)]
                                st.write(f"**Resultado:** {len(df_filtrado)} registro(s) encontrado(s)")
                                st.dataframe(df_filtrado.head(10), use_container_width=True)
                                
                                # Botão para exportar filtrado
                                csv_filtrado = df_filtrado.to_csv(index=False)
                                st.download_button(
                                    label=f"📥 Exportar {len(df_filtrado)} registro(s)",
                                    data=csv_filtrado,
                                    file_name=f"{nome_tabela}_filtrado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                            except:
                                st.warning("Não foi possível aplicar o filtro")
    
    except Error as e:
        st.error(f"Erro ao exportar: {e}")
    
    finally:
        cursor.close()
        conexao.close()


#======================================================================================
# ==================== EDITAR ESTRUTURA DA TABELA  ====================================
#======================================================================================
# ==========================   FUNÇÃO ESTRUTURA DA TABELA =============================     
def editar_estrutura_tabela(nome_banco, nome_tabela):
    """Edita a estrutura de uma tabela existente - VERSÃO COMPLETA"""
    st.title(f"⚙️ EDITAR ESTRUTURA DA TABELA: {nome_tabela}")
    
    # Botão para voltar à lista de tabelas (no topo)
    if st.button("🔙 Voltar à Lista de Tabelas", key=f"btn_voltar_top_{nome_tabela}"):
        st.session_state.pagina_atual = None
        st.session_state.tabela_selecionada = None
        st.rerun()
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Obter estrutura atual
        cursor.execute(f"DESCRIBE `{nome_tabela}`")
        estrutura = cursor.fetchall()
        
        # Obter FOREIGN KEYS
        fks = obter_foreign_keys(nome_banco, nome_tabela)
        fk_dict = {fk[0]: fk for fk in fks}
        
        # Criar DataFrame com informações completas
        dados_estrutura = []
        for col in estrutura:
            coluna_info = {
                'Campo': col[0],
                'Tipo': col[1],
                'Nulo': col[2],
                'Chave': col[3],
                'Default': col[4] if col[4] else '',
                'Extra': col[5]
            }
            
            # Adicionar informação de FOREIGN KEY
            if col[0] in fk_dict:
                fk_info = fk_dict[col[0]]
                coluna_info['Foreign Key'] = f"→ {fk_info[1]}.{fk_info[2]}"
            else:
                coluna_info['Foreign Key'] = ''
            
            dados_estrutura.append(coluna_info)
        
        df = pd.DataFrame(dados_estrutura)
        
        # Mostrar estrutura atual com cores
        st.subheader("🏗️ Estrutura Atual da Tabela")
        
        # Formatar DataFrame para mostrar FKs
        def color_fk_rows(row):
            if row['Foreign Key']:
                return ['background-color: #e8f5e8'] * len(row)
            elif row['Chave'] == 'PRI':
                return ['background-color: #fff3e0'] * len(row)
            return [''] * len(row)
        
        styled_df = df.style.apply(color_fk_rows, axis=1)
        st.dataframe(styled_df, use_container_width=True)
        
        # Legenda
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("🔑 **Chave Primária (PK)**")
        with col2:
            st.markdown("🔗 **Chave Estrangeira (FK)**")
        with col3:
            st.markdown("📝 **Coluna Normal**")
        
        st.markdown("---")
        
        # MENU DE OPERAÇÕES
        operacao = st.radio(
            "🔧 Selecione a operação:",
            ["➕ Adicionar Coluna", "✏️ Editar Coluna", "🗑️ Remover Coluna", 
             "🔗 Adicionar FOREIGN KEY", "🔒 Tornar Coluna Única", "📋 Ver Relacionamentos"],
            horizontal=True,
            key=f"radio_operacao_{nome_tabela}"  # KEY ÚNICA
        )
        
        # ==================== 1. ADICIONAR COLUNA ====================
        if operacao == "➕ Adicionar Coluna":
            st.subheader("➕ Adicionar Nova Coluna")
            
            # CHAVE ÚNICA: Combine nome da tabela com timestamp ou hash
            form_key = f"form_add_col_{nome_tabela}_{hash(nome_tabela)}"
            
            with st.form(key=form_key):  # USAR CHAVE ÚNICA AQUI
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    novo_nome = st.text_input(
                        "Nome da nova coluna:", 
                        placeholder="ex: telefone, email",
                        key=f"novo_nome_{nome_tabela}"
                    )
                
                with col2:
                    novo_tipo = st.selectbox(
                        "Tipo de dado:", 
                        [
                            "INT", "BIGINT", "SMALLINT", 
                            "VARCHAR(50)", "VARCHAR(100)", "VARCHAR(255)", 
                            "TEXT", "LONGTEXT", "MEDIUMTEXT",
                            "DATE", "DATETIME", "TIMESTAMP",
                            "DECIMAL(10,2)", "FLOAT", "DOUBLE",
                            "BOOLEAN", "ENUM('sim','não')", "JSON"
                        ],
                        key=f"novo_tipo_{nome_tabela}"
                    )
                
                with col3:
                    posicao = st.selectbox(
                        "Posição:", 
                        ["ÚLTIMA", "PRIMEIRA"],
                        key=f"posicao_{nome_tabela}"
                    )
                
                # NOVO: Mais opções em múltiplas colunas
                col_a, col_b, col_c, col_d = st.columns(4)
                
                with col_a:
                    permite_null = st.checkbox(
                        "Permitir NULL", 
                        value=True,
                        key=f"permite_null_{nome_tabela}"
                    )
                
                with col_b:
                    valor_default = st.text_input(
                        "Valor padrão:",
                        key=f"valor_default_{nome_tabela}"
                    )
                
                with col_c:
                    auto_increment = st.checkbox(
                        "AUTO_INCREMENT",
                        key=f"auto_inc_{nome_tabela}"
                    )
                
                with col_d:
                    # NOVA OPÇÃO: UNIQUE
                    coluna_unica = st.checkbox(
                        "Valores Únicos", 
                        help="Não permite valores duplicados",
                        key=f"coluna_unica_{nome_tabela}"
                    )
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submit = st.form_submit_button(
                        "✅ Adicionar Coluna", 
                        type="primary", 
                        use_container_width=True,
                        key=f"btn_add_col_submit_{nome_tabela}"  # KEY ÚNICA
                    )
                with col_btn2:
                    cancel = st.form_submit_button(
                        "❌ Cancelar", 
                        use_container_width=True,
                        key=f"btn_add_col_cancel_{nome_tabela}"  # KEY ÚNICA
                    )
            
            # Processar fora do formulário
            if submit and novo_nome:
                try:
                    # Construir SQL
                    sql = f"ALTER TABLE `{nome_tabela}` ADD COLUMN `{novo_nome}` {novo_tipo}"
                    
                    if not permite_null:
                        sql += " NOT NULL"
                    
                    if valor_default:
                        if novo_tipo.upper().startswith(('INT', 'BIGINT', 'DECIMAL', 'FLOAT', 'DOUBLE')):
                            sql += f" DEFAULT {valor_default}"
                        else:
                            sql += f" DEFAULT '{valor_default}'"
                    
                    if auto_increment:
                        sql += " AUTO_INCREMENT"
                    
                    # ADICIONAR UNIQUE SE SOLICITADO
                    if coluna_unica:
                        sql += " UNIQUE"
                    
                    if posicao == "PRIMEIRA":
                        sql += " FIRST"
                    
                    # Mostrar SQL
                    with st.expander("📄 SQL que será executado"):
                        st.code(sql)
                    
                    # Executar
                    cursor.execute(sql)
                    conexao.commit()
                    
                    # Mensagem com informações
                    mensagem = f"✅ Coluna '{novo_nome}' adicionada com sucesso!"
                    if coluna_unica:
                        mensagem += " 🔒 **(Valores Únicos)**"
                    if auto_increment:
                        mensagem += " 🔄 **(Auto Increment)**"
                    
                    st.success(mensagem)
                    st.balloons()
                    
                    # Botão para atualizar
                    if st.button("🔄 Atualizar Página", 
                               key=f"btn_atualizar_add_unique_{nome_tabela}"):
                        st.rerun()
                    
                except Error as e:
                    st.error(f"❌ Erro ao adicionar coluna: {e}")
                    conexao.rollback()
        
        # ==================== 2. TORNAR COLUNA ÚNICA ====================
        elif operacao == "🔒 Tornar Coluna Única":
            st.subheader("🔒 Tornar Coluna Única (UNIQUE)")
            
            # Obter lista de colunas que não são UNIQUE
            cursor.execute(f"""
                SELECT COLUMN_NAME 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = %s
            """, (nome_banco, nome_tabela))
            
            todas_colunas = [col[0] for col in cursor.fetchall()]
            
            # Verificar quais colunas já são UNIQUE
            colunas_unicas = []
            for coluna in todas_colunas:
                cursor.execute(f"""
                    SELECT CONSTRAINT_NAME 
                    FROM information_schema.KEY_COLUMN_USAGE 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = %s 
                    AND COLUMN_NAME = %s 
                    AND CONSTRAINT_NAME LIKE '%UNIQUE%'
                """, (nome_banco, nome_tabela, coluna))
                
                if not cursor.fetchone():
                    colunas_unicas.append(coluna)
            
            if colunas_unicas:
                coluna_selecionada = st.selectbox(
                    "Selecione a coluna para tornar única:",
                    colunas_unicas,
                    key=f"select_coluna_unica_{nome_tabela}"
                )
                
                if st.button("✅ Adicionar UNIQUE", 
                           type="primary", 
                           key=f"btn_add_unique_{nome_tabela}"):
                    if tornar_coluna_unica(nome_banco, nome_tabela, coluna_selecionada):
                        st.rerun()
            else:
                st.info("✅ Todas as colunas já têm constraint UNIQUE ou são chaves primárias.")
        
        # ==================== 3. EDITAR COLUNA ====================
        elif operacao == "✏️ Editar Coluna":
            st.subheader("✏️ Editar Coluna Existente")
            
            # Selecionar coluna para editar
            colunas_disponiveis = [col[0] for col in estrutura]
            if not colunas_disponiveis:
                st.info("📭 Nenhuma coluna para editar.")
                st.stop()
            
            coluna_selecionada = st.selectbox("Selecione a coluna para editar:", colunas_disponiveis, key="select_col_edit")
            
            if coluna_selecionada:
                # Encontrar informações da coluna selecionada
                col_info = None
                for col in estrutura:
                    if col[0] == coluna_selecionada:
                        col_info = col
                        break
                
                if col_info:
                    with st.form(key=f"form_edit_col_{coluna_selecionada}"):
                        st.write(f"**Editando coluna:** `{coluna_selecionada}`")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Se não for PK, permitir renomear
                            if col_info[3] != 'PRI':
                                novo_nome = st.text_input("Novo nome:", value=col_info[0])
                            else:
                                st.info("🔑 Esta coluna é PRIMARY KEY. O nome não pode ser alterado.")
                                novo_nome = col_info[0]
                            
                            # Tipos disponíveis
                            tipos_disponiveis = [
                                "INT", "BIGINT", "SMALLINT", 
                                "VARCHAR(50)", "VARCHAR(100)", "VARCHAR(255)", 
                                "TEXT", "LONGTEXT", "MEDIUMTEXT",
                                "DATE", "DATETIME", "TIMESTAMP",
                                "DECIMAL(10,2)", "FLOAT", "DOUBLE",
                                "BOOLEAN"
                            ]
                            
                            # Encontrar tipo atual na lista
                            tipo_atual = col_info[1]
                            tipo_base = tipo_atual.split('(')[0] if '(' in tipo_atual else tipo_atual
                            
                            # Encontrar índice do tipo atual
                            try:
                                indice_tipo = tipos_disponiveis.index(tipo_base)
                            except ValueError:
                                indice_tipo = 0
                            
                            novo_tipo = st.selectbox(
                                "Novo tipo:",
                                tipos_disponiveis,
                                index=indice_tipo
                            )
                        
                        with col2:
                            novo_null = st.checkbox("Permitir NULL", value=col_info[2] == 'YES')
                            default_atual = col_info[4] if col_info[4] else ""
                            novo_default = st.text_input("Novo valor padrão:", value=default_atual)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            submit_edit = st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
                        with col_btn2:
                            cancel_edit = st.form_submit_button("❌ Cancelar", use_container_width=True)
                    
                    # Processar edição
                    if submit_edit:
                        try:
                            # ALTER TABLE para modificar coluna
                            sql = f"ALTER TABLE `{nome_tabela}` CHANGE COLUMN `{coluna_selecionada}` `{novo_nome}` {novo_tipo}"
                            
                            if not novo_null:
                                sql += " NOT NULL"
                            
                            if novo_default:
                                sql += f" DEFAULT '{novo_default}'"
                            elif col_info[4] and not novo_default:
                                # Remover DEFAULT se existia antes
                                sql += " DEFAULT NULL"
                            
                            # Mostrar SQL
                            with st.expander("📄 SQL que será executado"):
                                st.code(sql)
                            
                            cursor.execute(sql)
                            conexao.commit()
                            
                            st.success(f"✅ Coluna '{coluna_selecionada}' atualizada para '{novo_nome}'!")
                            
                            # Botão para atualizar
                            if st.button("🔄 Atualizar Página", key="btn_atualizar_edit"):
                                st.rerun()
                            
                        except Error as e:
                            st.error(f"❌ Erro ao editar coluna: {e}")
                            conexao.rollback()
        
        # ==================== 4. REMOVER COLUNA ====================
        elif operacao == "🗑️ Remover Coluna":
            st.subheader("🗑️ Remover Coluna")
            
            # Não permitir remover colunas que são PK ou FK
            colunas_removiveis = []
            for col in estrutura:
                col_name = col[0]
                is_pk = col[3] == 'PRI'
                is_fk = col_name in fk_dict
                
                if not is_pk and not is_fk:
                    colunas_removiveis.append(col_name)
            
            if not colunas_removiveis:
                st.warning("⚠️ Não há colunas que possam ser removidas (PK e FK não podem ser removidas aqui).")
            else:
                coluna_para_remover = st.selectbox("Selecione a coluna para remover:", colunas_removiveis, key="select_col_remove")
                
                if coluna_para_remover:
                    st.warning(f"⚠️ Você está prestes a remover a coluna: **{coluna_para_remover}**")
                    st.write("**Esta ação é permanente e irá apagar todos os dados desta coluna!**")
                    
                    confirmacao = st.checkbox("Confirmo que quero remover esta coluna permanentemente", key="confirm_remove")
                    
                    if confirmacao:
                        # Usar form apenas para o botão de remoção
                        with st.form(key="form_remove_col"):
                            btn_remover = st.form_submit_button("🗑️ REMOVER COLUNA PERMANENTEMENTE", type="primary", use_container_width=True)
                        
                        if btn_remover:
                            try:
                                sql = f"ALTER TABLE `{nome_tabela}` DROP COLUMN `{coluna_para_remover}`"
                                
                                # Mostrar SQL
                                with st.expander("📄 SQL que será executado"):
                                    st.code(sql)
                                
                                cursor.execute(sql)
                                conexao.commit()
                                
                                st.success(f"✅ Coluna '{coluna_para_remover}' removida com sucesso!")
                                
                                # Botão para atualizar
                                if st.button("🔄 Atualizar Página", key="btn_atualizar_remove"):
                                    st.rerun()
                                
                            except Error as e:
                                st.error(f"❌ Erro ao remover coluna: {e}")
                                conexao.rollback()
        
        # ==================== 5. ADICIONAR FOREIGN KEY ====================
        elif operacao == "🔗 Adicionar FOREIGN KEY":
            st.subheader("🔗 Adicionar FOREIGN KEY a uma Coluna")
            
            # Obter tabelas disponíveis no banco (exceto a atual)
            tabelas_banco = obter_tabelas_banco(nome_banco)
            if nome_tabela in tabelas_banco:
                tabelas_banco.remove(nome_tabela)
            
            if not tabelas_banco:
                st.info("📭 Não há outras tabelas no banco para criar relacionamentos.")
                st.stop()
            
            # Selecionar coluna atual para ser FK
            colunas_para_fk = []
            for col in estrutura:
                # Apenas colunas que não são PK e não são já FK
                if col[3] != 'PRI' and col[0] not in fk_dict:
                    colunas_para_fk.append(col[0])
            
            if not colunas_para_fk:
                st.info("📭 Todas as colunas já são PRIMARY KEY ou já têm FOREIGN KEY.")
                st.stop()
            
            # Criar um formulário para todos os inputs
            with st.form(key="form_add_fk"):
                col_fk1, col_fk2 = st.columns(2)
                
                with col_fk1:
                    coluna_fk = st.selectbox("Coluna nesta tabela:", colunas_para_fk, key="coluna_fk_select")
                    
                    # Mostrar tipo da coluna selecionada
                    tipo_coluna_atual = ""
                    for col in estrutura:
                        if col[0] == coluna_fk:
                            tipo_coluna_atual = col[1]
                            break
                    
                    st.caption(f"Tipo: `{tipo_coluna_atual}`")
                
                with col_fk2:
                    tabela_ref = st.selectbox("Tabela de referência:", tabelas_banco, key="tabela_ref_select")
                    
                    # Obter colunas da tabela de referência
                    estrutura_ref = obter_estrutura_tabela(nome_banco, tabela_ref)
                    
                    # Filtrar apenas colunas compatíveis
                    colunas_compatíveis_info = []  # Armazenar informações completas
                    colunas_compatíveis_display = []  # Para exibição
                    
                    for col_ref in estrutura_ref:
                        col_ref_nome = col_ref[0]
                        col_ref_tipo = col_ref[1]
                        
                        # Verificar se é PK (tem prioridade)
                        is_pk = col_ref[3] == 'PRI'
                        
                        # Verificar compatibilidade básica
                        tipo_atual_base = tipo_coluna_atual.split('(')[0] if '(' in tipo_coluna_atual else tipo_coluna_atual
                        tipo_ref_base = col_ref_tipo.split('(')[0] if '(' in col_ref_tipo else col_ref_tipo
                        
                        if is_pk:
                            display_text = f"🔑 PK {col_ref_nome} ({col_ref_tipo})"
                            colunas_compatíveis_info.append({
                                'nome': col_ref_nome,
                                'tipo': col_ref_tipo,
                                'display': display_text,
                                'is_pk': True
                            })
                            colunas_compatíveis_display.append(display_text)
                        elif tipo_atual_base == tipo_ref_base:
                            display_text = f"✅ {col_ref_nome} ({col_ref_tipo})"
                            colunas_compatíveis_info.append({
                                'nome': col_ref_nome,
                                'tipo': col_ref_tipo,
                                'display': display_text,
                                'is_pk': False
                            })
                            colunas_compatíveis_display.append(display_text)
                    
                    if not colunas_compatíveis_display:
                        st.error("❌ Nenhuma coluna compatível encontrada!")
                        coluna_ref_selecionada = None
                    else:
                        # Selecionar coluna de referência
                        opcao_selecionada = st.selectbox(
                            "Coluna de referência:", 
                            colunas_compatíveis_display, 
                            key="coluna_ref_select"
                        )
                        
                        # Encontrar a coluna correspondente à opção selecionada
                        coluna_ref_selecionada = None
                        for info in colunas_compatíveis_info:
                            if info['display'] == opcao_selecionada:
                                coluna_ref_selecionada = info['nome']
                                tipo_ref_selecionada = info['tipo']
                                break
                
                # Opções da FK
                st.markdown("---")
                col_op1, col_op2, col_op3 = st.columns(3)
                with col_op1:
                    on_delete = st.selectbox("ON DELETE", 
                                        ["RESTRICT", "CASCADE", "SET NULL", "NO ACTION"],
                                        help="Ação ao excluir registro referenciado",
                                        key="on_delete_select")
                with col_op2:
                    on_update = st.selectbox("ON UPDATE", 
                                        ["RESTRICT", "CASCADE", "NO ACTION"],
                                        help="Ação ao atualizar registro referenciado",
                                        key="on_update_select")
                with col_op3:
                    fk_name = st.text_input("Nome da FK (opcional):", 
                                        placeholder=f"fk_{nome_tabela}_{coluna_fk}",
                                        help="Nome único para a constraint",
                                        key="fk_name_input")
                
                # Botão para criar FK
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    btn_criar = st.form_submit_button("✅ Criar FOREIGN KEY", type="primary", use_container_width=True)
                with col_btn2:
                    btn_limpar = st.form_submit_button("🔄 Limpar", use_container_width=True)
            
            # Processar criação da FK quando o botão for pressionado
            if btn_criar:
                # DEBUG: Mostrar valores recebidos
                st.info(f"🔍 **DEBUG - Valores recebidos:**")
                st.info(f"- coluna_fk: {coluna_fk}")
                st.info(f"- tabela_ref: {tabela_ref}")
                st.info(f"- coluna_ref_selecionada: {coluna_ref_selecionada}")
                st.info(f"- on_delete: {on_delete}")
                st.info(f"- on_update: {on_update}")
                st.info(f"- fk_name: {fk_name}")
                
                # Verificar se todas as variáveis necessárias estão definidas
                if not coluna_fk:
                    st.error("❌ Selecione uma coluna nesta tabela!")
                    st.stop()
                
                if not tabela_ref:
                    st.error("❌ Selecione uma tabela de referência!")
                    st.stop()
                
                if not coluna_ref_selecionada:
                    st.error("❌ Selecione uma coluna de referência!")
                    st.stop()
                
                # Se chegou aqui, todos os campos estão preenchidos
                st.success("✅ Todos os campos preenchidos! Processando...")
                
                try:
                    # Obter tipo exato da coluna atual
                    tipo_exato_atual = ""
                    for col in estrutura:
                        if col[0] == coluna_fk:
                            tipo_exato_atual = col[1]
                            break
                    
                    # Obter tipo exato da coluna de referência
                    tipo_exato_ref = ""
                    for col_ref in estrutura_ref:
                        if col_ref[0] == coluna_ref_selecionada:
                            tipo_exato_ref = col_ref[1]
                            break
                    
                    st.info(f"🔍 **Tipos encontrados:**")
                    st.info(f"- Tipo coluna atual: {tipo_exato_atual}")
                    st.info(f"- Tipo coluna referência: {tipo_exato_ref}")
                    
                    # Verificar compatibilidade
                    tipo_compativel = True
                    if tipo_exato_atual != tipo_exato_ref:
                        # Extrair apenas a parte principal do tipo
                        tipo_atual_base = tipo_exato_atual.split('(')[0] if '(' in tipo_exato_atual else tipo_exato_atual
                        tipo_ref_base = tipo_exato_ref.split('(')[0] if '(' in tipo_exato_ref else tipo_exato_ref
                        
                        if tipo_atual_base != tipo_ref_base:
                            tipo_compativel = False
                            st.warning(f"⚠️ **Tipos diferentes:** `{tipo_atual_base}` ≠ `{tipo_ref_base}`")
                            
                            # Lista de tipos compatíveis
                            tipos_compatíveis = {
                                'INT': ['INT', 'BIGINT', 'SMALLINT', 'MEDIUMINT', 'TINYINT'],
                                'BIGINT': ['BIGINT', 'INT'],
                                'VARCHAR': ['VARCHAR', 'CHAR', 'TEXT'],
                                'CHAR': ['CHAR', 'VARCHAR'],
                                'DECIMAL': ['DECIMAL', 'FLOAT', 'DOUBLE'],
                                'DATE': ['DATE', 'DATETIME', 'TIMESTAMP'],
                                'DATETIME': ['DATETIME', 'TIMESTAMP']
                            }
                            
                            # Verificar se são compatíveis
                            if (tipo_atual_base in tipos_compatíveis and 
                                tipo_ref_base in tipos_compatíveis[tipo_atual_base]):
                                st.info(f"✅ Tipos são compatíveis mesmo sendo diferentes")
                                tipo_compativel = True
                            else:
                                st.error(f"❌ Tipos incompatíveis!")
                                
                                # Oferecer opção de corrigir
                                corrigir = st.radio(
                                    "O que deseja fazer?",
                                    ["Alterar a coluna para o tipo da referência", 
                                    "Cancelar operação"],
                                    key="corrigir_fk_tipo"
                                )
                                
                                if corrigir == "Alterar a coluna para o tipo da referência":
                                    try:
                                        # Alterar a coluna para o tipo da referência
                                        sql_alterar = f"ALTER TABLE `{nome_tabela}` MODIFY COLUMN `{coluna_fk}` {tipo_exato_ref};"
                                        
                                        with st.expander("📄 SQL de alteração"):
                                            st.code(sql_alterar)
                                        
                                        cursor.execute(sql_alterar)
                                        conexao.commit()
                                        tipo_exato_atual = tipo_exato_ref
                                        st.success(f"✅ Coluna `{coluna_fk}` alterada para `{tipo_exato_ref}`")
                                    except Error as e:
                                        st.error(f"❌ Erro ao alterar coluna: {e}")
                                        conexao.rollback()
                                        st.stop()
                                else:
                                    st.info("Operação cancelada.")
                                    st.stop()
                    
                    # Construir SQL para criar FK
                    if fk_name and fk_name.strip():
                        fk_name_clean = fk_name.strip()
                        fk_name_sql = f" CONSTRAINT `{fk_name_clean}`"
                    else:
                        # Gerar nome automático
                        fk_name_clean = f"fk_{nome_tabela}_{coluna_fk}"
                        fk_name_sql = ""
                    
                    sql = f"""
                    ALTER TABLE `{nome_tabela}`
                    ADD{fk_name_sql} FOREIGN KEY (`{coluna_fk}`)
                    REFERENCES `{tabela_ref}` (`{coluna_ref_selecionada}`)
                    ON DELETE {on_delete}
                    ON UPDATE {on_update}
                    """
                    
                    # Mostrar SQL
                    with st.expander("📄 SQL que será executado", expanded=True):
                         st.code(sql)
                    
                    # Verificar se já existe FK
                    fks_existentes = obter_foreign_keys(nome_banco, nome_tabela)
                    ja_existe = False
                    for fk in fks_existentes:
                        if fk[0] == coluna_fk:
                            ja_existe = True
                            st.warning(f"⚠️ Já existe uma FOREIGN KEY na coluna `{coluna_fk}`")
                            break
                    
                    if not ja_existe:
                        # Executar
                        try:
                            st.info("🔄 Executando criação da FOREIGN KEY...")
                            cursor.execute(sql)
                            conexao.commit()
                            
                            # Verificar se foi criada
                            fks_atualizadas = obter_foreign_keys(nome_banco, nome_tabela)
                            fk_criada = False
                            
                            for fk in fks_atualizadas:
                                if fk[0] == coluna_fk and fk[1] == tabela_ref and fk[2] == coluna_ref_selecionada:
                                    fk_criada = True
                                    break
                            
                            if fk_criada:
                                st.success("🎉 **FOREIGN KEY criada com sucesso!**")
                                st.success(f"`{nome_tabela}.{coluna_fk}` → `{tabela_ref}.{coluna_ref_selecionada}`")
                                
                                # Mostrar detalhes
                                st.info(f"""
                                **Detalhes da FOREIGN KEY criada:**
                                - **Tabela origem:** `{nome_tabela}`
                                - **Coluna FK:** `{coluna_fk}` ({tipo_exato_atual})
                                - **Tabela referência:** `{tabela_ref}`
                                - **Coluna referência:** `{coluna_ref_selecionada}` ({tipo_exato_ref})
                                - **ON DELETE:** `{on_delete}`
                                - **ON UPDATE:** `{on_update}`
                                - **Nome da constraint:** `{fk_name_clean}`
                                """)
                                
                                # Botão para atualizar
                                if st.button("🔄 Atualizar Página", key="btn_atualizar_fk_success"):
                                    st.rerun()
                            else:
                                st.warning("⚠️ A FOREIGN KEY foi criada, mas não foi encontrada na verificação.")
                                st.info("A página será atualizada para mostrar as mudanças...")
                                st.rerun()
                            
                        except Error as e:
                            error_msg = str(e)
                            st.error(f"❌ **Erro ao criar FOREIGN KEY:** {error_msg}")
                            
                            # Tratamento específico de erros
                            if "foreign key constraint fails" in error_msg.lower():
                                st.error("""
                                ❌ **Erro: Dados inconsistentes!**
                                
                                Existem valores na coluna `{}` que não existem em `{}.{}`.
                                
                                **Para resolver, execute este SQL primeiro:**
                                ```sql
                                -- Verificar dados inconsistentes
                                SELECT DISTINCT `{}` 
                                FROM `{}` 
                                WHERE `{}` IS NOT NULL 
                                AND `{}` NOT IN (SELECT `{}` FROM `{}`);
                                
                                -- Limpar dados inconsistentes (se necessário)
                                -- UPDATE `{}` SET `{}` = NULL 
                                -- WHERE `{}` IS NOT NULL 
                                -- AND `{}` NOT IN (SELECT `{}` FROM `{}`);
                                ```
                                """.format(
                                    coluna_fk, tabela_ref, coluna_ref_selecionada,
                                    coluna_fk, nome_tabela, coluna_fk, coluna_fk, coluna_ref_selecionada, tabela_ref,
                                    nome_tabela, coluna_fk, coluna_fk, coluna_fk, coluna_ref_selecionada, tabela_ref
                                ))
                            elif "duplicate key" in error_msg.lower():
                                st.error("❌ Já existe uma FOREIGN KEY com esse nome!")
                            elif "errno 150" in error_msg.lower():
                                st.error("❌ Erro 150: Problema com tipos de dados ou índice.")
                            else:
                                st.error(f"❌ Erro detalhado: {error_msg}")
                            
                            conexao.rollback()
                    else:
                        st.info("ℹ️ Não foi criada nova FOREIGN KEY porque já existe uma.")
                
                except Exception as e:
                    st.error(f"❌ Erro inesperado: {e}")
                    import traceback
                    st.code(traceback.format_exc())
            
            # Botão para voltar
            st.markdown("---")
            if st.button("🔙 Voltar à Lista de Tabelas", key="btn_voltar_fk_bottom", use_container_width=True):
                st.session_state.pagina_atual = None
                st.session_state.tabela_selecionada = None
                st.rerun()
        
        # ==================== 6. VER RELACIONAMENTOS ====================
        elif operacao == "📋 Ver Relacionamentos":
            st.subheader("📋 Relacionamentos da Tabela")
            
            try:    
                # Verificar se há FKs
                if not fk_dict:
                    st.info("📭 Esta tabela não possui relacionamentos (FOREIGN KEYS).")
                    
                    st.markdown("---")
                    st.write("💡 **Para criar relacionamentos:**")
                    st.write("1. Use a opção '🔗 Adicionar FOREIGN KEY' acima")
                    st.write("2. Ou marque colunas como FK durante a criação da tabela")
                    
                    # Botão para criar FK
                    if st.button("🔗 Criar Primeira FOREIGN KEY", type="primary"):
                        # Mudar para a operação de adicionar FK
                        st.session_state.operacao_fk = "🔗 Adicionar FOREIGN KEY"
                        st.rerun()
                else:
                    # Mostrar FKs existentes
                    st.write(f"**📊 {len(fk_dict)} relacionamento(s) encontrado(s):**")
                    
                    for col_name, fk_info in fk_dict.items():
                        with st.container():
                            st.markdown(f"""
                            <div style="background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 5px solid #4CAF50;">
                                <h4 style="margin: 0;">🔗 {col_name}</h4>
                                <p style="margin: 5px 0;">→ <strong>{fk_info[1]}.{fk_info[2]}</strong></p>
                                <p style="margin: 5px 0; font-size: 0.9em;">
                                    <strong>ON DELETE:</strong> {fk_info[3]} | 
                                    <strong>ON UPDATE:</strong> {fk_info[4]}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
            except Error as e:  
                st.error(f"❌ Erro na operação: {e}")
    
    except Error as e:
        st.error(f"Erro: {e}")
    
    finally:
        cursor.close()
        conexao.close()
    
    # Botão para voltar no final
    st.markdown("---")
    if st.button("🔙 Voltar à Lista de Tabelas", key="btn_voltar_bottom", use_container_width=True):
        st.session_state.pagina_atual = None
        st.session_state.tabela_selecionada = None
        st.rerun()
#=======================================================================================
# ==================== FUNÇÃO PARA PARA COLUNA UNICA ===================================
#=======================================================================================        
def tornar_coluna_unica(nome_banco, nome_tabela, nome_coluna):
    """Adiciona constraint UNIQUE a uma coluna existente"""
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return False
    
    cursor = conexao.cursor()
    
    try:
        # Verificar se já existe constraint UNIQUE nesta coluna
        cursor.execute(f"""
            SELECT CONSTRAINT_NAME 
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = %s 
            AND COLUMN_NAME = %s 
            AND CONSTRAINT_NAME LIKE '%UNIQUE%'
        """, (nome_banco, nome_tabela, nome_coluna))
        
        if cursor.fetchone():
            st.warning(f"A coluna '{nome_coluna}' já tem constraint UNIQUE.")
            return True
        
        # Verificar se há valores duplicados
        cursor.execute(f"""
            SELECT `{nome_coluna}`, COUNT(*) 
            FROM `{nome_tabela}` 
            WHERE `{nome_coluna}` IS NOT NULL 
            GROUP BY `{nome_coluna}` 
            HAVING COUNT(*) > 1 
            LIMIT 1
        """)
        
        if cursor.fetchone():
            st.error(f"❌ Não é possível adicionar UNIQUE: A coluna '{nome_coluna}' tem valores duplicados!")
            return False
        
        # Adicionar constraint UNIQUE
        sql = f"ALTER TABLE `{nome_tabela}` ADD UNIQUE (`{nome_coluna}`)"
        cursor.execute(sql)
        conexao.commit()
        
        st.success(f"✅ Constraint UNIQUE adicionada à coluna '{nome_coluna}'!")
        return True
        
    except Error as e:
        st.error(f"❌ Erro ao adicionar UNIQUE: {e}")
        conexao.rollback()
        return False
    finally:
        cursor.close()
        conexao.close()
#=======================================================================================
# ==================== FUNÇÃO PARA MOSTRAR RELACIONAMENTOS DO BANCO ====================
#=======================================================================================
def mostrar_relacionamentos_banco(nome_banco):
    """Mostra todos os relacionamentos do banco de dados"""
    st.title(f"🔗 Relacionamentos do Banco: {nome_banco}")
    
    # Botão para voltar
    if st.button("🔙 Voltar a Lista de Tabelas", key="btn_voltar_rel"):
        st.session_state.pagina_atual = None
        st.rerun()
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Consulta para obter todos os relacionamentos
        query = """
        SELECT 
            TABLE_NAME,
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME,
            CONSTRAINT_NAME
        FROM 
            INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE 
            TABLE_SCHEMA = %s
            AND REFERENCED_TABLE_NAME IS NOT NULL
        ORDER BY TABLE_NAME, CONSTRAINT_NAME
        """
        
        cursor.execute(query, (nome_banco,))
        relacionamentos = cursor.fetchall()
        
        if relacionamentos:
            # Agrupar por CONSTRAINT
            fks_por_constraint = {}
            for rel in relacionamentos:
                constraint_name = rel[4]
                if constraint_name not in fks_por_constraint:
                    fks_por_constraint[constraint_name] = []
                fks_por_constraint[constraint_name].append(rel)
            
            st.subheader("📊 Mapa Completo de Relacionamentos")
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔗 FOREIGN KEYS", len(relacionamentos))
            with col2:
                st.metric("📋 Constraints", len(fks_por_constraint))
            with col3:
                tabelas_com_fk = len(set([r[0] for r in relacionamentos]))
                st.metric("🏗️ Tabelas Relacionadas", tabelas_com_fk)
            
            # Mostrar cada constraint
            for constraint, fks in fks_por_constraint.items():
                with st.expander(f"🔗 {constraint}", expanded=True):
                    # Obter informações da constraint
                    cursor.execute(f"""
                    SELECT DELETE_RULE, UPDATE_RULE 
                    FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS 
                    WHERE CONSTRAINT_SCHEMA = %s 
                    AND CONSTRAINT_NAME = %s
                    """, (nome_banco, constraint))
                    
                    regras = cursor.fetchone()
                    on_delete = regras[0] if regras else "RESTRICT"
                    on_update = regras[1] if regras else "RESTRICT"
                    
                    st.write(f"**Ações:** ON DELETE = {on_delete}, ON UPDATE = {on_update}")
                    
                    # Mostrar cada FK nesta constraint
                    for fk in fks:
                        tabela_origem = fk[0]
                        coluna_origem = fk[1]
                        tabela_destino = fk[2]
                        coluna_destino = fk[3]
                        
                        # Contar registros relacionados
                        cursor.execute(f"""
                        SELECT COUNT(*) 
                        FROM `{tabela_origem}` 
                        WHERE `{coluna_origem}` IS NOT NULL
                        """)
                        com_valor = cursor.fetchone()[0]
                        
                        cursor.execute(f"SELECT COUNT(*) FROM `{tabela_destino}`")
                        total_destino = cursor.fetchone()[0]
                        
                        st.markdown(f"""
                        <div style="background: #f0f8ff; padding: 10px; border-radius: 5px; margin: 5px 0;">
                            📍 **{tabela_origem}.{coluna_origem}** → **{tabela_destino}.{coluna_destino}**  
                            <small>Registros: {com_valor}/{total_destino} ({ (com_valor/total_destino*100 if total_destino > 0 else 0):.1f}%)</small>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Diagrama de relacionamentos simplificado
            st.markdown("---")
            st.subheader("🔄 Diagrama de Relacionamentos")
            
            diagrama = "```mermaid\nerDiagram\n"
            
            # Adicionar tabelas
            tabelas_envolvidas = set()
            for rel in relacionamentos:
                tabelas_envolvidas.add(rel[0])  # Tabela origem
                tabelas_envolvidas.add(rel[2])  # Tabela destino
            
            for tabela in tabelas_envolvidas:
                diagrama += f"    {tabela} {{\n"
                
                # Adicionar colunas PK
                cursor.execute(f"SHOW KEYS FROM `{tabela}` WHERE Key_name = 'PRIMARY'")
                pks = cursor.fetchall()
                for pk in pks:
                    diagrama += f"        INT {pk[4]}\n"
                
                diagrama += "    }\n"
            
            # Adicionar relacionamentos
            for rel in relacionamentos:
                tabela_origem = rel[0]
                tabela_destino = rel[2]
                diagrama += f'    {tabela_origem} ||--o{{ {tabela_destino} : "referencia"\n'
            
            diagrama += "```"
            
            st.code(diagrama, language="mermaid")
            
        else:
            st.info("📭 Nenhum relacionamento (FOREIGN KEY) encontrado neste banco.")
            
            st.markdown("""
            <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 10px 0;">
                💡 **Dica:** Para criar relacionamentos:
                1. Crie tabelas com colunas do mesmo tipo
                2. Use a opção "🔗 Adicionar FOREIGN KEY" na edição da tabela
                3. Ou marque colunas como FK durante a criação da tabela
            </div>
            """, unsafe_allow_html=True)
    
    except Error as e:
        st.error(f"❌ Erro ao carregar relacionamentos: {e}")
    
    finally:
        cursor.close()
        conexao.close()
        
    # Botão para voltar
    st.markdown("---")
    if st.button("🔙 Voltar a Lista de Tabelas", use_container_width=True):
        st.session_state.pagina_atual = None
        st.rerun() 
            
#=============================================================================        
# ==================== FUNÇÃO para EXCLUIR banco de dados ====================
#=============================================================================        
def excluir_banco_simples_mas_funcional(nome_banco):
    """Exclui banco COMO NO TERMINAL - Versão que FUNCIONA"""
    
    try:
        # 1. Configuração LIMPA sem banco
        config = {
            'host': st.session_state.db_config.get('host', 'localhost'),
            'user': st.session_state.db_config.get('user', 'root'),
            'password': st.session_state.db_config.get('password', ''),
            'autocommit': True  # IMPORTANTE!
        }
        
        # 2. Conecta
        conexao = mysql.connector.connect(**config)
        conexao.autocommit = True  # Garante
        
        cursor = conexao.cursor()
        
        # 3. COMANDO DIRETO (como no terminal)
        cursor.execute(f"DROP DATABASE IF EXISTS `{nome_banco}`")
        
        # 4. Verifica se realmente excluiu
        cursor.execute("SHOW DATABASES")
        bancos_atuais = [db[0] for db in cursor.fetchall()]
        
        cursor.close()
        conexao.close()
        
        if nome_banco in bancos_atuais:
            st.error(f"❌ Banco `{nome_banco}` ainda existe após exclusão!")
            return False
        else:
            st.success(f"✅ Banco `{nome_banco}` excluído com sucesso!")
            return True
            
    except Error as e:
        st.error(f"❌ Erro: {e}")
        
        # Mostra o COMANDO EXATO para executar manualmente
        st.code(f"""
# Comando que FALHOU no código:
DROP DATABASE IF EXISTS `{nome_banco}`;

# Tente manualmente no terminal:
mysql -u {config['user']} -p{config['password']} -e "DROP DATABASE IF EXISTS \\`{nome_banco}\\`;"
""")
        return False
#============================================================================    
# ================   FUNÇÃO NOVA PARA EXCLUIR  ==============================
#============================================================================
def dialog_exclusao_banco(banco):
    """Mostra diálogo de confirmação para excluir banco"""
    
    # Usa container para isolamento
    with st.container():
        st.error(f"🚨 EXCLUSÃO DO BANCO: `{banco}`")
        st.warning("Esta ação é IRREVERSÍVEL! Todos os dados serão perdidos.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"✅ Sim, excluir `{banco}`", 
                        key=f"yes_del_{banco}",
                        type="primary",
                        use_container_width=True):
                
                # Função de exclusão (a que testamos)
                if excluir_banco_simples_mas_funcional(banco):
                    st.rerun()
        
        with col2:
            if st.button(f"❌ Cancelar", 
                        key=f"no_del_{banco}",
                        use_container_width=True):
                st.session_state[f'dialog_{banco}'] = False
                st.rerun()  
#===================================================================                    
# ==================== FUNÇÃO DE PÁGINA INICIAL ====================
#===================================================================
def pagina_inicial():
    """Página inicial do sistema - VERSAO CORRIGIDA"""
    
    st.title("🗄️ MySQL Manager Pro")
    st.markdown("### Sistema de Gerenciamento de Bancos MySQL")
    
    # Função local para verificar conexão
    def verificar_conexao():
        """Verifica se consegue conectar ao MySQL"""
        if 'db_config' not in st.session_state:
            return False, "⚠️ Nenhuma configuração encontrada"
        
        try:
            # Tenta conectar sem banco específico
            config = st.session_state.db_config.copy()
            if 'database' in config:
                del config['database']
            
            conn = mysql.connector.connect(**config)
            if conn.is_connected():
                versao = conn.get_server_info()
                conn.close()
                return True, f"✅ Conectado (MySQL {versao})"
            return False, "❌ Conexão falhou"
        except mysql.connector.Error as e:
            if e.errno == 2003:
                return False, "❌ Servidor não encontrado"
            elif e.errno == 1045:
                return False, "❌ Acesso negado"
            else:
                return False, f"❌ Erro {e.errno}: {e.msg}"
        except Exception:
            return False, "❌ Não foi possível conectar"
    
    # Verificar status
    conexao_ok, mensagem = verificar_conexao()
    
    # MOSTRAR STATUS
    st.markdown("---")
    st.subheader("🔌 Status da Conexão")
    
    if conexao_ok:
        st.success(mensagem)
    else:
        st.error(mensagem)
    
    st.markdown("---")
    
    # ========== SE CONECTADO: MOSTRAR BANCOS ==========
    if conexao_ok:
        try:
            # Conectar (sem banco específico)
            config_conexao = st.session_state.db_config.copy()
            if 'database' in config_conexao:
                del config_conexao['database']
            
            conexao = mysql.connector.connect(**config_conexao)
            cursor = conexao.cursor()
            
            # Criar novo banco
            with st.expander("🏗️ Criar Novo Banco de Dados", expanded=False):
                novo_banco = st.text_input("Nome do novo banco:", placeholder="meu_novo_banco")
                
                col_criar1, col_criar2 = st.columns([3, 1])
                with col_criar2:
                    if st.button("✅ Criar", use_container_width=True):
                        if novo_banco:
                            try:
                                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{novo_banco}`")
                                conexao.commit()
                                st.success(f"✅ Banco '{novo_banco}' criado!")
                                st.rerun()
                            except Error as e:
                                st.error(f"❌ Erro: {e}")
            
            # Listar bancos existentes
            st.subheader("📂 Bancos de Dados Disponíveis")
            
            cursor.execute("SHOW DATABASES")
            todos_bancos = cursor.fetchall()
            
            # Filtrar bancos de sistema
            bancos = [db[0] for db in todos_bancos 
                     if db[0] not in ['information_schema', 'mysql', 'performance_schema', 'sys']]
            
            if bancos:
                st.write(f"**Encontrados {len(bancos)} banco(s):**")
                
                for banco in bancos:
                    # Container para cada banco
                    with st.container():
                        col_banco1, col_banco2, col_banco3 = st.columns([3, 1, 1])
                        
                        with col_banco1:
                            st.markdown(f"### `{banco}`")
                            
                            # Tentar contar tabelas
                            try:
                                cursor.execute(f"USE `{banco}`")
                                cursor.execute("SHOW TABLES")
                                tabelas = cursor.fetchall()
                                st.caption(f"📊 {len(tabelas)} tabela(s)")
                            except:
                                st.caption("📊 Não foi possível contar tabelas")
                        
                        with col_banco2:
                            if st.button("▶️ Entrar", key=f"entrar_{banco}", use_container_width=True):
                                st.session_state.banco_selecionado = banco
                                st.rerun()
                        
                        with col_banco3:
                            if st.button("🗑️", key=f"del_{banco}", help="Excluir banco", use_container_width=True):
                                st.session_state.banco_para_excluir = banco
                        
                        # Modal de confirmação para exclusão
                        if 'banco_para_excluir' in st.session_state and st.session_state.banco_para_excluir == banco:
                            st.warning(f"⚠️ **Confirmar exclusão do banco '{banco}'?**")
                            st.error("Todas as tabelas e dados serão perdidos permanentemente!")
                            
                            col_conf1, col_conf2 = st.columns(2)
                            with col_conf1:
                                if st.button("✅ Confirmar Exclusão", type="primary"):
                                    try:
                                        cursor.execute(f"DROP DATABASE `{banco}`")
                                        conexao.commit()
                                        st.error(f"🗑️ Banco '{banco}' excluído!")
                                        del st.session_state.banco_para_excluir
                                        st.rerun()
                                    except Error as e:
                                        st.error(f"❌ Erro: {e}")
                            with col_conf2:
                                if st.button("❌ Cancelar"):
                                    del st.session_state.banco_para_excluir
                                    st.rerun()
                        
                        st.markdown("---")
            
            else:
                st.info("📭 Nenhum banco de dados encontrado.")
                st.write("Use o formulário acima para criar seu primeiro banco.")
            
            # Fechar conexão
            cursor.close()
            conexao.close()
            
        except Error as e:
            st.error(f"❌ Erro ao acessar MySQL: {e}")
    # Botão para diagnóstico do sistema
    if st.button("🩺 Diagnóstico do Sistema MySQL", use_container_width=True):
        st.session_state.pagina_atual = "diagnostico_sistema"
        st.rerun()        
    
    # ========== SE NÃO CONECTADO: MOSTRAR FORMULÁRIO ==========
    else:
        st.subheader("⚙️ Configurar Conexão MySQL")
        
        # Usar valores salvos ou padrão
        config_atual = st.session_state.get('db_config', {})
        
        # Formulário de configuração - ESTA É A PARTE QUE DEVE APARECER!
        with st.form(key="form_config_inicial"):
            col1, col2 = st.columns(2)
            
            with col1:
                host = st.text_input("Host:", 
                                   value=config_atual.get('host', 'localhost'), 
                                   placeholder="localhost")
                usuario = st.text_input("Usuário:", 
                                      value=config_atual.get('user', 'root'), 
                                      placeholder="root")
            
            with col2:
                senha = st.text_input("Senha:", 
                                    type="password", 
                                    value=config_atual.get('password', ''),
                                    placeholder="Digite a senha")
                porta = st.number_input("Porta:", 
                                      min_value=1, 
                                      max_value=65535, 
                                      value=config_atual.get('port', 3306))
            
            st.markdown("---")
            col_test, col_save = st.columns(2)
            
            with col_test:
                testar = st.form_submit_button("🔍 Testar Conexão", use_container_width=True)
            
            with col_save:
                salvar = st.form_submit_button("💾 Salvar & Conectar", 
                                             type="primary", 
                                             use_container_width=True)
        
        # Testar conexão quando botão for pressionado
        if testar:
            config_test = {
                'host': host,
                'user': usuario,
                'password': senha,
                'port': porta
            }
            
            try:
                conn = mysql.connector.connect(**config_test)
                if conn.is_connected():
                    st.success(f"✅ Conexão bem-sucedida!")
                    st.info(f"Versão do MySQL: {conn.get_server_info()}")
                    conn.close()
                else:
                    st.error("❌ Conexão estabelecida mas não ativa")
            except mysql.connector.Error as e:
                if e.errno == 2003:
                    st.error("❌ Não foi possível conectar ao servidor MySQL")
                    st.info("""
                    **Verifique:**
                    1. O MySQL está instalado?
                    2. O serviço está rodando?
                    3. Firewall permite porta 3306?
                    """)
                elif e.errno == 1045:
                    st.error("❌ Acesso negado. Verifique usuário e senha")
                else:
                    st.error(f"❌ Erro {e.errno}: {e.msg}")
        
        # Salvar configuração quando botão for pressionado
        if salvar:
            nova_config = {
                'host': host,
                'user': usuario,
                'password': senha,
                'port': porta
            }
            
            st.session_state.db_config = nova_config
            st.success("✅ Configuração salva!")
            
            # Testar a nova configuração
            conexao_ok_nova, mensagem_nova = verificar_conexao()
            
            if conexao_ok_nova:
                st.success("🎉 Conexão verificada com sucesso!")
                st.balloons()
                st.info("🔃 A página será recarregada...")
                st.rerun()
            else:
                st.error(f"⚠️ Configuração salva, mas: {mensagem_nova}")
                st.info("Verifique os dados e tente novamente.")
        
        # Ajuda para troubleshooting
        with st.expander("🆘 Precisa de ajuda?", expanded=False):
            col_ajuda1, col_ajuda2 = st.columns(2)
            
            with col_ajuda1:
                st.markdown("""
                **Problemas comuns:**
                - MySQL não está instalado
                - Serviço MySQL não está rodando
                - Porta 3306 bloqueada pelo firewall
                - Usuário/senha incorretos
                - Hostname errado
                """)
            
            with col_ajuda2:
                st.markdown("""
                **Comandos úteis (Linux):**
                ```bash
                # Verificar status
                sudo service mysql status
                
                # Iniciar MySQL
                sudo service mysql start
                
                # Testar no terminal
                mysql -u root -p
                ```
                
                **Windows:**
                - Verifique no XAMPP/WAMP
                - Ou serviços do Windows
                """)
    
    # Debug opcional
    st.markdown("---")
    if st.checkbox("🔍 Modo Desenvolvedor (Debug)"):
        st.write("**Configuração atual:**", st.session_state.get('db_config', 'Não definida'))
        st.write("**Conexão OK:**", conexao_ok)
        
        if st.button("🔄 Testar Conexão Direta"):
            try:
                config = st.session_state.get('db_config', {})
                if config:
                    conn = mysql.connector.connect(**config)
                    st.success(f"✅ Conectado! Server: {conn.get_server_info()}")
                    conn.close()
                else:
                    st.error("❌ Nenhuma configuração")
            except Exception as e:
                st.error(f"❌ Erro: {e}")
                
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🩺 Centro de Diagnósticos", 
                    use_container_width=True,
                    help="Análise completa do sistema e bancos"):
            st.session_state.pagina_atual = "pagina_diagnosticos"
            st.rerun()            
                
# ================================================================                                  
# ==================== FUNÇÕES DE DIAGNÓSTICO ====================
# =========== FUNÇÃO PARA OBTER LISTA DE BANCOS ==================
# ================================================================                  
def obter_lista_bancos():
    """Obtém lista de bancos de dados disponíveis"""
    try:
        config = st.session_state.get('db_config', DEFAULT_CONFIG).copy()
        config.pop('database', None)
        
        conexao = mysql.connector.connect(**config)
        cursor = conexao.cursor()
        
        cursor.execute("SHOW DATABASES")
        todos_bancos = [db[0] for db in cursor.fetchall()]
        
        # Filtra bancos de sistema
        bancos_usuario = [
            db for db in todos_bancos 
            if db not in ['information_schema', 'mysql', 'performance_schema', 'sys']
        ]
        
        cursor.close()
        conexao.close()
        
        return bancos_usuario
        
    except Exception as e:
        st.error(f"Erro ao obter bancos: {str(e)}")
        return []                
                
# ================================================================                                  
# ==================== FUNÇÕES DE DIAGNÓSTICO ====================
# =========== FUNÇÃO PARA pagina de DIAGNOSTICO ==================
# ================================================================                
                
def pagina_diagnosticos():
    """Página principal de diagnósticos"""
    st.title("🩺 Centro de Diagnósticos")
    
    st.markdown("""
    <div style="
        background: #FFF3E0;
        color: #E65100;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
        border-left: 5px solid #FF9800;
    ">
        <h4 style="margin: 0; color: #E65100;">🔧 Ferramentas de Análise e Diagnóstico</h4>
        <p style="margin: 10px 0 0 0;">Aqui você pode analisar o estado do seu sistema MySQL e bancos de dados</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verifica se está conectado ao MySQL
    try:
        config = st.session_state.get('db_config', DEFAULT_CONFIG).copy()
        config.pop('database', None)
        conexao = mysql.connector.connect(**config)
        
        if not conexao.is_connected():
            st.error("❌ Não há conexão com o MySQL")
            conexao.close()
            # Botão para voltar
            if st.button("⬅️ Voltar à Página Inicial", use_container_width=True):
                st.session_state.pagina_atual = None
                st.rerun()
            return
        
        conexao.close()
        
    except Exception as e:
        st.error(f"❌ Não foi possível conectar ao MySQL: {str(e)}")
        if st.button("⚙️ Configurar Conexão", use_container_width=True):
            st.session_state.pagina_atual = None
            st.rerun()
        return
    
    # ============ OPÇÕES DE DIAGNÓSTICO ============
    st.markdown("### 📋 Escolha o tipo de diagnóstico:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="
            background: #E8F5E9;
            padding: 20px;
            border-radius: 10px;
            height: 200px;
            border: 1px solid #C8E6C9;
            text-align: center;
        ">
            <h3 style="color: #2E7D32;">🐬</h3>
            <h4 style="color: #2E7D32;">Sistema MySQL</h4>
            <p>Análise completa do servidor MySQL</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Analisar Sistema", key="btn_sistema", use_container_width=True):
            st.session_state.pagina_atual = "diagnostico_sistema"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="
            background: #E3F2FD;
            padding: 20px;
            border-radius: 10px;
            height: 200px;
            border: 1px solid #90CAF9;
            text-align: center;
        ">
            <h3 style="color: #1565C0;">📁</h3>
            <h4 style="color: #1565C0;">Banco Específico</h4>
            <p>Diagnóstico de um banco de dados</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Se tem banco selecionado, mostra opção direta
        if st.session_state.get('banco_selecionado'):
            if st.button(f"🔍 Analisar '{st.session_state.banco_selecionado}'", 
                        key="btn_banco_atual", use_container_width=True):
                st.session_state.pagina_atual = "diagnostico_banco"
                st.rerun()
        else:
            # Se não tem banco, pede para selecionar
            bancos = obter_lista_bancos()  # Você precisa ter essa função
            if bancos:
                banco_selecionado = st.selectbox(
                    "Selecione um banco para diagnóstico:",
                    bancos,
                    key="select_banco_diag"
                )
                if st.button("🔍 Analisar Banco Selecionado", use_container_width=True):
                    st.session_state.banco_selecionado = banco_selecionado
                    st.session_state.pagina_atual = "diagnostico_banco"
                    st.rerun()
            else:
                st.info("ℹ️ Nenhum banco disponível para análise")
    
    # ============ FERRAMENTAS ADICIONAIS ============
    st.markdown("---")
    st.markdown("### 🛠️ Outras Ferramentas")
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("📊 Estatísticas Gerais", use_container_width=True):
            st.session_state.pagina_atual = "estatisticas_sistema"
            st.rerun()
    
    with col4:
        if st.button("⚡ Teste de Performance", use_container_width=True):
            st.session_state.pagina_atual = "teste_performance"
            st.rerun()
    
    # ============ BOTÃO VOLTAR ============
    st.markdown("---")
    if st.button("⬅️ Voltar à Página Inicial", use_container_width=True):
        st.session_state.pagina_atual = None
        st.rerun()                
                                            
# ================================================================                                  
# ==================== FUNÇÕES DE DIAGNÓSTICO ====================
# =========== FUNÇÃO PARA DIAGNOSTICAR SISTEMA MYSQL =============
# ================================================================

def diagnosticar_sistema_mysql():
    """Faz diagnóstico completo do sistema MySQL"""
    st.subheader("🩺 Diagnóstico do Sistema MySQL")
    
    try:
        config = st.session_state.get('db_config', DEFAULT_CONFIG).copy()
        config.pop('database', None)
        
        conexao = mysql.connector.connect(**config)
        cursor = conexao.cursor()
        
        # 1. Versão do MySQL
        cursor.execute("SELECT VERSION()")
        versao = cursor.fetchone()[0]
        st.write(f"**1. Versão do MySQL:** `{versao}`")
        
        # 2. Status da conexão
        st.write(f"**2. Status da conexão:** {'✅ Ativa' if conexao.is_connected() else '❌ Inativa'}")
        
        # 3. Bancos totais
        cursor.execute("SHOW DATABASES")
        todos_bancos = [db[0] for db in cursor.fetchall()]
        bancos_sistema = [db for db in todos_bancos if db not in ['information_schema', 'mysql', 'performance_schema', 'sys']]
        
        st.write(f"**3. Bancos de dados no sistema:** {len(bancos_sistema)}")
        for i, banco in enumerate(bancos_sistema[:10]):  # Mostra os primeiros 10
            st.write(f"   {i+1}. `{banco}`")
        if len(bancos_sistema) > 10:
            st.write(f"   ... e mais {len(bancos_sistema)-10} bancos")
        
        # 4. Usuário atual e permissões
        cursor.execute("SELECT CURRENT_USER()")
        usuario = cursor.fetchone()[0]
        st.write(f"**4. Usuário atual:** `{usuario}`")
        
        # 5. Configurações importantes
        st.write("**5. Configurações do servidor:**")
        configs = [
            ('max_connections', 'Conexões máximas'),
            ('innodb_buffer_pool_size', 'Buffer Pool InnoDB'),
            ('character_set_server', 'Charset do servidor'),
            ('collation_server', 'Collation do servidor')
        ]
        
        for config_name, descricao in configs:
            try:
                cursor.execute(f"SHOW VARIABLES LIKE '{config_name}'")
                valor = cursor.fetchone()
                if valor:
                    st.write(f"   - **{descricao}:** `{valor[1]}`")
            except:
                pass
        
        # 6. Processos ativos
        cursor.execute("SHOW PROCESSLIST")
        processos = cursor.fetchall()
        st.write(f"**6. Processos ativos:** {len(processos)}")
        
        # 7. Tabelas com mais conexões
        try:
            cursor.execute("""
                SELECT DB, COUNT(*) as conexoes 
                FROM INFORMATION_SCHEMA.PROCESSLIST 
                WHERE DB IS NOT NULL 
                GROUP BY DB 
                ORDER BY conexoes DESC 
                LIMIT 5
            """)
            bancos_ativos = cursor.fetchall()
            if bancos_ativos:
                st.write("**7. Bancos com mais conexões ativas:**")
                for banco, conexoes in bancos_ativos:
                    st.write(f"   - `{banco}`: {conexoes} conexões")
        except:
            pass
        
        cursor.close()
        conexao.close()
        
        # Recomendações
        st.markdown("---")
        st.subheader("💡 Recomendações")
        
        if len(bancos_sistema) == 0:
            st.success("✅ Sistema limpo, pode criar seu primeiro banco!")
        elif len(processos) > 50:
            st.warning("⚠️ Muitos processos ativos. Considere otimizar conexões.")
        
    except Error as e:
        st.error(f"❌ Erro no diagnóstico: {e}")
        
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar aos Diagnósticos", use_container_width=True):
            st.session_state.pagina_atual = "pagina_diagnosticos"
            st.rerun()
    with col2:
        if st.button("🏠 Página Inicial", use_container_width=True):
            st.session_state.pagina_atual = None
            st.rerun()    
        
# ============================================================================================          
# ==================== FUNÇÃO PARA DIAGNOSTICAR BANCO DE DADOS ===============================
#=============================================================================================          

def diagnosticar_banco(nome_banco):
    """Diagnóstico detalhado de um banco específico"""
    st.subheader(f"🔍 Diagnóstico do Banco: `{nome_banco}`")
    
    try:
        config = st.session_state.get('db_config', DEFAULT_CONFIG).copy()
        config.pop('database', None)
        
        conexao = mysql.connector.connect(**config)
        cursor = conexao.cursor()
        
        # 1. Verifica existência
        cursor.execute(f"SHOW DATABASES LIKE '{nome_banco}'")
        existe = cursor.fetchone()
        
        if not existe:
            st.error(f"❌ Banco `{nome_banco}` não existe!")
            return
        
        st.success(f"✅ Banco `{nome_banco}` existe no sistema")
        
        # 2. Tenta usar o banco
        try:
            cursor.execute(f"USE `{nome_banco}`")
            st.success("✅ Permissão de acesso: OK")
        except Error as e:
            st.error(f"❌ Sem permissão para acessar: {e}")
            return
        
        # 3. Tabelas
        cursor.execute("SHOW TABLES")
        tabelas = [t[0] for t in cursor.fetchall()]
        st.write(f"**Tabelas no banco:** {len(tabelas)}")
        
        if tabelas:
            # Mostra estatísticas das tabelas
            for tabela in tabelas[:5]:  # Primeiras 5
                cursor.execute(f"""
                    SELECT 
                        TABLE_NAME,
                        ENGINE,
                        TABLE_ROWS,
                        DATA_LENGTH,
                        INDEX_LENGTH,
                        CREATE_TIME,
                        UPDATE_TIME
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = '{nome_banco}'
                    AND TABLE_NAME = '{tabela}'
                """)
                info = cursor.fetchone()
                
                if info:
                    st.write(f"**📊 `{tabela}`**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"Linhas: {info[2]:,}")
                    with col2:
                        st.write(f"Tamanho: {(info[3] or 0) / (1024*1024):.2f} MB")
                    with col3:
                        st.write(f"Engine: {info[1]}")
            
            if len(tabelas) > 5:
                st.write(f"*... e mais {len(tabelas)-5} tabelas*")
        
        # 4. Conexões ativas neste banco
        cursor.execute(f"""
            SELECT COUNT(*) as conexoes_ativas
            FROM INFORMATION_SCHEMA.PROCESSLIST 
            WHERE DB = '{nome_banco}'
        """)
        conexoes = cursor.fetchone()[0]
        st.write(f"**Conexões ativas no banco:** {conexoes}")
        
        if conexoes > 0:
            st.warning("⚠️ Há conexões ativas. Pode interferir na exclusão.")
        
        # 5. Foreign Keys
        cursor.execute(f"""
            SELECT COUNT(*) as total_fks
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = '{nome_banco}'
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        total_fks = cursor.fetchone()[0]
        st.write(f"**Foreign Keys no banco:** {total_fks}")
        
        # 6. Tamanho total do banco
        cursor.execute(f"""
            SELECT 
                SUM(DATA_LENGTH + INDEX_LENGTH) as tamanho_total
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{nome_banco}'
        """)
        tamanho = cursor.fetchone()[0] or 0
        st.write(f"**Tamanho total do banco:** {tamanho / (1024*1024):.2f} MB")
        
        # 7. Última atividade
        cursor.execute(f"""
            SELECT 
                MAX(UPDATE_TIME) as ultima_atualizacao,
                MAX(CREATE_TIME) as criacao_mais_recente
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{nome_banco}'
        """)
        atividade = cursor.fetchone()
        if atividade[0]:
            st.write(f"**Última atualização:** {atividade[0]}")
        
        # 8. Problemas comuns
        st.markdown("---")
        st.subheader("🔧 Verificação de Problemas")
        
        problemas = []
        
        # Tabelas sem PRIMARY KEY
        cursor.execute(f"""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES t
            LEFT JOIN INFORMATION_SCHEMA.STATISTICS s 
                ON t.TABLE_SCHEMA = s.TABLE_SCHEMA 
                AND t.TABLE_NAME = s.TABLE_NAME 
                AND s.INDEX_NAME = 'PRIMARY'
            WHERE t.TABLE_SCHEMA = '{nome_banco}'
            AND s.INDEX_NAME IS NULL
            AND t.TABLE_TYPE = 'BASE TABLE'
        """)
        tabelas_sem_pk = [t[0] for t in cursor.fetchall()]
        
        if tabelas_sem_pk:
            problemas.append(f"❌ Tabelas sem PRIMARY KEY: {', '.join(tabelas_sem_pk[:3])}")
        
        # Tabelas MyISAM (se houver)
        cursor.execute(f"""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{nome_banco}'
            AND ENGINE = 'MyISAM'
        """)
        tabelas_myisam = [t[0] for t in cursor.fetchall()]
        
        if tabelas_myisam:
            problemas.append(f"⚠️ Tabelas MyISAM (prefira InnoDB): {', '.join(tabelas_myisam[:3])}")
        
        if problemas:
            st.warning("**Problemas encontrados:**")
            for problema in problemas:
                st.write(problema)
        else:
            st.success("✅ Nenhum problema crítico detectado!")
        
        cursor.close()
        conexao.close()
        
    except Error as e:
        st.error(f"❌ Erro no diagnóstico: {e}")      
        
    # 8. Problemas comuns
    st.markdown("---")
    st.subheader("🔧 Verificação de Problemas criticos ")

    problemas = []

    # Tabelas sem PRIMARY KEY - CORRIGIDO
    cursor.execute(f"""
        SELECT t.TABLE_NAME  # ← Especifica que vem da tabela t
        FROM INFORMATION_SCHEMA.TABLES t
        LEFT JOIN INFORMATION_SCHEMA.STATISTICS s 
            ON t.TABLE_SCHEMA = s.TABLE_SCHEMA 
            AND t.TABLE_NAME = s.TABLE_NAME 
            AND s.INDEX_NAME = 'PRIMARY'
        WHERE t.TABLE_SCHEMA = '{nome_banco}'
        AND s.INDEX_NAME IS NULL
        AND t.TABLE_TYPE = 'BASE TABLE'
    """)
    tabelas_sem_pk = [t[0] for t in cursor.fetchall()]

    if tabelas_sem_pk:
        problemas.append(f"❌ Tabelas sem PRIMARY KEY: {', '.join(tabelas_sem_pk[:3])}")
        if len(tabelas_sem_pk) > 3:
            problemas[-1] += f" e mais {len(tabelas_sem_pk)-3}"

    # Tabelas MyISAM (se houver)
    cursor.execute(f"""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = '{nome_banco}'
        AND ENGINE = 'MyISAM'
    """)
    tabelas_myisam = [t[0] for t in cursor.fetchall()]

    if tabelas_myisam:
        problemas.append(f"⚠️ Tabelas MyISAM (prefira InnoDB): {', '.join(tabelas_myisam[:3])}")
        if len(tabelas_myisam) > 3:
            problemas[-1] += f" e mais {len(tabelas_myisam)-3}"

    # Outros checks podem ser adicionados aqui:
    # Tabelas muito grandes, índices faltando, etc.

    if problemas:
        st.warning("**Problemas encontrados:**")
        for problema in problemas:
            st.write(problema)
    else:
        st.success("✅ Nenhum problema crítico detectado!") 
        
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar aos Diagnósticos", use_container_width=True):
            st.session_state.pagina_atual = "pagina_diagnosticos"
            st.rerun()
    with col2:
        if st.button("📊 Ver Tabelas do Banco", use_container_width=True):
            st.session_state.pagina_atual = None  # Vai para gerenciar_banco()
            st.rerun()        
# ===============================================================================          
# ===================== FUNÇÃO PARA CONFIGURAÇÕES DO BANCO DE DADOS =============
# ===============================================================================  
def configurar_banco(nome_banco):
    st.subheader(f"⚙️ Configurações: {nome_banco}")
    
    tab1, tab2, tab3 = st.tabs(["💾 Backup", "📤 Exportar", "🔧 Manutenção"])
    
    with tab1:
        st.info("Funcionalidade em desenvolvimento")
        if st.button("🔄 Fazer Backup Agora"):
            st.success(f"Backup do banco '{nome_banco}' criado com sucesso!")
    
    with tab2:
        formato = st.selectbox("Formato de exportação", ["SQL", "CSV"])
        if st.button("📥 Exportar"):
            st.success(f"Banco exportado como {formato}")
    
    with tab3:
        if st.button("🧹 Otimizar Tabelas"):
            st.success("Tabelas otimizadas!")                                 
# =====================================================================  
# ==================== FUNÇÃO PARA GERENCIAR BANCO ====================
# =====================================================================  
def gerenciar_banco(nome_banco):
    """Interface para gerenciar um banco específico"""
    st.title(f"📁 Banco: {nome_banco}")
    
    # Menu lateral
    with st.sidebar:
        st.subheader("📋 Menu")
        opcao = st.radio(
            "Selecione:",
            ["🏠 Visão Geral", "📊 Tabelas", "➕ Nova Tabela"]
        )
        
        st.markdown("---")
        
        if 'pagina_atual' in st.session_state:
             del st.session_state.pagina_atual
        if 'tabela_selecionada' in st.session_state:
             del st.session_state.tabela_selecionada
        if st.button("🔙 Voltar ao Início"):
           st.session_state.banco_selecionado = None    
           st.rerun()
    
    # Conteúdo principal
    if opcao == "🏠 Visão Geral":
        mostrar_visao_geral(nome_banco)
    
    elif opcao == "📊 Tabelas":
        gerenciar_tabelas(nome_banco)
    
    elif opcao == "➕ Nova Tabela":
        criar_nova_tabela(nome_banco)
        
        # Adicione um botão de diagnóstico do banco
col_diag1, col_diag2 = st.columns(2)
with col_diag1:
    if st.button("🔍 Diagnóstico do Banco", use_container_width=True):
        st.session_state.pagina_atual = "diagnostico_banco"
        st.rerun()
with col_diag2:
    if st.button("⚙️ Configurações", use_container_width=True):
        st.session_state.pagina_atual = "configurar_banco"
        st.rerun()
    
          
# ==========================================================================          
# ==================== FUNÇÃO DE VISÃO GERAL DO PROJETO ====================
# ==========================================================================  
def mostrar_visao_geral(nome_banco):
    """Mostra estatísticas do banco"""
    st.subheader("📋 Lista de Tabelas")
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Contar tabelas
        cursor.execute("SHOW TABLES")
        tabelas = cursor.fetchall()
        num_tabelas = len(tabelas)
        
        # Contar registros totais
        total_registros = 0
        
        for tabela in tabelas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM `{tabela[0]}`")
                total_registros += cursor.fetchone()[0]
            except:
                pass
        # ⭐⭐ ADICIONE ESTA PARTE NOVA AQUI ⭐⭐
        # Primeiro: Estatísticas com 4 colunas agora
        st.subheader("📊 Estatistica :")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📋 Tabelas", num_tabelas)
        with col2:
            st.metric("📝 Registros", f"{total_registros:,}")
        with col3:
            status = "✅ Online" if conexao.is_connected() else "❌ Offline"
            st.metric("🔄 Status", status)
        with col4:
            # Nova métrica para relacionamentos
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = %s 
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """, (nome_banco,))
            num_fks = cursor.fetchone()[0]
            st.metric("🔗 Relacionamentos", num_fks)
        
        # ⭐⭐ BOTÃO PARA MAPA DE RELACIONAMENTOS ⭐⭐
        st.markdown("---")
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("🗺️ Mapa de Relacionamentos", 
                        use_container_width=True,
                        #icon="🔗",
                        help="Ver todos os relacionamentos do banco"):
                st.session_state.pagina_atual = "relacionamentos_banco"
                st.rerun()
        
        with col_btn2:
            if st.button(" Otimizar Tabelas", 
                        use_container_width=True,
                        icon="⚡",
                        help="Otimizar todas as tabelas do banco"):
                # Função de otimização se tiver
                st.info("Funcionalidade em desenvolvimento")
                # Se tiver a função: otimizar_tabelas_banco(nome_banco)
        
        with col_btn3:
            if st.button(" Exportar Banco", 
                        use_container_width=True,
                        icon="📥",
                        help="Exportar estrutura e dados"):
                # Função de exportação se tiver
                st.info("Funcionalidade em desenvolvimento")
                # Se tiver a função: exportar_banco(nome_banco)
        
        st.markdown("---")
        
        # ⭐⭐ Listar tabelas  ⭐⭐
        if tabelas:
            st.subheader("📋 Tabelas Presentes Atualmente:")
            for tabela in tabelas:
                col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
                with col1:
                    st.markdown(f'<div class="tabela-row"><b>{tabela[0]}</b></div>', unsafe_allow_html=True)
                with col2:
                    if st.button("📊 Ver", key=f"view_{tabela[0]}"):
                        st.session_state.tabela_selecionada = tabela[0]
                        st.session_state.pagina_atual = "dados_tabela"
                        st.rerun()
                with col3:
                    if st.button("💾 Inserir", key=f"insert_{tabela[0]}"):
                        st.session_state.tabela_selecionada = tabela[0]
                        st.session_state.pagina_atual = "inserir_dados"  # Corrigi para "inserir_dados"
                        st.rerun()
                with col4:
                    if st.button("⚙️ Configurar", key=f"config_{tabela[0]}"):
                        st.session_state.tabela_selecionada = tabela[0]
                        st.session_state.pagina_atual = "editar_tabela"
                        st.rerun()                        
        else:
            st.info("Nenhuma tabela encontrada. Crie a primeira!")
            
            if st.button("➕ Criar Primeira Tabela", type="primary", use_container_width=True):
                # Muda para a página de criação de tabelas
                st.session_state.pagina_atual = "nova_tabela"
                st.rerun()
                
    except Error as e:
        st.error(f"Erro: {e}")
    
    finally:
        cursor.close()
        conexao.close()
        
    # Botão para voltar
    st.markdown("---")
    if st.button("⬅️ Voltar a Lista de Bancos de Dados", use_container_width=True):
    #if st.button("🔙 Voltar ao Banco"):
       st.session_state.banco_selecionado = None
       st.rerun() 
    st.markdown("---")       
# ==================================================================  
# ==================== FUNÇÃO GERENCIAR TABELAS ====================
# ==================================================================  
def gerenciar_tabelas(nome_banco):
    """Listar e gerencia tabelas do banco"""
    st.title("📋 Listar Tabelas")
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    cursor.execute("SHOW TABLES")
    tabelas = [t[0] for t in cursor.fetchall()]
    
    if not tabelas:
        st.info("📭 Nenhuma tabela encontrada. Crie a primeira!")
        return
    
    st.subheader("📋 Tabelas Disponíveis")
    
    for tabela in tabelas:
        with st.expander(f"📊 {tabela}", expanded=False):
            # Mostrar estrutura
            cursor.execute(f"DESCRIBE `{tabela}`")
            estrutura = cursor.fetchall()
            
            df_estrutura = pd.DataFrame(
                estrutura,
                columns=['Campo', 'Tipo', 'Nulo', 'Chave', 'Default', 'Extra']
            )
            
            st.dataframe(df_estrutura, use_container_width=True)
            
            # Botões de ação
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if st.button("👁️ Ver Dados", key=f"view_data_{tabela}"):
                    st.session_state.tabela_selecionada = tabela
                    st.session_state.pagina_atual = "dados_tabela"
                    st.rerun()
            
            with col2:
                if st.button("➕ Inserir Registos", key=f"insert_{tabela}"):
                    st.session_state.tabela_selecionada = tabela
                    st.session_state.pagina_atual = "inserir_dados"
                    st.rerun()
            
            with col3:
                if st.button("✏️ Editar Tabela", key=f"struct_{tabela}"):
                    st.session_state.tabela_selecionada = tabela
                    st.session_state.pagina_atual = "editar_tabela"
                    st.rerun()
            
            with col4:
                if st.button("📝 Nova Coluna", key=f"addcol_{tabela}"):
                    st.session_state.tabela_selecionada = tabela
                    st.session_state.pagina_atual = "adicionar_coluna"
                    st.rerun()
            
            with col5:
                # Usando st.checkbox diretamente (simples)
                excluir = st.checkbox(f"Excluir {tabela}", key=f"chk_drop_{tabela}")
                
                if excluir:
                    st.warning(f"Tem certeza que deseja excluir '{tabela}'?")
                    
                    col_sim, col_nao = st.columns(2)
                    with col_sim:
                        if st.button("Sim, excluir", key=f"btn_sim_{tabela}", type="primary"):
                            try:
                                cursor.execute(f"DROP TABLE IF EXISTS `{tabela}`")
                                conexao.commit()
                                st.success(f"✅ Tabela '{tabela}' excluída!")
                                st.rerun()
                            except Error as e:
                                st.error(f"❌ Erro: {e}")
                    
                    with col_nao:
                        if st.button("Cancelar", key=f"btn_nao_{tabela}"):
                            # Desmarca o checkbox
                            st.session_state[f"chk_drop_{tabela}"] = False
                            st.rerun()
                            
    # Botão para voltar
    st.markdown("---")
    if st.button("⬅️ Voltar a Lista de Bancos de Dados", use_container_width=True):
       st.session_state.banco_selecionado = None
       st.rerun() 
    st.markdown("---")                         
    
    cursor.close()
    conexao.close()
# =======================================================================  
# ==================== FUNÇÃO PARA CRIAR NOVA TABELA ====================
# =======================================================================   
def criar_nova_tabela(nome_banco):
    """Cria uma nova tabela com campos personalizados"""
    # Título principal grande
    st.title("🏗️ Criar Nova Tabela")
    
    # Indicador do banco logo abaixo
    st.markdown(f"""
    <div style="
        background: #E3F2FD;
        color: #0D47A1;
        padding: 10px 20px;
        border-radius: 10px;
        margin: -10px 0 30px 0;
        border-left: 5px solid #2196F3;
        font-size: 16px;
    ">
        📁 Banco: <strong>{nome_banco}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # ============ BOTÃO VOLTAR NO TOPO ============
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar às Tabelas", use_container_width=True):
            st.session_state.pagina_atual = "dados_tabela"
            st.rerun()
    with col2:
        if st.button("🏠 Página Inicial", use_container_width=True):
            st.session_state.banco_selecionado = None
            st.session_state.pagina_atual = None
            st.rerun()
    
        st.markdown("---")
        
        # 1. NOME DA TABELA
        nome_tabela = st.text_input(
            "🔤 Nome da nova tabela:", 
            placeholder="ex: clientes, produtos, vendas",
            key=f"nome_tabela_{nome_banco}"
        )
        
        st.markdown("---")
    
    if not nome_tabela:
        # Mostrar apenas UMA mensagem
        st.info("👆 Digite um nome para a tabela acima para começar")
        
        # Botão CANCELAR visível mesmo sem nome
        if st.button("❌ Cancelar", type="secondary", use_container_width=True):
            # Mesma lógica do botão Voltar
            st.session_state.pagina_atual = None
            st.session_state.banco_selecionado = nome_banco
            st.rerun()
        return
    
    # Continuar com o resto se tiver nome da tabela
    st.markdown(f"### 📋 Criando tabela: **{nome_tabela}**")
    st.markdown("---")
    
    # Inicializar estado para colunas
    chave = f"colunas_{nome_banco}"
    if chave not in st.session_state:
        st.session_state[chave] = []
    
    # 2. ADICIONAR COLUNAS
    st.markdown("### 🎯 Adicionar Campos/Colunas")
    st.caption("Configure cada campo da tabela abaixo:")
    
    with st.form(key=f"form_add_col_{nome_banco}", border=True):
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
        
        with col1:
            nome_col = st.text_input("Nome do campo", placeholder="ex: id, nome, email", key=f"nome_col_{nome_banco}")
        
        with col2:
            tipo_col = st.selectbox(
                "Tipo de dado", 
                ["INT", "VARCHAR(100)", "VARCHAR(255)", "TEXT", "DATE", 
                 "DATETIME", "DECIMAL(10,2)", "FLOAT", "BOOLEAN"],
                index=1,
                key=f"tipo_col_{nome_banco}"
            )
        
        with col3:
            pk_col = st.checkbox("PK", help="Chave Primária", key=f"pk_col_{nome_banco}")
        
        with col4:
            null_col = st.checkbox("NULL", value=True, help="Permite valores nulos", key=f"null_col_{nome_banco}")
        
        with col5:
            ai_col = st.checkbox("AI", help="Auto Incremento (só para INT)", key=f"ai_col_{nome_banco}")
        
        # Botões do formulário
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            btn_adicionar = st.form_submit_button(
                "➕ Adicionar Campo", 
                type="primary",
                use_container_width=True
            )
        with col_btn2:
            btn_limpar = st.form_submit_button(
                "🧹 Limpar Campos", 
                use_container_width=True
            )
        
        if btn_adicionar:
            if nome_col:
                # Validar combinações
                temp_ai = ai_col
                temp_null = null_col
                
                if ai_col and tipo_col != "INT":
                    st.warning("⚠️ Auto Incremento só funciona com tipo INT")
                    temp_ai = False
                
                if pk_col and null_col:
                    st.warning("⚠️ Chave Primária geralmente não permite NULL")
                    temp_null = False
                
                st.session_state[chave].append({
                    'nome': nome_col,
                    'tipo': tipo_col,
                    'pk': pk_col,
                    'null': temp_null,
                    'ai': temp_ai
                })
                st.success(f"Campo '{nome_col}' adicionado!")
                st.rerun()
            else:
                st.warning("⚠️ Digite um nome para o campo!")
        
        if btn_limpar:
            st.session_state[chave] = []
            st.rerun()
    
    # 3. MOSTRAR COLUNAS ADICIONADAS
    if st.session_state[chave]:
        st.markdown(f"### 📊 Estrutura da Tabela ({len(st.session_state[chave])} campos)")
        
        for i, col in enumerate(st.session_state[chave]):
            with st.container(border=True):
                col_disp1, col_disp2, col_disp3 = st.columns([3, 1, 1])
                
                with col_disp1:
                    icones = []
                    if col['pk']: icones.append("🔑 PK")
                    if col['ai']: icones.append("⚡ AI")
                    if not col['null']: icones.append("❌ NOT NULL")
                    
                    info_icones = " | ".join(icones) if icones else "✅ Normal"
                    
                    st.markdown(f"**{col['nome']}** `{col['tipo']}`")
                    st.caption(info_icones)
                
                with col_disp2:
                    if st.button("✏️", key=f"edit_{i}_{nome_banco}", help="Editar"):
                        st.info("Para editar, remova e adicione novamente")
                
                with col_disp3:
                    if st.button("🗑️", key=f"del_{i}_{nome_banco}", help="Remover"):
                        st.session_state[chave].pop(i)
                        st.rerun()
    
    else:
        st.info("👆 Adicione o primeiro campo acima para começar a construir a tabela.")
    
    # ============ RODAPÉ COM AÇÕES ============
    st.markdown("---")
    
    with st.container():
        st.markdown("### 🎯 Ações")
        
        col_acao1, col_acao2, col_acao3 = st.columns(3)
        
        with col_acao1:
            if st.session_state.get(chave):
                if st.button("✅ Criar Tabela", 
                           type="primary", 
                           use_container_width=True,
                           key="criar_tabela_btn_final"):
                    # Chama sua função para criar a tabela
                    criar_tabela_no_banco(nome_banco, nome_tabela, st.session_state[chave])
                    # Limpar após criação
                    if f"colunas_{nome_banco}" in st.session_state:
                        del st.session_state[f"colunas_{nome_banco}"]
                    # Voltar para gerenciar banco
                    st.session_state.pagina_atual = None
                    st.session_state.banco_selecionado = nome_banco
                    st.rerun()
        
        with col_acao2:
            if st.button("🧹 Limpar Campos", 
                       use_container_width=True,
                       key="limpar_campos_final"):
                if chave in st.session_state:
                    st.session_state[chave] = []
                st.rerun()
        
        with col_acao3:
            if st.button("❌ Cancelar", 
                       type="secondary",
                       use_container_width=True,
                       key="cancelar_final"):
                # Limpar TUDO
                if chave in st.session_state:
                    del st.session_state[chave]
                # Voltar para gerenciar banco
                st.session_state.pagina_atual = None
                st.session_state.banco_selecionado = nome_banco
                st.rerun()
    
# ===========================================================================  
# ==================== FUNÇÃO QUE CRIA A TABELA NO BANCO ====================
# ===========================================================================  
def criar_tabela_no_banco(nome_banco, nome_tabela, colunas):
    """Executa o SQL para criar a tabela no MySQL"""
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Construir SQL
        definicoes = []
        chaves_primarias = []
        
        for col in colunas:
            definicao = f"`{col['nome']}` {col['tipo']}"
            
            if not col['null']:
                definicao += " NOT NULL"
            
            if col['ai']:
                definicao += " AUTO_INCREMENT"
            
            if col['pk']:
                chaves_primarias.append(col['nome'])
            
            definicoes.append(definicao)
        
        # Adicionar PRIMARY KEY se houver
        if chaves_primarias:
            pk_def = f"PRIMARY KEY ({', '.join([f'`{pk}`' for pk in chaves_primarias])})"
            definicoes.append(pk_def)
        
        sql_colunas = ",\n    ".join(definicoes)
        sql = f"""CREATE TABLE IF NOT EXISTS `{nome_tabela}` (
    {sql_colunas}
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
        
        # Mostrar SQL (para debug/transparência)
        with st.expander("📝 Ver SQL que será executado"):
            st.code(sql, language="sql")
        
        # Executar
        cursor.execute(sql)
        conexao.commit()
        
        # Sucesso!
        st.balloons()
        st.success(f"🎉 Tabela **'{nome_tabela}'** criada com sucesso!")
        
        # Mostrar estrutura criada
        st.markdown("### 📋 Estrutura Criada:")
        cursor.execute(f"DESCRIBE `{nome_tabela}`")
        estrutura = cursor.fetchall()
        
        if estrutura:
            df = pd.DataFrame(
                estrutura,
                columns=['Campo', 'Tipo', 'Nulo', 'Chave', 'Default', 'Extra']
            )
            st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        
        # Opções pós-criação
        st.markdown("### 📝 O que deseja fazer agora?")
        
        col_op1, col_op2, col_op3 = st.columns(3)
        
        with col_op1:
            if st.button("➕ Inserir dados", use_container_width=True):
                st.session_state.tabela_selecionada = nome_tabela
                st.session_state.pagina_atual = "inserir_registro"
                st.rerun()
        
        with col_op2:
            if st.button("📋 Ver tabela", use_container_width=True):
                st.session_state.tabela_selecionada = nome_tabela
                st.session_state.pagina_atual = "dados_tabela"
                st.rerun()
        
        with col_op3:
            if st.button("🏠 Voltar ao banco", use_container_width=True):
                # Limpar estado
                chave = f"colunas_{nome_banco}"
                if chave in st.session_state:
                    del st.session_state[chave]
                st.rerun()
        
    except Error as e:
        st.error(f"❌ Erro ao criar tabela: {e}")
        st.info("💡 Dica: Verifique se o nome da tabela já existe ou se há erros na sintaxe.")
        conexao.rollback()
    
    finally:
        cursor.close()
        conexao.close()
# ===============================================================================  
# ==================== FUNÇÃO PARA ADICIONAR COLUNA À TABELA ====================
# ===============================================================================   
def adicionar_coluna_tabela(nome_banco, nome_tabela):
    """Adiciona uma nova coluna a uma tabela existente"""
    st.title(f"📝 Adicionar Coluna à Tabela: {nome_tabela}")
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Mostrar estrutura atual
        cursor.execute(f"DESCRIBE `{nome_tabela}`")
        estrutura = cursor.fetchall()
        
        st.subheader("🏗️ Estrutura Atual")
        df = pd.DataFrame(
            estrutura,
            columns=['Campo', 'Tipo', 'Nulo', 'Chave', 'Default', 'Extra']
        )
        st.dataframe(df, use_container_width=True)
        
        # Formulário para adicionar nova coluna
        st.markdown("---")
        st.subheader("➕ Adicionar Nova Coluna")
        
        # ⚠️ IMPORTANTE: Criar variáveis fora do formulário
        form_submitted = False
        novo_nome = ""
        novo_tipo = ""
        posicao = ""
        permite_null = True
        valor_default = ""
        coluna_unica = False
        chave_primaria = False
        
        with st.form(key=f"form_add_col_{nome_tabela}_{hash(nome_tabela)}"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                novo_nome = st.text_input("Nome da nova coluna:", 
                                        placeholder="ex: telefone, email, preco",
                                        key=f"novo_nome_{nome_tabela}")
            
            with col2:
                novo_tipo = st.selectbox(
                    "Tipo de dado:", 
                    ["VARCHAR(100)", "VARCHAR(255)", "INT", "BIGINT", "TEXT", 
                     "DATE", "DATETIME", "TIMESTAMP", "DECIMAL(10,2)", "FLOAT", 
                     "BOOLEAN", "ENUM('ativo','inativo')"],
                    key=f"novo_tipo_{nome_tabela}"
                )
            
            with col3:
                posicao = st.selectbox(
                    "Posição:",
                    ["ÚLTIMA", "PRIMEIRA", "APÓS id"],
                    key=f"posicao_{nome_tabela}"
                )
            
            # Opções adicionais em múltiplas colunas
            col_a, col_b, col_c, col_d = st.columns(4)
            
            with col_a:
                permite_null = st.checkbox("Permitir NULL", value=True,
                                         key=f"permite_null_{nome_tabela}")
            
            with col_b:
                # ⭐⭐ MELHORIA: Ajuda para campos DATE ⭐⭐
                tipo_atual = st.session_state.get(f"novo_tipo_{nome_tabela}", "VARCHAR(100)")
                
                placeholder_text = "ex: João"
                help_text = "Valor inicial para novos registros"
                
                if "DATE" in tipo_atual.upper():
                    placeholder_text = "CURRENT_DATE ou 2024-01-15"
                    help_text = "Para datas: CURRENT_DATE ou formato YYYY-MM-DD"
                elif "INT" in tipo_atual.upper():
                    placeholder_text = "ex: 0, 100"
                    help_text = "Apenas números"
                
                valor_default = st.text_input(
                    "Valor padrão (opcional):",
                    placeholder=placeholder_text,
                    help=help_text,
                    key=f"valor_default_{nome_tabela}"
                )
            
            with col_c:
                coluna_unica = st.checkbox("Valores Únicos (UNIQUE)", 
                                         help="Não permitir valores duplicados nesta coluna",
                                         key=f"coluna_unica_{nome_tabela}")
            
            with col_d:
                chave_primaria = st.checkbox("Chave Primária (PK)", 
                                           help="Define como chave primária",
                                           key=f"chave_primaria_{nome_tabela}")
            
            # ⚠️ CORRIGIDO: Usar form_submit_button DENTRO do formulário
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            
            with col_btn1:
                submit = st.form_submit_button("✅ Adicionar Coluna", 
                                             type="primary", 
                                             use_container_width=True)
            
            with col_btn2:
                limpar = st.form_submit_button("🧹 Limpar", 
                                             use_container_width=True)
            
            with col_btn3:
                cancelar = st.form_submit_button("❌ Cancelar", 
                                               use_container_width=True)
                
            with col_btn4:
                voltar = st.form_submit_button("🔙 Voltar", 
                                             use_container_width=True)
        
        # ⚠️ IMPORTANTE: Processar ações FORA do formulário
        if submit:
            form_submitted = True
        elif limpar:
            st.rerun()
        elif cancelar or voltar:
            st.session_state.pagina_atual = None
            st.rerun()
        
        # Se foi submetido, processar
        if form_submitted and novo_nome:
            try:
                # Construir SQL para adicionar coluna
                sql = f"ALTER TABLE `{nome_tabela}` ADD COLUMN `{novo_nome}` {novo_tipo}"
                
                if not permite_null:
                    sql += " NOT NULL"
                
                if valor_default:
                    # ⭐⭐ CORREÇÃO PARA CAMPOS DATE ⭐⭐
                    tipo_upper = novo_tipo.upper()
                    
                    if tipo_upper.startswith(('INT', 'BIGINT', 'DECIMAL', 'FLOAT', 'DOUBLE')):
                        # Para números
                        sql += f" DEFAULT {valor_default}"
                    
                    elif 'DATE' in tipo_upper or 'TIMESTAMP' in tipo_upper:
                        # Para datas
                        valor_default_upper = valor_default.upper().strip()
                        
                        # Valores especiais do MySQL para datas
                        valores_especiais = [
                            'CURRENT_DATE', 'CURRENT_TIMESTAMP', 'NOW()',
                            'CURDATE()', 'CURTIME()', 'UTC_DATE', 'UTC_TIMESTAMP'
                        ]
                        
                        if valor_default_upper in valores_especiais:
                            # Funções do MySQL
                            sql += f" DEFAULT {valor_default_upper}"
                        else:
                            # Tentar validar formato de data
                            try:
                                # Verificar se está em formato YYYY-MM-DD
                                from datetime import datetime
                                datetime.strptime(valor_default, '%Y-%m-%d')
                                sql += f" DEFAULT '{valor_default}'"
                            except ValueError:
                                # Tentar outros formatos comuns
                                formatos_tentados = ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%Y/%m/%d']
                                data_convertida = None
                                
                                for formato in formatos_tentados:
                                    try:
                                        dt = datetime.strptime(valor_default, formato)
                                        data_convertida = dt.strftime('%Y-%m-%d')
                                        break
                                    except ValueError:
                                        continue
                                
                                if data_convertida:
                                    sql += f" DEFAULT '{data_convertida}'"
                                else:
                                    st.error(f"❌ Formato de data inválido! Use: CURRENT_DATE ou YYYY-MM-DD")
                                    conexao.rollback()
                                    return
                    
                    elif 'TIME' in tipo_upper:
                        # Para horas
                        sql += f" DEFAULT '{valor_default}'"
                    
                    else:
                        # Para strings (VARCHAR, TEXT, ENUM, etc)
                        sql += f" DEFAULT '{valor_default}'"
                
                # ADICIONAR UNIQUE SE SOLICITADO
                if coluna_unica:
                    sql += " UNIQUE"
                
                if posicao == "PRIMEIRA":
                    sql += " FIRST"
                elif posicao == "APÓS id":
                    # Verificar se existe coluna 'id'
                    cursor.execute(f"SHOW COLUMNS FROM `{nome_tabela}` LIKE 'id'")
                    if cursor.fetchone():
                        sql += " AFTER id"
                
                # Executar SQL da coluna
                cursor.execute(sql)
                
                # SE FOR CHAVE PRIMÁRIA, ADICIONAR APÓS CRIAR A COLUNA
                if chave_primaria:
                    try:
                        # Primeiro, remover PK existente se houver
                        cursor.execute(f"SHOW KEYS FROM `{nome_tabela}` WHERE Key_name = 'PRIMARY'")
                        if cursor.fetchone():
                            st.warning("⚠️ A tabela já tem uma chave primária. Adicionando apenas UNIQUE.")
                            # Se já tem PK, adiciona apenas UNIQUE se não tiver sido adicionado
                            if coluna_unica:
                                sql_unique = f"ALTER TABLE `{nome_tabela}` ADD UNIQUE (`{novo_nome}`)"
                                cursor.execute(sql_unique)
                        else:
                            sql_pk = f"ALTER TABLE `{nome_tabela}` ADD PRIMARY KEY (`{novo_nome}`)"
                            cursor.execute(sql_pk)
                    except Error as e:
                        st.error(f"❌ Erro ao definir chave primária: {e}")
                        conexao.rollback()
                        return
                
                conexao.commit()
                
                # Mensagem de sucesso detalhada
                mensagem = f"✅ Coluna **{novo_nome}** adicionada com sucesso!"
                if coluna_unica:
                    mensagem += " 🔒 **(UNIQUE - Valores Únicos)**"
                if chave_primaria:
                    mensagem += " 🗝️ **(PRIMARY KEY)**"
                
                st.markdown(f"""
                <div class="success-message">
                    {mensagem}
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar SQL executado
                with st.expander("📄 SQL Executado", expanded=True):
                    st.code(sql + (f";\nALTER TABLE `{nome_tabela}` ADD PRIMARY KEY (`{novo_nome}`)" 
                                  if chave_primaria else ""))
                
                # Mostrar nova estrutura
                cursor.execute(f"DESCRIBE `{nome_tabela}`")
                nova_estrutura = cursor.fetchall()
                
                df_nova = pd.DataFrame(
                    nova_estrutura,
                    columns=['Campo', 'Tipo', 'Nulo', 'Chave', 'Default', 'Extra']
                )
                
                st.subheader("🏗️ Nova Estrutura da Tabela")
                st.dataframe(df_nova, use_container_width=True)
                
                # ========== ⚠️ CORRIGIDO: Botões FORA do formulário ==========
                # Agora sim podemos usar st.button() normalmente
                st.markdown("---")
                col_op1, col_op2, col_op3 = st.columns(3)
               
                with col_op1:
                    # ⚠️ AGORA É st.button() normal (fora do formulário)
                    if st.button("➕ Adicionar outra coluna", 
                              use_container_width=True,
                              key=f"btn_outra_col_{nome_tabela}_{hash(nome_tabela)}"):
                        st.rerun()
                
                with col_op2:
                    # ⚠️ AGORA É st.button() normal (fora do formulário)
                    if st.button("📊 Ver dados da tabela", 
                               use_container_width=True,
                               key=f"btn_ver_dados_{nome_tabela}_{hash(nome_tabela)}"):
                        st.session_state.pagina_atual = "dados_tabela"
                        st.rerun()
                
                with col_op3:
                    # ⚠️ AGORA É st.button() normal (fora do formulário)
                    if st.button("🔙 Voltar ao banco", 
                               use_container_width=True,
                               key=f"btn_voltar_banco_{nome_tabela}_{hash(nome_tabela)}"):
                        st.session_state.pagina_atual = None
                        st.session_state.tabela_selecionada = None
                        st.rerun()
                
            except Error as e:
                st.error(f"❌ Erro ao adicionar coluna: {e}")
                conexao.rollback()
    
    except Error as e:
        st.error(f"Erro: {e}")
    
    finally:
        cursor.close()
        conexao.close()
# ===========================================================================================          
# ====================           TABELAS DE REFERENCIA         ==============================        
# =========================   FUNÇÃO PARA TABELAS DE REFERENCIA =============================
#============================================================================================          
        
def criar_tabela_referencia(nome_banco, nome_tabela, campo_referencia):
    """Cria uma tabela de referência para um campo combobox"""
    
    st.subheader("📋 Criar Tabela de Referência")
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # 1. Criar tabela de referência
        tabela_ref = f"ref_{nome_tabela}_{campo_referencia}"
        
        st.info(f"Vou criar a tabela: **{tabela_ref}**")
        
        # SQL para criar tabela de referência
        sql_criar_ref = f"""
        CREATE TABLE IF NOT EXISTS `{tabela_ref}` (
            id INT PRIMARY KEY AUTO_INCREMENT,
            valor VARCHAR(100) UNIQUE NOT NULL,
            descricao VARCHAR(255),
            ordem INT DEFAULT 0,
            ativo BOOLEAN DEFAULT TRUE
        );
        """
        
        # 2. Alterar a coluna original para ser FOREIGN KEY
        sql_alterar_coluna = f"""
        ALTER TABLE `{nome_tabela}` 
        MODIFY COLUMN `{campo_referencia}` INT,
        ADD FOREIGN KEY (`{campo_referencia}`) REFERENCES `{tabela_ref}`(id);
        """
        
        # Mostrar SQLs
        with st.expander("📄 SQLs que serão executados"):
            st.code(sql_criar_ref)
            st.code(sql_alterar_coluna)
        
        # Executar
        if st.button("✅ Criar Tabela de Referência", type="primary"):
            cursor.execute(sql_criar_ref)
            
            # Inserir valores padrão se especificados
            valores_padrao = st.text_area(
                "Valores iniciais (um por linha):",
                value="Livre\nOcupado\nManutenção\nLimpeza",
                height=100
            )
            
            if valores_padrao:
                valores = [v.strip() for v in valores_padrao.split('\n') if v.strip()]
                for i, valor in enumerate(valores):
                    cursor.execute(
                        f"INSERT INTO `{tabela_ref}` (valor, ordem) VALUES (%s, %s)",
                        (valor, i+1)
                    )
            
            # Alterar a coluna original
            cursor.execute(sql_alterar_coluna)
            conexao.commit()
            
            st.success(f"""
            ✅ Tabela de referência criada com sucesso!
            
            **Estrutura criada:**
            - Tabela de referência: `{tabela_ref}`
            - Coluna original `{campo_referencia}` agora é FOREIGN KEY
            - Use a opção 'Gerenciar Valores' para adicionar/remover opções
            """)
            
            # Mostrar valores inseridos
            cursor.execute(f"SELECT id, valor FROM `{tabela_ref}` ORDER BY ordem")
            valores_inseridos = cursor.fetchall()
            
            if valores_inseridos:
                st.write("**Valores inseridos:**")
                for id_val, valor in valores_inseridos:
                    st.write(f"`{id_val}` - {valor}")
    
    except Error as e:
        st.error(f"❌ Erro: {e}")
        conexao.rollback()
    
    finally:
        cursor.close()
        conexao.close()
        
    # Botão para voltar
    st.markdown("---")
    if st.button("🔙 Voltar", use_container_width=True):
        st.session_state.pagina_atual = None
        st.rerun()     
# ===========================================================================================          
# ====================     FUNÇÃO GERENCIAMENTO DE VALORES   ================================        
#============================================================================================          
def gerenciar_tabela_referencia(nome_banco, nome_tabela_ref):
    """Gerencia os valores de uma tabela de referência"""
    
    st.title(f"📋 Gerenciar: {nome_tabela_ref}")
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Verificar se é uma tabela de referência
        cursor.execute(f"SHOW COLUMNS FROM `{nome_tabela_ref}`")
        colunas = cursor.fetchall()
        
        # Buscar valores atuais
        cursor.execute(f"SELECT id, valor, descricao, ordem, ativo FROM `{nome_tabela_ref}` ORDER BY ordem")
        valores = cursor.fetchall()
        
        st.subheader("📝 Valores Atuais")
        
        if valores:
            # Criar DataFrame para mostrar
            df = pd.DataFrame(
                valores,
                columns=['ID', 'Valor', 'Descrição', 'Ordem', 'Ativo']
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📭 Nenhum valor cadastrado ainda.")
        
        st.markdown("---")
        
        # Ações disponíveis
        acao = st.radio(
            "📋 Ação:",
            ["➕ Adicionar Novo", "✏️ Editar Existente", "🗑️ Remover", "🔄 Reordenar"],
            horizontal=True
        )
        
        if acao == "➕ Adicionar Novo":
            with st.form(key=f"form_add_ref_{nome_tabela_ref}"):
                novo_valor = st.text_input("Novo valor:", placeholder="ex: Reservado")
                descricao = st.text_input("Descrição (opcional):", placeholder="Descrição detalhada")
                ordem = st.number_input("Ordem:", min_value=1, value=len(valores)+1)
                
                if st.form_submit_button("✅ Adicionar", type="primary"):
                    cursor.execute(
                        f"INSERT INTO `{nome_tabela_ref}` (valor, descricao, ordem) VALUES (%s, %s, %s)",
                        (novo_valor, descricao, ordem)
                    )
                    conexao.commit()
                    st.success(f"✅ Valor '{novo_valor}' adicionado!")
                    st.rerun()
        
        elif acao == "✏️ Editar Existente":
            if valores:
                # Selecionar valor para editar
                opcoes = [f"{v[0]} - {v[1]}" for v in valores]
                selecionado = st.selectbox("Selecione o valor para editar:", opcoes)
                
                if selecionado:
                    id_selecionado = int(selecionado.split(" - ")[0])
                    
                    # Buscar dados atuais
                    cursor.execute(f"SELECT valor, descricao, ordem, ativo FROM `{nome_tabela_ref}` WHERE id = %s", (id_selecionado,))
                    atual = cursor.fetchone()
                    
                    with st.form(key=f"form_edit_ref_{nome_tabela_ref}"):
                        novo_valor = st.text_input("Valor:", value=atual[0])
                        nova_desc = st.text_input("Descrição:", value=atual[1] if atual[1] else "")
                        nova_ordem = st.number_input("Ordem:", min_value=1, value=atual[2])
                        novo_status = st.checkbox("Ativo", value=bool(atual[3]))
                        
                        if st.form_submit_button("💾 Salvar Alterações", type="primary"):
                            cursor.execute(
                                f"UPDATE `{nome_tabela_ref}` SET valor = %s, descricao = %s, ordem = %s, ativo = %s WHERE id = %s",
                                (novo_valor, nova_desc, nova_ordem, novo_status, id_selecionado)
                            )
                            conexao.commit()
                            st.success("✅ Valor atualizado!")
                            st.rerun()
        
        elif acao == "🗑️ Remover":
            if valores:
                selecionado = st.selectbox(
                    "Selecione o valor para remover:",
                    [f"{v[0]} - {v[1]}" for v in valores]
                )
                
                if selecionado and st.button("🗑️ Remover Permanentemente", type="primary"):
                    id_remover = int(selecionado.split(" - ")[0])
                    
                    # Verificar se está sendo usado
                    # (precisa identificar quais tabelas usam esta referência)
                    st.warning("⚠️ Verifique se este valor não está sendo usado antes de remover!")
                    
                    if st.checkbox("Confirmar remoção"):
                        cursor.execute(f"DELETE FROM `{nome_tabela_ref}` WHERE id = %s", (id_remover,))
                        conexao.commit()
                        st.success("✅ Valor removido!")
                        st.rerun()
        
        elif acao == "🔄 Reordenar":
            if valores:
                st.write("Arraste para reordenar os valores:")
                
                # Criar lista ordenável
                valores_ordenaveis = [{"id": v[0], "valor": v[1], "ordem": v[3]} for v in valores]
                
                # Interface simples de reordenação
                for i, item in enumerate(valores_ordenaveis):
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        st.write(f"**{i+1}.**")
                    with col2:
                        st.write(item['valor'])
                    with col3:
                        nova_ordem = st.number_input(
                            "Nova ordem:", 
                            min_value=1, 
                            value=item['ordem'],
                            key=f"ordem_{item['id']}"
                        )
                        
                        if nova_ordem != item['ordem']:
                            cursor.execute(
                                f"UPDATE `{nome_tabela_ref}` SET ordem = %s WHERE id = %s",
                                (nova_ordem, item['id'])
                            )
                
                if st.button("💾 Salvar Ordenação", type="primary"):
                    conexao.commit()
                    st.success("✅ Ordenação salva!")
                    st.rerun()
    
    except Error as e:
        st.error(f"❌ Erro: {e}")
    
    finally:
        cursor.close()
        conexao.close()
# ===========================================================================================          
# ====================       FUNÇÃO INSERIR/EDITAR DADOS     ================================        
#============================================================================================ 
def inserir_dados_com_combobox(nome_banco, nome_tabela):
    """Insere dados com combobox de referências"""
    
    st.title(f"📝 Inserir Dados em: {nome_tabela}")
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Obter estrutura da tabela
        cursor.execute(f"DESCRIBE `{nome_tabela}`")
        colunas = cursor.fetchall()
        
        # Obter FOREIGN KEYS para identificar combobox
        cursor.execute(f"""
            SELECT 
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = %s
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """, (nome_banco, nome_tabela))
        
        foreign_keys = cursor.fetchall()
        fk_dict = {fk[0]: (fk[1], fk[2]) for fk in foreign_keys}
        
        # Formulário para inserir dados
        with st.form(key=f"form_insert_{nome_tabela}"):
            dados = {}
            
            for coluna in colunas:
                nome_col = coluna[0]
                tipo_col = coluna[1]
                
                # Pular colunas auto_increment
                if 'auto_increment' in coluna[5].lower():
                    continue
                
                # Verificar se é FOREIGN KEY (combobox)
                if nome_col in fk_dict:
                    tabela_ref, col_ref = fk_dict[nome_col]
                    
                    # Buscar valores da tabela de referência
                    cursor.execute(f"SELECT id, valor FROM `{tabela_ref}` WHERE ativo = TRUE ORDER BY ordem")
                    valores_ref = cursor.fetchall()
                    
                    if valores_ref:
                        # Criar combobox
                        opcoes = [(None, "-- Selecione --")] + valores_ref
                        opcoes_display = [f"{v[0]} - {v[1]}" if v[0] else "-- Selecione --" for v in opcoes]
                        
                        selecionado = st.selectbox(
                            f"{nome_col}:",
                            opcoes_display,
                            key=f"cb_{nome_col}"
                        )
                        
                        # Extrair ID selecionado
                        if selecionado != "-- Selecione --":
                            id_selecionado = int(selecionado.split(" - ")[0])
                            dados[nome_col] = id_selecionado
                        else:
                            dados[nome_col] = None
                        
                        # Botão para gerenciar valores
                        if st.button(f"📋 Gerenciar {tabela_ref}", key=f"btn_ger_{nome_col}"):
                            st.session_state.gerenciar_tabela = tabela_ref
                            st.rerun()
                    
                else:
                    # Campo normal
                    if tipo_col.startswith('varchar') or tipo_col.startswith('text'):
                        valor = st.text_input(f"{nome_col}:", key=f"inp_{nome_col}")
                        dados[nome_col] = valor if valor else None
                    
                    elif tipo_col.startswith('int') or tipo_col.startswith('decimal'):
                        valor = st.number_input(f"{nome_col}:", key=f"num_{nome_col}")
                        dados[nome_col] = valor
                    
                    elif 'date' in tipo_col.lower():
                        valor = st.date_input(f"{nome_col}:", key=f"date_{nome_col}")
                        dados[nome_col] = valor
                    
                    elif tipo_col.lower() == 'boolean':
                        valor = st.checkbox(f"{nome_col}:", key=f"bool_{nome_col}")
                        dados[nome_col] = valor
                    
                    else:
                        valor = st.text_input(f"{nome_col} ({tipo_col}):", key=f"other_{nome_col}")
                        dados[nome_col] = valor
            
            # Botão de submit
            if st.form_submit_button("💾 Salvar Dados", type="primary"):
                # Construir SQL
                colunas_nomes = [f"`{k}`" for k in dados.keys()]
                placeholders = ["%s"] * len(dados)
                
                sql = f"INSERT INTO `{nome_tabela}` ({', '.join(colunas_nomes)}) VALUES ({', '.join(placeholders)})"
                
                # Executar
                try:
                    cursor.execute(sql, list(dados.values()))
                    conexao.commit()
                    
                    # Obter ID inserido
                    id_inserido = cursor.lastrowid
                    
                    st.success(f"✅ Dados inseridos com sucesso! (ID: {id_inserido})")
                    
                    # Mostrar dados inseridos
                    cursor.execute(f"SELECT * FROM `{nome_tabela}` WHERE id = %s", (id_inserido,))
                    registro = cursor.fetchone()
                    
                    # Converter para DataFrame com nomes de colunas
                    col_names = [col[0] for col in colunas]
                    df_registro = pd.DataFrame([registro], columns=col_names)
                    
                    st.write("**Registro inserido:**")
                    st.dataframe(df_registro, use_container_width=True)
                    
                except Error as e:
                    st.error(f"❌ Erro ao inserir: {e}")
                    conexao.rollback()
        
        # Verificar se precisa gerenciar tabela de referência
        if 'gerenciar_tabela' in st.session_state:
            gerenciar_tabela_referencia(nome_banco, st.session_state.gerenciar_tabela)
    
    except Error as e:
        st.error(f"Erro: {e}")
    
    finally:
        cursor.close()
        conexao.close()    
           
# ===========================================================================================          
# ====================            INICIO DO C.R.U.D.         ================================        
# =========================   FUNÇÃO DE VISUALIZAR DADOS  ===================================
#============================================================================================  

def visualizar_dados(nome_banco, nome_tabela):
    """Visualiza todos os dados da tabela"""
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
# Obter dados    
    try:
        cursor.execute(f"SELECT * FROM `{nome_tabela}` LIMIT 1000")
        dados = cursor.fetchall()
        
        if dados:
            # Obter nomes das colunas
            cursor.execute(f"DESCRIBE `{nome_tabela}`")
            colunas_info = cursor.fetchall()
            nomes_colunas = [col[0] for col in colunas_info]
            
            df = pd.DataFrame(dados, columns=nomes_colunas)
            
            st.subheader(f"📝 Registros ({len(df)} encontrados)")
            
# Mostrar estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", len(df))
            with col2:
                st.metric("Colunas", len(df.columns))
            with col3:
                st.metric("Página", "1/1")
            
# Mostrar dados
            st.dataframe(df, use_container_width=True, height=400)
            
# Opções de filtro simples
            with st.expander("🔍 Filtrar Dados"):
                if not df.empty:
                    col_filtro = st.selectbox("Coluna para filtrar:", df.columns)
                    valor_filtro = st.text_input("Valor:")
                    if st.button("Aplicar Filtro"):
                        if valor_filtro and col_filtro:
                            try:
                                # Converter para string para busca
                                df_filtrado = df[df[col_filtro].astype(str).str.contains(valor_filtro, case=False, na=False)]
                                st.dataframe(df_filtrado, use_container_width=True)
                                st.info(f"Encontrados {len(df_filtrado)} registros")
                            except:
                                st.warning("Não foi possível aplicar o filtro")
        else:
            st.info("📭 A tabela está vazia. Adicione o primeiro registro!")
    
    except Error as e:
        st.error(f"Erro ao carregar dados: {e}")
    
    finally:
        cursor.close()
        conexao.close()
 
#============================================================================================  
# ====================    FUNÇÃO PARA CRIAR/INSERIR REGISTOS    =============================
#============================================================================================  
def inserir_registro(nome_banco, nome_tabela):
    """Insere um novo registro na tabela COM visualização dos existentes"""
    
    # ============ CABEÇALHO ============
     # Título principal grande
    st.title("🏗️  Inserir Novo Registo na Tabela")
    st.subheader("➕ Adicionar Novo Registro")
    
    st.markdown(f"""
    <div style="
        background: #E8F5E9;
        padding: 15px 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 30px;
    ">
        <p style="margin: 0; font-size: 16px;">
            <strong>Tabela:</strong> <code>{nome_tabela}</code> | 
            <strong>Banco:</strong> <code>{nome_banco}</code>
        </p>
    </div>
    """, unsafe_allow_html=True)
      
    # ============ PARTE 1: MOSTRAR REGISTROS EXISTENTES ============
    with st.expander("📋 **Visualizar Registros Existentes**", expanded=True):
        conexao_view = conectar_mysql(nome_banco)
        if conexao_view:
            cursor_view = conexao_view.cursor()
            try:
                cursor_view.execute(f"SELECT * FROM `{nome_tabela}` LIMIT 50")
                registros = cursor_view.fetchall()
                
                if registros:
                    cursor_view.execute(f"DESCRIBE `{nome_tabela}`")
                    colunas = [col[0] for col in cursor_view.fetchall()]
                    
                    import pandas as pd
                    df = pd.DataFrame(registros, columns=colunas)
                    st.dataframe(df, use_container_width=True, height=250)
                    st.write(f"**Total:** {len(df)} registros")
                else:
                    st.info("📭 Nenhum registro encontrado. Você está criando o primeiro!")
                    
            except Error as e:
                st.warning(f"Não foi possível carregar registros: {e}")
            finally:
                cursor_view.close()
                conexao_view.close()
    
    st.markdown("---")
    
    # ============ PARTE 2: FORMULÁRIO DE INSERÇÃO ============
    st.subheader("📝 **Formulario para Inserir Novo Registro**")
    
    # Nova conexão para o formulário
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Obter estrutura da tabela
        cursor.execute(f"DESCRIBE `{nome_tabela}`")
        colunas_info = cursor.fetchall()
        
        # Criar formulário
        valores = {}
        
        for col in colunas_info:
            col_name = col[0]
            col_type = col[1].upper()
            col_extra = col[5]
            
            # Pular auto_increment
            if 'AUTO_INCREMENT' in col_extra.upper():
                st.info(f"Campo '{col_name}' é auto_increment (gerado automaticamente)")
                continue
            
            # Label
            label = f"**{col_name}**"
            if col[3] == 'PRI':
                label += " 🔑"
            if col[2] == 'NO':
                label += " *"
            
            # Tooltip
            tooltip = f"Tipo: {col_type}"
            
            # Inputs baseados no tipo
            if 'INT' in col_type:
                valores[col_name] = st.number_input(
                    label, 
                    step=1, 
                    value=0,
                    help=tooltip,
                    key=f"num_{col_name}_{nome_tabela}"
                )
            elif 'DECIMAL' in col_type or 'FLOAT' in col_type:
                valores[col_name] = st.number_input(
                    label, 
                    step=0.01,
                    format="%.2f",
                    value=0.0,
                    help=tooltip,
                    key=f"dec_{col_name}_{nome_tabela}"
                )
            elif 'DATE' in col_type:
                valores[col_name] = st.date_input(
                    label,
                    help=tooltip,
                    key=f"date_{col_name}_{nome_tabela}"
                )
            elif 'DATETIME' in col_type or 'TIMESTAMP' in col_type:
                col1, col2 = st.columns(2)
                with col1:
                    data = st.date_input(
                        f"{col_name} (data)",
                        key=f"dt_date_{col_name}_{nome_tabela}"
                    )
                with col2:
                    hora = st.time_input(
                        f"{col_name} (hora)", 
                        key=f"dt_time_{col_name}_{nome_tabela}"
                    )
                valores[col_name] = f"{data} {hora}:00"
            elif 'TEXT' in col_type:
                valores[col_name] = st.text_area(
                    label,
                    height=100,
                    help=tooltip,
                    key=f"area_{col_name}_{nome_tabela}"
                )
            elif 'VARCHAR' in col_type or 'CHAR' in col_type:
                # Input simples - SEM selectbox que limita a valores existentes
                valores[col_name] = st.text_input(
                    label,
                    help=tooltip,
                    key=f"text_{col_name}_{nome_tabela}"
                )
            elif 'BOOLEAN' in col_type or 'BOOL' in col_type:
                valores[col_name] = st.checkbox(
                    label,
                    value=False,
                    help=tooltip,
                    key=f"bool_{col_name}_{nome_tabela}"
                )
            else:
                valores[col_name] = st.text_input(
                    label,
                    help=tooltip,
                    key=f"other_{col_name}_{nome_tabela}"
                )
        
        # ============ BOTÕES ============
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 **Salvar Registro**", 
                        type="primary", 
                        use_container_width=True):
                
                # Fechar cursor atual antes de inserir
                cursor.close()
                
                # Nova conexão para inserção
                conexao_insert = conectar_mysql(nome_banco)
                if not conexao_insert:
                    return
                
                cursor_insert = conexao_insert.cursor()
                
                try:
                    # Preparar dados
                    campos = []
                    valores_list = []
                    
                    for campo, valor in valores.items():
                        if valor is not None and str(valor).strip() != "":
                            campos.append(f"`{campo}`")
                            
                            # Converter tipos de data/hora
                            if isinstance(valor, date):
                                # É uma data (do datetime.date)
                                valor = valor.strftime('%Y-%m-%d')
                            elif isinstance(valor, time):
                                # É uma hora (do datetime.time)
                                valor = valor.strftime('%H:%M:%S')
                            elif isinstance(valor, datetime):
                                # É datetime completo
                                valor = valor.strftime('%Y-%m-%d %H:%M:%S')
                            
                            valores_list.append(valor)
                    
                    if not campos:
                        st.error("⚠️ Nenhum campo preenchido!")
                        return
                    
                    # Montar SQL
                    placeholders = ["%s"] * len(campos)
                    sql = f"INSERT INTO `{nome_tabela}` ({', '.join(campos)}) VALUES ({', '.join(placeholders)})"
                    
                    # DEBUG: Mostrar SQL
                    with st.expander("🔍 Ver SQL que será executado"):
                        st.code(sql)
                        st.write("Valores:", valores_list)
                    
                    # Executar
                    cursor_insert.execute(sql, valores_list)
                    conexao_insert.commit()
                    
                    # Sucesso!
                    st.balloons()
                    st.success(f"✅ Registro inserido com sucesso!")
                    
                    # Opções
                    col_s1, col_s2 = st.columns(2)
                    with col_s1:
                        if st.button("👁️ Ver Tabela", use_container_width=True):
                            st.session_state.pagina_atual = "dados_tabela"
                            st.rerun()
                    with col_s2:
                        if st.button("➕ Novo Registro", use_container_width=True):
                            st.rerun()
                    
                except Error as e:
                    error_msg = str(e)
                    st.error(f"❌ Erro ao inserir: {error_msg}")
                    
                    # Dicas específicas
                    if "Duplicate entry" in error_msg:
                        st.info("💡 **Dica:** Este valor já existe na tabela. Verifique os registros acima.")
                    elif "Data too long" in error_msg:
                        st.info("💡 **Dica:** O texto é muito longo para esta coluna.")
                    elif "Incorrect date value" in error_msg:
                        st.info("💡 **Dica:** Formato de data incorreto.")
                    
                    conexao_insert.rollback()
                
                finally:
                    cursor_insert.close()
                    conexao_insert.close()
        
        with col2:
            if st.button("🔄 **Limpar Formulário**", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.button("🔙 **Voltar à Tabela**", use_container_width=True):
                st.session_state.pagina_atual = "dados_tabela"
                st.rerun()
    
    except Error as e:
        st.error(f"❌ Erro: {e}")
    
    finally:
        # Fechar conexão do formulário
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conexao' in locals() and conexao:
            conexao.close()
#============================================================================================          
# ==================== FUNÇÃO PARA EDITAR/ATULIZAR  REGISTOS ================================
#============================================================================================  

def editar_registro(nome_banco, nome_tabela):
    """Edita um registro existente - VERSÃO CORRIGIDA"""
    st.title(" 🔀 Editar/ Atualizar Registro")
    
    # Inicializar estado da edição
    if f'editando_{nome_tabela}' not in st.session_state:
        st.session_state[f'editando_{nome_tabela}'] = {
            'modo': 'selecionar',  # 'selecionar' ou 'editando'
            'registro_id': None,
            'valores': {}
        }
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Obter estrutura da tabela
        cursor.execute(f"DESCRIBE `{nome_tabela}`")
        colunas_info = cursor.fetchall()
        nomes_colunas = [col[0] for col in colunas_info]
        
        # Encontrar chave primária
        chave_primaria = None
        for col in colunas_info:
            if col[3] == 'PRI':
                chave_primaria = col[0]
                break
        
        if not chave_primaria:
            st.error("❌ Esta tabela não tem chave primária definida.")
            st.info("Para editar registros, adicione uma PRIMARY KEY à tabela.")
            return
        
        # MODO 1: SELECIONAR REGISTRO
        if st.session_state[f'editando_{nome_tabela}']['modo'] == 'selecionar':
            st.write("### 📋 Selecione um registro para editar")
            
            # Obter dados
            cursor.execute(f"SELECT * FROM `{nome_tabela}` LIMIT 100")
            dados = cursor.fetchall()
            
            if not dados:
                st.info("📭 Nenhum registro para editar.")
                return
            
            df = pd.DataFrame(dados, columns=nomes_colunas)
            st.dataframe(df, use_container_width=True)
            
            # Selecionar pelo ID
            cursor.execute(f"SELECT DISTINCT `{chave_primaria}` FROM `{nome_tabela}` ORDER BY `{chave_primaria}`")
            ids_disponiveis = [str(row[0]) for row in cursor.fetchall()]
            
            selected_id = st.selectbox(
                f"Selecione o {chave_primaria} para editar:",
                ids_disponiveis,
                key=f"select_id_{nome_tabela}"
            )
            
            if st.button("✏️ Editar Este Registro", type="primary"):
                # Buscar o registro
                cursor.execute(f"SELECT * FROM `{nome_tabela}` WHERE `{chave_primaria}` = %s", (selected_id,))
                registro = cursor.fetchone()
                
                if registro:
                    # Salvar no estado
                    st.session_state[f'editando_{nome_tabela}'] = {
                        'modo': 'editando',
                        'registro_id': selected_id,
                        'valores': {nomes_colunas[i]: registro[i] for i in range(len(nomes_colunas))}
                    }
                    st.rerun()
        
        # MODO 2: EDITANDO REGISTRO
        elif st.session_state[f'editando_{nome_tabela}']['modo'] == 'editando':
            registro_id = st.session_state[f'editando_{nome_tabela}']['registro_id']
            valores = st.session_state[f'editando_{nome_tabela}']['valores']
            
            st.success(f"✏️ Editando registro: **{chave_primaria} = {registro_id}**")
            
            # Formulário de edição
            novos_valores = {}
            
            for col in colunas_info:
                col_name = col[0]
                col_type = col[1].upper()
                valor_atual = valores.get(col_name)
                
                # Chave primária (não editável)
                if col[3] == 'PRI':
                    st.text_input(f"{col_name} 🔑", value=str(valor_atual), disabled=True)
                    novos_valores[col_name] = valor_atual
                    continue
                
                # Campos editáveis
                label = f"{col_name}"
                
                # Determinar tipo de input
                if 'INT' in col_type:
                    novos_valores[col_name] = st.number_input(
                        label,
                        value=int(valor_atual) if valor_atual not in [None, ''] else 0,
                        step=1,
                        key=f"edit_{col_name}_{registro_id}"
                    )
                elif 'DECIMAL' in col_type or 'FLOAT' in col_type or 'DOUBLE' in col_type:
                    novos_valores[col_name] = st.number_input(
                        label,
                        value=float(valor_atual) if valor_atual not in [None, ''] else 0.0,
                        step=0.01,
                        format="%.2f",
                        key=f"edit_{col_name}_{registro_id}"
                    )
                elif 'DATE' in col_type:
                    if valor_atual:
                        try:
                            if isinstance(valor_atual, (datetime.date, datetime.datetime)):
                                data_val = valor_atual
                            else:
                                # Tenta converter string para data
                                data_val = datetime.datetime.strptime(str(valor_atual), '%Y-%m-%d').date()
                            novos_valores[col_name] = st.date_input(
                                label,
                                value=data_val,
                                key=f"edit_{col_name}_{registro_id}"
                            )
                        except:
                            novos_valores[col_name] = st.date_input(label, key=f"edit_{col_name}_{registro_id}")
                    else:
                        novos_valores[col_name] = st.date_input(label, key=f"edit_{col_name}_{registro_id}")
                elif 'DATETIME' in col_type or 'TIMESTAMP' in col_type:
                    if valor_atual:
                        st.info(f"{col_name}: `{valor_atual}`")
                        novos_valores[col_name] = valor_atual
                    else:
                        novos_valores[col_name] = st.text_input(
                            label,
                            value=str(valor_atual) if valor_atual not in [None, ''] else "",
                            key=f"edit_{col_name}_{registro_id}"
                        )
                elif 'TEXT' in col_type:
                    novos_valores[col_name] = st.text_area(
                        label,
                        value=str(valor_atual) if valor_atual not in [None, ''] else "",
                        height=100,
                        key=f"edit_{col_name}_{registro_id}"
                    )
                elif 'VARCHAR' in col_type or 'CHAR' in col_type:
                    novos_valores[col_name] = st.text_input(
                        label,
                        value=str(valor_atual) if valor_atual not in [None, ''] else "",
                        key=f"edit_{col_name}_{registro_id}"
                    )
                elif 'BOOL' in col_type or 'TINYINT(1)' in col_type:
                    novos_valores[col_name] = st.checkbox(
                        label,
                        value=bool(valor_atual) if valor_atual not in [None, ''] else False,
                        key=f"edit_{col_name}_{registro_id}"
                    )
                else:
                    novos_valores[col_name] = st.text_input(
                        label,
                        value=str(valor_atual) if valor_atual not in [None, ''] else "",
                        key=f"edit_{col_name}_{registro_id}"
                    )
            
            # Botões de ação
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
                    try:
                        # Construir UPDATE
                        set_clause = []
                        valores_update = []
                        
                        for campo, valor in novos_valores.items():
                            if campo != chave_primaria:
                                set_clause.append(f"`{campo}` = %s")
                                valores_update.append(valor)
                        
                        valores_update.append(registro_id)
                        sql = f"UPDATE `{nome_tabela}` SET {', '.join(set_clause)} WHERE `{chave_primaria}` = %s"
                        
                        # Mostrar SQL (para debug)
                        with st.expander("📄 Ver SQL"):
                            st.code(sql)
                        
                        cursor.execute(sql, valores_update)
                        conexao.commit()
                        
                        st.success("✅ Registro atualizado com sucesso!")
                        st.balloons()
                        
                        # Resetar estado
                        st.session_state[f'editando_{nome_tabela}'] = {
                            'modo': 'selecionar',
                            'registro_id': None,
                            'valores': {}
                        }
                        
                        st.rerun()
                        
                    except Error as e:
                        st.error(f"❌ Erro ao atualizar: {e}")
                        conexao.rollback()
            
            with col2:
                if st.button("🔄 Recarregar Valores Originais", use_container_width=True):
                    # Recarrega valores do banco
                    cursor.execute(f"SELECT * FROM `{nome_tabela}` WHERE `{chave_primaria}` = %s", (registro_id,))
                    novo_registro = cursor.fetchone()
                    if novo_registro:
                        st.session_state[f'editando_{nome_tabela}']['valores'] = {
                            nomes_colunas[i]: novo_registro[i] for i in range(len(nomes_colunas))
                        }
                    st.rerun()
            
            with col3:
                if st.button("❌ Cancelar Edição", use_container_width=True):
                    st.session_state[f'editando_{nome_tabela}'] = {
                        'modo': 'selecionar',
                        'registro_id': None,
                        'valores': {}
                    }
                    st.rerun()
    
    except Error as e:
        st.error(f"❌ Erro: {e}")
    
    finally:
        cursor.close()
        conexao.close()
#============================================================================================          
# ============================ FUNÇÃO PARA EXCLUIR REGISTOS  ================================
#============================================================================================  
def excluir_registro(nome_banco, nome_tabela):
    """Exclui um registro específico - Versão Simplificada"""
    st.title("🗑️ Excluir Registro")
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Obter dados da tabela
        cursor.execute(f"SELECT * FROM `{nome_tabela}` LIMIT 50")
        dados = cursor.fetchall()
        
        if not dados:
            st.info("Nenhum registro para excluir.")
            return
        
        # Obter nomes das colunas
        cursor.execute(f"DESCRIBE `{nome_tabela}`")
        colunas_info = cursor.fetchall()
        nomes_colunas = [col[0] for col in colunas_info]
        
        df = pd.DataFrame(dados, columns=nomes_colunas)
        
        # Mostrar tabela
        st.write("Registros disponíveis:")
        st.dataframe(df, use_container_width=True)
        
        # Encontrar colunas que são chaves primárias
        chaves_primarias = []
        for col in colunas_info:
            if col[3] == 'PRI':  # Coluna Key
                chaves_primarias.append(col[0])
        
        if not chaves_primarias:
            st.warning("Não foi possível identificar uma chave primária.")
            return
        
        # Usar primeira chave primária
        pk_column = chaves_primarias[0]
        
        # Listar valores únicos da chave primária
        cursor.execute(f"SELECT DISTINCT `{pk_column}` FROM `{nome_tabela}` ORDER BY `{pk_column}` LIMIT 100")
        pk_values = [str(row[0]) for row in cursor.fetchall()]
        
        if not pk_values:
            st.info("Nenhum registro encontrado.")
            return
        
        # Selecionar registro para excluir
        selected_pk = st.selectbox(f"Selecione o {pk_column} para excluir:", pk_values)
        
        if selected_pk:
            # Mostrar registro selecionado
            cursor.execute(f"SELECT * FROM `{nome_tabela}` WHERE `{pk_column}` = %s", (selected_pk,))
            registro = cursor.fetchone()
            
            if registro:
                registro_dict = {nomes_colunas[i]: registro[i] for i in range(len(nomes_colunas))}
                
                st.warning(f"⚠️ Registro selecionado para exclusão ({pk_column} = {selected_pk}):")
                
                # Mostrar em formato de tabela
                for chave, valor in registro_dict.items():
                    st.write(f"**{chave}:** {valor}")
                
                st.markdown("---")
                
                # Confirmação
                confirm = st.checkbox("Confirmar exclusão permanente deste registro?")
                
                if confirm:
                    if st.button("🗑️ Excluir Permanentemente", type="primary"):
                        try:
                            cursor.execute(f"DELETE FROM `{nome_tabela}` WHERE `{pk_column}` = %s", (selected_pk,))
                            conexao.commit()
                            st.success(f"✅ Registro {selected_pk} excluído com sucesso!")
                            st.rerun()
                        except Error as e:
                            st.error(f"❌ Erro ao excluir: {e}")
                            conexao.rollback()
    
    except Error as e:
        st.error(f"Erro: {e}")
    
    finally:
        cursor.close()
        conexao.close()
        
    

#============================================================================================  
# ==================== FUNÇÃO PARA GERENCIAR DADOS NA TABELA  ===============================
#============================================================================================  
def gerenciar_dados_tabela(nome_banco, nome_tabela):
    """CRUD completo para uma tabela específica - VERSÃO COMPLETA"""
    st.title("📊 Tabela ")
    st.subheader(f"📁 Nome do Banco de dados: {nome_banco}")
    st.subheader(f"📊 Nome da Tabela: {nome_tabela}")
    # Mostrar foreign keys da tabela
    fks = obter_foreign_keys(nome_banco, nome_tabela)
    if fks:
        with st.expander("🔗 Relacionamentos desta tabela", expanded=False):
            for fk in fks:
                st.write(f"• `{fk[0]}` → `{fk[1]}.{fk[2]}`")
    
    # Menu de operações - AGORA COM TODAS AS FUNÇÕES DEFINIDAS
    opcao = st.radio(
        "Operação:",
        ["📋 Ver Dados", "➕ Inserir Registro", "✏️ Editar Registro", "🗑️ Excluir Registro", "📥 Exportar Dados"],
        horizontal=True
    )
    
    if opcao == "📋 Ver Dados":
        visualizar_dados(nome_banco, nome_tabela)
    
    elif opcao == "➕ Inserir Registro":
        inserir_registro_com_fks(nome_banco, nome_tabela)
    
    elif opcao == "✏️ Editar Registro":
        editar_registro(nome_banco, nome_tabela)  # ✅ AGORA DEFINIDA
    
    elif opcao == "🗑️ Excluir Registro":
        excluir_registro(nome_banco, nome_tabela)  # ✅ AGORA DEFINIDA
    
    elif opcao == "📥 Exportar Dados":
        exportar_tabela(nome_banco, nome_tabela)  # ✅ AGORA DEFINIDA
    
    # Botões adicionais
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Adicionar Coluna", use_container_width=True):
            st.session_state.pagina_atual = "adicionar_coluna"
            st.rerun()
    
    with col2:
        if st.button("⚙️ Editar Estrutura", use_container_width=True):
            st.session_state.pagina_atual = "editar_tabela"
            st.rerun()
    
    with col3:
        if st.button("🔙 Voltar ao Banco", use_container_width=True):
            st.session_state.pagina_atual = None
            st.session_state.tabela_selecionada = None
            st.rerun()
#============================================================================================            
# ==================== FUNÇÃO PARA INSERIR REGISTOS COM (FOREIGN KEY) FK ==================== 
#============================================================================================             
def inserir_registro_com_fks(nome_banco, nome_tabela):
    """Insere um novo registro na tabela, com validação de FOREIGN KEYS"""
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Obter estrutura da tabela
        cursor.execute(f"DESCRIBE `{nome_tabela}`")
        colunas_info = cursor.fetchall()
        
        # Obter foreign keys
        fks = obter_foreign_keys(nome_banco, nome_tabela)
        fk_dict = {fk[0]: (fk[1], fk[2]) for fk in fks}
        
        st.subheader("➕ Inserir Novo Registro")
        
        # Criar formulário dinâmico
        valores = {}
        colunas_para_mostrar = []
        
        for col in colunas_info:
            col_name = col[0]
            col_type = col[1].upper()
            col_extra = col[5]
            
            # Pular auto_increment
            if 'AUTO_INCREMENT' in col_extra.upper():
                continue
            
            colunas_para_mostrar.append(col)
        
        if not colunas_para_mostrar:
            st.info("Esta tabela só tem colunas auto_increment. Use 'Ver Dados' para ver os registros.")
            return
        
        for col in colunas_para_mostrar:
            col_name = col[0]
            col_type = col[1]
            col_null = col[2]
            col_key = col[3]
            
            # Verificar se é FOREIGN KEY
            is_foreign_key = col_name in fk_dict
            
            # Determinar tipo de input
            input_label = col_name
            if col_key == 'PRI':
                input_label += " 🔑"
            if is_foreign_key:
                tabela_ref, coluna_ref = fk_dict[col_name]
                input_label += f" 🔗→ {tabela_ref}.{coluna_ref}"
            
            if is_foreign_key:
                # Para FOREIGN KEY, mostrar dropdown com valores válidos
                tabela_ref, coluna_ref = fk_dict[col_name]
                cursor_ref = conexao.cursor()
                cursor_ref.execute(f"SELECT `{coluna_ref}` FROM `{tabela_ref}` ORDER BY `{coluna_ref}` LIMIT 100")
                valores_validos = [str(v[0]) for v in cursor_ref.fetchall()]
                cursor_ref.close()
                
                if valores_validos:
                    valores[col_name] = st.selectbox(input_label, valores_validos)
                else:
                    st.warning(f"Tabela `{tabela_ref}` está vazia. Insira dados lá primeiro.")
                    valores[col_name] = st.text_input(input_label)
            
            elif 'INT' in col_type.upper():
                valores[col_name] = st.number_input(input_label, step=1, value=0)
            elif 'DECIMAL' in col_type.upper() or 'FLOAT' in col_type.upper() or 'DOUBLE' in col_type.upper():
                valores[col_name] = st.number_input(input_label, step=0.01, format="%.2f", value=0.0)
            elif 'DATE' in col_type.upper():
                valores[col_name] = st.date_input(input_label)
            elif 'DATETIME' in col_type.upper() or 'TIMESTAMP' in col_type.upper():
                col1, col2 = st.columns(2)
                with col1:
                    data = st.date_input(f"{input_label} (data)")
                with col2:
                    hora = st.time_input(f"{input_label} (hora)")
                valores[col_name] = f"{data} {hora}"
            elif 'TEXT' in col_type.upper() or 'LONGTEXT' in col_type.upper():
                valores[col_name] = st.text_area(input_label, height=100)
            elif 'VARCHAR' in col_type.upper() or 'CHAR' in col_type.upper():
                valores[col_name] = st.text_input(input_label)
            elif 'BOOL' in col_type.upper():
                valores[col_name] = st.checkbox(input_label, value=False)
            else:
                valores[col_name] = st.text_input(input_label)
        
        # Botão para inserir
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("💾 Salvar Registro", type="primary", use_container_width=True):
                try:
                    # Construir SQL dinâmico
                    campos = []
                    valores_list = []
                    placeholders = []
                    
                    for campo, valor in valores.items():
                        if valor is not None and str(valor).strip() != "":
                            campos.append(f"`{campo}`")
                            valores_list.append(valor)
                            placeholders.append("%s")
                    
                    if not campos:
                        st.error("Nenhum valor para inserir!")
                        return
                    
                    sql = f"INSERT INTO `{nome_tabela}` ({', '.join(campos)}) VALUES ({', '.join(placeholders)})"
                    
                    cursor.execute(sql, valores_list)
                    conexao.commit()
                    
                    st.success("✅ Registro inserido com sucesso!")
                    st.balloons()
                    
                except Error as e:
                    if "foreign key constraint fails" in str(e).lower():
                        st.error(f"❌ Erro de FOREIGN KEY: O valor não existe na tabela de referência!")
                    else:
                        st.error(f"❌ Erro ao inserir: {e}")
                    conexao.rollback()
        
        with col2:
            if st.button("🔄 Limpar Formulário", use_container_width=True):
                st.rerun()
    
    except Error as e:
        st.error(f"Erro: {e}")
    
    finally:
        cursor.close()
        conexao.close() 
# ===================================================================================        
# ==================== FUNÇÃO PARA CRIAR COMBOBOX (JEITO ACCESS) ====================
# ===================================================================================          

def adicionar_campo_combobox_simples(nome_banco, nome_tabela):
    """Adiciona um campo combobox do jeito Access - SIMPLES E PRÁTICO!"""
    
    st.title(f"🎯 Criar Combobox ")
    st.markdown(f"**Tabela:** `{nome_tabela}`")
    
    with st.expander("💡 **Como funciona :**", expanded=True):
        st.markdown("""
        **No Access você faria:**
        1. Criar tabela de referência separada
        2. Inserir os valores (Livre, Ocupado, etc.)
        3. Criar relacionamento com a tabela principal
        
        **Aqui faremos automaticamente:**
        ✅ Cria tabela de referência  
        ✅ Insere seus valores  
        ✅ Cria campo com FOREIGN KEY  
        ✅ Tudo pronto para usar como combobox!
        """)
    
    # DIVISÃO
    st.markdown("---")
    
    # PASSO 1: Nome do campo
    st.subheader("1️⃣ Nome do Campo")
    nome_campo = st.text_input(
        "Nome do campo combobox:", 
        placeholder="ex: estado_quarto, status_pedido, tipo_pagamento",
        help="Este será o nome da coluna na sua tabela"
    )
            
    if nome_campo:
        # PASSO 2: Valores do combobox
        st.subheader("2️⃣ Valores do Combobox")
        
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            if st.button("📋 Exemplo: Estados Quarto", use_container_width=True):
                st.session_state.valores_exemplo = "Livre\nOcupado\nManutenção\nLimpeza"
                st.rerun()
        with col_ex2:
            if st.button("📋 Exemplo: Status Pedido", use_container_width=True):
                st.session_state.valores_exemplo = "Pendente\nProcessando\nEnviado\nEntregue\nCancelado"
                st.rerun()
        
        # Textarea para valores
        valores_default = st.text_area(
            "Digite os valores (um por linha):",
            value=st.session_state.get('valores_exemplo', "Livre\nOcupado\nManutenção\nLimpeza"),
            height=150,
            key=f"valores_cb_{nome_tabela}",
            help="Cada linha será uma opção no combobox"
        )
        
        # Mostrar preview
        valores_lista = [v.strip() for v in valores_default.split('\n') if v.strip()]
        
        if valores_lista:
            st.info(f"✅ **{len(valores_lista)} valores serão criados:**")
            for i, valor in enumerate(valores_lista, 1):
                st.write(f"`{i}`. {valor}")
        
        # PASSO 3: Opções adicionais
        st.subheader("3️⃣ Configurações Adicionais")
        
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            permite_null = st.checkbox(
                "Permitir valor vazio", 
                value=True,
                help="Se marcado, o campo pode ficar sem valor selecionado"
            )
        
        with col_opt2:
            valor_padrao = st.selectbox(
                "Valor padrão:",
                ["Nenhum"] + valores_lista if valores_lista else ["Nenhum"],
                help="Valor selecionado automaticamente"
            )
        
        # DIVISÃO
        st.markdown("---")
        
        # PASSO 4: Botão para criar tudo
        st.subheader("4️⃣ Criar Combobox")
        
        if not nome_campo:
            st.warning("⚠️ Digite um nome para o campo!")
        elif not valores_lista:
            st.warning("⚠️ Adicione pelo menos um valor!")
        else:
            # Mostrar resumo
            st.info("**Resumo do que será criado:**")
            
            tabela_ref = f"ref_{nome_tabela}_{nome_campo}"
            
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.markdown(f"""
                **Tabela de referência:**
                ```
                {tabela_ref}
                ├── id (INT, AUTO_INCREMENT)
                ├── valor (VARCHAR, UNIQUE)
                └── ordem (INT)
                ```
                """)
            
            with col_res2:
                st.markdown(f"""
                **Campo na tabela `{nome_tabela}`:**
                ```
                {nome_campo} (INT, FOREIGN KEY)
                → {tabela_ref}.id
                ```
                """)
            
            # BOTÃO PRINCIPAL
            col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
            
            with col_btn1:
                if st.button("🚀 CRIAR COMBOBOX COMPLETO", 
                           type="primary", 
                           use_container_width=True,
                           key=f"btn_criar_cb_{nome_tabela}"):
                    
                    # Conectar ao banco
                    conexao = conectar_mysql(nome_banco)
                    if not conexao:
                        return
                    
                    cursor = conexao.cursor()
                    
                    try:
                        # 1. CRIAR TABELA DE REFERÊNCIA
                        st.info("🔄 Criando tabela de referência...")
                        
                        sql_criar_ref = f"""
                        CREATE TABLE IF NOT EXISTS `{tabela_ref}` (
                            id INT PRIMARY KEY AUTO_INCREMENT,
                            valor VARCHAR(100) UNIQUE NOT NULL,
                            descricao VARCHAR(255) NULL,
                            ordem INT DEFAULT 0,
                            ativo BOOLEAN DEFAULT TRUE,
                            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                        """
                        
                        cursor.execute(sql_criar_ref)
                        
                        # 2. INSERIR VALORES
                        st.info(f"🔄 Inserindo {len(valores_lista)} valores...")
                        
                        for i, valor in enumerate(valores_lista):
                            # Verificar se já existe
                            cursor.execute(f"SELECT id FROM `{tabela_ref}` WHERE valor = %s", (valor,))
                            if not cursor.fetchone():
                                cursor.execute(
                                    f"INSERT INTO `{tabela_ref}` (valor, ordem) VALUES (%s, %s)",
                                    (valor, i+1)
                                )
                        
                        # 3. ADICIONAR CAMPO NA TABELA PRINCIPAL
                        st.info("🔄 Adicionando campo com FOREIGN KEY...")
                        
                        # Primeiro, adicionar a coluna
                        sql_add_coluna = f"ALTER TABLE `{nome_tabela}` ADD COLUMN `{nome_campo}` INT"
                        
                        if not permite_null:
                            sql_add_coluna += " NOT NULL"
                        
                        if valor_padrao != "Nenhum":
                            # Buscar ID do valor padrão
                            cursor.execute(f"SELECT id FROM `{tabela_ref}` WHERE valor = %s", (valor_padrao,))
                            id_padrao = cursor.fetchone()
                            if id_padrao:
                                sql_add_coluna += f" DEFAULT {id_padrao[0]}"
                        
                        cursor.execute(sql_add_coluna)
                        
                        # 4. ADICIONAR FOREIGN KEY
                        sql_add_fk = f"""
                        ALTER TABLE `{nome_tabela}` 
                        ADD CONSTRAINT `fk_{nome_tabela}_{nome_campo}` 
                        FOREIGN KEY (`{nome_campo}`) REFERENCES `{tabela_ref}`(id)
                        ON DELETE RESTRICT ON UPDATE CASCADE;
                        """
                        
                        cursor.execute(sql_add_fk)
                        conexao.commit()
                        
                        # MENSAGEM DE SUCESSO
                        st.success("""
                        ✅ **Combobox criado com sucesso!**
                        
                        **O que foi criado automaticamente:**
                        1. 📊 **Tabela de referência**: `{}`
                        2. 📝 **{} valores** inseridos
                        3. 🔗 **Campo `{}`** na tabela `{}`
                        4. 🔄 **Relacionamento** configurado
                        
                        **Próximos passos:**
                        - Ao inserir/editar dados, verá um combobox
                        - Use 'Gerenciar Valores' para adicionar opções
                        - Valores aparecerão como `ID - Valor` (ex: `1 - Livre`)
                        """.format(tabela_ref, len(valores_lista), nome_campo, nome_tabela))
                        
                        # Mostrar valores criados
                        cursor.execute(f"SELECT id, valor FROM `{tabela_ref}` ORDER BY ordem")
                        valores_criados = cursor.fetchall()
                        
                        st.write("**Valores disponíveis no combobox:**")
                        for id_val, valor in valores_criados:
                            st.code(f"{id_val} - {valor}")
                        
                        # Opções após criação
                        st.markdown("---")
                        col_op1, col_op2, col_op3 = st.columns(3)
                        
                        with col_op1:
                            if st.button("➕ Adicionar mais valores", use_container_width=True):
                                st.session_state.gerenciar_tabela_ref = tabela_ref
                                st.rerun()
                        
                        with col_op2:
                            if st.button("📋 Ver todos os valores", use_container_width=True):
                                st.session_state.ver_valores_ref = tabela_ref
                                st.rerun()
                        
                        with col_op3:
                            if st.button("🔙 Voltar à estrutura", use_container_width=True):
                                st.rerun()
                        
                    except Error as e:
                        st.error(f"❌ **Erro ao criar combobox:** {e}")
                        conexao.rollback()
                        
                        # Dicas para erro comum
                        if "Duplicate column" in str(e):
                            st.error("Já existe uma coluna com este nome na tabela!")
                        elif "foreign key constraint" in str(e):
                            st.error("Erro no relacionamento. Verifique se a tabela de referência foi criada.")
                    
                    finally:
                        cursor.close()
                        conexao.close()
            
            with col_btn2:
                if st.button("📄 Ver SQL", use_container_width=True):
                    # Mostrar SQLs que seriam executados
                    st.code(f"""
                    -- 1. Criar tabela de referência
                    CREATE TABLE `{tabela_ref}` (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        valor VARCHAR(100) UNIQUE NOT NULL,
                        ordem INT DEFAULT 0,
                        ativo BOOLEAN DEFAULT TRUE
                    );
                    
                    -- 2. Inserir valores
                    INSERT INTO `{tabela_ref}` (valor, ordem) VALUES
                    {', '.join([f"('{v}', {i+1})" for i, v in enumerate(valores_lista)])};
                    
                    -- 3. Adicionar campo
                    ALTER TABLE `{nome_tabela}` 
                    ADD COLUMN `{nome_campo}` INT{" NOT NULL" if not permite_null else ""}{f" DEFAULT (SELECT id FROM `{tabela_ref}` WHERE valor = '{valor_padrao}')" if valor_padrao != "Nenhum" else ""};
                    
                    -- 4. Adicionar FOREIGN KEY
                    ALTER TABLE `{nome_tabela}` 
                    ADD FOREIGN KEY (`{nome_campo}`) REFERENCES `{tabela_ref}`(id);
                    """)
            
            with col_btn3:
                if st.button("🔄 Cancelar", use_container_width=True):
                    st.rerun()
                    
                    
    
    # Se precisar gerenciar valores após criação
    if 'gerenciar_tabela_ref' in st.session_state:
        st.markdown("---")
        gerenciar_tabela_referencia_simples(nome_banco, st.session_state.gerenciar_tabela_ref)
    
    if 'ver_valores_ref' in st.session_state:
        st.markdown("---")
        mostrar_valores_tabela_ref(nome_banco, st.session_state.ver_valores_ref)
        
    # Botão para voltar a tabelas
    st.markdown("---")
    if st.button("🔙 Voltar as Tabelas", use_container_width=True):
       st.session_state.pagina_atual = None
       st.rerun()     
                  
# =======================================================================        
# ==================== FUNÇÃO PARA COMBOBOX SIMPLES  ====================
# =======================================================================           
def gerenciar_tabela_referencia_simples(nome_banco, nome_tabela_ref):
    """Versão simplificada para gerenciar valores"""
    
    st.subheader(f"📋 Gerenciar Valores: {nome_tabela_ref}")
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Buscar valores atuais
        cursor.execute(f"""
            SELECT id, valor, ordem, ativo 
            FROM `{nome_tabela_ref}` 
            ORDER BY ordem
        """)
        valores = cursor.fetchall()
        
        # Mostrar valores atuais
        if valores:
            st.write(f"**📊 {len(valores)} valores cadastrados:**")
            
            for id_val, valor, ordem, ativo in valores:
                status = "✅" if ativo else "⏸️"
                st.write(f"{status} `{id_val}` - {valor} (Ordem: {ordem})")
        
        # Formulário para adicionar novo
        st.markdown("---")
        st.write("**➕ Adicionar novo valor:**")
        
        with st.form(key=f"add_valor_{nome_tabela_ref}"):
            novo_valor = st.text_input("Novo valor:", placeholder="ex: Reservado")
            nova_ordem = st.number_input("Ordem:", min_value=1, value=len(valores)+1)
            
            if st.form_submit_button("✅ Adicionar", use_container_width=True):
                if novo_valor:
                    cursor.execute(
                        f"INSERT INTO `{nome_tabela_ref}` (valor, ordem) VALUES (%s, %s)",
                        (novo_valor, nova_ordem)
                    )
                    conexao.commit()
                    st.success(f"✅ Valor '{novo_valor}' adicionado!")
                    st.rerun()
        
    except Error as e:
        st.error(f"❌ Erro: {e}")
    finally:
        cursor.close()
        conexao.close()
        
        # Botão para voltar
    st.markdown("---")
    if st.button("🔙 Voltar", use_container_width=True):
        st.session_state.pagina_atual = None
        st.rerun() 
# =======================================================================        
# ==================== FUNÇÃO PARA Mostrar dados inseridos ==============
# =======================================================================   
def mostrar_valores_tabela_ref(nome_banco, nome_tabela_ref):
    """Mostra todos os valores de uma tabela de referência"""
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM `{nome_tabela_ref}` ORDER BY ordem")
        valores = cursor.fetchall()
        
        if valores:
            # Obter nomes das colunas
            cursor.execute(f"SHOW COLUMNS FROM `{nome_tabela_ref}`")
            colunas = [col[0] for col in cursor.fetchall()]
            
            # Criar DataFrame
            df = pd.DataFrame(valores, columns=colunas)
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📭 Nenhum valor cadastrado.")
    
    except Error as e:
        st.error(f"Erro: {e}")
    finally:
        cursor.close()
        conexao.close()  
# =======================================================================        
# ==================== FUNÇÃO PARA inserir dados   ======================
# =======================================================================             
def inserir_dados_com_combobox_real(nome_banco, nome_tabela):
    """Versão SUPER Access-like para inserir dados"""
    
    st.title(f"📝 Inserir Dados - {nome_tabela}")
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Obter estrutura
        cursor.execute(f"DESCRIBE `{nome_tabela}`")
        colunas = cursor.fetchall()
        
        # Criar formulário tipo Access
        with st.form(key=f"form_access_{nome_tabela}"):
            st.subheader("📋 Formulário de Entrada")
            
            dados = {}
            
            for coluna in colunas:
                nome_col = coluna[0]
                tipo_col = coluna[1]
                
                # Pular auto_increment
                if 'auto_increment' in coluna[5].lower():
                    continue
                
                # Verificar se é combobox (FK)
                cursor.execute(f"""
                    SELECT REFERENCED_TABLE_NAME 
                    FROM information_schema.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = %s 
                    AND COLUMN_NAME = %s
                    AND REFERENCED_TABLE_NAME LIKE 'ref_%'
                """, (nome_banco, nome_tabela, nome_col))
                
                fk_info = cursor.fetchone()
                
                if fk_info:
                    # É um COMBOBOX!
                    tabela_ref = fk_info[0]
                    
                    # Buscar valores
                    cursor.execute(f"""
                        SELECT id, valor, descricao 
                        FROM `{tabela_ref}` 
                        WHERE ativo = TRUE 
                        ORDER BY ordem
                    """)
                    valores = cursor.fetchall()
                    
                    # Interface tipo Access
                    col_left, col_right = st.columns([3, 1])
                    
                    with col_left:
                        # Dropdown estilizado
                        opcoes = {f"{v[0]}": f"{v[1]}" + (f" - {v[2]}" if v[2] else "") for v in valores}
                        selecao = st.selectbox(
                            f"{nome_col.replace('_', ' ').title()}:",
                            options=list(opcoes.keys()),
                            format_func=lambda x: opcoes[x],
                            index=0
                        )
                        dados[nome_col] = selecao if selecao != "0" else None
                    
                    with col_right:
                        # Botão para gerenciar
                        if st.button("📋", key=f"btn_ger_{nome_col}", help="Gerenciar valores"):
                            st.session_state.gerenciar_ref = tabela_ref
                            st.session_state.voltar_para = "inserir"
                            st.rerun()
                
                else:
                    # Campo normal
                    label = nome_col.replace('_', ' ').title()
                    
                    if tipo_col.startswith('varchar') or tipo_col.startswith('text'):
                        dados[nome_col] = st.text_input(f"{label}:")
                    
                    elif tipo_col.startswith('int'):
                        dados[nome_col] = st.number_input(f"{label}:", step=1)
                    
                    elif 'date' in tipo_col.lower():
                        dados[nome_col] = st.date_input(f"{label}:")
                    
                    elif tipo_col.lower() == 'boolean':
                        dados[nome_col] = st.checkbox(f"{label}:")
                    
                    else:
                        dados[nome_col] = st.text_input(f"{label} ({tipo_col}):")
            
            # Botões estilo Access
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                salvar = st.form_submit_button("💾 Salvar Registro", type="primary", use_container_width=True)
            
            with col_btn2:
                limpar = st.form_submit_button("🧹 Novo", use_container_width=True)
            
            with col_btn3:
                cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if salvar:
                # Processar inserção...
                pass
            
            if limpar:
                st.rerun()
            
            if cancelar:
                st.session_state.pagina_atual = None
                st.rerun()
    
    except Error as e:
        st.error(f"Erro: {e}")
    finally:
        cursor.close()
        conexao.close()
# =========================================================================        
# ==================== FUNÇÃO PARA configurar conexão  ====================
# =========================================================================         
def pagina_configuracao_conexao():
    """Página dedicada para configurar conexão MySQL"""
    
    st.title("⚙️ Configuração de Conexão MySQL")
    
    st.markdown("""
    ### Configure a conexão com seu servidor MySQL
    
    **Informações necessárias:**
    - **Host:** Endereço do servidor (geralmente `localhost`)
    - **Usuário:** Nome de usuário (geralmente `root`)
    - **Senha:** Senha do usuário
    - **Porta:** Porta do MySQL (padrão: `3306`)
    """)
    
    # Formulário de configuração
    with st.form(key="form_config_conexao"):
        col1, col2 = st.columns(2)
        
        with col1:
            host = st.text_input("Host:", value="localhost", placeholder="localhost")
            usuario = st.text_input("Usuário:", value="root", placeholder="root")
        
        with col2:
            senha = st.text_input("Senha:", type="password", placeholder="Digite a senha")
            porta = st.number_input("Porta:", min_value=1, max_value=65535, value=3306)
        
        col_test, col_save = st.columns(2)
        
        with col_test:
            testar = st.form_submit_button("🔍 Testar Conexão")
        
        with col_save:
            salvar = st.form_submit_button("💾 Salvar & Conectar", type="primary")
    
    # Testar conexão
    if testar:
        config_test = {
            'host': host,
            'user': usuario,
            'password': senha,
            'port': porta
        }
        
        try:
            conn = mysql.connector.connect(**config_test)
            if conn.is_connected():
                st.success(f"✅ Conexão bem-sucedida!")
                st.info(f"Versão do MySQL: {conn.get_server_info()}")
                conn.close()
            else:
                st.error("❌ Conexão estabelecida mas não ativa")
        except mysql.connector.Error as e:
            if e.errno == 2003:
                st.error("❌ Não foi possível conectar ao servidor MySQL")
                st.info("Verifique se o MySQL está instalado e rodando")
            elif e.errno == 1045:
                st.error("❌ Acesso negado. Verifique usuário e senha")
            else:
                st.error(f"❌ Erro {e.errno}: {e.msg}")
    
    # Salvar configuração
    if salvar:
        st.session_state.db_config = {
            'host': host,
            'user': usuario,
            'password': senha,
            'port': porta
        }
        
        # Testar a configuração salva
        conexao_ok, mensagem = verificar_conexao_mysql()
        
        if conexao_ok:
            st.success("✅ Configuração salva e conexão verificada!")
            st.balloons()
            
            # Voltar para página inicial
            if st.button("🏠 Ir para Página Inicial"):
                st.session_state.pagina_atual = None
                st.rerun()
        else:
            st.error(f"❌ Configuração salva, mas conexão falhou: {mensagem}")
    
                   
# ======================================================================        
# ==================== FUNÇÃO PARA GERIR COMBOBOX   ====================
# ======================================================================        
def gerenciar_combobox_menu(nome_banco, nome_tabela):
    """Página principal para gerenciar combobox de uma tabela"""
    
    st.title(f"📋 Gerenciar Combobox - {nome_tabela}")
    
    conexao = conectar_mysql(nome_banco)
    if not conexao:
        return
    
    cursor = conexao.cursor()
    
    try:
        # Buscar todos os combobox da tabela
        cursor.execute("SHOW TABLES LIKE %s", (f"ref_{nome_tabela}_%",))
        tabelas_ref = [t[0] for t in cursor.fetchall()]
        
        if not tabelas_ref:
            st.info("📭 Esta tabela não possui combobox criados.")
            
            st.markdown("---")
            st.subheader("🎯 Criar Primeiro Combobox")
            
            if st.button("🚀 Criar Novo Combobox", type="primary", use_container_width=True):
                adicionar_campo_combobox_simples(nome_banco, nome_tabela)
                st.stop()
            
            return
        
        st.success(f"✅ Encontrados {len(tabelas_ref)} combobox:")
        
        # Mostrar cada combobox
        for tabela_ref in tabelas_ref:
            # Extrair nome do campo
            nome_campo = tabela_ref.replace(f"ref_{nome_tabela}_", "")
            
            with st.container():
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #4CAF50;">
                    <h3 style="margin: 0;">🔘 {nome_campo}</h3>
                    <p style="margin: 5px 0; color: #666;">Tabela: <code>{tabela_ref}</code></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Estatísticas
                cursor.execute(f"SELECT COUNT(*) FROM `{tabela_ref}`")
                total = cursor.fetchone()[0]
                
                cursor.execute(f"SELECT COUNT(*) FROM `{tabela_ref}` WHERE ativo = TRUE")
                ativos = cursor.fetchone()[0]
                
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Total Valores", total)
                with col_stat2:
                    st.metric("Valores Ativos", ativos)
                with col_stat3:
                    if ativos < total:
                        st.metric("Inativos", total - ativos)
                
                # Ações
                col_act1, col_act2, col_act3 = st.columns(3)
                
                with col_act1:
                    if st.button("📋 Ver Valores", key=f"view_{tabela_ref}", use_container_width=True):
                        mostrar_valores_tabela_ref(nome_banco, tabela_ref)
                
                with col_act2:
                    if st.button("✏️ Gerenciar", key=f"edit_{tabela_ref}", use_container_width=True):
                        gerenciar_tabela_referencia_simples(nome_banco, tabela_ref)
                
                with col_act3:
                    if st.button("➕ Adicionar", key=f"add_{tabela_ref}", use_container_width=True):
                        # Form rápido para adicionar valor
                        with st.form(key=f"quick_add_{tabela_ref}"):
                            novo_valor = st.text_input("Novo valor:", key=f"new_{tabela_ref}")
                            if st.form_submit_button("✅ Adicionar"):
                                if novo_valor:
                                    cursor.execute(
                                        f"INSERT INTO `{tabela_ref}` (valor) VALUES (%s)",
                                        (novo_valor,)
                                    )
                                    conexao.commit()
                                    st.success("✅ Adicionado!")
                                    st.rerun()
                
                st.markdown("---")
        
        # Opção para criar novo combobox
        st.markdown("### 🎯 Criar Novo Combobox")
        
        if st.button("➕ Criar Novo Combobox para esta Tabela", 
                   type="primary", 
                   use_container_width=True):
            adicionar_campo_combobox_simples(nome_banco, nome_tabela)
    
    except Error as e:
        st.error(f"Erro: {e}")
    finally:
        cursor.close()
        conexao.close() 
# ========================================================================        
# ==================== FUNÇÃO PARA O (PRINCIPAL) MAIN ====================
# ========================================================================
def main():
    """função principal"""
    st.set_page_config(
        page_icon="🗄️",
        page_title="MySQL Manager Pro",
        layout="wide"
    )
    
    # Cabeçalho personalizado
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <h1 style='text-align: center;'>
            🐍 + 🐬 <br>
            MySQL Manager Pro
        </h1>
        """, unsafe_allow_html=True)
    
    aplicar_estilos()
    
    # Inicializar estados
    estados_padrao = {
        'banco_selecionado': None,
        'tabela_selecionada': None,
        'pagina_atual': None,
        'db_config': DEFAULT_CONFIG,
        'adicionando_coluna': False,
        'excluindo_coluna': False
    }
    
    for key, value in estados_padrao.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # ⭐⭐ FUNÇÃO DE VERIFICAÇÃO DE CONEXÃO ⭐⭐
    def verificar_conexao_mysql():
        """Verifica se o MySQL está conectado"""
        if 'db_config' not in st.session_state:
            return False, "⚠️ Nenhuma configuração encontrada"
        
        try:
            # Tenta conectar SEM banco específico
            config = st.session_state.db_config.copy()
            if 'database' in config:
                del config['database']
            
            conn = mysql.connector.connect(**config)
            if conn.is_connected():
                versao = conn.get_server_info()
                conn.close()
                return True, f"🟢 CONECTADO (MySQL {versao})"
            else:
                return False, "🔴 CONEXÃO FALHOU"
                
        except mysql.connector.Error as e:
            if e.errno == 2003:
                return False, "🔴 SERVIDOR NÃO ENCONTRADO"
            elif e.errno == 1045:
                return False, "🔴 ACESSO NEGADO"
            else:
                return False, f"🔴 ERRO: {e.msg}"
        except Exception as e:
            return False, f"🔴 ERRO: {str(e)}"
    
    # Sidebar
    with st.sidebar:
        st.markdown("criado por: Luís Gomes 2026")
        
        # Ícone e título
        st.markdown("""
        <div style="text-align: center;">
            <img src="https://icons.iconarchive.com/icons/icojam/blueberry-basic/32/base-icon.png" 
                width="64" height="64">
            <h3 style="color: #2E86C1;">MySQL MANAGER</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # ⭐⭐ STATUS DINÂMICO DA CONEXÃO ⭐⭐
        st.markdown("**🔌 Status da Conexão:**")
        
        conexao_ok, mensagem_conexao = verificar_conexao_mysql()
        
        if conexao_ok:
            st.success(mensagem_conexao)
        else:
            st.error(mensagem_conexao)
            st.caption("Configure a conexão na página inicial")
        
        st.markdown("---")
        
        # ⭐⭐ INFORMAÇÕES APENAS SE CONECTADO ⭐⭐
        if conexao_ok:
            if st.session_state.banco_selecionado:
                st.markdown("**📁 Banco Atual:**")
                st.success(f"`{st.session_state.banco_selecionado}`")
                
                if st.session_state.tabela_selecionada:
                    st.markdown("**📊 Tabela Selecionada:**")
                    st.info(f"`{st.session_state.tabela_selecionada}`")
            else:
                st.info("ℹ️ Nenhum banco selecionado")
            
            # ⭐⭐ BOTÕES DE ANÁLISE - APENAS SE CONECTADO E COM BANCO ⭐⭐
            if st.session_state.banco_selecionado:
                st.markdown("---")
                st.markdown("### 🔍 Análise")
                
                col_side1, col_side2 = st.columns(2)
                
                with col_side1:
                    if st.button("🗺️ Mapa", 
                                help="Mapa de relacionamentos",
                                use_container_width=True):
                        st.session_state.pagina_atual = "relacionamentos_banco"
                        st.rerun()
                
                with col_side2:
                    if st.button("📈 Stats", 
                                help="Estatísticas avançadas",
                                use_container_width=True):
                        st.info("📊 Em desenvolvimento")
            
            # ⭐⭐ COMBOBOX - APENAS SE CONECTADO E COM TABELA ⭐⭐
            if st.session_state.banco_selecionado and st.session_state.tabela_selecionada:
                st.markdown("---")
                st.markdown("### 🎯 Combobox")
                
                col_cb1, col_cb2 = st.columns(2)
                
                with col_cb1:
                    if st.button("➕ Criar Combobox", 
                                help="Criar campo combobox (estilo Access)",
                                use_container_width=True):
                        st.session_state.pagina_atual = "criar_combobox"
                        st.rerun()
                
                with col_cb2:
                    if st.button("📋 Gerir Combobox", 
                                help="Gerenciar valores dos combobox",
                                use_container_width=True):
                        st.session_state.pagina_atual = "gerenciar_combobox"
                        st.rerun()
        
        st.markdown("---")
        
        # Botão para limpar tudo
        if st.button("🔄 Reiniciar Sistema", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ['db_config']:  # Mantém a configuração
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.caption("Versão 3.0 • CRUD Completo • Desenvolvido com Python 🐍 + MySQL 🐬")

# ========================================================================================    
# ================================  Lógica de navegação ==================================
# ========================================================================================

    # ⭐⭐ LISTA DE PÁGINAS QUE PRECISAM DE CONEXÃO MYSQL ⭐⭐
    paginas_que_precisam_conexao = [
        "dados_tabela", "editar_tabela", "inserir_dados", "adicionar_coluna",
        "criar_combobox", "gerenciar_combobox", "nova_tabela", 
        "relacionamentos_banco"
    ]
    
    # ⭐⭐ VERIFICA CONEXÃO PARA PÁGINAS CRÍTICAS ⭐⭐
    if st.session_state.pagina_atual in paginas_que_precisam_conexao:
        conexao_ok, _ = verificar_conexao_mysql()
        if not conexao_ok:
            st.error("""
            ❌ **MySQL não está conectado!**
            
            **Por favor:**
            1. Volte à página inicial
            2. Configure a conexão com o MySQL
            3. Verifique se o servidor está rodando
            """)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🏠 Voltar à Página Inicial", use_container_width=True):
                    st.session_state.pagina_atual = None
                    st.rerun()
            
            with col_btn2:
                if st.button("⚙️ Configurar Conexão", use_container_width=True):
                    # Força mostrar a página inicial para configurar
                    st.session_state.pagina_atual = None
                    st.session_state.banco_selecionado = None
                    st.rerun()
            
            # Para a execução aqui
            st.stop()
    
    # ⭐⭐ NAVEGAÇÃO NORMAL (AGORA SEGURA) ⭐⭐
    if st.session_state.pagina_atual == "dados_tabela":
        if st.session_state.banco_selecionado and st.session_state.tabela_selecionada:
            gerenciar_dados_tabela(
                st.session_state.banco_selecionado, 
                st.session_state.tabela_selecionada
            )
        else:
            st.session_state.pagina_atual = None
            st.rerun()
    
    elif st.session_state.pagina_atual == "editar_tabela":
        if st.session_state.banco_selecionado and st.session_state.tabela_selecionada:
            editar_estrutura_tabela(
                st.session_state.banco_selecionado,
                st.session_state.tabela_selecionada
            )
        else:
            st.session_state.pagina_atual = None
            st.rerun()
    
    elif st.session_state.pagina_atual == "inserir_dados":
        if st.session_state.banco_selecionado and st.session_state.tabela_selecionada:
            inserir_registro(
                st.session_state.banco_selecionado,
                st.session_state.tabela_selecionada
            )
        else:
            st.session_state.pagina_atual = None
            st.rerun()
    
    elif st.session_state.pagina_atual == "adicionar_coluna":
        if st.session_state.banco_selecionado and st.session_state.tabela_selecionada:
            adicionar_coluna_tabela(
                st.session_state.banco_selecionado,
                st.session_state.tabela_selecionada
            )
        else:
            st.session_state.pagina_atual = None
            st.rerun()
    
    elif st.session_state.pagina_atual == "criar_combobox":
        if st.session_state.banco_selecionado and st.session_state.tabela_selecionada:
            adicionar_campo_combobox_simples(
                st.session_state.banco_selecionado,
                st.session_state.tabela_selecionada
            )
        else:
            st.error("❌ Selecione um banco e uma tabela primeiro!")
            st.session_state.pagina_atual = None
            st.rerun()
    
    elif st.session_state.pagina_atual == "gerenciar_combobox":
        if st.session_state.banco_selecionado and st.session_state.tabela_selecionada:
            gerenciar_combobox_menu(
                st.session_state.banco_selecionado,
                st.session_state.tabela_selecionada
            )
        else:
            st.error("❌ Selecione um banco e uma tabela primeiro!")
            st.session_state.pagina_atual = None
            st.rerun()
    
    elif st.session_state.pagina_atual == "nova_tabela":
        if st.session_state.banco_selecionado:
            criar_nova_tabela(st.session_state.banco_selecionado)
        else:
            st.error("❌ Nenhum banco selecionado!")
            st.session_state.pagina_atual = None
            st.rerun()
    
    elif st.session_state.pagina_atual == "relacionamentos_banco":
        if st.session_state.banco_selecionado:
            mostrar_relacionamentos_banco(st.session_state.banco_selecionado)
        else:
            st.session_state.pagina_atual = None
            st.rerun()
    
    elif st.session_state.banco_selecionado:
        gerenciar_banco(st.session_state.banco_selecionado)
    
    elif st.session_state.pagina_atual == "pagina_diagnosticos":
         pagina_diagnosticos()

    elif st.session_state.pagina_atual == "diagnostico_sistema":
         diagnosticar_sistema_mysql()

    elif st.session_state.pagina_atual == "diagnostico_banco":
        if st.session_state.banco_selecionado:
            diagnosticar_banco(st.session_state.banco_selecionado)
        else:
            st.error("❌ Nenhum banco selecionado!")
            st.session_state.pagina_atual = "pagina_diagnosticos"
            st.rerun()

    elif st.session_state.pagina_atual == "configurar_banco":
        if st.session_state.banco_selecionado:
            configurar_banco(st.session_state.banco_selecionado)
        else:
            st.error("❌ Nenhum banco selecionado!")
            st.session_state.pagina_atual = "pagina_diagnosticos"
            st.rerun()
    
    else:
        pagina_inicial()        
                        

# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    # Para completar 100%, você precisa combinar este código
    # com todas as outras funções da versão anterior que eu forneci
    main()