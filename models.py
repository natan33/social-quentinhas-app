from app import db,login_manager
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    

    # Para definir a senha, armazena hash em vez do texto
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Para verificar senha
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Requisito do Flask-Login
    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}>'

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_produto = db.Column(db.String(100), nullable=False)
    nome_vendedor = db.Column(db.String(100), nullable=False)
    nome_comprador = db.Column(db.String(100), nullable=False)
    grupo = db.Column(db.String(10), nullable=False)  # 'M' para masculino, 'F' para feminino
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    status_pagamento = db.Column(db.Boolean, nullable=False, default=False)  # True para pago, False para pendente
    data_venda = db.Column(db.DateTime, nullable=False, default=datetime.now())
    preco_unitario = db.Column(db.Float, nullable=False, default=0.0)

    entrega = relationship('VendaEntregue', backref='venda', lazy=True)

    entrega_status =  db.Column(db.Boolean, nullable=True, default=False)
     
    def __repr__(self):
        return f'<Venda {self.id}: {self.nome_produto} - {self.nome_comprador}>'
    
    @property
    def valor_total(self):
        return  self.preco_unitario
    
    @property
    def status_pagamento_texto(self):
        return "Pago" if self.status_pagamento else "Pendente"


# NOVO: Definição do modelo VendaEntregue
class VendaEntregue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Chave estrangeira que referencia o id da tabela Venda
    venda_id = db.Column(db.Integer, db.ForeignKey('venda.id'), nullable=False)
    data_entrega = db.Column(db.DateTime, nullable=False, default=datetime.now())
    status_entrega = db.Column(db.String(50), nullable=False, default='Pendente') # Ex: 'Pendente', 'Entregue', 'Cancelada'
    observacoes = db.Column(db.Text, nullable=True)
    nome_vendedor_entrega = db.Column(db.String(100), nullable=True) # NOVO: Vendedor que fez a entrega

    def __repr__(self):
        return f'<VendaEntregue {self.id} - Venda ID: {self.venda_id} - Status: {self.status_entrega}>'

