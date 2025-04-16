#!/usr/bin/env python3
"""
RuTracker Magnet Downloader - Упрощенная версия
Только получение magnet-ссылок с Rutracker
"""

import argparse
import requests
import os
from urllib.parse import urlparse, parse_qs

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def get_magnet_from_rutracker(topic_id: int) -> str:
    """Получает magnet-ссылку с Rutracker"""
    url = f"https://rutracker.org/forum/viewtopic.php?t={topic_id}"
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
            },
            timeout=10
        )
        response.raise_for_status()
        
        # Ищем magnet-ссылку в коде страницы
        for line in response.text.splitlines():
            if "magnet:?" in line and "href=" in line:
                magnet = line.split('href="')[1].split('"')[0]
                return magnet.replace("&amp;", "&")
        
        raise ValueError("Magnet-ссылка не найдена в коде страницы")
    except Exception as e:
        print(f"🚨 Ошибка при получении magnet-ссылки: {str(e)}")
        return None

def save_file(content: str, file_path: str) -> bool:
    """Сохраняет magnet-ссылку в файл"""
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"🚨 Ошибка сохранения файла: {str(e)}")
        return False

def parse_topic_id(url: str) -> int:
    """Извлекает ID темы из URL или строки"""
    try:
        if url.isdigit():
            return int(url)
        
        parsed = urlparse(url)
        if 't=' in parsed.query:
            return int(parse_qs(parsed.query)['t'][0])
        elif '/t' in parsed.path:
            return int(parsed.path.split('/t')[-1].split('.')[0])
        raise ValueError("Не удалось извлечь ID темы")
    except Exception as e:
        print(f"🚨 Ошибка парсинга URL: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description="📥 Загрузчик magnet-ссылок с Rutracker",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "topic",
        help="ID темы или URL (например: 6673601 или https://rutracker.org/forum/viewtopic.php?t=6673601)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Имя выходного файла (по умолчанию: <ID_темы>.magnet)",
        default=None
    )
    parser.add_argument(
        "-d", "--directory",
        help="Директория для сохранения",
        default=""
    )
    
    args = parser.parse_args()
    topic_id = parse_topic_id(args.topic)
    if not topic_id:
        return

    # Определяем путь для сохранения
    output_file = args.output or f"{topic_id}.magnet"
    if args.directory:
        os.makedirs(args.directory, exist_ok=True)
        output_file = os.path.join(args.directory, output_file)

    print(f"🔍 Получаем magnet-ссылку для темы #{topic_id}...")

    # Получаем magnet-ссылку
    magnet = get_magnet_from_rutracker(topic_id)
    
    if magnet:
        if save_file(magnet, output_file):
            print(f"✅ Успешно сохранена magnet-ссылка: {output_file}")
            print(f"🔗 {magnet[:60]}...")  # Показываем начало ссылки
            return
    
    print("❌ Не удалось получить magnet-ссылку")
    print("Возможные причины:")
    print("- Требуется авторизация на сайте")
    print("- Тема удалена или недоступна")
    print("- Проблемы с соединением")

if __name__ == "__main__":
    main()
