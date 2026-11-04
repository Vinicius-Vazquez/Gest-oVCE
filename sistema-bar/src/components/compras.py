import streamlit as st
from src.database import SessionLocal
from src.crud import get_produtos, get_fornecedores, registrar_compra

def render_compras():
    st.subheader("📦 Entrada de Mercadorias (Registro de Compras)")
    
    db = SessionLocal()
    produtos = get_produtos(db)
    fornecedores = get_fornecedores(db)
    db.close()
    
    if not produtos:
        st.warning("Cadastre produtos no estoque antes de registrar compras.")
        return

    # Inicializa o carrinho de compras na sessão
    if "carrinho_compra" not in st.session_state:
        st.session_state.carrinho_compra = []

    # Seleção de Fornecedor
    fornecedor_selecionado = None
    if fornecedores:
        opcoes_forn = {f.id: f.nome for f in fornecedores}
        forn_id = st.selectbox("Fornecedor (Opcional)", options=list(opcoes_forn.keys()), format_func=lambda x: opcoes_forn[x])
        fornecedor_selecionado = forn_id
    else:
        st.info("Dica: Cadastre fornecedores na aba 'Fornecedores' para vinculá-los às compras.")

    st.markdown("---")
    
    # Adicionar itens à compra
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        prod_selecionado = st.selectbox(
            "Selecionar Produto",
            produtos,
            format_func=lambda p: f"{p.nome} (Estoque atual: {p.estoque_atual})"
        )
    with col2:
        qtd_compra = st.number_input("Quantidade", min_value=1, step=1, value=1)
    with col3:
        preco_unit = st.number_input("Preço de Custo Unit. (R$)", min_value=0.0, value=float(prod_selecionado.preco_custo), format="%.2f")

    if st.button("Adicionar à Nota de Compra"):
        item_existente = next((item for item in st.session_state.carrinho_compra if item['produto_id'] == prod_selecionado.id), None)
        if item_existente:
            item_existente['quantidade'] += qtd_compra
            item_existente['preco_unitario'] = preco_unit
        else:
            st.session_state.carrinho_compra.append({
                'produto_id': prod_selecionado.id,
                'nome': prod_selecionado.nome,
                'quantidade': qtd_compra,
                'preco_unitario': preco_unit
            })
        st.success(f"Item adicionado à compra!")
        st.rerun()

    # Exibe itens da Compra Atual
    st.markdown("### 📋 Itens da Compra Atual")
    if st.session_state.carrinho_compra:
        total_compra = 0
        remover_idx = []
        
        for idx, item in enumerate(st.session_state.carrinho_compra):
            subtotal = item['quantidade'] * item['preco_unitario']
            total_compra += subtotal
            
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            c1.write(f"**{item['nome']}**")
            c2.write(f"Qtd: {item['quantidade']}")
            c3.write(f"Subtotal: R$ {subtotal:.2f}")
            if c4.button("❌ Remover", key=f"del_compra_{idx}"):
                remover_idx.append(idx)
                
        for idx in sorted(remover_idx, reverse=True):
            st.session_state.carrinho_compra.pop(idx)
            st.rerun()

        st.markdown(f"### **Valor Total da Compra: R$ {total_compra:.2f}**")
        
        if st.button("Finalizar Entrada no Estoque", type="primary"):
            db = SessionLocal()
            sucesso, msg = registrar_compra(db, fornecedor_selecionado, st.session_state.carrinho_compra)
            db.close()
            
            if sucesso:
                st.success(msg)
                st.session_state.carrinho_compra = []
                st.rerun()
            else:
                st.error(f"Erro ao registrar compra: {msg}")
    else:
        st.info("Nenhum item adicionado à compra atual.")