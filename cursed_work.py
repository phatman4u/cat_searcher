import requests
import json
import os

FOLDER_NAME = "PD-160"

CATAAS_URL = "https://cataas.com/cat/says/"
YANDEX_DISK_UPLOAD_URL = "https://cloud-api.yandex.net/v1/disk/resources/upload"
YANDEX_DISK_CREATE_URL = "https://cloud-api.yandex.net/v1/disk/resources"

def get_cat_image(text):
    url = f"{CATAAS_URL}{text}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении картинки: {e}")
        return None

def create_folder_on_disk(token, path):
    headers = {"Authorization": f"OAuth {token}"}
    params = {"path": path}
    try:
        response = requests.put(YANDEX_DISK_CREATE_URL, headers=headers, params=params)
        if response.status_code == 201:
            print(f"Папка '{path}' успешно создана.")
        elif response.status_code == 409:
            print(f"Папка '{path}' уже существует.")
        else:
            print(f"Ошибка создания папки: {response.status_code}")
    except Exception as e:
        print(f"Критическая ошибка при создании папки: {e}")

def get_upload_link(token, file_path):
    headers = {"Authorization": f"OAuth {token}"}
    params = {"path": file_path, "overwrite": "true"}
    try:
        response = requests.get(YANDEX_DISK_UPLOAD_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("href")
    except Exception as e:
        print(f"Не удалось получить ссылку для загрузки: {e}")
        return None

def upload_file(upload_link, file_content):
    try:
        response = requests.put(upload_link, data=file_content)
        return response.status_code == 201
    except Exception as e:
        print(f"Ошибка при отправке файла: {e}")
        return False

def save_report(report_data, filename="backup_report.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=4)
    print(f"Отчёт сохранён в {filename}")

def main():
    print("--- Резервное копирование картинок с котиками ---")

    text_input = input("Введите текст для картинки: ").strip()
    if not text_input:
        print("Текст не может быть пустым!")
        return

    token = input("Введите токен Яндекс.Диска: ").strip()
    if not token:
        print("Токен обязателен!")
        return

    file_name = f"{text_input}.jpg"
    full_path = f"/{FOLDER_NAME}/{file_name}"

    image_data = get_cat_image(text_input)
    if not image_data:
        return

    print(f"Картинка получена. Размер: {len(image_data)} байт.")

    create_folder_on_disk(token, f"/{FOLDER_NAME}")

    upload_link = get_upload_link(token, full_path)
    if not upload_link:
        return

    if upload_file(upload_link, image_data):
        print("Файл успешно загружен на Яндекс.Диск!")
        file_size = len(image_data)
        report_entry = {
            "filename": file_name,
            "original_text": text_input,
            "size_bytes": file_size,
            "disk_path": full_path
        }
        report_filename = "backup_report.json"
        all_reports = []
        if os.path.exists(report_filename):
            with open(report_filename, "r", encoding="utf-8") as f:
                all_reports = json.load(f)
        all_reports.append(report_entry)
        save_report(all_reports, report_filename)
    else:
        print("Не удалось загрузить файл.")

if __name__ == "__main__":
    main()
