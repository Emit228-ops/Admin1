from flask import Blueprint, request, jsonify, render_template, redirect, url_for
import requests
import os

gates_bp = Blueprint('gates', __name__)

BASE_URL = 'https://admin.crypto-team.ru/api/v1'
TOKEN_FILE = 'token.txt'

def get_token():
    """Загружает токен из файла."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as file:
            return file.read().strip()
    return None

@gates_bp.route('/gates/add', methods=['GET', 'POST'])
def add_gate():
    token = get_token()
    gates = []

    if request.method == 'POST':
        if not token:
            return jsonify({"error": "Не удалось получить токен"}), 401

        data = {
            "name": request.form['name'],
            "exchangerDomain": request.form['exchangerDomain'],
            "wallets": [
                {
                    "address": request.form['address'],
                    "currencyId": request.form['currencyId'],
                    "networkId": request.form['networkId'],
                    "tag": request.form['tag'],
                    "memo": request.form['memo']
                }
            ]
        }

        url = f"{BASE_URL}/gates/add"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.put(url, headers=headers, json=data)

        if response.status_code == 200:
            return jsonify({"message": "Ворота успешно добавлены!", "data": response.json()})
        else:
            return jsonify({"error": "Ошибка добавления ворот", "details": response.text}), response.status_code
    else:
        # Возврат формы для добавления ворот
        if token:
            # Получаем существующие ворота
            url = f"{BASE_URL}/gates"
            headers = {
                "Authorization": f"Bearer {token}"
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                gates = response.json().get('gates', [])

        return render_template('add_gate.html', gates=gates)

@gates_bp.route('/gates/delete', methods=['POST'])
def delete_gate():
    token = get_token()
    if not token:
        return jsonify({"error": "Не удалось получить токен"}), 401

    gate_id = request.form.get('id')
    if not gate_id:
        return jsonify({"error": "ID ворот не указан"}), 400

    url = f"{BASE_URL}/gates/delete?id={gate_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        return redirect(url_for('gates.add_gate'))  # Перенаправление на страницу добавления ворот
    else:
        return jsonify({"error": "Ошибка удаления ворот", "details": response.text}), response.status_code

@gates_bp.route('/gates', methods=['GET'])
def get_gates():
    token = get_token()
    if not token:
        return jsonify({"error": "Не удалось получить токен"}), 401

    url = f"{BASE_URL}/gates"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Ошибка получения ворот", "details": response.text}), response.status_code
