from flask import Blueprint, request, jsonify, render_template
import requests
import os

exchangers_bp = Blueprint('exchangers', __name__)

BASE_URL = 'https://admin.crypto-team.ru/api/v1'
TOKEN_FILE = 'token.txt'

def get_token():
    """Загружает токен из файла."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as file:
            return file.read().strip()
    return None

@exchangers_bp.route('/exchangers', methods=['GET'])
def get_exchangers():
    token = get_token()
    if not token:
        return jsonify({"error": "Не удалось получить токен"}), 401

    url = f"{BASE_URL}/exchangers"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        exchangers_domains = response.json().get('exchangerDomains', [])
        exchangers_status = {}

        # Получаем статус для каждого обменника
        for domain in exchangers_domains:
            status_response = requests.get(f"{BASE_URL}/status/site?exchangerDomain={domain}", headers=headers)
            if status_response.status_code == 200:
                exchangers_status[domain] = status_response.json().get('status', 'Unknown')

        return render_template('exchangers.html', exchangers=exchangers_domains, statuses=exchangers_status)
    else:
        return jsonify({"error": "Ошибка получения обменников", "details": response.text}), response.status_code

@exchangers_bp.route('/exchangers/status/update', methods=['POST'])
def update_status():
    token = get_token()
    if not token:
        return jsonify({"error": "Не удалось получить токен"}), 401

    exchanger_domain = request.form.get('exchangerDomain')
    new_status = request.form.get('newStatus')

    if not exchanger_domain or new_status is None:
        return jsonify({"error": "Не указаны все необходимые параметры"}), 400

    url = f"{BASE_URL}/status/site"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "exchangerDomain": exchanger_domain,
        "newStatus": int(new_status)  # Убедитесь, что newStatus является целым числом
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        return jsonify({"message": "Статус обменника успешно обновлен!"})
    else:
        return jsonify({"error": "Ошибка обновления статуса", "details": response.text}), response.status_code
