from BD import conectar_banco
from Servicos.logger_utils import log_acesso

def menu_participante(id_usuario):
    while True:
        print("\n--- MENU PARTICIPANTE ---")
        print("1 - Ver eventos")
        print("2 - Inscrever-se em evento")
        print("3 - Sair e voltar para o menu principal")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            ver_eventos(id_usuario)

        elif opcao == "2":
            inscrever_em_evento(id_usuario)

        elif opcao == "3":
            print("Voltando ao menu principal...")
            return

        else:
            print("Opção inválida.")

def ver_eventos(id_usuario):
    con = conectar_banco.conectar()
    cursor = con.cursor()

    # Recupera email do participante
    cursor.execute("SELECT email FROM USUARIO WHERE id_usuario = %s", (id_usuario,))
    email = cursor.fetchone()[0]

    cursor.execute("SELECT id_evento, nome, data_inicio FROM EVENTO")
    eventos = cursor.fetchall()

    if eventos:
        print("\n--- Eventos Disponíveis ---")
        for evento in eventos:
            print(f"\nID: {evento[0]}")
            print(f"Nome: {evento[1]}")
            print(f"Data: {evento[2]}")
        log_acesso(email, "Visualização de Eventos", "Sucesso")
    else:
        print("\nNenhum evento cadastrado.")
        log_acesso(email, "Visualização de Eventos", "Nenhum evento encontrado")

    cursor.close()
    con.close()

def inscrever_em_evento(id_usuario):
    con = conectar_banco.conectar()
    cursor = con.cursor()

    # Recupera email do participante também
    cursor.execute("SELECT email FROM USUARIO WHERE id_usuario = %s", (id_usuario,))
    email = cursor.fetchone()[0]

    ver_eventos(id_usuario)
    
    id_evento = input("\nDigite o ID do evento que deseja se inscrever: ")

    # Verifica existência do evento
    cursor.execute("SELECT * FROM EVENTO WHERE id_evento = %s", (id_evento,))
    evento = cursor.fetchone()

    if not evento:
        print("\nEsse evento não existe. Tente novamente com um ID válido.")
        log_acesso(email, "Inscrição em Evento", "Falha: Evento não encontrado")
        cursor.close()
        con.close()
        return

    # Verifica inscrição existente
    cursor.execute("SELECT * FROM INSCRICAO WHERE id_usuario = %s AND id_evento = %s", 
                 (id_usuario, id_evento))
    inscricao_existente = cursor.fetchone()

    if inscricao_existente:
        print("\nVocê já está inscrito nesse evento.")
        log_acesso(email, "Inscrição em Evento", "Falha: Inscrição duplicada")
        cursor.close()
        con.close()
        return

    try:
        cursor.execute("INSERT INTO INSCRICAO (id_usuario, id_evento) VALUES (%s, %s)", 
                      (id_usuario, id_evento))
        con.commit()
        print("\nInscrição realizada com sucesso!")
        log_acesso(email, "Inscrição em Evento", f"Sucesso: Evento {id_evento}")

    except Exception as e:
        print(f"\nErro na inscrição: {e}")
        log_acesso(email, "Inscrição em Evento", f"Erro: {str(e)}")

    finally:
        cursor.close()
        con.close()