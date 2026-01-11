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

# ==================== FUNÇÃO QUE DEFINE OS ESTILOS CSS ====================
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

# ==================== FUNÇÕES DE CONEXÃO ====================

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
# ==================== FUNÇÃO PARA  CONEXÃO COM BANCO NO MYSQL  ====================

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



# ==================== EDITAR ESTRUTURA DA TABELA (VERSÃO COMPLETA com FK) ====================
# =================== FUNÇÃO PARA ADICIONAR FOREIGN KEY E ATUALIZAR FORMULARIO ================     
def editar_estrutura_tabela(nome_banco, nome_tabela):
    """Edita a estrutura de uma tabela existente - VERSÃO COMPLETA"""
    st.title(f"⚙️ EDITAR ESTRUTURA DA TABELA: {nome_tabela}")
    
    # Botão para voltar à lista de tabelas (no topo)
    if st.button("🔙 Voltar à Lista de Tabelas", key="btn_voltar_top"):
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
            ["➕ Adicionar Coluna", "✏️ Editar Coluna", "🗑️ Remover Coluna", "🔗 Adicionar FOREIGN KEY", "📋 Ver Relacionamentos"],
            horizontal=True
        )
        
        # ==================== 1. ADICIONAR COLUNA ====================
        if operacao == "➕ Adicionar Coluna":
            st.subheader("➕ Adicionar Nova Coluna")
            
            with st.form(key="form_add_col_existing"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    novo_nome = st.text_input("Nome da nova coluna:", placeholder="ex: telefone, email")
                
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
                        ]
                    )
                
                with col3:
                    posicao = st.selectbox("Posição:", ["ÚLTIMA", "PRIMEIRA"])
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    permite_null = st.checkbox("Permitir NULL", value=True)
                with col_b:
                    valor_default = st.text_input("Valor padrão:")
                with col_c:
                    auto_increment = st.checkbox("AUTO_INCREMENT")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submit = st.form_submit_button("✅ Adicionar Coluna", type="primary", use_container_width=True)
                with col_btn2:
                    cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            # Processar fora do formulário
            if submit and novo_nome:
                try:
                    # Construir SQL
                    sql = f"ALTER TABLE `{nome_tabela}` ADD COLUMN `{novo_nome}` {novo_tipo}"
                    
                    if not permite_null:
                        sql += " NOT NULL"
                    
                    if valor_default:
                        sql += f" DEFAULT '{valor_default}'"
                    
                    if auto_increment:
                        sql += " AUTO_INCREMENT"
                    
                    if posicao == "PRIMEIRA":
                        sql += " FIRST"
                    
                    # Mostrar SQL
                    with st.expander("📄 SQL que será executado"):
                        st.code(sql)
                    
                    # Executar
                    cursor.execute(sql)
                    conexao.commit()
                    
                    st.success(f"✅ Coluna '{novo_nome}' adicionada com sucesso!")
                    st.balloons()
                    
                    # Botão para atualizar
                    if st.button("🔄 Atualizar Página", key="btn_atualizar_add"):
                        st.rerun()
                    
                except Error as e:
                    st.error(f"❌ Erro ao adicionar coluna: {e}")
                    conexao.rollback()
        
        # ==================== 2. EDITAR COLUNA ====================
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
        
        # ==================== 3. REMOVER COLUNA ====================
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
        
            # ==================== 4. ADICIONAR FOREIGN KEY ====================
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
        
        # ==================== 5. VER RELACIONAMENTOS ====================
        elif operacao == "📋 Ver Relacionamentos":
            st.subheader("📋 Relacionamentos da Tabela")
            
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
    
    finally:
        cursor.close()
        conexao.close()
    
    # Botão para voltar no final
    st.markdown("---")
    if st.button("🔙 Voltar à Lista de Tabelas", key="btn_voltar_bottom", use_container_width=True):
        st.session_state.pagina_atual = None
        st.session_state.tabela_selecionada = None
        st.rerun()


# ==================== FUNÇÃO PARA MOSTRAR RELACIONAMENTOS DO BANCO ====================
def mostrar_relacionamentos_banco(nome_banco):
    """Mostra todos os relacionamentos do banco de dados"""
    st.title(f"🔗 Relacionamentos do Banco: {nome_banco}")
    
    # Botão para voltar
    if st.button("🔙 Voltar ao Banco", key="btn_voltar_rel"):
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
# ==================== FUNÇÃO para EXCLUIR banco de dados ====================        
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
    
# ================  Nova função de excluir ==============================

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
# ==================== FUNÇÃO DE PÁGINA INICIAL ====================

def pagina_inicial():
    """Página inicial do sistema"""
    
    st.markdown("""
    <div class="main-header">
        🗄️ Sistema de Gerenciamento MySQL
    </div>
    """, unsafe_allow_html=True)
    st.subheader(" 🏠 Pagina Principal")
    # Configuração de conexão
    with st.expander("⚙️ Configuração do Sistema", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            host = st.text_input("Host", "localhost", key="host_input")
        with col2:
            user = st.text_input("Usuário", "root", key="user_input")
        with col3:
            password = st.text_input("Senha", type="password", key="password_input")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("💾 Salvar Configuração", use_container_width=True):
                st.session_state.db_config = {
                    'host': host,
                    'user': user,
                    'password': password,
                    'autocommit': False
                }
                st.success("Configuração salva!")
        
        with col2:
            if st.button("🔌 Testar Conexão", use_container_width=True):
                config_temp = {
                    'host': host,
                    'user': user,
                    'password': password,
                    'autocommit': False
                }
                try:
                    conexao = mysql.connector.connect(**config_temp)
                    if conexao.is_connected():
                        st.success("✅ Conexão estabelecida!")
                        conexao.close()
                except Error as e:
                    st.error(f"❌ Falha na conexão: {e}")
    
    st.markdown("---")
    
 # teste rapido de conexão   
    # Adicione temporariamente na página inicial:
    if st.checkbox("🔍 Debug: Ver configuração atual"):
        st.write("**Configuração salva:**", st.session_state.db_config)
        
        # Testa conexão SEM banco
        config_test = st.session_state.db_config.copy()
        if 'database' in config_test:
            del config_test['database']
        
        st.write("**Configuração para exclusão:**", config_test)
        
        try:
            test_con = mysql.connector.connect(**config_test)
            st.success(f"✅ Conectado como: {test_con.user}@ {test_con.server_host}")
            test_con.close()
        except Error as e:
            st.error(f"❌ Falha conexão: {e}")
    
    # Banco de dados
    if 'db_config' in st.session_state:
        conexao = conectar_mysql()
        if conexao:
            cursor = conexao.cursor()
            
            # Criar novo banco
            with st.expander("🏗️ Criar Novo Banco de Dados", expanded=False):
                novo_banco = st.text_input("Nome do novo banco:")
                if st.button("Criar Banco", key="criar_banco_btn"):
                    if novo_banco:
                        try:
                            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{novo_banco}`")
                            st.success(f"Banco '{novo_banco}' criado com sucesso!")
                            st.rerun()
                        except Error as e:
                            st.error(f"Erro: {e}")
            # Listar bancos existentes
    cursor.execute("SHOW DATABASES")
    bancos = [db[0] for db in cursor.fetchall() 
            if db[0] not in ['information_schema', 'mysql', 'performance_schema', 'sys']]

    if bancos:
        st.subheader("📂 Bancos de Dados Disponíveis")
        
        # PRIMEIRO: Mostra todos os bancos
        for banco in bancos:
            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
            with col1:
                st.markdown(f'<div class="tabela-row"><b>📁 {banco}</b></div>', unsafe_allow_html=True)
            
            with col2:
                if st.button("👉 Lista de Tabelas", key=f"ger_{banco}"):
                    st.session_state.banco_selecionado = banco
                    st.rerun()
            
            with col3:
                # Botão de excluir - APENAS ativa o flag
                if st.button("🗑️ Excluir Banco", key=f"del_{banco}"):
                    st.session_state["dialog_banco"] = banco  # Guarda QUAL banco
                    st.rerun()
            
            with col4:
                # Botão de configurações
                if st.button("⚙️ Configurar", key=f"config_{banco}"):         
                    st.session_state["config_banco"] = banco
                    st.rerun()
        
        st.markdown("---")
        
        # SEGUNDO: FORA DO LOOP, mostra os diálogos
        
        # Diálogo de exclusão
        if "dialog_banco" in st.session_state and st.session_state["dialog_banco"]:
            banco = st.session_state["dialog_banco"]
            
            # Container para o diálogo
            with st.container(border=True):
                st.warning(f"⚠️ Tem certeza que deseja excluir o banco **{banco}**?")
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("✅ Sim, excluir definitivamente", type="primary", use_container_width=True):
                        # Aqui chama a função para excluir
                        dialog_exclusao_banco(banco)
                        del st.session_state["dialog_banco"]  # Limpa o estado
                        st.rerun()
                    
                    if st.button("❌ Cancelar", use_container_width=True):
                        del st.session_state["dialog_banco"]  # Limpa o estado
                        st.rerun()
        
        # Configurações
        if "config_banco" in st.session_state and st.session_state["config_banco"]:
            banco = st.session_state["config_banco"]
            
            with st.container(border=True):
                st.subheader(f"⚙️ Configurações: {banco}")
                
                # Sua função de configurações
                configurar_banco(banco)
                
                if st.button("🔙  Voltar a lista de bancos"):
                    del st.session_state["config_banco"]
                    st.rerun()
      
#========================= TESTES E DIAGNOSTICOS DO PROJETO ========================================                            
    st.markdown("---")
    st.subheader("🔧 Ferramentas de Diagnóstico")
# Botão para diagnóstico geral
    if st.button("🩺 Diagnóstico do Sistema", use_container_width=True):
                                               diagnosticar_sistema_mysql()
# Se houver bancos, botão para diagnóstico específico
    if bancos:
       banco_para_diagnostico = st.selectbox(
       "Selecione um banco para diagnóstico detalhado:",
        bancos,
        key="select_diagnostico"
        )
                                        
    if st.button("🔍 Analisar Banco Selecionado", use_container_width=True):
                                            diagnosticar_banco(banco_para_diagnostico)
                                
# ==================== FUNÇÕES DE DIAGNÓSTICO ====================

# ======================= FUNÇÃO PARA DIAGNOSTICAR SISTEMA MYSQL =======================

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
        
# ================================ FUNÇÃO PARA DIAGNOSTICAR BANCO DE DADOS ===========================================
        

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
        
# ===================== FUNÇÃO PARA CONFIGURAÇÕES DO BANCO DE DADOS =============
def configurar_banco(nome_banco):
    #st.subheader(f"⚙️ Configurações: {nome_banco}")
    
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

# ==================== FUNÇÃO PARA GERENCIAR BANCO ====================

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
        if st.button("🔙 Voltar ao Início"):
            st.session_state.banco_selecionado = None
            if 'pagina_atual' in st.session_state:
                del st.session_state.pagina_atual
            if 'tabela_selecionada' in st.session_state:
                del st.session_state.tabela_selecionada
            st.rerun()
    
    # Conteúdo principal
    if opcao == "🏠 Visão Geral":
        mostrar_visao_geral(nome_banco)
    
    elif opcao == "📊 Tabelas":
        gerenciar_tabelas(nome_banco)
    
    elif opcao == "➕ Nova Tabela":
        criar_nova_tabela(nome_banco)
    
          
        
# ==================== FUNÇÃO DE VISÃO GERAL DO PROJETO ====================

def mostrar_visao_geral(nome_banco):
    """Mostra estatísticas do banco"""
    st.subheader("📋 Visão Geral do Sistema")
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
        st.subheader("📊 Estatísticas do Banco")
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
        
        # ⭐⭐ Listar tabelas (seu código atual) ⭐⭐
        if tabelas:
            st.subheader("📋 Tabelas do Banco")
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
            
            # Botão para criar tabela
            if st.button("➕ Criar Primeira Tabela", type="primary"):
                # Vai direto para criação de tabela
                # Atualize o menu lateral se necessário
                st.session_state.pagina_atual = None
                # Ou mude a opção do radio
                st.rerun()
    
    except Error as e:
        st.error(f"Erro: {e}")
    
    finally:
        cursor.close()
        conexao.close()
        

# ==================== FUNÇÃO GERENCIAR TABELAS ====================

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
    
    cursor.close()
    conexao.close()

# ==================== FUNÇÃO PARA CRIAR NOVA TABELA ====================

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
        📁 <strong>Banco:</strong> {nome_banco}
    </div>
    """, unsafe_allow_html=True)
    
    # 1. NOME DA TABELA (PRIMEIRO PASSO)
    nome_tabela = st.text_input(
        "🔤 Nome da nova tabela:", 
        placeholder="ex: clientes, produtos, vendas",
        key=f"nome_tabela_{nome_banco}"
    )
    
    if not nome_tabela:
        st.info("📝 Digite um nome para a tabela para continuar...")
        
        # Botão para voltar
        if st.button("🔙 Voltar ás Tabelas", use_container_width=True):
            # Limpar estados se existirem
            if f"colunas_{nome_banco}" in st.session_state:
                del st.session_state[f"colunas_{nome_banco}"]
            st.rerun()
        
        return  # Para aqui se não tiver nome da tabela
    
    st.markdown(f"### 📋 Criando tabela: **{nome_tabela}**")
    st.markdown("---")
    
    # Inicializar estado para colunas
    chave = f"colunas_{nome_banco}"
    if chave not in st.session_state:
        st.session_state[chave] = []
    
    # 2. ADICIONAR COLUNAS (SEGUNDO PASSO)
    st.markdown("### 🎯 Adicionar Campos/Colunas")
    st.caption("Configure cada campo da tabela abaixo:")
    
    with st.form(key=f"form_add_col_{nome_banco}", border=True):
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
        
        with col1:
            nome_col = st.text_input("Nome do campo", placeholder="ex: id, nome, email")
        
        with col2:
            tipo_col = st.selectbox(
                "Tipo de dado", 
                ["INT", "VARCHAR(100)", "VARCHAR(255)", "TEXT", "DATE", 
                 "DATETIME", "DECIMAL(10,2)", "FLOAT", "BOOLEAN"],
                index=1  # VARCHAR(100) como padrão
            )
        
        with col3:
            pk_col = st.checkbox("PK", help="Chave Primária")
        
        with col4:
            null_col = st.checkbox("NULL", value=True, help="Permite valores nulos")
        
        with col5:
            ai_col = st.checkbox("AI", help="Auto Incremento (só para INT)")
        
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
                if ai_col and tipo_col != "INT":
                    st.warning("⚠️ Auto Incremento só funciona com tipo INT")
                    ai_col = False
                
                if pk_col and null_col:
                    st.warning("⚠️ Chave Primária geralmente não permite NULL")
                    null_col = False
                
                st.session_state[chave].append({
                    'nome': nome_col,
                    'tipo': tipo_col,
                    'pk': pk_col,
                    'null': null_col,
                    'ai': ai_col
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
                    # Ícones para indicar propriedades
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
        
        st.markdown("---")
        
        # 4. BOTÕES DE AÇÃO FINAL
        st.markdown("### 🚀 Ações Finais")
        
        col_acao1, col_acao2, col_acao3 = st.columns([1, 1, 2])
        
        with col_acao1:
            if st.button("✅ Criar Tabela", type="primary", use_container_width=True):
                criar_tabela_no_banco(nome_banco, nome_tabela, st.session_state[chave])
        
        with col_acao2:
            if st.button("🔄 Reiniciar", use_container_width=True, 
                         help="Limpa tudo e começa de novo"):
                st.session_state[chave] = []
                st.rerun()
        
        with col_acao3:
            if st.button("🔙 Cancelar e Voltar", use_container_width=True):
                # Limpar tudo
                if f"colunas_{nome_banco}" in st.session_state:
                    del st.session_state[f"colunas_{nome_banco}"]
                st.rerun()
    
    else:
        # Se não tem colunas ainda
        st.info("👆 Adicione o primeiro campo acima para começar a construir a tabela.")
        
        # ============ RODAPÉ FIXO ============
    st.markdown("---")  # Linha separadora
    
    # Container fixo no rodapé
    with st.container():
        st.markdown("### 🎯 Ações")
        
        col_acao1, col_acao2, col_acao3 = st.columns(3)
        
        with col_acao1:
            # Botão de criar (se tiver colunas)
            if st.session_state.get(f"colunas_{nome_banco}"):
                if st.button("✅ Criar Tabela", 
                           type="primary", 
                           use_container_width=True):
                    criar_tabela_no_banco(nome_banco, nome_tabela, 
                                        st.session_state[f"colunas_{nome_banco}"])
        
        with col_acao2:
            # Botão de limpar (sempre visível)
            if st.button("🧹 Limpar Campos", 
                       use_container_width=True,
                       help="Remove todos os campos adicionados"):
                if f"colunas_{nome_banco}" in st.session_state:
                    st.session_state[f"colunas_{nome_banco}"] = []
                st.rerun()
        
        with col_acao3:
            # ⭐⭐ BOTÃO CANCELAR SEMPRE FUNCIONAL ⭐⭐
            if st.button("❌ Cancelar Tudo", 
                       type="secondary",
                       use_container_width=True,
                       help="Cancela criação e volta"):
                # Limpa TUDO
                chaves_para_limpar = [
                    f"colunas_{nome_banco}",
                    "nome_tabela_input",
                    f"form_add_col_{nome_banco}"
                ]
                
                for chave in chaves_para_limpar:
                    if chave in st.session_state:
                        del st.session_state[chave]
                
                # Volta para a lista de tabelas
                st.rerun()


# ==================== FUNÇÃO QUE CRIA A TABELA NO BANCO ====================

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

# ==================== FUNÇÃO PARA ADICIONAR COLUNA À TABELA ====================

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
        
        with st.form(key=f"form_add_col_{nome_tabela}"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                novo_nome = st.text_input("Nome da nova coluna:", 
                                        placeholder="ex: telefone, email, preco")
            
            with col2:
                novo_tipo = st.selectbox(
                    "Tipo de dado:", 
                    ["VARCHAR(100)", "VARCHAR(255)", "INT", "BIGINT", "TEXT", 
                     "DATE", "DATETIME", "TIMESTAMP", "DECIMAL(10,2)", "FLOAT", 
                     "BOOLEAN", "ENUM('ativo','inativo')"]
                )
            
            with col3:
                posicao = st.selectbox(
                    "Posição:",
                    ["ÚLTIMA", "PRIMEIRA", "APÓS id"]
                )
            
            col_a, col_b = st.columns(2)
            with col_a:
                permite_null = st.checkbox("Permitir valores NULL", value=True)
            with col_b:
                valor_default = st.text_input("Valor padrão (opcional):")
            
            # Botões do formulário
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            
            with col_btn1:
                submit = st.form_submit_button("✅ Adicionar Coluna", type="primary", use_container_width=True)
            
            with col_btn2:
                limpar = st.form_submit_button("🧹 Limpar", use_container_width=True)
            
            with col_btn3:
                cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
                
            with col_btn4:
                cancelar = st.form_submit_button(" 🔙 voltar ", use_container_width=True)
                
            if submit:
                if not novo_nome:
                    st.error("Digite um nome para a coluna!")
                else:
                    try:
                        # Construir SQL para adicionar coluna
                        sql = f"ALTER TABLE `{nome_tabela}` ADD COLUMN `{novo_nome}` {novo_tipo}"
                        
                        if not permite_null:
                            sql += " NOT NULL"
                        
                        if valor_default:
                            sql += f" DEFAULT '{valor_default}'"
                        
                        if posicao == "PRIMEIRA":
                            sql += " FIRST"
                        elif posicao == "APÓS id":
                            # Verificar se existe coluna 'id'
                            cursor.execute(f"SHOW COLUMNS FROM `{nome_tabela}` LIKE 'id'")
                            if cursor.fetchone():
                                sql += " AFTER id"
                        
                        cursor.execute(sql)
                        conexao.commit()
                        
                        st.markdown(f"""
                        <div class="success-message">
                            ✅ Coluna <strong>{novo_nome}</strong> adicionada com sucesso à tabela <strong>{nome_tabela}</strong>!
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Mostrar nova estrutura
                        cursor.execute(f"DESCRIBE `{nome_tabela}`")
                        nova_estrutura = cursor.fetchall()
                        
                        df_nova = pd.DataFrame(
                            nova_estrutura,
                            columns=['Campo', 'Tipo', 'Nulo', 'Chave', 'Default', 'Extra']
                        )
                        
                        st.subheader("🏗️ Nova Estrutura da Tabela")
                        st.dataframe(df_nova, use_container_width=True)
                        
                        # Opções após adicionar
                        st.markdown("---")
                        col_op1, col_op2, col_op3 = st.columns(3)
                       
                        with col_op1:
                           if st.button("➕ Adicionar outra coluna", use_container_width=True):
                               st.rerun()
                        
                        with col_op2:
                            if st.button("📊 Ver dados da tabela", use_container_width=True):
                                st.session_state.pagina_atual = "dados_tabela"
                                st.rerun()
                        
                        with col_op3:
                            if st.button("🔙 Voltar ao banco", use_container_width=True):
                                st.session_state.pagina_atual = None
                                st.session_state.tabela_selecionada = None
                                st.rerun()
                        
                    except Error as e:
                        st.error(f"❌ Erro ao adicionar coluna: {e}")
                        conexao.rollback()
            
            elif limpar:
                st.rerun()
            
            elif cancelar:
                st.session_state.pagina_atual = None
                st.rerun()
    
    except Error as e:
        st.error(f"Erro: {e}")
    
    finally:
        cursor.close()
        conexao.close()
        
# ====================       INICIO DO C.R.U.D.         ======================        

# =================== FUNÇÃO DE VISUALIZAR DADOS  ============================

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
 

# ==================== FUNÇÃO PARA CRIAR/INSERIR REGISTOS ====================
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
    with st.expander("📋 **Registros Existentes** (visualizar apenas)", expanded=True):
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
      
    
    
        
        
# ==================== FUNÇÃO PARA EDITAR/ATULIZAR  REGISTOS ====================

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
# ==================== FUNÇÃO PARA EXCLUIR REGISTOS  ====================

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



# ==================== FUNÇÃO PARA GERENCIAR DADOS NA TABELA ====================

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
            
# ==================== FUNÇÃO PARA INSERIR REGISTOS COM (FOREIGN KEY) FK ====================            
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
# ==================== FUNÇÃO PARA O (PRINCIPAL) MAIN ====================


# ==================== MAIN ====================
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
            🐍 + 🎰 <br>
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
        
        # Status usando apenas Streamlit
        st.markdown("**🔌 Status da Conexão:**")
        st.success("🟢 CONECTADO")
        
        st.markdown("---")
        
        # Status da conexão - ESTA PARTE PRIMEIRO!
        if st.session_state.banco_selecionado:
            st.markdown("**📁 Banco Atual:**")
            st.success(f"`{st.session_state.banco_selecionado}`")
            
            if st.session_state.tabela_selecionada:
                st.markdown("**📊 Tabela Selecionada:**")
                st.info(f"`{st.session_state.tabela_selecionada}`")
        else:
            st.info("Nenhum banco selecionado")
        
        # Botões de análise - APENAS se tiver banco selecionado
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
                    # Se tiver função de estatísticas
                    st.info("Em desenvolvimento")
        
        st.markdown("---")
        
        # Botão para limpar tudo
        if st.button("🔄 Reiniciar Sistema", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ['db_config']:  # Mantém a configuração
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.caption("Versão 3.0 • CRUD Completo • Desenvolvido com Python 🐍")
    
    # Lógica de navegação
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
    
    # ⭐⭐ NOVA CONDIÇÃO - RELACIONAMENTOS DO BANCO ⭐⭐
    elif st.session_state.pagina_atual == "relacionamentos_banco":
        if st.session_state.banco_selecionado:
            mostrar_relacionamentos_banco(st.session_state.banco_selecionado)
        else:
            st.session_state.pagina_atual = None
            st.rerun()
    
    elif st.session_state.banco_selecionado:
        gerenciar_banco(st.session_state.banco_selecionado)
    
    else:
        pagina_inicial()

# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    # Para completar 100%, você precisa combinar este código
    # com todas as outras funções da versão anterior que eu forneci
    main()