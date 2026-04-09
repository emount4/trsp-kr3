
Task 8.1 — Сервис регистрации на SQLite 

Короткая инструкция по запуску (Windows PowerShell):

1) Создать виртуальное окружение и активировать его:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Установить зависимости:

```powershell
pip install -r task_8_1_sqlite\requirements.txt
```

3) Создать таблицу `users` (запустить один раз):

```powershell
python -m task_8_1_sqlite.create_tables
```

4) Запустить сервис (Hypercorn, порт 8001):

```powershell
hypercorn task_8_1_sqlite.main:app --reload --bind 127.0.0.1:8001
```

