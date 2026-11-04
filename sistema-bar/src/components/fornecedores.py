import streamlit as st
from src.database import SessionLocal
from src.crud import get_fornecedores, criar_fornecedor

def render_fornecedores():
    st.subheader("👥 Cadastro e Gestão de Fornecedores")
    
    db = SessionLocal()
    
    # Formulário para cadastrar novo fornecedor
    with st.expander("➕ Cadastrar Novo Fornecedor"):
        with st.form("form_fornecedor"):
            nome = st.text_input("Nome da Empresa / Fornecedor (ex: Distribuidora de Bebidas Alfa)")
            contato = st.text_input("Nome do Representante / Contato (ex: Carlos)")
            telefone = st.text_input("Telefone / WhatsApp (ex: (37) 99999-9999)")
            
            submitted = st.form_submit_button("Salvar Fornecedor")
            if submitted:
                if nome:
                    try:
                        criar_fornecedor(db, nome, contato, telefone)
                        st.success(f"Fornecedor '{nome}' cadastrado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao cadastrar fornecedor: {e}")
                else:
                    st.warning("O nome do fornecedor é obrigatório.")

    # Tabela com fornecedores cadastrados
    st.markdown("### Fornecedores Cadastrados")
    fornecedores = get_fornecedores(db)
    db.close()
    
    if fornecedores:
        dados = []
        for f in fornecedores:
            dados.append({
                "ID": f.id,
                "Fornecedor": f.nome,
                "Contato": f.contato or "-",
                "Telefone": f.telefone or "-"
            })
        st.dataframe(dados, use_container_width=True)
    else:
        st.info("Nenhum fornecedor cadastrado ainda.")