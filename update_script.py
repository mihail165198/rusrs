#!/usr/bin/env python3
"""
Скрипт для полного обновления файлов из sing-box архива
Гарантирует обновление всех указанных файлов
"""

import requests
import zipfile
import io
import os
import shutil
import time
from datetime import datetime

# Конфигурация
ZIP_URL = "https://github.com/runetfreedom/russia-v2ray-rules-dat/releases/latest/download/sing-box.zip"
MAX_RETRIES = 3
RETRY_DELAY = 5

# Все файлы для обновления
FILES_TO_UPDATE = {
    # GeoIP файлы
    "rule-set-geoip/geoip-ru-blocked.srs": "geoip-ru-blocked.srs",
    "rule-set-geoip/geoip-ru-blocked-community.srs": "geoip-ru-blocked-community.srs",
    
    # Geosite файлы
    "rule-set-geosite/geosite-ru-blocked-all.srs": "geosite-ru-blocked-all.srs",
    "rule-set-geosite/geosite-category-ads-all.srs": "geosite-category-ads-all.srs",
    "rule-set-geosite/geosite-twitch.srs": "geosite-twitch.srs",
    "rule-set-geosite/geosite-discord.srs": "geosite-discord.srs",
    "rule-set-geosite/geosite-steam.srs": "geosite-steam.srs",
    "rule-set-geosite/geosite-amazon.srs": "geosite-amazon.srs",
    "rule-set-geosite/geosite-speedtest.srs": "geosite-speedtest.srs",
    "rule-set-geosite/geosite-google.srs": "geosite-google.srs",
    "rule-set-geosite/geosite-aws.srs": "geosite-aws.srs",  # Новый файл
    "rule-set-geosite/geosite-azure.srs": "geosite-azure.srs"  # Новый файл
}

def log_message(message, level="INFO"):
    """Логирование сообщений с временными метками"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def ensure_directory(directory):
    """Создает директорию если она не существует"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        log_message(f"Создана директория: {directory}")

def download_archive_with_retry():
    """Скачивает архив с повторными попытками"""
    for attempt in range(MAX_RETRIES):
        try:
            log_message(f"Попытка скачивания архива ({attempt + 1}/{MAX_RETRIES})...")
            response = requests.get(ZIP_URL, timeout=30)
            response.raise_for_status()
            log_message("Архив успешно скачан")
            return response.content
        except requests.exceptions.RequestException as e:
            log_message(f"Ошибка скачивания: {e}", "WARNING")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                log_message("Не удалось скачать архив после всех попыток", "ERROR")
                raise

def get_archive_files(zip_content):
    """Получает список файлов в архиве"""
    try:
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_ref:
            return zip_ref.namelist()
    except zipfile.BadZipFile:
        log_message("Архив поврежден или не является ZIP-файлом", "ERROR")
        raise

def extract_single_file(zip_content, archive_path, output_path):
    """Извлекает один файл из архива"""
    try:
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_ref:
            with zip_ref.open(archive_path) as source_file:
                content = source_file.read()
        
        with open(output_path, "wb") as f:
            f.write(content)
        
        file_size_kb = len(content) / 1024
        log_message(f"Файл {output_path} успешно извлечен ({file_size_kb:.1f} KB)")
        return True
        
    except Exception as e:
        log_message(f"Ошибка извлечения {archive_path}: {e}", "ERROR")
        return False

def backup_existing_files():
    """Создает backup существующих файлов"""
    backup_dir = "old"
    ensure_directory(backup_dir)
    
    backed_up_files = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for output_file in FILES_TO_UPDATE.values():
        if os.path.exists(output_file):
            backup_name = f"{output_file}.{timestamp}.bak"
            backup_path = os.path.join(backup_dir, backup_name)
            
            try:
                shutil.move(output_file, backup_path)
                backed_up_files.append((output_file, backup_name))
                log_message(f"Создан backup: {output_file} -> old/{backup_name}")
            except Exception as e:
                log_message(f"Ошибка создания backup для {output_file}: {e}", "ERROR")
    
    return backed_up_files

def cleanup_old_backups():
    """Очищает старые backup файлы"""
    backup_dir = "old"
    if not os.path.exists(backup_dir):
        return 0
    
    try:
        # Оставляем последние 3 backup для каждого файла
        all_backups = {}
        for filename in os.listdir(backup_dir):
            if filename.endswith('.bak'):
                base_name = '.'.join(filename.split('.')[:-2])  # Убираем timestamp и .bak
                if base_name in FILES_TO_UPDATE.values():
                    file_path = os.path.join(backup_dir, filename)
                    all_backups.setdefault(base_name, []).append((filename, os.path.getmtime(file_path)))
        
        deleted_count = 0
        for base_name, backups in all_backups.items():
            # Сортируем по времени (сначала старые)
            backups.sort(key=lambda x: x[1])
            # Удаляем все кроме последних 3
            for filename, _ in backups[:-3]:
                file_path = os.path.join(backup_dir, filename)
                os.remove(file_path)
                deleted_count += 1
                log_message(f"Удален старый backup: old/{filename}")
        
        return deleted_count
        
    except Exception as e:
        log_message(f"Ошибка очистки backup: {e}", "WARNING")
        return 0

def update_all_files():
    """Основная функция обновления всех файлов"""
    log_message("=" * 60)
    log_message("НАЧАЛО ОБНОВЛЕНИЯ ФАЙЛОВ")
    log_message("=" * 60)
    
    # Шаг 1: Backup существующих файлов
    log_message("Создание backup существующих файлов...")
    backed_up_files = backup_existing_files()
    log_message(f"Создано backup: {len(backed_up_files)} файлов")
    
    # Шаг 2: Скачивание архива
    log_message("Скачивание архива...")
    try:
        zip_content = download_archive_with_retry()
    except Exception as e:
        log_message("Не удалось продолжить без архива", "ERROR")
        return False
    
    # Шаг 3: Получение списка файлов в архиве
    log_message("Анализ архива...")
    try:
        archive_files = get_archive_files(zip_content)
        log_message(f"Найдено файлов в архиве: {len(archive_files)}")
    except Exception as e:
        log_message("Не удалось проанализировать архив", "ERROR")
        return False
    
    # Шаг 4: Извлечение всех файлов
    log_message("Извлечение файлов...")
    success_count = 0
    failed_files = []
    
    for archive_path, output_file in FILES_TO_UPDATE.items():
        if archive_path in archive_files:
            if extract_single_file(zip_content, archive_path, output_file):
                success_count += 1
            else:
                failed_files.append(archive_path)
        else:
            log_message(f"Файл не найден в архиве: {archive_path}", "WARNING")
            failed_files.append(archive_path)
    
    # Шаг 5: Очистка старых backup
    log_message("Очистка старых backup...")
    deleted_backups = cleanup_old_backups()
    if deleted_backups > 0:
        log_message(f"Удалено старых backup: {deleted_backups}")
    
    # Шаг 6: Итоги
    log_message("=" * 60)
    log_message("ИТОГИ ОБНОВЛЕНИЯ")
    log_message("=" * 60)
    log_message(f"Успешно обновлено: {success_count}/{len(FILES_TO_UPDATE)} файлов")
    
    if success_count > 0:
        log_message("Обновленные файлы:")
        for output_file in FILES_TO_UPDATE.values():
            if os.path.exists(output_file):
                size_kb = os.path.getsize(output_file) / 1024
                log_message(f"  ✓ {output_file} ({size_kb:.1f} KB)")
    
    if failed_files:
        log_message("Не удалось обновить:", "WARNING")
        for failed in failed_files:
            log_message(f"  ✗ {failed}", "WARNING")
    
    log_message("=" * 60)
    return success_count > 0

def main():
    """Основная функция"""
    try:
        success = update_all_files()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        log_message("Обновление прервано пользователем", "WARNING")
        exit(1)
    except Exception as e:
        log_message(f"Критическая ошибка: {e}", "ERROR")
        exit(1)

if __name__ == "__main__":
    main()
