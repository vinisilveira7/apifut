import os.path
import re
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup

# Se modificar esses escopos, exclua o arquivo token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_message_content(msg):
    """Extrai o conteúdo HTML do e-mail, preservando tags e formatação."""
    payload = msg['payload']
    
    if 'parts' in payload:
        # Se a mensagem tem partes, procura pela parte HTML
        for part in payload['parts']:
            if part['mimeType'] == 'text/html':
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    else:
        # Se não tem partes, tenta extrair o conteúdo diretamente do corpo
        if payload['mimeType'] == 'text/html':
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    return None

def extract_info_from_html(html_content):
    """Extrai informações específicas do HTML do e-mail usando BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extrair nome do remetente
    sender_name_div = soup.find_all(string=lambda x: x and 'Você recebeu uma transferência de' in x)
    
    if sender_name_div:
        for text in sender_name_div:
            # Verifica o texto onde o nome do remetente está
            sender_info = text.split('Você recebeu uma transferência de ')[-1]
            sender_name = sender_info.split(' e ')[0]
            return sender_name
        
    return "Não encontrado"

def extract_value_from_html(html_content):
    """Extrai o valor do HTML do e-mail usando BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')
    value_div = soup.find_all(string=lambda x: x and 'R$' in x)
    if value_div:
        return value_div[0].strip()
    return "Não encontrado"

def extract_date_time_from_html(html_content):
    """Extrai a data e hora do HTML do e-mail usando BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')
    date_div = soup.find_all(string=lambda x: x and 'às' in x)
    if date_div:
        return date_div[0].strip()
    return "Não encontrado"

def main():
    """Busca e imprime o conteúdo HTML dos e-mails com títulos específicos e extrai informações."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Chama a API do Gmail para buscar mensagens na INBOX
        service = build("gmail", "v1", credentials=creds)
        query = 'subject:"Você recebeu uma transferência!" OR subject:"Você recebeu uma transferência pelo PIX!"'
        results = service.users().messages().list(userId="me", q=query).execute()
        messages = results.get("messages", [])

        if not messages:
            print("Nenhuma mensagem encontrada.")
            return

        for message in messages:
            msg = service.users().messages().get(userId="me", id=message["id"], format='full').execute()
            snippet = msg['snippet']
            html_content = get_message_content(msg)
            
            # Extrair informações do snippet
            pattern = r'transferência(?: pelo Pix)? de (.*?) e o valor'
            match = re.search(pattern, snippet)
            
            if match:
                nome_remetente = match.group(1)  # Captura o nome do remetente
                print(f"Nome do remetente: {nome_remetente}")
            else:
                print("Nome do remetente (do snippet): Não encontrado")

            # Extrair informações do conteúdo HTML
            if html_content:
                sender_name = extract_info_from_html(html_content)
                value = extract_value_from_html(html_content)
                date_time = extract_date_time_from_html(html_content)
                print(f"Nome do remetente (do HTML): {sender_name}")
                print(f"Valor: {value}")
                print(f"Data e Hora: {date_time}")
                print('-' * 40)

    except HttpError as error:
        print(f"Ocorreu um erro: {error}")

if __name__ == "__main__":
    main()







# import os.path
# import re
# import base64
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from bs4 import BeautifulSoup

# # Se modificar esses escopos, exclua o arquivo token.json.
# SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# def get_message_content(msg):
#     """Extrai o conteúdo HTML do e-mail, preservando tags e formatação."""
#     payload = msg['payload']
    
#     if 'parts' in payload:
#         # Se a mensagem tem partes, procura pela parte HTML
#         for part in payload['parts']:
#             if part['mimeType'] == 'text/html':
#                 return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
#     else:
#         # Se não tem partes, tenta extrair o conteúdo diretamente do corpo
#         if payload['mimeType'] == 'text/html':
#             return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
#     return None

# def extract_info_from_html(html_content):
#     """Extrai informações específicas do HTML do e-mail usando BeautifulSoup."""
#     soup = BeautifulSoup(html_content, 'html.parser')
    
#     # Debug: imprimir o HTML completo para verificar a estrutura
#     # print("HTML completo do e-mail:")
#     # print(html_content)
    
#     # Extrair nome do remetente
#     sender_name_div = soup.find_all(text=lambda x: x and 'Você recebeu uma transferência de' in x)
    
#     if sender_name_div:
#         for text in sender_name_div:
#             # Verifica o texto onde o nome do remetente está
#             sender_info = text.split('Você recebeu uma transferência de ')[-1]
#             sender_name = sender_info.split(' e ')[0]
#             return sender_name
        
#     return "Não encontrado"

# def extract_value_from_html(html_content):
#     """Extrai o valor do HTML do e-mail usando BeautifulSoup."""
#     soup = BeautifulSoup(html_content, 'html.parser')
#     value_div = soup.find_all(text=lambda x: x and 'R$' in x)
#     if value_div:
#         return value_div[0].strip()
#     return "Não encontrado"

# def extract_date_time_from_html(html_content):
#     """Extrai a data e hora do HTML do e-mail usando BeautifulSoup."""
#     soup = BeautifulSoup(html_content, 'html.parser')
#     date_div = soup.find_all(text=lambda x: x and 'às' in x)
#     if date_div:
#         return date_div[0].strip()
#     return "Não encontrado"

# def main():
#     """Busca e imprime o conteúdo HTML dos e-mails com títulos específicos e extrai informações."""
#     creds = None
#     if os.path.exists("token.json"):
#         creds = Credentials.from_authorized_user_file("token.json", SCOPES)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 "credentials.json", SCOPES)
#             creds = flow.run_local_server(port=0)
#         with open("token.json", "w") as token:
#             token.write(creds.to_json())

#     try:
#         # Chama a API do Gmail para buscar mensagens na INBOX
#         service = build("gmail", "v1", credentials=creds)
#         query = 'subject:"Você recebeu uma transferência!" OR subject:"Você recebeu uma transferência pelo PIX!"'
#         results = service.users().messages().list(userId="me", q=query).execute()
#         messages = results.get("messages", [])

#         if not messages:
#             print("Nenhuma mensagem encontrada.")
#             return

#         for message in messages:
#             msg = service.users().messages().get(userId="me", id=message["id"], format='full').execute()
#             snippet = msg['snippet']
#             html_content = get_message_content(msg)
            
#             # Extrair informações do snippet
#             pattern = r'transferência(?: pelo Pix)? de (.*?) e o valor'
#             match = re.search(pattern, snippet)
            
#             if match:
#                 nome_remetente = match.group(1)  # Captura o nome do remetente
#                 print(f"Nome do remetente: {nome_remetente}")
#             else:
#                 print("Nome do remetente (do snippet): Não encontrado")

#             # Extrair informações do conteúdo HTML
#             if html_content:
#                 sender_name = extract_info_from_html(html_content)
#                 value = extract_value_from_html(html_content)
#                 date_time = extract_date_time_from_html(html_content)
#                 # print(f"Nome do remetente (do HTML): {sender_name}")
#                 print(f"Valor: {value}")
#                 print(f"Data e Hora: {date_time}")
#                 print('-' * 40)

#     except HttpError as error:
#         print(f"Ocorreu um erro: {error}")

# if __name__ == "__main__":
#     main()
