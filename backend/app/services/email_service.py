# vaveforgepro/backend/app/services/email_service.py

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import current_app

def send_password_reset_email(to_email, reset_link):
    """
    Wysyła e-mail z linkiem do resetowania hasła przy użyciu SendGrid.
    Zawiera szczegółowe logowanie do debugowania.
    """
    # ====================================================================
    # PAMIĘTAJ, ABY ZMIENIĆ PONIŻSZY ADRES NA TEN, KTÓRY
    # ZOSTAŁ ZWERYFIKOWANY W PANELU SENDGRID (STATUS "VERIFIED")
    # ====================================================================
    from_email = 'marcin.lugowski@learnetic.com'

    # Tworzymy treść wiadomości w HTML
    html_content = f"""
    <html>
    <body>
        <h2>Resetowanie hasła w WaveBulk</h2>
        <p>Otrzymaliśmy prośbę o zresetowanie Twojego hasła. Kliknij w poniższy link, aby ustawić nowe hasło:</p>
        <p><a href="{reset_link}" style="padding: 10px 15px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px;">Zresetuj hasło</a></p>
        <p>Jeśli to nie Ty prosiłeś o zmianę hasła, zignoruj tę wiadomość.</p>
        <p>Link jest ważny przez 1 godzinę.</p>
        <br>
        <p>Pozdrawiamy,</p>
        <p>Zespół WaveBulk</p>
    </body>
    </html>
    """

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject='[WaveBulk] Resetowanie hasła',
        html_content=html_content
    )

    try:
        # Pobieramy klucz API ze zmiennych środowiskowych
        api_key = current_app.config.get('SENDGRID_API_KEY') or os.environ.get('SENDGRID_API_KEY')
        if not api_key:
            print("!!! BŁĄD KRYTYCZNY: Klucz SENDGRID_API_KEY nie jest ustawiony w .env !!!")
            current_app.logger.error("Klucz API SendGrid nie został ustawiony.")
            return False

        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        # Logowanie diagnostyczne udanej odpowiedzi
        print(f"--- DEBUG: Odpowiedź z SendGrid ---")
        print(f"Status Code: {response.status_code}")
        print(f"Body: {response.body}")
        print(f"Headers: {response.headers}")
        print("---------------------------------")
        
        current_app.logger.info(f"Wysłano e-mail do {to_email}. Status: {response.status_code}")
        return response.status_code == 202

    except Exception as e:
        # Logowanie diagnostyczne błędu
        print("\n!!! WYSTĄPIŁ KRYTYCZNY BŁĄD PODCZAS WYSYŁKI E-MAILA !!!\n")
        print(f"Typ błędu: {type(e)}")
        print(f"Treść błędu: {e}")
        
        # Błędy API SendGrid często mają dodatkowe, cenne informacje w atrybucie 'body'
        if hasattr(e, 'body'):
            print(f"\nSzczegóły z API (body): {e.body}\n")

        current_app.logger.error(f"Nie udało się wysłać e-maila przez SendGrid: {e}")
        return False