from db_manager import DBManager
from crypto_manager import criptografar, descriptografar
from bson import ObjectId

db = DBManager()

def menu():
    print("\n--- CHAT SEGURO ---")
    print("1 - Enviar mensagem")
    print("2 - Ler mensagens novas")
    print("0 - Sair")
    return input("Escolha: ")

def enviar():
    remetente = input("Seu @: ")
    destinatario = input("@ do destinatário: ")
    texto = input("Mensagem (50-2000 caracteres): ")
    if len(texto) < 50 or len(texto) > 2000:
        print("Tamanho inválido.")
        return
    chave = input("Chave criptográfica: ")

    msg_cifrada = criptografar(texto, chave)
    db.salvar_mensagem(remetente, destinatario, msg_cifrada)
    print("Mensagem enviada e criptografada com sucesso!")

def ler():
    destinatario = input("Seu @: ")
    msgs = db.buscar_nao_lidas(destinatario)
    if not msgs:
        print("Nenhuma nova mensagem.")
        return

    for i, msg in enumerate(msgs):
        print(f"{i + 1}. De: {msg['from']}")

    escolha = int(input("Escolha uma mensagem: ")) - 1
    selecionada = msgs[escolha]
    chave = input("Digite a chave para decifrar: ")

    try:
        texto = descriptografar(selecionada["message"], chave)
        print("\nMensagem decifrada:")
        print(texto)
        db.marcar_como_lida(selecionada["_id"])
    except Exception:
        print("Chave incorreta. Não foi possível decifrar.")

def main():
    while True:
        op = menu()
        if op == "1":
            enviar()
        elif op == "2":
            ler()
        elif op == "0":
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()
