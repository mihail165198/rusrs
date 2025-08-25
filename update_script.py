import requests
import zipfile
import io
import os
from datetime import datetime

# URL последней версии архива
ZIP_URL = "https://github.com/runetfreedom/russia-v2ray-rules-dat/releases/latest/download/sing-box.zip"
# Путь к нужному файлу внутри архива
TARGET_FILE = "rule-set-geosite/geosite-ru-blocked-all.srs"
OUTPUT_FILE = "geosite-ru-blocked-all.srs"  # Итоговый файл

def update_file():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Начало обновления...")
    
    try:
        # Скачать архив
        print("Скачивание архива...")
        response = requests.get(ZIP_URL, timeout=30)
        response.raise_for_status()
        print("Архив успешно скачан")

        # Извлечь нужный файл
        print("Извлечение файла из архива...")
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            # Проверить наличие файла
            if TARGET_FILE not in zip_ref.namelist():
                available_files = [f for f in zip_ref.namelist() if 'geosite' in f.lower()]
                print(f"Файл {TARGET_FILE} не найден в архиве!")
                print(f"Доступные geosite файлы: {available_files}")
                return False
            
            # Извлечь файл
            with zip_ref.open(TARGET_FILE) as source_file:
                content = source_file.read()
            
            # Сохранить файл
            with open(OUTPUT_FILE, "wb") as f:
                f.write(content)
            
            file_size = len(content) / 1024  # Размер в KB
            print(f"Файл {OUTPUT_FILE} успешно обновлен! Размер: {file_size:.2f} KB")
            return True

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при скачивании архива: {e}")
    except zipfile.BadZipFile:
        print("Ошибка: архив поврежден или не является ZIP-файлом")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    
    return False

if __name__ == "__main__":
    update_file()