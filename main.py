from flask import Flask, render_template
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.currencies import currencies_bp
from routes.gates import gates_bp
from routes.exchangers import exchangers_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Замените на ваш секретный ключ

# Регистрация блюпринтов
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(currencies_bp)
app.register_blueprint(gates_bp)  # Регистрация блюпринта для ворот
app.register_blueprint(exchangers_bp)  # Регистрация блюпринта для обменников

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
