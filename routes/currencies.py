from flask import Blueprint, request, render_template, jsonify
import requests
import uuid  # Для генерации UUID
from utils.headers import get_headers
from config import API_BASE_URL
from error_messages.currency_errors import (
    ADD_CURRENCY_FAILURE_REASONS,
)
from utils.log_errors import log_error

currencies_bp = Blueprint('currencies', __name__)

def get_error_message(code, reason_dict):
    """Возвращает сообщение об ошибке на основе кода."""
    return reason_dict.get(code, "Неизвестная ошибка")

@currencies_bp.route('/currencies', methods=['GET'])
def get_currencies():
    headers = get_headers()
    params = {"count": 10}  # Значение по умолчанию 10
    response = requests.get(f"{API_BASE_URL}/currencies", headers=headers, params=params)
    currencies = []

    if response.status_code == 200:
        currencies = response.json().get("currencies", [])
    else:
        log_error(f"Ошибка получения списка валют: {response.text}")

    return render_template('currencies.html', currencies=currencies)

@currencies_bp.route('/add_currency', methods=['GET', 'POST'])
def add_currency():
    if request.method == 'GET':
        return render_template('add_currency.html')

    headers = get_headers()
    if not isinstance(headers, dict):
        return headers

    currency_type = int(request.form.get("type"))

    data = {
        "name": request.form.get("name"),
        "shortName": request.form.get("shortName"),
        "type": currency_type,
        "restrictions": [int(x) for x in request.form.get("restrictions", "").split(',') if x],
        "isPopular": bool(request.form.get("isPopular")),
        "iconPath": request.form.get("iconPath"),
    }

    if currency_type == 0:  # Для криптовалют
        data["gates"] = [{
            "name": request.form.get("gate_name"),
            "exchangerDomain": request.form.get("exchangerDomain"),
            "wallets": []
        }]
        data["wallets"] = []

        wallet_data = {
            "address": request.form.get("wallet_address"),
            "tag": request.form.get("tag"),
            "memo": request.form.get("memo")
        }

        # Проверка, является ли сеть новой или существующей
        if request.form.get("networkId"):  # Существующая сеть
            wallet_data["networkId"] = request.form.get("networkId")
        elif request.form.get("network_name"):  # Новая сеть
            anchor_id = str(uuid.uuid4())
            wallet_data["networkAnchorId"] = anchor_id
            new_network = {
                "anchorId": anchor_id,
                "name": request.form.get("network_name"),
                "hasTag": bool(request.form.get("hasTag")),
                "hasMemo": bool(request.form.get("hasMemo")),
                "approvesRequired": int(request.form.get("approvesRequired", 0))
            }
            data["newNetworks"] = [new_network]
        else:
            data["newNetworks"] = []

        wallet_data = {k: v for k, v in wallet_data.items() if v}

        if wallet_data:
            data["gates"][0]["wallets"].append(wallet_data)
            data["wallets"].append(wallet_data)

        existing_ids = request.form.get("existingNetworkIds", "").split(',')
        data["existingNetworkIds"] = [eid.strip() for eid in existing_ids if eid.strip()]

    # Логирование данных, отправляемых на сервер
    log_error(f"Отправка запроса на сервер: {data}")

    response = requests.put(f"{API_BASE_URL}/currencies/add", json=data, headers=headers)

    if response.status_code == 200:
        return jsonify({"message": "Валюта успешно добавлена"})
    else:
        try:
            error_code = response.json().get("errorCode", 0)
            error_message = get_error_message(error_code, ADD_CURRENCY_FAILURE_REASONS)
        except (ValueError, AttributeError):
            error_message = "Ошибка сервера, получен невалидный ответ"
        log_error(f"Ошибка добавления валюты: {error_message}")
        return jsonify({"error": error_message, "details": response.text}), response.status_code
