import os.path
import base64
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail messages and extracts transfer amounts and sender names.
    """
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
        # Call the Gmail API to fetch INBOX messages
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return

        print("Messages:")
        with open("output.txt", "w", encoding="utf-8") as f:
            for message in messages:
                msg = service.users().messages().get(userId="me", id=message["id"]).execute()

                # Debug: Print message snippet
                snippet = msg.get('snippet', 'No snippet available')
                print(f"Message snippet: {snippet}")

                # Verifica se a mensagem tem partes
                if "parts" in msg["payload"]:
                    for part in msg["payload"]["parts"]:
                        if part["mimeType"] in ["text/plain", "text/html"]:
                            body = part["body"]["data"]
                            decoded_body = base64.urlsafe_b64decode(body).decode("utf-8")
                            
                            # Debug: Print decoded body
                            print(f"Decoded body: {decoded_body}")

                            if "Você recebeu uma transferência de" in decoded_body:
                                # Captura o nome do remetente e o valor da transferência
                                match_sender = re.search(r'Você recebeu uma transferência de ([\w\s]+)', decoded_body)
                                match_value = re.search(r'R\$ ?(\d{1,3}(?:\.\d{3})*,\d{2})', decoded_body)
                                if match_sender and match_value:
                                    sender = match_sender.group(1).strip()
                                    value = match_value.group(1)
                                    f.write(f"Transfer amount: R$ {value} from {sender}\n")
                                    print(f"Transfer amount: R$ {value} from {sender}")
                else:
                    # Caso não haja partes, verificar o corpo principal
                    body = msg["payload"]["body"]["data"]
                    decoded_body = base64.urlsafe_b64decode(body).decode("utf-8")

                    # Debug: Print decoded body
                    print(f"Decoded body: {decoded_body}")

                    if "Você recebeu uma transferência de" in decoded_body:
                        match_sender = re.search(r'Você recebeu uma transferência de ([\w\s]+)', decoded_body)
                        match_value = re.search(r'R\$ ?(\d{1,3}(?:\.\d{3})*,\d{2})', decoded_body)
                        if match_sender and match_value:
                            sender = match_sender.group(1).strip()
                            value = match_value.group(1)
                            f.write(f"Transfer amount: R$ {value} from {sender}\n")
                            print(f"Transfer amount: R$ {value} from {sender}")

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
