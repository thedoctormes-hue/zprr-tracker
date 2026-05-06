#!/usr/bin/env python3
"""
fedlab.ru Parser — БЕЗОПАСНЫЙ вариант (без учётных данных в коде)
"""
import os, sys, getpass, requests, json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def get_credentials():
    """Безопасный ввод учётных данных"""
    email = os.getenv('FEDLAB_EMAIL') or input("Email: ")
    password = os.getenv('FEDLAB_PASSWORD') or getpass.getpass("Password: ")
    return email, password

def login_session(email: str, password: str):
    """Создаёт авторизованную сессию"""
    session = requests.Session()
    
    # Получаем страницу логина (CSRF токен и т.д.)
    login_page = session.get('https://fedlab.ru/login')
    
    # Вводим данные
    payload = {
        'email': email,
        'password': password,
        # Добавь остальные поля формы
    }
    
    response = session.post('https://fedlab.ru/login', data=payload)
    
    if 'logout' in response.text.lower() or response.status_code == 200:
        return session
    raise ValueError("Ошибка авторизации")

def parse_events(session):
    """Парсит мероприятия"""
    response = session.get('https://fedlab.ru/events')
    # TODO: парсинг
    return []

if __name__ == "__main__":
    try:
        email, password = get_credentials()
        session = login_session(email, password)
        print("✅ Авторизация успешна")
        events = parse_events(session)
        print(f"📊 Найдено {len(events)} мероприятий")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)