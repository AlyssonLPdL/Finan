import datetime
from flask import Flask, render_template, request, redirect, jsonify, send_file
import sqlite3
import io
import openpyxl
from openpyxl import Workbook
import os
from io import BytesIO

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configuração inicial do banco de dados
def init_db():
    with sqlite3.connect('finance.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                quantia NUMERIC NOT NULL,
                description TEXT NOT NULL,
                value REAL NOT NULL,
                payment_method TEXT NOT NULL,
                type TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date = request.form['date']
        quantia = request.form['quantia']
        description = request.form['description']
        value = float(request.form['value'])
        payment_method = request.form['payment_method']
        type_ = request.form['type']

        if not date:
            date = datetime.today().strftime('%Y-%m-%d')  # Formato YYYY-MM-DD

        parcelas = request.form.get('parcelas')  # Pega o valor de parcelas
        if parcelas:
            parcelas = int(parcelas)
        else:
            parcelas = 1  # Valor padrão para parcelas se não for fornecido

        # Se o método de pagamento for Crédito, adicionar a informação das parcelas na descrição
        if payment_method in ['Credito_nu', 'Credito_c6']:
            description = f"{description} - x{parcelas}"

        # Se a quantia não for fornecida, usa o valor padrão de 1
        if not quantia:
            quantia = 1  # Valor padrão para quantia

        with sqlite3.connect('finance.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (date, quantia, description, value, payment_method, type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (date, quantia, description, value, payment_method, type_))
            conn.commit()

        return redirect('/')

    search_query = request.args.get('search', '')  # Captura a busca inteligente
    month_year_filter = request.args.get('month_year')  # Captura o filtro de mês (se houver)
    payment_filter = request.args.get('payment_method', '')  # Pega o filtro da URL
    tipe_filter = request.args.get('type', '')
    payment_methods = ["Pix", "Dinheiro", "Credito_c6", "Credito_nu"]
    tipos = ["Gasto", "Ganho"]

    query = "SELECT * FROM transactions WHERE 1=1"  # Consulta base
    params = []

    if payment_filter:
        query += " AND payment_method = ?"
        params.append(payment_filter)
        
    if month_year_filter:
        query += " AND strftime('%Y-%m', date) = ?"
        params.append(month_year_filter)

    if tipe_filter:
        query += " AND type = ?"
        params.append(tipe_filter)

    # Implementação da busca inteligente
    if search_query:
        if search_query.startswith('>'):
            try:
                value = float(search_query[1:])  # Captura o valor após o `>`
                query += ' AND value > ?'
                params.append(value)
            except ValueError:
                pass  # Ignorar se não for um número válido
        elif search_query.startswith('<'):
            try:
                value = float(search_query[1:])  # Captura o valor após o `<`
                query += ' AND value < ?'
                params.append(value)
            except ValueError:
                pass  # Ignorar se não for um número válido
        else:
            # Busca em outros campos: descrição, data, método de pagamento
            query += '''
                AND (description LIKE ? OR 
                     date LIKE ? OR 
                     payment_method LIKE ? OR 
                     CAST(value AS TEXT) LIKE ?)
            '''
            search_term = f'%{search_query}%'  # Termo genérico
            params.extend([search_term, search_term, search_term, search_term])

    query += ' ORDER BY date'

    with sqlite3.connect('finance.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        transactions = cursor.fetchall()

        # Obter todos os meses únicos disponíveis
        cursor.execute("SELECT DISTINCT strftime('%Y-%m', date) as month_year FROM transactions ORDER BY month_year")
        months_years = [row[0] for row in cursor.fetchall()]

    return render_template('index.html', transactions=transactions, months_years=months_years, month_year_filter=month_year_filter, payment_filter=payment_filter, payment_methods=payment_methods, tipos=tipos, tipe_filter=tipe_filter)

@app.route('/generate_excel', methods=['GET'])
def generate_excel():
    # Conectar ao banco de dados e obter as transações
    with sqlite3.connect('finance.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, quantia, description, value, payment_method, type FROM transactions")
        transactions = cursor.fetchall()

    # Criar um arquivo Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Transações"

    # Cabeçalho da planilha
    ws.append(["ID", "Data", "Quantia", "Descrição", "Valor", "Método de Pagamento", "Tipo"])

    # Adicionar os dados das transações
    for transaction in transactions:
        ws.append(transaction)

    # Salvar a planilha em memória (em vez de salvar fisicamente)
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # Enviar a planilha para o cliente
    return send_file(output, as_attachment=True, download_name="transacoes.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def save_excel_to_db(file_path):
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    
    with sqlite3.connect('finance.db') as conn:
        cursor = conn.cursor()
        for row in ws.iter_rows(min_row=2, values_only=True):
            # Truncar para as primeiras 6 colunas
            row = row[:6]

            # Validar se a linha tem valores válidos
            if None in row or len(row) < 6:
                print(f"Erro na linha: {row} - Dados incompletos ou inválidos.")
                continue

            try:
                cursor.execute('''
                    INSERT INTO transactions (date, quantia, description, value, payment_method, type)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', row)
            except Exception as e:
                print(f"Erro ao inserir: {row} - {e}")

        conn.commit()

# Rota para upload da planilha
@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    file = request.files['file']
    if file and file.filename.endswith('.xlsx'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Salvar os dados da planilha no banco
        save_excel_to_db(file_path)
        
        # Redirecionar para a página inicial após o upload
        return redirect('/')

    return "Arquivo inválido. Por favor, envie um arquivo .xlsx."

# Rota para baixar a planilha de exemplo
@app.route('/download_example')
def download_example():
    # Criar um arquivo de exemplo
    wb = Workbook()
    ws = wb.active
    ws.title = "Transações Exemplo"
    
    # Cabeçalho da planilha
    ws.append(["ID", "Data", "Quantia", "Descrição", "Valor", "Método de Pagamento", "Tipo"])
    
    # Dados de exemplo
    ws.append([1, "2023-01-01", 100, "Exemplo de Descrição", 50.5, "Pix", "Gasto"])
    
    # Salvar o arquivo em memória
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return send_file(output, as_attachment=True, download_name="exemplo_transacoes.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.route('/download_relatorio')
def download_relatorio():
    # Conectando ao banco de dados
    with sqlite3.connect('finance.db') as conn:
        cursor = conn.cursor()

        # Consulta para obter os meses e anos e os totais por método de pagamento
        query = '''
            SELECT strftime('%Y-%m', date) AS month_year,
                   SUM(CASE WHEN payment_method = 'Pix' THEN value ELSE 0 END) AS pix_total,
                   SUM(CASE WHEN payment_method = 'Dinheiro' THEN value ELSE 0 END) AS dinheiro_total,
                   SUM(CASE WHEN payment_method = 'Credito_nu' THEN value ELSE 0 END) AS cartao_nu_total,
                   SUM(CASE WHEN payment_method = 'Credito_c6' THEN value ELSE 0 END) AS cartao_c6_total
            FROM transactions
            WHERE type = 'Gasto'
            GROUP BY month_year
            ORDER BY month_year
        '''
        cursor.execute(query)
        rows = cursor.fetchall()

    # Criando a planilha
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Relatório Financeiro"

    # Cabeçalhos
    headers = ["Data (Mês/Ano)", "Pix", "Dinheiro", "Cartão Nu", "Cartão C6"]
    sheet.append(headers)

    # Adicionando os dados ao Excel
    for row in rows:
        sheet.append(row)

    # Ajustando a largura das colunas
    for column in sheet.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value)
        column_letter = column[0].column_letter
        sheet.column_dimensions[column_letter].width = max_length + 2

    # Salvando a planilha em um buffer
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Enviando o arquivo para download
    return send_file(
        buffer,
        as_attachment=True,
        download_name="relatorio_financeiro.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route('/delete/<int:id>', methods=['POST'])
def delete_transaction(id):
    with sqlite3.connect('finance.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE id = ?', (id,))
        conn.commit()
    return jsonify({'success': True})

@app.route('/get_transaction/<int:id>', methods=['GET'])
def get_transaction(id):
    with sqlite3.connect('finance.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE id = ?', (id,))
        transaction = cursor.fetchone()
    return jsonify(transaction)

@app.route('/edit/<int:id>', methods=['POST'])
def edit_transaction(id):
    data = request.json
    with sqlite3.connect('finance.db') as conn: 
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE transactions
            SET date = ?, quantia =?, description = ?, value = ?, payment_method = ?, type = ?
            WHERE id = ?
        ''', (data['date'], data['quantia'], data['description'], data['value'], data['payment_method'], data['type'], id))
        conn.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
