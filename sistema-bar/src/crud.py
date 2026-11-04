from sqlalchemy.orm import Session
from src.models import Produto, Venda, ItemVenda, Fornecedor, Compra, ItemCompra

# ==========================================
# GESTÃO DE PRODUTOS E ESTOQUE
# ==========================================

def get_produtos(db: Session):
    """Retorna todos os produtos cadastrados no sistema."""
    return db.query(Produto).all()

def criar_produto(db: Session, nome: str, categoria: str, preco_custo: float, preco_venda: float, estoque_atual: int, estoque_minimo: int):
    """Cadastra um novo produto no banco de dados."""
    db_produto = Produto(
        nome=nome,
        categoria=categoria,
        preco_custo=preco_custo,
        preco_venda=preco_venda,
        estoque_atual=estoque_atual,
        estoque_minimo=estoque_minimo
    )
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto


# ==========================================
# GESTÃO DE FORNECEDORES
# ==========================================

def get_fornecedores(db: Session):
    """Retorna todos os fornecedores cadastrados."""
    return db.query(Fornecedor).all()

def criar_fornecedor(db: Session, nome: str, contato: str, telefone: str):
    """Cadastra um novo fornecedor."""
    db_fornecedor = Fornecedor(
        nome=nome,
        contato=contato,
        telefone=telefone
    )
    db.add(db_fornecedor)
    db.commit()
    db.refresh(db_fornecedor)
    return db_fornecedor


# ==========================================
# GESTÃO DE VENDAS (FRENTE DE CAIXA)
# ==========================================

def registrar_venda(db: Session, itens_carrinho: list, forma_pagamento: str):
    """
    Registra uma venda transacionalmente:
    - Calcula o valor total
    - Cria o registro da venda
    - Adiciona os itens da venda
    - Abate automaticamente a quantidade do estoque dos produtos
    """
    try:
        valor_total_venda = sum(item['quantidade'] * item['preco_praticado'] for item in itens_carrinho)
        
        # 1. Cria a Venda principal
        nova_venda = Venda(
            valor_total=valor_total_venda,
            forma_pagamento=forma_pagamento
        )
        db.add(nova_venda)
        db.flush() # Gera o ID da venda para associar aos itens
        
        # 2. Processa os itens e abate o estoque
        for item in itens_carrinho:
            produto = db.query(Produto).filter(Produto.id == item['produto_id']).first()
            
            if not produto:
                raise Exception(f"Produto ID {item['produto_id']} não encontrado.")
            
            if produto.estoque_atual < item['quantidade']:
                raise Exception(f"Estoque insuficiente para o produto '{produto.nome}'! Disponível: {produto.estoque_atual}")
            
            # Abate o estoque atual
            produto.estoque_atual -= item['quantidade']
            
            # Registra o item da venda
            novo_item = ItemVenda(
                venda_id=nova_venda.id,
                produto_id=produto.id,
                quantidade=item['quantidade'],
                preco_praticado=item['preco_praticado']
            )
            db.add(novo_item)
            
        db.commit()
        return True, "Venda registrada e estoque atualizado com sucesso!"
    except Exception as e:
        db.rollback()
        return False, str(e)


# ==========================================
# GESTÃO DE COMPRAS (ENTRADA DE MERCADORIAS)
# ==========================================

def registrar_compra(db: Session, fornecedor_id: int, itens_compra: list):
    """
    Registra uma compra de mercadorias:
    - Cria o registro da compra vinculada ao fornecedor
    - Adiciona os itens comprados
    - Aumenta o estoque dos produtos correspondentes
    itens_compra: [{'produto_id': 1, 'quantidade': 10, 'preco_unitario': 4.50}]
    """
    try:
        valor_total_compra = sum(item['quantidade'] * item['preco_unitario'] for item in itens_compra)
        
        # 1. Cria a Compra principal
        nova_compra = Compra(
            fornecedor_id=fornecedor_id if fornecedor_id else None,
            valor_total=valor_total_compra
        )
        db.add(nova_compra)
        db.flush()
        
        # 2. Processa os itens e aumenta o estoque
        for item in itens_compra:
            produto = db.query(Produto).filter(Produto.id == item['produto_id']).first()
            
            if not produto:
                raise Exception(f"Produto ID {item['produto_id']} não encontrado.")
            
            # Aumenta o estoque
            produto.estoque_atual += item['quantidade']
            
            # Opcional: Atualiza o preço de custo com o valor mais recente da compra
            produto.preco_custo = item['preco_unitario']
            
            # Registra o item da compra
            novo_item = ItemCompra(
                compra_id=nova_compra.id,
                produto_id=produto.id,
                quantidade=item['quantidade'],
                preco_unitario=item['preco_unitario']
            )
            db.add(novo_item)
            
        db.commit()
        return True, "Compra registrada e estoque atualizado com sucesso!"
    except Exception as e:
        db.rollback()
        return False, str(e)