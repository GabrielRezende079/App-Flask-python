# python app.py - Arquivo principal da aplicação Flask

from flask import Flask, request, jsonify
from flask_cors import CORS  
from tinydb import TinyDB, Query
from datetime import datetime
import uuid
import os

app = Flask(__name__) # Inicializa a aplicação Flask
CORS(app)  # Habilita CORS para permitir requisições de diferentes origens

# Inicializa o TinyDB no arquivo db.json
db = TinyDB('db.json')

# Cria ou acessa a tabela 'plantas'
Plantas = db.table('plantas')

# Cria um objeto Query para buscas eficientes
PlantasQuery = Query()

# --- Simulação de Configuração AWS  ---

# Usaria esta variáveis para enviar mensagens ao SQS na AWS
# Por enquanto, o envio de mensagem será apenas um print.
SQS_QUEUE_URL = os.environ.get('SQS_URL', 'SQS_URL_MOCKADA') 




# --- Funções de Serviço ---

def enviar_mensagem_sqs(planta_id):
    """Simula o envio de uma mensagem para o SQS (na vida real usaria boto3)."""
    print(f"\n[SQS MOCK] Enviando notificação para processamento da Planta ID: {planta_id}")
    print(f"[SQS MOCK] Mensagem enviada para a fila: {SQS_QUEUE_URL}")
    # Quando migrar para AWS, substitua por:
    # sqs_client = boto3.client('sqs')
    # sqs_client.send_message(...)


# --- Rotas CRUD ---

@app.route('/api/plantas', methods=['POST'])
def criar_planta():
    """Cria uma nova planta no inventário."""
    dados = request.get_json()
    
    if not dados or 'nome_comum' not in dados:
        return jsonify({"erro": "O campo 'nome_comum' é obrigatório"}), 400

    # Adiciona campos de controle
    dados['id'] = str(uuid.uuid4())
    dados['data_criacao'] = datetime.now().isoformat()
    
    # Inserir no TinyDB
    Plantas.insert(dados)
    
    # Simular o envio de tarefa para processamento assíncrono
    enviar_mensagem_sqs(dados['id'])
    
    return jsonify({
        "mensagem": "Planta adicionada e processamento assíncrono iniciado", 
        "planta": dados
    }), 201


@app.route('/api/plantas', methods=['GET'])
def listar_plantas():
    """Retorna todas as plantas no inventário."""
    todas_plantas = Plantas.all()
    
    return jsonify(todas_plantas), 200


@app.route('/api/plantas/<string:planta_id>', methods=['GET'])
def buscar_planta(planta_id):
    """Retorna os detalhes de uma planta específica."""
    
    # Busca pelo campo 'id'
    planta = Plantas.search(PlantasQuery.id == planta_id)
    
    if not planta:
        return jsonify({"erro": f"Planta com ID {planta_id} não encontrada"}), 404
    
    return jsonify(planta[0]), 200


@app.route('/api/plantas/<string:planta_id>', methods=['PUT'])
def atualizar_planta(planta_id):
    """Atualiza os dados de uma planta existente."""
    novos_dados = request.get_json()
    
    if not novos_dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização"}), 400
        
    # Remove a chave 'id' e 'data_criacao' para evitar que sejam alteradas
    novos_dados.pop('id', None)
    novos_dados.pop('data_criacao', None)
        
    # Adiciona a data de atualização
    novos_dados['data_atualizacao'] = datetime.now().isoformat()
        
    # Atualiza o documento
    num_atualizados = Plantas.update(novos_dados, PlantasQuery.id == planta_id)
    
    if num_atualizados == 0:
        return jsonify({"erro": f"Planta com ID {planta_id} não encontrada"}), 404
    
    # Retorna o item atualizado
    planta_atualizada = Plantas.search(PlantasQuery.id == planta_id)[0]
    
    return jsonify({
        "mensagem": "Planta atualizada com sucesso", 
        "planta": planta_atualizada
    }), 200


@app.route('/api/plantas/<string:planta_id>', methods=['DELETE'])
def deletar_planta(planta_id):
    """Remove uma planta do inventário."""
    
    # Remove o documento
    num_removidos = Plantas.remove(PlantasQuery.id == planta_id)
    
    if num_removidos == 0:
        return jsonify({"erro": f"Planta com ID {planta_id} não encontrada"}), 404
        
    return jsonify({"mensagem": "Planta removida com sucesso"}), 204

# --- Início da Aplicação ---
if __name__ == '__main__':
    # Usar debug=True é ideal para desenvolvimento
    app.run(debug=True, port=5000)