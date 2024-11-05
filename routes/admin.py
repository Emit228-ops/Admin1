from flask import Blueprint, request, jsonify, render_template
import requests
from utils.headers import get_headers
from config import API_BASE_URL
from error_messages.admin_errors import ADD_ADMIN_FAILURE_REASONS, DELETE_ADMIN_FAILURE_REASONS
from utils.log_errors import log_error

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_panel')
def admin_panel():
    headers = get_headers()
    if not isinstance(headers, dict):
        return headers

    params = {
        "count": request.args.get('count', 10),
        "position": request.args.get('position', 0),
        "filter": request.args.get('filter', '')
    }
    response = requests.get(f"{API_BASE_URL}/admins", params=params, headers=headers)
    admins = []

    if response.status_code == 200:
        admins = response.json().get("admins", [])
    else:
        log_error(f"Ошибка получения списка администраторов: {response.text}")

    return render_template('admin_panel.html', admins=admins)

@admin_bp.route('/add_admin', methods=['GET', 'POST'])
def add_admin():
    if request.method == 'GET':
        return render_template('add_admin.html')

    headers = get_headers()
    if not isinstance(headers, dict):
        return headers

    allowed_domains = request.form.get('allowed_domains', '').split(',')
    data = {
        "login": request.form['login'],
        "permissions": int(request.form['permissions']),
        "allowedExchangerDomains": [domain.strip() for domain in allowed_domains if domain.strip()]
    }
    response = requests.post(f"{API_BASE_URL}/admins/addAdmin", json=data, headers=headers)

    if response.status_code == 200:
        return jsonify({"message": "Администратор добавлен", "temp_password": response.json().get("temporalPassword")})

    try:
        error_code = response.json().get("errorCode", 0)
        error_message = ADD_ADMIN_FAILURE_REASONS.get(error_code, "Неизвестная ошибка")
    except (ValueError, AttributeError):
        error_message = "Ошибка сервера, получен невалидный ответ"

    log_error(f"Ошибка добавления администратора: {error_message}")
    return jsonify({"error": error_message, "details": response.text}), response.status_code

@admin_bp.route('/delete_admin', methods=['POST'])
def delete_admin():
    headers = get_headers()
    if not isinstance(headers, dict):
        return headers

    admin_id = request.form.get('id')
    response = requests.delete(f"{API_BASE_URL}/admins/admin", params={"id": admin_id}, headers=headers)
    if response.status_code == 200:
        return jsonify({"message": "Администратор удален"})

    try:
        error_code = response.json().get("errorCode", 0)
        error_message = DELETE_ADMIN_FAILURE_REASONS.get(error_code, "Неизвестная ошибка")
    except (ValueError, AttributeError):
        error_message = "Ошибка сервера, получен невалидный ответ"

    log_error(f"Ошибка удаления администратора: {error_message}")
    return jsonify({"error": error_message, "details": response.text}), response.status_code
