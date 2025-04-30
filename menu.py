from Usuarios import User_CRUD
from Usuarios import login_page

def menu():
    while True:
        print("\n--- MENU PRINCIPAL ---")
        print("1 - Cadastrar Usuário")
        print("2 - Fazer Login")
        print("3 - Atualizar Usuário")
        print("4 - Deletar Usuário")
        print("5 - Listar Usuários")
        print("6 - Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            User_CRUD.cadastrar()
        elif opcao == "2":
            login_page.login()
        elif opcao == "3":
            User_CRUD.atualizar_porId()
        elif opcao == "4":
            User_CRUD.deletar_porId()
        elif opcao == "5":
            User_CRUD.listar()
        elif opcao == "6":
            print("\nSaindo...")
            break
        else:
            print("\nOpção inválida!")

if __name__ == "__main__":
    menu()