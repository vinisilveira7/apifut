import os.path
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Se modificar esses escopos, exclua o arquivo token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def main():
    """Busca emails cujos títulos contenham frases específicas."""
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
            msg = service.users().messages().get(userId="me", id=message["id"]).execute()
            snippet = msg['snippet']

            # Expressão regular para capturar o nome do remetente
            pattern = r'transferência(?: pelo Pix)? de (.*?) e o valor'
            match = re.search(pattern, snippet)
            
            if match:
                nome_remetente = match.group(1)  # Captura o nome do remetente
                print(f"Nome do remetente: {nome_remetente}")
            else:
                print("Nome do remetente não encontrado")

    except HttpError as error:
        print(f"Ocorreu um erro: {error}")

if __name__ == "__main__":
    main()
