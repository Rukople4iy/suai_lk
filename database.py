import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('instance/bot_database.db')
cursor = conn.cursor()

# ======= Добавление начальных данных ======= #

# Добавление групп
groups = [("Группа 1",), ("Группа 2",)]
cursor.executemany("INSERT INTO groups (name) VALUES (?)", groups)

# Добавление администратора
admin_data = (123456789, "admin", "adminpass", "admin", None)
cursor.execute("INSERT INTO users (telegram_id, login, password, role, group_id) VALUES (?, ?, ?, ?, ?)", admin_data)

# Сохранение изменений и закрытие подключения
conn.commit()
conn.close()

print("Начальные данные успешно добавлены!")
