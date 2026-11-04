import streamlit as st
from src.database import SessionLocal
from src.crud import get_produtos, criar_produto

def render_estoque():
    st.subheader("📦 Gerenciamento de Estoque e Produtos")
    
    db = SessionLocal()
    
    # Formulário para cadastrar novo produto
    with st.expander("➕ Cadastrar Novo Produto"):
        with st.form("form_produto"):
            nome = st.text_input("Nome do Produto (ex: Cerveja Pilsen 600ml)")
            categoria = st.selectbox("Categoria", ["Bebidas Alcoólicas", "Não Alcoólicos", "Porções", "Petiscos", "Outros"])
            
            col1, col2 = st.columns(2)
            with col1:
                preco_custo = st.number_input("Preço de Custo (R$)", min_value=0.0, format="%.2f")
                estoque_atual = st.number_input("Quantidade Inicial em Estoque", min_value=0, step=1)
            with col2:
                preco_venda = st.number_input("Preço de Venda (R$)", min_value=0.0, format="%.2f")
                estoque_minimo = st.number_input("Estoque Mínimo (Alerta)", min_value=0, step=1, value=5)
                
            submitted = st.form_submit_button("Salvar Produto")
            if submitted:
                if nome:
                    try:
                        criar_produto(db, nome, categoria, preco_custo, preco_venda, estoque_atual, estoque_minimo)
                        st.success(f"Produto '{nome}' cadastrado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao cadastrar (talvez o produto já exista): {e}")
                else:
                    st.warning("O nome do produto é obrigatório.")

    # Tabela com produtos cadastrados
    st.markdown("### Produtos Cadastrados")
    produtos = get_produtos(db)
    db.close()
    
    if produtos:
        dados = []
        for p in produtos:
            status = "⚠️ Baixo" if p.estoque_atual <= p.estoque_minimo else "✅ Normal"
            dados.append({
                "ID": p.id,
                "Nome": p.nome,
                "Categoria": p.categoria,
                "Custo (R$)": f"R$ {p.preco_custo:.2f}",
                "Venda (R$)": f"R$ {p.preco_venda:.2f}",
                "Estoque": p.estoque_atual,
                "Mínimo": p.estoque_minimo,
                "Status": status
            })
        st.dataframe(dados, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado ainda. Use o botão acima para adicionar o primeiro item.")