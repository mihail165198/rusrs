import requests
import zipfile
import io
import os
from datetime import datetime

# URL последней версии архива
ZIP_URL = "https://github.com/runetfreedom/russia-v2ray-rules-dat/releases/latest/download/sing-box.zip"

# Пути к нужным файлам внутри архива и их выходные имена
TARGET_FILES = {
    "rule-set-geoip/geoip-ru-blocked.srs": "geoip-ru-blocked.srs",
    "rule-set-geoip/geoip-ru-blocked-community.srs": "geoip-ru-blocked-community.srs", 
    "rule-set-geosite/geosite-ru-blocked-all.srs": "geosite-ru-blocked-all.srs",
    "rule-set-geosite/geosite-category-speedtest.srs": "geosite-speedtest.srs",
    "rule-set-geosite/geosite-twitch.srs": "geosite-twitch.srs"
}

def update_files():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Начало обновления файлов...")
    print(f"Репозиторий: https://github.com/mihail165198/rusrs")
    print("=" * 60)
    
    try:
        # Скачать архив
        print("📦 Скачивание архива...")
        response = requests.get(ZIP_URL, timeout=30)
        response.raise_for_status()
        print("✅ Архив успешно скачан")

        # Получить список файлов в архиве
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            archive_files = zip_ref.namelist()
            print(f"📁 Файлов в архиве: {len(archive_files)}")
            
            success_count = 0
            total_size = 0
            
            # Извлечь каждый целевой файл
            for target_path, output_file in TARGET_FILES.items():
                print(f"\n🔍 Обработка: {target_path} -> {output_file}")
                
                # Проверить наличие файла
                if target_path not in archive_files:
                    # Поиск похожих файлов
                    filename = target_path.split('/')[-1]
                    similar_files = [f for f in archive_files if filename in f]
                    print(f"❌ Файл не найден в архиве!")
                    if similar_files:
                        print(f"   Похожие файлы: {similar_files}")
                    continue
                
                # Извлечь файл
                try:
                    with zip_ref.open(target_path) as source_file:
                        content = source_file.read()
                    
                    # Сохранить файл
                    with open(output_file, "wb") as f:
                        f.write(content)
                    
                    file_size_kb = len(content) / 1024
                    total_size += file_size_kb
                    print(f"✅ Успешно сохранен! Размер: {file_size_kb:.2f} KB")
                    success_count += 1
                    
                except Exception as e:
                    print(f"❌ Ошибка при обработке: {e}")
            
            # Вывести итоги
            print(f"\n{'='*60}")
            print(f"📊 ИТОГ: Успешно обработано {success_count} из {len(TARGET_FILES)} файлов")
            print(f"💾 Общий размер: {total_size:.2f} KB")
            
            if success_count > 0:
                print("\n📋 Обновленные файлы:")
                for output_file in TARGET_FILES.values():
                    if os.path.exists(output_file):
                        file_size = os.path.getsize(output_file) / 1024
                        print(f"   - {output_file} ({file_size:.2f} KB)")
            
            # Ссылки для скачивания
            print(f"\n🌐 Прямые ссылки для скачивания:")
            for output_file in TARGET_FILES.values():
                if os.path.exists(output_file):
                    download_url = f"https://raw.githubusercontent.com/mihail165198/rusrs/main/{output_file}"
                    print(f"   - {download_url}")
            
            return success_count > 0

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при скачивании архива: {e}")
    except zipfile.BadZipFile:
        print("❌ Ошибка: архив поврежден или не является ZIP-файлом")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
    
    return False

if __name__ == "__main__":
    success = update_files()
    exit(0 if success else 1)
