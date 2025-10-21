import getpass # Para esconder a senha/chave no terminal
from database import DatabaseManager
import crypto
import sys

def show_menu():
    """Exibe o menu principal."""
    print("\n--- Chat Seguro (Mensageria) ---")
    print("1. Enviar mensagem")
    print("2. Ler mensagens novas")
    print("0. Sair")
    return input("Escolha uma opção: ")

def send_message_flow(db_manager: DatabaseManager, current_user: str):
    """Fluxo de envio de mensagem."""
    recipient = input("Digite o @ do destinatário: ")
    
    # Validação do tamanho da mensagem
    message = ""
    while not (50 <= len(message) <= 2000):
        message = input("Digite a mensagem (mínimo 50, máximo 2000 caracteres):\n")
        if not (50 <= len(message) <= 2000):
            print(f"Erro: Sua mensagem tem {len(message)} caracteres. "
                  "Deve ter entre 50 e 2000.")
            
    # Solicita a chave (senha) de forma segura
    password = getpass.getpass("Digite a chave criptográfica (combinada verbalmente): ")
    
    try:
        # Criptografa
        encrypted_token = crypto.encrypt(message, password)
        
        # Envia para o banco
        db_manager.send_message(
            sender=current_user,
            recipient=recipient,
            encrypted_message=encrypted_token
        )
        
    except Exception as e:
        print(f"Ocorreu um erro ao enviar a mensagem: {e}")

def read_messages_flow(db_manager: DatabaseManager, current_user: str):
    """Fluxo de leitura de mensagens."""
    messages = db_manager.get_unread_messages(current_user)
    
    if not messages:
        print("Você não tem mensagens novas.")
        return

    print("--- Suas Mensagens Não Lidas ---")
    for i, msg in enumerate(messages):
        # Exibe apenas o remetente, como solicitado
        print(f"[{i + 1}] De: {msg['sender']} (em {msg['timestamp'].strftime('%Y-%m-%d %H:%M')})")
    
    try:
        choice_str = input("\nEscolha uma mensagem para ler (ou 0 para voltar): ")
        choice = int(choice_str)
        
        if choice == 0 or choice > len(messages):
            return
            
        # Pega a mensagem escolhida
        selected_msg = messages[choice - 1]
        
        # Solicita a chave para esta mensagem
        password = getpass.getpass("Digite a chave criptográfica da mensagem: ")
        
        # Tenta descriptografar
        # O token é o campo 'message' que está em binário (BSON) no banco
        encrypted_token = selected_msg['message']
        decrypted_message = crypto.decrypt(encrypted_token, password)
        
        if decrypted_message:
            print("\n" + "="*20)
            print(f"MENSAGEM DE: {selected_msg['sender']}")
            print("-" * 20)
            print(decrypted_message)
            print("=" * 20)
            
            # Atualiza o status no banco
            db_manager.mark_message_as_read(selected_msg['_id'])
        else:
            print("\n[ERRO] Chave criptográfica incorreta. A descriptografia falhou.")
            
    except ValueError:
        print("Opção inválida. Digite um número.")
    except Exception as e:
        print(f"Ocorreu um erro ao ler a mensagem: {e}")

def main():
    """Função principal da aplicação."""
    try:
        # 1. Inicializa o gerenciador do banco
        db = DatabaseManager()
    except Exception as e:
        print("Falha crítica ao iniciar o banco de dados. Saindo.")
        sys.exit(1)

    # Simulação de login (já que não há cadastro)
    print("\nUsuários de exemplo no sistema: @alice, @bob, @charlie")
    current_user = input("Digite seu @ para 'logar': ")
    print(f"Bem-vindo, {current_user}!")

    # Loop principal da aplicação
    while True:
        choice = show_menu()
        
        if choice == '1':
            send_message_flow(db, current_user)
        elif choice == '2':
            read_messages_flow(db, current_user)
        elif choice == '0':
            db.close_connection()
            print("Saindo do Chat Seguro. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()