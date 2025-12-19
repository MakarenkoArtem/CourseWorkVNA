#!/usr/bin/env python3
"""
Финальный тест: показываем, как данные из CSV файла будут храниться в новой БД
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from data.db_session import global_init, create_session
from data.users import User
from data.settings import Setting
from data.measurement_data import MeasurementData
from datetime import datetime


def csv_data_test():
    """Тест с реальными данными из CSV файла"""

    print("=== ТЕСТ С ДАННЫМИ ИЗ CSV ФАЙЛА ===\n")

    # Инициализация базы данных
    db_file = "csv_test.db"
    global_init(db_file)

    session = create_session()

    try:
        # Создаем тестового пользователя
        user = User()
        user.email = "test@example.com"
        user.hashed_password = "hashed_password_123"
        user.status = 1
        session.add(user)
        session.flush()
        print(f"✅ Создан пользователь с ID: {user.id}")

        # Читаем данные из CSV файла (пример)
        csv_sample = [
            [
                500.0,
                0.0004589529144342598,
                -0.0011958096014995864,
                0.0428372809422851,
                -0.0015363897678804933,
                0.0,
                0.0,
                -2.2103573481143963e-05,
                9.218466075938322e-06,
                -7.342969027763288e-07,
                1.5332993464708605e-05,
                -1.854341956179564e-06,
                -3.9139933599902115e-07,
            ],
            [
                505.5,
                0.00026416124859720376,
                -0.0014081881527069594,
                0.042837153665063896,
                -0.004467981185984495,
                0.0,
                0.0,
                -1.5406468589578785e-05,
                6.936987029280209e-07,
                -1.035035444628275e-05,
                2.175233287396514e-06,
                -1.0883090041117053e-06,
                2.0160224750629052e-07,
            ],
            [
                511.0,
                -1.004317205998388e-05,
                -0.00155465943766085,
                0.042588823840577085,
                -0.0073948113637250555,
                0.0,
                0.0,
                7.85992700765514e-06,
                -7.579803609975797e-06,
                6.057301588506132e-06,
                -9.43068069797835e-06,
                1.3199059788976075e-06,
                6.765031244751927e-07,
            ],
        ]

        # Извлекаем частоты
        frequency_data = [row[0] for row in csv_sample]
        print(f"✅ Частоты из CSV: {frequency_data}")

        # Создаем измерение с данными из CSV
        measurement = MeasurementData.create_raw_measurement(
            session, user.id, "2match3.csv данные", frequency_data, csv_sample
        )
        print(f"✅ Создано измерение с ID: {measurement.id}")

        # Сравнение с оригинальным форматом CSV
        print("\n=== СРАВНЕНИЕ С ОРИГИНАЛЬНЫМ ФОРМАТОМ ===")
        original_row = csv_sample[0]
        print(f"Оригинальная строка CSV:")
        print(f"  Частота: {original_row[0]}")
        print(f"  b0_3_real: {original_row[1]}")
        print(f"  b0_3_imag: {original_row[2]}")
        print(f"  a0_real: {original_row[3]}")
        print(f"  a0_imag: {original_row[4]}")
        print(f"  b3_3_real: {original_row[5]}")
        print(f"  b3_3_imag: {original_row[6]}")
        print(f"  b0_6_real: {original_row[7]}")
        print(f"  b0_6_imag: {original_row[8]}")
        print(f"  a3_real: {original_row[9]}")
        print(f"  a3_imag: {original_row[10]}")
        print(f"  b3_6_real: {original_row[11]}")
        print(f"  b3_6_imag: {original_row[12]}")

        session.commit()
        print("\n✅ Тест завершен успешно!")

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        session.rollback()
        raise
    finally:
        session.close()
        # Удаляем тестовую базу данных
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"Тестовая БД {db_file} удалена")


if __name__ == "__main__":
    csv_data_test()
