from BD import conectar_banco
from Usuarios import menu_organizador
from Usuarios import menu_participante

def login():
    con = conectar_banco.conectar()
    cursor = con.cursor()

    email = input("\nDigite o seu E-mail: ")
    senha = input("Digite a sua senha: ")
    credencial = input("Digite sua credencial: ")

    sql = """
        SELECT id_usuario, nome, tipo_usuario 
        FROM USUARIO 
        WHERE email = %s AND senha = %s AND credencial = %s
    """
    cursor.execute(sql, (email, senha, credencial))
    usuario = cursor.fetchone()

    if usuario:
        id_usuario, nome, tipo_usuario = usuario

        if tipo_usuario == "organizador":
        
            print(f"\nBem-vindo(a), {nome}!")
            menu_organizador.menu_organizador(id_usuario)

        elif tipo_usuario == "participante":
            print(f"\nBem-vindo(a),{nome}!")
            menu_participante.menu_participante(id_usuario)
    
    else:
        print("Entradas Inválidas!")


    cursor.close()
    con.close()