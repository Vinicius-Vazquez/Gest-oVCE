import streamlit as st
from src.database import SessionLocal
from src.crud import get_produtos, registrar_venda

def render_vendas():
    st.subheader("🛒 Frente de Caixa / Registrar Venda")
    
    db = SessionLocal()
    produtos = get_produtos(db)
    db.close()
    
    if not produtos:
        st.warning("Cadastre produtos no estoque antes de realizar vendas.")
        return

    # Inicializa o carrinho na sessão do Streamlit se não existir
    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []

    # Seleção de produtos para adicionar ao carrinho
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        produto_selecionado = st.selectbox(
            "Selecione o Produto", 
            produtos, 
            format_func=lambda p: f"{p.nome} - R$ {p.preco_venda:.2f} (Estoque: {p.estoque_atual})"
        )
    with col2:
        quantidade = st.number_input("Qtd", min_value=1, step=1, value=1)
    with col3:
        st.text("") # Espaçamento
        st.text("")
        adicionar = st.button("Adicionar")

    if adicionar:
        if produto_selecionado.estoque_atual < quantidade:
            st.error(f"Estoque insuficiente! Disponível: {produto_selecionado.estoque_atual}")
        else:
            item_existente = next((item for item in st.session_state.carrinho if item['produto_id'] == produto_selecionado.id), None)
            if item_existente:
                item_existente['quantidade'] += quantidade
            else:
                st.session_state.carrinho.append({
                    'produto_id': produto_selecionado.id,
                    'nome': produto_selecionado.nome,
                    'quantidade': quantidade,
                    'preco_praticado': produto_selecionado.preco_venda
                })
            st.success(f"{quantidade}x {produto_selecionado.nome} adicionado ao carrinho!")
            st.rerun()

    # Exibe o Carrinho Atual
    st.markdown("### 🛍️ Carrinho da Venda Atual")
    if st.session_state.carrinho:
        total_geral = 0
        itens_para_remover = []
        
        for idx, item in enumerate(st.session_state.carrinho):
            subtotal = item['quantidade'] * item['preco_praticado']
            total_geral += subtotal
            
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            c1.write(f"**{item['nome']}**")
            c2.write(f"Qtd: {item['quantidade']}")
            c3.write(f"Subtotal: R$ {subtotal:.2f}")
            if c4.button("❌ Remover", key=f"del_{idx}"):
                itens_para_remover.append(idx)
                
        for idx in sorted(itens_para_remover, reverse=True):
            st.session_state.carrinho.pop(idx)
            st.rerun()

        st.markdown(f"### **Total a Pagar: R$ {total_geral:.2f}**")
        
        forma_pagamento = st.selectbox("Forma de Pagamento", ["Dinheiro", "Pix", "Cartão de Crédito", "Cartão de Débito"])
        
        if st.button("Finalizar Venda", type="primary"):
            db = SessionLocal()
            sucesso, mensagem = registrar_venda(db, st.session_state.carrinho, forma_pagamento)
            db.close()
            
            if sucesso:
                st.success(mensagem)
                st.session_state.carrinho = []
                st.rerun()
            else:
                st.error(f"Erro ao registrar venda: {mensagem}")
    else:
        st.info("O carrinho está vazio.")