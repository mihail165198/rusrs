import requests
import re
from datetime import datetime

def get_latest_release_file():
    # API для получения последнего релиза
    API_URL = "https://api.github.com/repos/runetfreedom/russia-blocked-geosite/releases/latest"
    OUTPUT_FILE = "blocked-russia.lst"
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Поиск последнего релиза...")
    
    try:
        # Получаем информацию о последнем релизе
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        release_info = response.json()
        
        # Ищем файл ru-blocked-all.txt в активах релиза
        download_url = None
        for asset in release_info.get('assets', []):
            if asset['name'] == 'ru-blocked.txt':
                download_url = asset['browser_download_url']
                break
        
        if not download_url:
            print("Файл ru-blocked.txt не найден в релизе!")
            return False
        
        print(f"Найден релиз: {release_info['tag_name']}")
        print(f"Скачивание: {download_url}")
        
        # Скачиваем файл
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()
        
        # Обрабатываем содержимое
        content = response.text
        lines = content.split('\n')
        
        # Фильтруем и очищаем записи
        cleaned_entries = set()
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('#', '!', '//')) and not line.isspace():
                # Убираем возможные префиксы
                if ':' in line:
                    line = line.split(':', 1)[1].strip()
                if ' ' in line:
                    line = line.split(' ', 1)[0].strip()
                cleaned_entries.add(line)
        
        # Сохраняем в .lst формат
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for entry in sorted(cleaned_entries):
                f.write(entry + '\n')
        
        print(f"Готово! Обработано записей: {len(cleaned_entries)}")
        print(f"Файл сохранен: {OUTPUT_FILE}")
        
        return True
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

if __name__ == "__main__":
    get_latest_release_file()
