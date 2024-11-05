from utils.token_manager import load_token
from flask import redirect, url_for

def get_headers():
    token = load_token()
    if not token:
        return redirect(url_for('auth.login_page'))
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
