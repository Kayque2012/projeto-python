import re
from BD import conectar_banco
from Servicos.relatorio_usuarios import gerar_relatorio_usuarios
from datetime import datetime
from Servicos.logger_utils import log_acesso

def menu_organizador(id_usuario):
    while True:
        print("\n--- MENU ORGANIZADOR ---")
        print("1 - Criar evento")
        print("2 - Ver seus participantes")
        print("3 - Apagar evento")
        print("4 - Gerar Relatório de Usuarios")
        print("5 - Sair e voltar para o menu principal")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            criar_evento(id_usuario)

        elif opcao == "2":
            ver_participantes(id_usuario)

        elif opcao == "3":
            apagar_evento(id_usuario)

        elif opcao == "4":
            gerar_relatorio_usuarios()

        elif opcao == "5":
            print("Voltando ao menu principal...")
            return

        else:
            print("Opção inválida.")

def validar_data(data):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data):
        return False
    
    # Tenta converter para objeto de data
    try:
        data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    except ValueError:
        return False  # Data inexistente (ex: 2025-02-30)
    
    if data_obj.year < 2025:
        return False
    
    return True

def criar_evento(id_organizador):
    con = conectar_banco.conectar()
    cursor = con.cursor()

    # Recupera o e-mail do organizador para o log
    cursor.execute("SELECT email FROM USUARIO WHERE id_usuario = %s", (id_organizador,))
    email_organizador = cursor.fetchone()[0]

    nome = input("\nDigite o nome do evento: ")

    # Validação da data inicial
    while True:
        data_inicio = input("Digite a data inicial do evento (formato AAAA-MM-DD): ")
        if validar_data(data_inicio):
            break
        print("Data inválida. Use o formato AAAA-MM-DD e ano igual ou posterior a 2025.")
        log_acesso(email_organizador, "Criação de Evento", "Falha: Data inválida")

    # Validação da data final
    while True:
        data_fim = input("Digite a data final do evento (formato AAAA-MM-DD): ")
        if validar_data(data_fim):
            break
        print("Data inválida. Use o formato AAAA-MM-DD e ano igual ou posterior a 2025.")
        log_acesso(email_organizador, "Criação de Evento", "Falha: Data inválida")

    try:
        sql = """
            INSERT INTO EVENTO (
                nome, data_inicio, data_fim, id_organizador
            ) VALUES (%s, %s, %s, %s)
        """
        valores = (nome, data_inicio, data_fim, id_organizador)
        cursor.execute(sql, valores)
        con.commit()
        print("\nEvento criado com sucesso!")
        log_acesso(email_organizador, "Criação de Evento", "Sucesso")

    except Exception as e:
        print(f"\nErro ao criar evento: {e}")
        log_acesso(email_organizador, "Criação de Evento", f"Falha: {str(e)}")

    finally:
        cursor.close()
        con.close()

def ver_participantes(id_organizador):
    con = conectar_banco.conectar()
    cursor = con.cursor()

    # Recupera email do organizador para log também
    cursor.execute("SELECT email FROM USUARIO WHERE id_usuario = %s", (id_organizador,))
    email_organizador = cursor.fetchone()[0]

    # Lista eventos do organizador
    cursor.execute("SELECT id_evento, nome FROM EVENTO WHERE id_organizador = %s", (id_organizador,))
    eventos = cursor.fetchall()

    if not eventos:
        print("\nVocê ainda não criou nenhum evento.")
        log_acesso(email_organizador, "Visualização de Participantes", "Falha: Nenhum evento criado")
        cursor.close()
        con.close()
        return

    print("\n--- Seus Eventos ---")
    for evento in eventos:
        print(f"{evento[0]} - {evento[1]}")

    id_evento = input("\nDigite o ID do evento que deseja ver os participantes: ")

    # Verifica se o evento pertence ao organizador
    evento_ids = [str(e[0]) for e in eventos]
    if id_evento not in evento_ids:
        print("\nEvento não encontrado ou não pertence a você.")
        log_acesso(email_organizador, "Visualização de Participantes", "Falha: Evento não encontrado")
        cursor.close()
        con.close()
        return

    # Busca participantes
    sql = """
    SELECT U.nome, U.email
    FROM INSCRICAO I
    JOIN USUARIO U ON I.id_usuario = U.id_usuario
    WHERE I.id_evento = %s
    """
    cursor.execute(sql, (id_evento,))
    participantes = cursor.fetchall()

    if participantes:
        print("\n--- Participantes Inscritos ---")
        for p in participantes:
            print(f"Nome: {p[0]}, Email: {p[1]}")
        log_acesso(email_organizador, "Visualização de Participantes", f"Sucesso: Evento {id_evento} com participantes")
    else:
        print("\nNenhum participante inscrito neste evento.")
        log_acesso(email_organizador, "Visualização de Participantes", f"Sucesso: Evento {id_evento} sem participantes")

    cursor.close()
    con.close()

def apagar_evento(id_organizador):
    con = conectar_banco.conectar()
    cursor = con.cursor()

    # Recupera o e-mail do organizador
    cursor.execute("SELECT email FROM USUARIO WHERE id_usuario = %s", (id_organizador,))
    email_organizador = cursor.fetchone()[0]

    # Lista eventos do organizador
    cursor.execute("SELECT id_evento, nome FROM EVENTO WHERE id_organizador = %s", (id_organizador,))
    eventos = cursor.fetchall()

    if not eventos:
        print("\nVocê não tem eventos para apagar.")
        log_acesso(email_organizador, "Exclusão de Evento", "Falha: Nenhum evento encontrado")
        cursor.close()
        con.close()
        return

    print("\n--- Seus Eventos ---")
    for evento in eventos:
        print(f"{evento[0]} - {evento[1]}")

    id_evento = input("\nDigite o ID do evento que deseja apagar: ")

    # Verifica se o evento pertence ao organizador
    evento_ids = [str(e[0]) for e in eventos]
    if id_evento not in evento_ids:
        print("Evento não encontrado ou sem permissão.")
        log_acesso(email_organizador, "Exclusão de Evento", "Falha: Evento não encontrado")
        cursor.close()
        con.close()
        return

    confirmacao = input("Tem certeza que deseja apagar este evento? (s/n): ").lower()
    if confirmacao != "s":
        print("Operação cancelada.")
        log_acesso(email_organizador, "Exclusão de Evento", "Cancelada")
        cursor.close()
        con.close()
        return

    try:
        # Remove inscrições e o evento
        cursor.execute("DELETE FROM INSCRICAO WHERE id_evento = %s", (id_evento,))
        cursor.execute("DELETE FROM EVENTO WHERE id_evento = %s AND id_organizador = %s", (id_evento, id_organizador))
        con.commit()
        print("\nEvento apagado com sucesso.")
        log_acesso(email_organizador, "Exclusão de Evento", "Sucesso")

    except Exception as e:
        print(f"\nErro ao apagar evento: {e}")
        log_acesso(email_organizador, "Exclusão de Evento", f"Falha: {str(e)}")

    finally:
        cursor.close()
        con.close()