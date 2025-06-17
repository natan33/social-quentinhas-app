
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response,session
from sqlalchemy import func
from app import app, db
from forms import LoginForm
from models import Venda,VendaEntregue,User
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO

from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user,login_required
from forms import LoginForm
from functools import wraps
from flask import request, abort

ALLOWED_IPS = {'127.0.0.1', '192.168.0.105','192.168.1.213','192.168.1.71','192.168.1.218'}

def ip_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.remote_addr not in ALLOWED_IPS:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
@ip_required
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = form.usuario.data
        senha = form.senha.data

        user = User.query.filter_by(username=usuario).first()

        if user and user.check_password(senha):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/')
@login_required
@ip_required
def index():
    # Filtros
    filtro_vendedor = request.args.get('vendedor', '')
    filtro_comprador = request.args.get('comprador', '')
    filtro_id = request.args.get('id', '')
    status_pagamento = request.args.get('status_pagamento', '')
    print(request)
    
    # Query base
    query = Venda.query
    
    # Aplicar filtros
    if status_pagamento == 'Pago':
        query = query.filter(Venda.status_pagamento == True)
    elif status_pagamento == 'Pendente':
        query = query.filter(Venda.status_pagamento == False)
    if filtro_vendedor:
        query = query.filter(Venda.nome_vendedor.ilike(f'%{filtro_vendedor}%'))
    if filtro_comprador:
        query = query.filter(Venda.nome_comprador.ilike(f'%{filtro_comprador}%'))
    if filtro_id:
        try:
            query = query.filter(Venda.id == int(filtro_id))
        except ValueError:
            pass
    
    vendas = query.order_by(Venda.data_venda.desc()).all()
    
    # Estatísticas
    todas_vendas = Venda.query.all()
    quantidade_total = sum(venda.quantidade for venda in todas_vendas)
    print(quantidade_total)
    vendas_meninos = sum(venda.quantidade for venda in todas_vendas if venda.grupo == 'M')
    vendas_meninas = sum(venda.quantidade for venda in todas_vendas if venda.grupo == 'F')
    vendas_igreja = sum(venda.quantidade for venda in todas_vendas if venda.grupo == 'IG')
    valor_total_geral = sum(venda.valor_total for venda in todas_vendas)
    valor_total_pago = sum(venda.valor_total for venda in todas_vendas if venda.status_pagamento == True)
    valor_total_nao_pago = sum(venda.valor_total for venda in todas_vendas if venda.status_pagamento == False)
    qtde_quentinhas_pagas = sum(venda.quantidade for venda in todas_vendas if venda.status_pagamento == True)
    qtde_quentinhas_nao_pagas = sum(venda.quantidade for venda in todas_vendas if venda.status_pagamento == False)

    value_despesas = '858'
    qtde_quetinhas_entegues = sum(venda.quantidade for venda in todas_vendas if venda.entrega_status == True)

    # vinculado com as quentinhas pagas
    qtde_n_quetinhas_entegues = sum(venda.quantidade for venda in todas_vendas if venda.entrega_status == False)
    
    stats = {
        'quantidade_total': quantidade_total,
        'vendas_meninos': vendas_meninos,
        'vendas_meninas': vendas_meninas,
        "vendas_igreja":vendas_igreja,
        'valor_total': valor_total_geral,
        'valor_total_pago':valor_total_pago,
        'valor_total_nao_pago':valor_total_nao_pago,
        'qtde_quentinhas_pagas':qtde_quentinhas_pagas,
        'qtde_quentinhas_nao_pagas':qtde_quentinhas_nao_pagas,
        'qtde_quetinhas_entegues':qtde_quetinhas_entegues,
        'qtde_n_quetinhas_entegues':qtde_n_quetinhas_entegues,
        'value_despesas':value_despesas


    }
    query_vendedor = (
        db.session.query(Venda.nome_vendedor)
        .filter(Venda.nome_vendedor.ilike(f"%{filtro_vendedor}%"))
        .distinct()
        .order_by(Venda.nome_vendedor)
        .all()
    )

    response = [{"id":i, "nome":name.nome_vendedor}for i,name in enumerate(query_vendedor)]

    entregadores=  response
    
    return render_template('index.html', 
                         vendas=vendas, 
                         stats=stats,
                         entregadores=entregadores,
                         filtros={
                             'vendedor': filtro_vendedor,
                             'comprador': filtro_comprador,
                             'id': filtro_id
                         })






@app.route('/api/vendas')
@login_required
def api_vendas():
    vendedor = request.args.get('vendedor', '').strip()
    comprador = request.args.get('comprador', '').strip()
    venda_id = request.args.get('id', '').strip()
    status_pagamento = request.args.get('status_pagamento', '')
    
    # Query base
    query = Venda.query
    
    # Aplicar filtros
    if status_pagamento == 'Pago':
        query = query.filter(Venda.status_pagamento == True)
    elif status_pagamento == 'Pendente':
        query = query.filter(Venda.status_pagamento == False)

    elif venda_id:
        query = query.filter(Venda.id == venda_id)
    elif vendedor:
        query = query.filter(Venda.nome_vendedor.ilike(f'%{vendedor}%'))
    elif comprador:
        query = query.filter(Venda.nome_comprador.ilike(f'%{comprador}%'))

    vendas = query.all()

    data = []
    for v in vendas:
        data.append({
            "id": v.id,
            "nome_produto": v.nome_produto,
            "nome_vendedor": v.nome_vendedor,
            "nome_comprador": v.nome_comprador,
            "grupo": v.grupo,
            "quantidade": v.quantidade,
            "preco_unitario": f"R$ {v.preco_unitario:.2f}",
            "valor_total": f"R$ {v.valor_total:.2f}",
            "status_pagamento": "Pago" if v.status_pagamento else "Pendente",
            "entrega_status": "Entregue" if v.entrega_status else "Pendente",
            "data_venda": v.data_venda.strftime('%d/%m/%Y %H:%M'),
        })
    return jsonify(data)



@app.route('/adicionar_venda', methods=['POST'])
@login_required
def adicionar_venda():
    try:
        print(request.form)
        nome_produto = request.form['nome_produto']
        nome_vendedor = request.form['nome_vendedor']
        nome_comprador = request.form['nome_comprador']
        grupo_comprador = request.form['grupo_comprador']
        quantidade = int(request.form['quantidade'])
        preco_unitario = float(request.form['preco_unitario'])
        status_pagamento = 'status_pagamento' in request.form
        print()
        print(status_pagamento)
        nova_venda = Venda(
            nome_produto=nome_produto,
            nome_vendedor=nome_vendedor,
            nome_comprador=nome_comprador,
            grupo=grupo_comprador,
            quantidade=quantidade,
            preco_unitario=preco_unitario,
            status_pagamento=status_pagamento
        )
        
        db.session.add(nova_venda)
        db.session.commit()
        
        flash('Venda adicionada com sucesso!', 'success')
    except Exception as e:
        print(e)
        flash(f'Erro ao adicionar venda: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('index'))

@app.route('/editar_venda/<int:id>', methods=['POST'])
@login_required
def editar_venda(id):
    try:
        venda = Venda.query.get_or_404(id)
        
        venda.nome_produto = request.form['nome_produto']
        venda.nome_vendedor = request.form['nome_vendedor']
        venda.nome_comprador = request.form['nome_comprador']
        venda.grupo_comprador = request.form['grupo_comprador']
        venda.quantidade = int(request.form['quantidade'])
        venda.preco_unitario = float(request.form['preco_unitario'])
        venda.status_pagamento = 'status_pagamento' in request.form
        
        db.session.commit()
        
        flash('Venda atualizada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar venda: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('index'))

@app.route('/excluir_venda/<int:id>', methods=['POST'])
@login_required
def excluir_venda(id):
    try:
        venda = Venda.query.get_or_404(id)
        db.session.delete(venda)
        db.session.commit()
        
        flash('Venda excluída com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir venda: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('index'))

@app.route('/obter_venda/<int:id>')
@login_required
def obter_venda(id):
    venda = Venda.query.get_or_404(id)
    return jsonify({
        'id': venda.id,
        'nome_produto': venda.nome_produto,
        'nome_vendedor': venda.nome_vendedor,
        'nome_comprador': venda.nome_comprador,
        'grupo_comprador': venda.grupo,
        'quantidade': venda.quantidade,
        'preco_unitario': venda.preco_unitario,
        'status_pagamento': venda.status_pagamento
    })

@app.route('/exportar_excel')
@login_required
def exportar_excel():
    try:
        vendas = Venda.query.order_by(Venda.data_venda.desc()).all()
        
        # Preparar dados para o DataFrame
        dados = []
        for venda in vendas:
            dados.append({
                'ID': venda.id,
                'Produto': venda.nome_produto,
                'Vendedor': venda.nome_vendedor,
                'Comprador': venda.nome_comprador,
                'grupo': 'Masculino' if venda.grupo == 'M' else 'Feminino',
                'Quantidade': venda.quantidade,
                'Preço Unitário': f'R$ {venda.preco_unitario:.2f}',
                'Valor Total': f'R$ {venda.valor_total:.2f}',
                'Status Pagamento': venda.status_pagamento_texto,
                'Data da Venda': venda.data_venda.strftime('%d/%m/%Y %H:%M')
            })
        
        # Criar DataFrame
        df = pd.DataFrame(dados)
        
        # Criar arquivo Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Vendas Quentinhas', index=False)
        
        output.seek(0)
        
        # Criar resposta
        response = make_response(output.read())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=vendas_quentinhas_{datetime.now().strftime("%d%m%Y")}.xlsx'
        
        return response
        
    except Exception as e:
        flash(f'Erro ao exportar dados: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/filter_vendedor', methods=['GET'])
@login_required
def filter_vendedor():
    search = request.args.get('searh','')

    query = (
        db.session.query(Venda.nome_vendedor)
        .filter(Venda.nome_vendedor.ilike(f"%{search}%"))
        .distinct()
        .order_by(Venda.nome_vendedor)
        .all()
    )

    response = [{"id":i, "text":name.nome_vendedor}for i,name in enumerate(query)]

    return jsonify(response)


@app.route('/api/sales_by_group')
@login_required
def get_sales_by_group():
    # Lógica para consultar o banco de dados e agrupar vendas por 'grupo_comprador'
    # Exemplo (substitua pela sua lógica real do DB):
    todas_vendas = Venda.query.all()
    quantidade_total = sum(venda.quantidade for venda in todas_vendas)
    print(quantidade_total)
    vendas_meninos = sum(venda.quantidade for venda in todas_vendas if venda.grupo == 'M')
    vendas_meninas = sum(venda.quantidade for venda in todas_vendas if venda.grupo == 'F')
    vendas_igreja = sum(venda.quantidade for venda in todas_vendas if venda.grupo == 'IG')


    data = {
        'labels': ['Meninos', 'Meninas', 'Igreja', 'Outros'], # Busque os grupos distintos do DB
        'values': [vendas_meninos, vendas_meninas, vendas_igreja, 0] # Busque a soma das quantidades ou vendas para cada grupo
    }
    return jsonify(data)

@app.route('/api/payment_status')
@login_required
def get_payment_status():
    # Lógica para consultar o banco de dados e contar vendas pagas/não pagas
    # Exemplo (substitua pela sua lógica real do DB):

    query = Venda.query
    
    vendas = query.order_by(Venda.data_venda.desc()).all()

    todas_vendas = Venda.query.all()
    
    qtde_quentinhas_pagas = sum(venda.quantidade for venda in todas_vendas if venda.status_pagamento == True)
    qtde_quentinhas_nao_pagas = sum(venda.quantidade for venda in todas_vendas if venda.status_pagamento == False)

    data = {
        'labels': ['Pago', 'Não Pago'],
        'values': [qtde_quentinhas_pagas, qtde_quentinhas_nao_pagas] # Qtde Pagas e Qtde Não Pagas
    }
    return jsonify(data)

@app.route('/api/daily_sales')
@login_required
def get_daily_sales():
    today = datetime.now().date()
    # Pega os últimos 7 dias, incluindo o dia atual
    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

    # Inicializa um dicionário para armazenar as vendas diárias, com 0 para cada dia
    daily_sales_data = {date.strftime('%d/%m'): 0.0 for date in dates}

    # Consulta ao banco de dados para somar as vendas por dia
    # Usamos func.date(Venda.data_venda) para agrupar apenas pela data, ignorando a hora
    sales_query = db.session.query(
        func.date(Venda.data_venda),
        func.sum(Venda.quantidade * Venda.preco_unitario)
    ).filter(
        Venda.data_venda >= (dates[0] - timedelta(days=1)), # Começa um dia antes para garantir todos os registros do primeiro dia
        Venda.data_venda < (today + timedelta(days=1)) # Pega até o final do dia atual
    ).group_by(
        func.date(Venda.data_venda)
    ).order_by(
        func.date(Venda.data_venda)
    ).all()

    # Preenche o dicionário com os dados do banco de dados
    for date_str, total_value in sales_query:
        # Formata a data do banco para 'DD/MM' para corresponder às chaves do dicionário
        formatted_date = datetime.strptime(str(date_str), '%Y-%m-%d').strftime('%d/%m')
        if formatted_date in daily_sales_data:
            daily_sales_data[formatted_date] = total_value if total_value is not None else 0.0

    # Extrai os rótulos (labels) e os valores para o Chart.js
    labels = list(daily_sales_data.keys())
    values = list(daily_sales_data.values())

    data = {
        'labels': labels,
        'values': values
    }
    return jsonify(data)




@app.route('/entregar_pedido', methods=['POST'])
@login_required
def entregar_pedido():
    try:
        # Captura os dados do formulário
        pedido_id = request.form.get('pedido_id')
        acao = request.form.get('acao_entrega')
        print('pedido_id',pedido_id)
        vendedor_nome = request.form.get('vendedor')
        observacoes = request.form.get('observacoes')

        # Validação básica
        venda = Venda.query.get(pedido_id)
        if not venda:
            return jsonify({'erro': 'Venda não encontrada.'}), 404
        
        elif acao == 'retirar':
            venda.entrega_status = False
            entrega = VendaEntregue.query.filter_by(venda_id=pedido_id).first()
            if entrega:
                db.session.delete(entrega)
        # 1. Atualiza a venda
        venda = Venda.query.get(pedido_id)
        if not venda:
            return jsonify({'erro': 'Venda não encontrada.'}), 404

        if acao == 'confirmar':
            venda.entrega_status = True
        db.session.add(venda)

        # 2. Verifica se já existe entrega registrada
        entrega = VendaEntregue.query.filter_by(venda_id=pedido_id).first()
        if entrega:
            # Atualiza os dados
            entrega.status_entrega = 'Entregue'
            entrega.observacoes = observacoes
            entrega.nome_vendedor_entrega = vendedor_nome
            entrega.data_entrega = datetime.now()
        else:
            # Cria novo registro
            entrega = VendaEntregue(
                venda_id=pedido_id,
                data_entrega=datetime.now(),
                status_entrega='Entregue',
                observacoes=observacoes,
                nome_vendedor_entrega=vendedor_nome
            )
            db.session.add(entrega)

        # Commit das operações
        db.session.commit()
        print('Entrega registrada com sucesso!')
        return jsonify({'mensagem': 'Entrega registrada com sucesso!'}), 200
        

    except Exception as e:
        db.session.rollback()
        print(f'Ocorreu um erro: {str(e)}')
        return jsonify({'erro': f'Ocorreu um erro: {str(e)}'}), 500


