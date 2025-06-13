
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response,session
from app import app, db
from forms import LoginForm
from models import Venda
from datetime import datetime
import pandas as pd
from io import BytesIO

@app.route('/')
def index():
    # Filtros
    filtro_vendedor = request.args.get('vendedor', '')
    filtro_comprador = request.args.get('comprador', '')
    filtro_id = request.args.get('id', '')
    
    # Query base
    query = Venda.query
    
    # Aplicar filtros
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
    
    stats = {
        'quantidade_total': quantidade_total,
        'vendas_meninos': vendas_meninos,
        'vendas_meninas': vendas_meninas,
        "vendas_igreja":vendas_igreja,
        'valor_total': valor_total_geral,
        'valor_total_pago':valor_total_pago,
        'valor_total_nao_pago':valor_total_nao_pago
    }
    
    return render_template('index.html', 
                         vendas=vendas, 
                         stats=stats,
                         filtros={
                             'vendedor': filtro_vendedor,
                             'comprador': filtro_comprador,
                             'id': filtro_id
                         })



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = form.usuario.data
        senha = form.senha.data
        if usuario == 'admin' and senha == '123':  # Exemplo simples
            session['usuario'] = usuario
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html', form=form)


@app.route('/api/vendas')
def api_vendas():
    vendedor = request.args.get('vendedor', '').strip()
    comprador = request.args.get('comprador', '').strip()
    venda_id = request.args.get('id', '').strip()

    query = Venda.query

    if venda_id:
        query = query.filter(Venda.id == venda_id)
    if vendedor:
        query = query.filter(Venda.nome_vendedor.ilike(f'%{vendedor}%'))
    if comprador:
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
            "data_venda": v.data_venda.strftime('%d/%m/%Y %H:%M'),
        })
    return jsonify(data)



@app.route('/adicionar_venda', methods=['POST'])
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




