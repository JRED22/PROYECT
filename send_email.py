from flask_mail import Message
from app import mail

def send_confirmation_email(email, username, confirmation_code):
    msg = Message('Confirmación de Registro', recipients=[email])
    msg.html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Confirmación de Registro</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: auto;
                background: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                color: #333;
            }}
            p {{
                font-size: 16px;
                line-height: 1.5;
                color: #555;
            }}
            .code {{
                font-weight: bold;
                font-size: 20px;
                color: #007BFF;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hola {username},</h1>
            <p>Tu código de confirmación es: <span class="code">{confirmation_code}</span></p>
            <p>Por favor, ingresa este código en la aplicación para confirmar tu registro.</p>
        </div>
    </body>
    </html>
    """
    mail.send(msg)