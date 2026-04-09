Task 8.2 Сервис CRUD для ресурса Todo на PostgreSQL

Короткая инструкция по запуску и тестированию:

1) Настройте параметры подключения к PostgreSQL (пример для PowerShell):

```powershell
$env:PG_HOST = "localhost"
$env:PG_PORT = "5432"
$env:PG_DB = "testdb"
$env:PG_USER = "postgres"
$env:PG_PASSWORD = "postgres"
# либо установите переменную PG_DSN: "host=... port=... dbname=... user=... password=..."
```

2) Установите зависимости:

```powershell
pip install -r task_8_2_postgres\requirements.txt
```

3) Создайте таблицу `todos` (запустите один раз):

```powershell
python -m task_8_2_postgres.create_tables
```

4) Запустите сервис (Hypercorn, порт 8002):

```powershell
hypercorn task_8_2_postgres.main:app --reload --bind 127.0.0.1:8002
```

