import requests
import zipfile
import io
import struct
from datetime import datetime

def parse_srs_file(content):
    """
    Парсит бинарный формат .srs и извлекает домены и IP-адреса
    """
    domains = []
    ips = []
    
    try:
        # Sing-box .srs format parsing
        pos = 0
        while pos < len(content):
            # Читаем тип записи (1 byte)
            if pos + 1 > len(content):
                break
            record_type = content[pos]
            pos += 1
            
            # Читаем длину данных (2 bytes)
            if pos + 2 > len(content):
                break
            data_length = struct.unpack_from('>H', content, pos)[0]
            pos += 2
            
            # Читаем данные
            if pos + data_length > len(content):
                break
            
            data = content[pos:pos + data_length]
            pos += data_length
            
            # Обрабатываем в зависимости от типа
            if record_type == 0x01:  # Domain
                try:
                    domain = data.decode('utf-8')
                    domains.append(domain)
                except:
                    continue
                    
            elif record_type == 0x02:  # IP CIDR
                try:
                    # IP адрес в формате CIDR
                    ip_cidr = data.decode('utf-8')
                    ips.append(ip_cidr)
                except:
                    continue
    
    except Exception as e:
        print(f"Ошибка при парсинге .srs файла: {e}")
    
    return domains, ips

def convert_srs_to_lst():
    # URL архива
    ZIP_URL = "https://github.com/runetfreedom/russia-v2ray-rules-dat/releases/latest/download/sing-box.zip"
    TARGET_FILE = "rule-set-geosite/geosite-ru-blocked-all.srs"
    OUTPUT_FILE = "blocked-russia.lst"
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Конвертация .srs в .lst...")
    
    try:
        # Скачать архив
        print("Скачивание архива...")
        response = requests.get(ZIP_URL, timeout=30)
        response.raise_for_status()
        print("Архив успешно скачан")

        # Извлечь и распарсить .srs файл
        print("Извлечение и парсинг .srs файла...")
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            if TARGET_FILE not in zip_ref.namelist():
                print(f"Файл {TARGET_FILE} не найден!")
                return False
            
            with zip_ref.open(TARGET_FILE) as source_file:
                srs_content = source_file.read()
        
        # Парсим .srs файл
        domains, ips = parse_srs_file(srs_content)
        
        print(f"Найдено: {len(domains)} доменов, {len(ips)} IP-адресов")
        
        # Сохраняем в .lst формат
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            # Сначала домены
            for domain in domains:
                f.write(domain + "\n")
            
            # Затем IP-адреса
            for ip in ips:
                f.write(ip + "\n")
        
        print(f"Файл {OUTPUT_FILE} успешно создан!")
        return True

    except Exception as e:
        print(f"Ошибка: {e}")
        return False

if __name__ == "__main__":
    convert_srs_to_lst()