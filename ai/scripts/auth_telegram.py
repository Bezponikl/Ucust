import os
import sys
import asyncio

def update_env(api_id, api_hash):
    env_paths = ['ai/.env', '.env', '/opt/ucust/ai/.env']
    for ep in env_paths:
        if os.path.exists(ep):
            try:
                with open(ep, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                new_lines = []
                for line in lines:
                    if line.startswith('TELETHON_API_ID='):
                        new_lines.append(f'TELETHON_API_ID={api_id}\n')
                    elif line.startswith('TELETHON_API_HASH='):
                        new_lines.append(f'TELETHON_API_HASH={api_hash}\n')
                    elif line.startswith('TELEGRAM_API_ID='):
                        new_lines.append(f'TELEGRAM_API_ID={api_id}\n')
                    elif line.startswith('TELEGRAM_API_HASH='):
                        new_lines.append(f'TELEGRAM_API_HASH={api_hash}\n')
                    else:
                        new_lines.append(line)
                with open(ep, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                print(f'Файл {ep} успешно обновлен с новыми ключами!')
            except Exception as e:
                print(f'Ошибка обновления {ep}: {e}')

async def main():
    print('=== АВТОРИЗАЦИЯ TELEGRAM (TELETHON) ДЛЯ UCUST ===')
    
    api_id_input = input('Введите TELEGRAM API ID (с my.telegram.org): ').strip()
    api_hash_input = input('Введите TELEGRAM API HASH: ').strip()
    phone_input = input('Введите номер телефона (например +79991234567): ').strip()

    if not api_id_input or not api_hash_input:
        print('Ошибка: API ID и API Hash обязательны.')
        return

    update_env(api_id_input, api_hash_input)

    try:
        from telethon import TelegramClient
    except ImportError:
        print('Установка telethon...')
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'telethon'], check=True)
        from telethon import TelegramClient

    session_path = os.getenv('TELETHON_SESSION', 'ucust_session')
    client = TelegramClient(session_path, int(api_id_input), api_hash_input)

    print(f'\nПодключение к Telegram для номера {phone_input}...')
    await client.start(phone=phone_input)

    if await client.is_user_authorized():
        me = await client.get_me()
        uname = me.username or 'без юзернейма'
        print(f'\nУСПЕШНО! Авторизован как: {me.first_name} (@{uname})')
        print(f'Сессия сохранена в {session_path}.session')
    else:
        print('Не удалось авторизоваться.')

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
