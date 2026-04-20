import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailService:
    @staticmethod
    def enviar_email(destinatario, assunto, corpo):
        # Configurações (Use variáveis de ambiente para segurança!)
        remetente = "seu_email@gmail.com"
        senha = "sua_senha_de_app"

        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo, 'plain'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(remetente, senha)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Falha ao enviar e-mail: {e}")
            return False