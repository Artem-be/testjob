import requests
from django.shortcuts import render, redirect
import logging
import uuid
import urllib.parse
import os
# Ваши Client ID и Client Secret
CLIENT_ID = '61e7dbc41ed44e849d62dc82ff328f8c'
CLIENT_SECRET = '2c875637ce68436099912d38ecde406b'
REDIRECT_URI = 'http://127.0.0.1:8000/oauth/callback/'  # Убедитесь, что этот URI соответствует настройкам вашего приложения

# Настройка логгирования
logger = logging.getLogger(__name__)


def home(request):
    public_key = request.GET.get('public_key')

    if public_key:
        files = []
        response = requests.get(f'https://cloud-api.yandex.net/v1/disk/public/resources?public_key={public_key}')

        if response.status_code == 200:
            data = response.json()
            items = data.get('_embedded', {}).get('items', [])

            for item in items:
                if item['type'] == 'file':
                    files.append({
                        'name': item['name'],
                        'download_link': item['file']  # Ссылка для скачивания
                    })

        else:
            return render(request, 'home.html', {'error': 'Не удалось получить файлы. Проверьте публичный ключ.'})

        return render(request, 'home.html', {'files': files})

    return render(request, 'home.html')

def index(request):
    public_key = request.GET.get('public_key')

    if public_key:
        files = []
        response = requests.get(f'https://cloud-api.yandex.net/v1/disk/public/resources?public_key={public_key}')

        if response.status_code == 200:
            data = response.json()
            items = data.get('_embedded', {}).get('items', [])

            for item in items:
                if item['type'] == 'file':
                    files.append({
                        'name': item['name'],
                        'download_link': item['file']  # Ссылка для скачивания
                    })

        else:
            return render(request, 'index.html', {'error': 'Не удалось получить файлы. Проверьте публичный ключ.'})

        return render(request, 'index.html', {'files': files})

    return render(request, 'index.html')


def download_file(request):
    file_url = request.GET.get('file_url')

    if file_url:
        try:
            # Добавляем заголовок для аутентификации, если требуется
            headers = {
                'Authorization': 'OAuth <ваш_токен_авторизации>'  # Замените на ваш OAuth токен
            }

            response = requests.get(file_url, headers=headers)
            response.raise_for_status()  # Вызывает HTTPError для плохих ответов
            filename = file_url.split('/')[-1]  # Сохраним файл с его именем
            with open(filename, 'wb') as f:
                f.write(response.content)

            return render(request, 'download_success.html', {'filename': filename})

        except requests.exceptions.HTTPError as http_err:
            return render(request, 'download_error.html', {'error': f'HTTP ошибка: {http_err}'})
        except Exception as err:
            return render(request, 'download_error.html', {'error': f'Произошла ошибка: {err}'})

    return render(request, 'download_error.html', {'error': 'URL файла не найден.'})


def oauth_register(request):
    state = uuid.uuid4().hex  # Generate a unique state value
    request.session['oauth_state'] = state  # Store the state value in the session

    auth_url = f"https://oauth.yandex.ru/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state={state}"
    return redirect(auth_url)


def oauth_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    if state != request.session.get('oauth_state'):
        # State mismatch, invalidate the authorization code
        return render(request, 'error.html', {'error': 'Invalid state'})

    # Exchange the authorization code for an access token
    token_url = "https://oauth.yandex.ru/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        # Save the access token to the session or database
        request.session['access_token'] = access_token
        # Redirect to the main page with the access token
        return redirect('home')
    else:
        return render(request, 'error.html', {'error': 'Error exchanging code for token'})