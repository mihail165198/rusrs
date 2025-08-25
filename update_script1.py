import requests
import zipfile
import io
import os
from datetime import datetime

# URL последней версии архива
ZIP_URL = "https://github.com/runetfreedom/russia-v2ray-rules-dat/releases/latest/download/sing-box.zip"
# Пути к нужным файлам внутри архива
TARGET_FILES = [
    "rule-set-geosite/geosite-ru-blocked-all.srs",
    "rule-set-geosite/geosite-category-speedtest.srs"
]
OUTPUT_FILES = [
    "geosite-ru-blocked-all.srs",
    "geosite-category-speedtest.srs"
]

def update_files():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Начало обновления...")
    
    try:
        # Скачать архив
        print("Скачивание архива...")
        response = requests.get(ZIP_URL, timeout=30)
        response.raise_for_status()
        print("Архив успешно скачан")

        # Получить список файлов в архиве
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            archive_files = zip_ref.namelist()
            print(f"Файлов в архиве: {len(archive_files)}")
            
            # Извлечь каждый целевой файл
            success_count = 0
            for i, target_file in enumerate(TARGET_FILES):
                output_file = OUTPUT_FILES[i]
                
                print(f"\nОбработка файла: {target_file}")
                
                # Проверить наличие файла
                if target_file not in archive_files:
                    available_files = [f for f in archive_files if target_file.split('/')[-1].split('.')[0] in f.lower()]
                    print(f"Файл {target_file} не найден в архиве!")
                    print(f"Похожие файлы: {available_files}")
                    continue
                
                # Извлечь файл
                try:
                    with zip_ref.open(target_file) as source_file:
                        content = source_file.read()
                    
                    # Сохранить файл
                    with open(output_file, "wb") as f:
                        f.write(content)
                    
                    file_size = len(content) / 1024  # Размер в KB
                    print(f"Файл {output_file} успешно сохранен! Размер: {file_size:.2f} KB")
                    success_count += 1
                    
                except Exception as e:
                    print(f"Ошибка при обработке файла {target_file}: {e}")
            
            # Вывести итоги
            print(f"\n{'='*50}")
            print(f"ИТОГ: Успешно обработано {success_count} из {len(TARGET_FILES)} файлов")
            
            if success_count > 0:
                print("Обновленные файлы:")
                for output_file in OUTPUT_FILES:
                    if os.path.exists(output_file):
                        file_size = os.path.getsize(output_file) / 1024
                        print(f"  - {output_file} ({file_size:.2f} KB)")
            
            return success_count > 0

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при скачивании архива: {e}")
    except zipfile.BadZipFile:
        print("Ошибка: архив поврежден или не является ZIP-файлом")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    
    return False

if __name__ == "__main__":
    update_files()
