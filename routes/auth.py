from flask import Blueprint, request, jsonify, redirect, url_for, render_template
import requests
from utils.token_manager import save_token
from config import API_BASE_URL
from utils.log_errors import log_error

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        login_data = {
            "login": request.form['login'],
            "password": request.form['password']
        }
        response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get("token")
            save_token(token)
            return redirect(url_for('home'))
        else:
            log_error(f"Ошибка авторизации: {response.text}")
            return jsonify({"error": "Не удалось выполнить вход", "details": response.text}), 401
    return render_template('login.html')
