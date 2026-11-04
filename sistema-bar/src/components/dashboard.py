import streamlit as st
import pandas as pd
from datetime import date, datetime
from src.database import SessionLocal
from src.models import Produto, Venda

def render_dashboard():
    st.subheader("📊 Dashboard e Visão Geral do Bar")
    
    db = SessionLocal()
    produtos = db.query(Produto).all()
    vendas = db.query(Venda).all()
    db.close()
    
    # Métricas Principais
    total_produtos = len(produtos)
    total_vendas_realizadas = len(vendas)
    faturamento_total = sum(v.valor_total for v in vendas) if vendas else 0.0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Produtos Cadastrados", total_produtos)
    col2.metric("🛒 Vendas Realizadas", total_vendas_realizadas)
    col3.metric("💰 Faturamento Total", f"R$ {faturamento_total:.2f}")
    
    st.markdown("---")
    
    # Alerta de Estoque Baixo
    st.markdown("### ⚠️ Alerta de Estoque Mínimo")
    produtos_baixos = [p for p in produtos if p.estoque_atual <= p.estoque_minimo]
    
    if produtos_baixos:
        dados_alerta = [{
            "Produto": p.nome,
            "Categoria": p.categoria,
            "Estoque Atual": p.estoque_atual,
            "Estoque Mínimo": p.estoque_minimo
        } for p in produtos_baixos]
        st.warning("Atenção: Os produtos abaixo estão com o estoque crítico:")
        st.dataframe(dados_alerta, use_container_width=True)
    else:
        st.success("✅ Todos os produtos estão com níveis de estoque saudáveis!")

    st.markdown("---")

    # Histórico de Vendas com Filtro e Exportação
    st.markdown("### 🕒 Histórico e Relatório de Vendas")
    if vendas:
        dados_vendas = []
        for v in vendas:
            dados_vendas.append({
                "ID Venda": v.id,
                "Data": v.data_venda.date(),
                "Hora": v.data_venda.strftime("%H:%M:%S"),
                "Forma de Pagamento": v.forma_pagamento,
                "Valor Total (R$)": v.valor_total
            })
        
        df_vendas = pd.DataFrame(dados_vendas)
        
        # Filtro por data na barra lateral ou na tela
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            data_inicio = st.date_input("Data Inicial", value=date.today())
        with col_f2:
            data_fim = st.date_input("Data Final", value=date.today())
            
        # Converte para datetime.date para comparar
        df_vendas_filtrado = df_vendas[
            (df_vendas["Data"] >= data_inicio) & 
            (df_vendas["Data"] <= data_fim)
        ]
        
        st.metric("Faturamento no Período Selecionado", f"R$ {df_vendas_filtrado['Valor Total (R$)'].sum():.2f}")
        
        # Exibe tabela formatada
        st.dataframe(df_vendas_filtrado, use_container_width=True)
        
        # Botão para exportar para CSV
        csv_data = df_vendas_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Relatório em CSV",
            data=csv_data,
            file_name=f"relatorio_vendas_{data_inicio}_a_{data_fim}.csv",
            mime="text/csv",
        )
    else:
        st.info("Nenhuma venda registrada até o momento.")