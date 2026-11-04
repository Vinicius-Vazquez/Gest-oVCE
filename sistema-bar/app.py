import streamlit as st
from src.database import Base, engine
from src.components.estoque import render_estoque
from src.components.vendas import render_vendas
from src.components.compras import render_compras
from src.components.fornecedores import render_fornecedores
from src.components.dashboard import render_dashboard

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Gestão de Bar - Sistema",
    page_icon="🍻",
    layout="wide",
)

# Inicializa as tabelas no banco de dados caso não existam
@st.cache_resource
def init_db():
    Base.metadata.create_all(bind=engine)

init_db()

# Cabeçalho Principal
st.title("🍻 Sistema de Gestão para Bar")
st.markdown("Gerencie seu estoque, registre vendas e controle compras de forma simples e segura.")

# Barra lateral de navegação
menu = st.sidebar.selectbox(
    "Menu Principal",
    ["📊 Dashboard", "📦 Estoque", "🛒 Registrar Venda", "📦 Registrar Compra", "👥 Fornecedores"]
)

# Roteamento das páginas
if menu == "📊 Dashboard":
    render_dashboard()
    
elif menu == "📦 Estoque":
    render_estoque()
    
elif menu == "🛒 Registrar Venda":
    render_vendas()
    
elif menu == "📦 Registrar Compra":
    render_compras()

elif menu == "👥 Fornecedores":
    render_fornecedores()