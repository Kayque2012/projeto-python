import logging
import os

# Pega o caminho da raiz do projeto
root_path = os.path.dirname(os.path.dirname(__file__))  # sobe duas pastas
log_path = os.path.join(root_path, 'Log')  # cria caminho para a pasta Log

# Cria a pasta Log se não existir
os.makedirs(log_path, exist_ok=True)

# Configuração do logger
logging.basicConfig(
    filename=os.path.join(log_path, 'app.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    encoding='utf-8'
)

def log_acesso(usuario, acao, status):
    logging.info(f'Usuário: {usuario} | Ação: {acao} | Status: {status}')