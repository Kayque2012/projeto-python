import os
import re
import time
import random
import string
from BD import conectar_banco
from Servicos.logger_utils import log_acesso


def validar_nome(nome):
    return all(c.isalpha() or c.isspace() for c in nome)


def validar_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+",email)

    
def validar_senha_forte(senha):
    criterios = [
        len(senha) >= 8,
        re.search(r"[A-Za-z]", senha) is not None,
        re.search(r"\d", senha) is not None,
        re.search(r"[!@#$%^&*()_+{}\[\]:;<>,.?/~]", senha) is not None
    ]
    return all(criterios)


def gerar_credencial():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def validar_chave(chave_inserida):
    if not os.path.exists("chave.txt"):
        print("Erro: Arquivo de chave não encontrado. Inicie o gerador primeiro.")
        return False

    with open("chave.txt", "r") as arquivo:
        chave_correta = arquivo.read().strip()
        return chave_inserida.upper() == chave_correta


def cadastrar():
    print("\n--- CADASTRO DE USUÁRIO ---")
    credencial = gerar_credencial()
    con = conectar_banco.conectar()
    cursor = con.cursor()

    while True:
        nome = input("\nNome do usuário: ").strip()
        if not validar_nome(nome):
            print("\nNome inválido! Use apenas letras (sem números ou símbolos).")
            log_acesso("Sistema", "Validação de nome", "Falha - Nome inválido")
        else:
            break

    while True:
        email = input("\nEmail do usuário: ").strip()
        if not validar_email(email):
            print("\nFormato de email inválido. Ex: nome@exemplo.com")
            log_acesso(email, "Validação de email", "Falha - Formato inválido")
            continue

        cursor.execute("SELECT * FROM USUARIO WHERE email = %s", (email,))

        if cursor.fetchone():
            print("\nJá existe um usuário com esse E-mail. Tente outro!")
            log_acesso(email, "Validação de email", "Falha - Email já existe")
        else:
            break

    while True:
        senha = input("\nSenha (mínimo 8 caracteres, letras, números e símbolos): ").strip()

        if not validar_senha_forte(senha):
            print("\nA senha não atende aos critérios! Tente novamente.")
            log_acesso(email, "Validação de senha", "Falha - Senha fraca")
        else:
            break

    tipo = ""
    while tipo not in ["Organizador", "Participante"]:
        tipo = input("\nTipo (Organizador/Participante): ").strip().capitalize()
        if tipo not in ["Organizador", "Participante"]:
            print("\nTipo Inválido! Digite Organizador ou Participante.")
            log_acesso(email, "Validação de tipo", "Falha - Tipo inválido")

    if tipo == "Organizador":
        while True:
            chave_usuario = input("\nDigite a chave temporária: ").strip()
            
            if validar_chave(chave_usuario):
                print("\nAcesso concedido! Bem-vindo!")
                print(f"Sua chave de acesso é: {credencial}")
                log_acesso(email, "Validação de chave organizador", "Sucesso")
                break
            else:
                print("\nChave inválida. Tente novamente.")
                log_acesso(email, "Validação de chave organizador", "Falha - Chave inválida")
                time.sleep(1)  # Evita sobrecarga do loop           
    
    elif tipo == "Participante":
        print("\nAcesso concedido! Bem-vindo!")
        print(f"Sua Credencial é: {credencial}")
        log_acesso(email, "Cadastro participante", "Sucesso")

    try:
        # tratamento de erro
        with con.cursor() as cursor:
            cursor.execute("""
                INSERT INTO USUARIO (nome, email, senha, tipo_usuario, credencial)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, email, senha, tipo, credencial))
        con.commit()
        log_acesso(email, "Cadastro de Usuário", "Sucesso")
    except Exception as e:
        print(f"\nErro ao cadastrar usuário: {e}")
        log_acesso(email, "Cadastro de Usuário", f"Falha - {str(e)}")
    finally:
        con.close()


def atualizar_porId():
    con = conectar_banco.conectar()
    cursor = con.cursor()

    id_usuario = int(input("\nDigite o ID do usuário que deseja atualizar: "))

    select = "SELECT * FROM USUARIO WHERE id_usuario = %s"
    
    cursor.execute(select, (id_usuario,))
    resultado = cursor.fetchone()

    if resultado is None:
        print("\nNenhum usuário encontrado com esse ID. Tente novamente.")
        log_acesso("Sistema", f"Atualização usuário ID {id_usuario}", "Falha - Usuário não encontrado")
        cursor.close()
        con.close()
        return

    email_atual = resultado[2]

    while True:
        novo_nome = input("\nDigite o novo nome: ").strip()
        if not validar_nome(novo_nome):
            print("Nome inválido!Use apenas letras(sem números ou símbolos).")
            log_acesso(email_atual, "Validação nome atualização", "Falha - Nome inválido")
        else:
            break

    while True:
        novo_email = input("\nDigite o novo email: ").strip()
        if not validar_email(novo_email):
            print("Formato de email inválido. Ex: nome@exemplo.com")
            log_acesso(email_atual, "Validação email atualização", "Falha - Formato inválido")
            continue

        if novo_email == resultado[2]:
            break

        cursor.execute("SELECT * FROM USUARIO WHERE email = %s", (novo_email,))
        if cursor.fetchone():
            print("\nJá existe um usuário com esse E-mail. Tente outro!")
            log_acesso(email_atual, "Validação email atualização", "Falha - Email já existe")
        else:
            break

    nova_senha = input("\nDigite a nova senha: ").strip()
    novo_tipo = input("\nDigite o novo tipo do usuário(Organizador ou Participante): ").strip().capitalize()

    try:
        # tratamento de erro
        sql = "UPDATE USUARIO SET nome = %s, email = %s, senha = %s, tipo_usuario = %s WHERE id_usuario = %s"
        valores = (novo_nome, novo_email, nova_senha, novo_tipo, id_usuario)
        cursor.execute(sql, valores)
        con.commit()
        print("\nUsuário Atualizado com Sucesso!")
        log_acesso(novo_email, f"Atualização usuário ID {id_usuario}", "Sucesso")
    except Exception as e:
        print(f"\nErro ao atualizar usuário: {e}")
        log_acesso(email_atual, f"Atualização usuário ID {id_usuario}", f"Falha - {str(e)}")
    finally:
        cursor.close()
        con.close()


def deletar_porId():
    con = conectar_banco.conectar()
    cursor = con.cursor()

    id_usuario = int(input("\nDigite o ID do usuário que deseja deletar: "))

    select = "SELECT * FROM USUARIO WHERE id_usuario = %s"
    cursor.execute(select, (id_usuario,))
    resultado = cursor.fetchone()

    if resultado is None:
        print("\nNenhum usuário encontrado com esse ID. Tente novamente.")
        log_acesso("Sistema", f"Exclusão usuário ID {id_usuario}", "Falha - Usuário não encontrado")
        cursor.close()
        con.close()
        return

    email_usuario = resultado[2]

    try:
        # Operação crítica que precisa de tratamento de erro
        sql = "DELETE FROM USUARIO WHERE id_usuario = %s"
        valores = (id_usuario,)
        cursor.execute(sql, valores)
        con.commit()
        print("\nUsuário Deletado com Sucesso!")
        log_acesso(email_usuario, f"Exclusão usuário ID {id_usuario}", "Sucesso")
    except Exception as e:
        print(f"\nErro ao deletar usuário: {e}")
        log_acesso(email_usuario, f"Exclusão usuário ID {id_usuario}", f"Falha - {str(e)}")
    finally:
        cursor.close()
        con.close()


def listar():
    con = conectar_banco.conectar()
    cursor = con.cursor()

    sql = "SELECT nome, id_usuario FROM USUARIO"
    cursor.execute(sql)
    USUARIO = cursor.fetchall()

    if USUARIO:
        print("\nUsuários Cadastrados: ")
        for usuario in USUARIO:
            print(usuario)
        log_acesso("Sistema", "Listagem de usuários", "Sucesso")
    else:
        print("\nNenhum Usuário Encontrado")
        log_acesso("Sistema", "Listagem de usuários", "Falha - Nenhum usuário encontrado")

    cursor.close()
    con.close()
