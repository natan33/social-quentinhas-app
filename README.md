
# 📦 Sistema de Vendas - Gincana IBVA

Este projeto é um sistema social de vendas de quentinhas desenvolvido para a **Igreja Batista em Vista Alegre**, com o objetivo de auxiliar nas gincanas e eventos. Ele foi construído com foco em simplicidade, economia e facilidade de uso.

## 🛠 Tecnologias Utilizadas

- **Back-end**: [Flask](https://flask.palletsprojects.com/)
- **Front-end**: HTML5, CSS3, JavaScript (com bibliotecas via CDN)
- **Banco de Dados**: SQLite
- **Bibliotecas JS**:
  - [Bootstrap 5](https://getbootstrap.com/)
  - [Select2](https://select2.org/)
  - [DataTables](https://datatables.net/)
  - [Font Awesome](https://fontawesome.com/)

## 🚀 Funcionalidades

- Autenticação simples com usuário e senha
- Cadastro, edição e exclusão de vendas
- Filtros por vendedor, comprador e ID
- Estatísticas por grupo (Meninos, Meninas, Igreja)
- Exportação dos dados em planilha Excel
- API para consulta de vendas
- Interface responsiva

## 📷 Interface

A interface foi construída com Bootstrap 5, focando em usabilidade e legibilidade, mesmo em dispositivos móveis. Todos os recursos JS foram importados via CDN para manter o projeto leve e barato.

## 🧱 Estrutura do Projeto

```
/app
│
├── static/
│   ├── css/style.css
│   └── js/main.js
│
├── templates/
│   ├── index.html
│   ├── login.html
│   └── base.html
│
├── models.py
├── forms.py
├── routes.py
└── app.py
```

## 📦 Como Baixar e Rodar o Projeto

### 1. Clone o repositório

```bash
git clone https://github.com/seuusuario/sistema-vendas-ibva.git
cd sistema-vendas-ibva
```

### 2. Crie e ative um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Para Linux/macOS
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

> Certifique-se de que você tem Python 3.8+ instalado.

### 4. Rode o projeto

```bash
python app.py
```

## ☁️ Deploy com NGINX (Linux)

O projeto foi implementado em produção utilizando:

- **Sistema Operacional**: Ubuntu Server
- **Servidor WSGI**: Gunicorn
- **Servidor HTTP reverso**: Nginx

### Exemplo de comandos básicos:

```bash
sudo apt update && sudo apt install python3-venv nginx
cd /caminho/do/projeto
source venv/bin/activate
gunicorn -w 4 -b 127.0.0.1:8000 app:app
```

### Exemplo de configuração para Nginx:

```nginx
server {
    listen 80;
    server_name seu_dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📤 Exportação para Excel

O sistema permite exportar todas as vendas para uma planilha `.xlsx`, contendo os campos:

- Produto
- Vendedor
- Comprador
- Grupo
- Quantidade
- Valor Total
- Status do Pagamento
- Data da Venda

## 🔐 Login Padrão

- **Usuário:** `admin`
- **Senha:** `123`

> *Para fins de produção, modifique as credenciais no arquivo `routes.py`.*

## ✝️ Finalidade

Este sistema foi desenvolvido para uso comunitário pela **Igreja Batista em Vista Alegre** durante eventos e campanhas evangelísticas, como gincanas e ações sociais.

---

Desenvolvido com 💙 e simplicidade para servir bem a obra de Deus.
