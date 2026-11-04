import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Tenta pegar a URL do Supabase configurada nos segredos do Streamlit ou variáveis de ambiente
DATABASE_URL = st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", "sqlite:///./data/bar_database.db"))

# Ajuste para compatibilidade com SQLAlchemy caso venha com o prefixo antigo do postgres
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Cria a engine do SQLAlchemy de acordo com o banco escolhido
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Fornece uma sessão de banco de dados para as operações."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()