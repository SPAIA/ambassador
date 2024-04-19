import secrets

def generate_token():
    return secrets.token_urlsafe(32)

def create_env_file():
    token = generate_token()
    with open('.env', 'w') as file:
        file.write(f'API_TOKEN={token}\n')

create_env_file()
