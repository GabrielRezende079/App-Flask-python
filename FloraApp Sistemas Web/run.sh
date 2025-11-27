# Script simples para rodar a aplicação

#!/bin/bash

# Cria ou ativa o ambiente virtual
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

# Instala as dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Define a variável de ambiente (necessária para Flask)
export FLASK_APP=app.py

# Roda a aplicação
echo "Iniciando a API FloraTrack em http://127.0.0.1:5000"
flask run