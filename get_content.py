import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64

# Se modificar esses escopos, exclua o arquivo token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_message_content(msg):
    """Extrai o conteúdo do e-mail, lidando com diferentes formatos."""
    payload = msg['payload']
    
    if 'parts' in payload:
        # Se a mensagem tem partes, procura pela parte de texto simples
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    else:
        # Se não tem partes, tenta extrair o texto simples diretamente do corpo
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    return None

def main():
    """Busca e imprime o conteúdo de e-mails com títulos específicos."""
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
            content = get_message_content(msg)
            if content:
                print(f"Message content:\n{content}\n{'-'*40}")

    except HttpError as error:
        print(f"Ocorreu um erro: {error}")

if __name__ == "__main__":
    main()
