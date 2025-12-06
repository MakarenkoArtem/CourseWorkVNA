#!/bin/bash

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "Этот скрипт нужно запускать через source:"
  echo "   source installer.sh"
  exit 1
fi

# Создание виртуального окружения
echo "Создание виртуального окружения..."
python3 -m venv venv

# Активация виртуального окружения
source venv/bin/activate

# Установка пакетов из requirements.txt
echo "Установка зависимостей из requirements.txt..."
pip install -r requirements.txt

# Вывод информации о портах и IP адресе
echo "Информация о подключении:"
echo "IP адреса:"
hostname -I
echo "Для запуска сервера:"
echo "   python3 server.py"