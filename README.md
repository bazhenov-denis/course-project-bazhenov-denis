
# Minimal Notes API (security-flavored demo)

Быстрый минимальный сервис на FastAPI, покрывающий базовые NFR из курса:
единый конверт ошибок (Problem Details) с correlation-id, пагинация, ограничение `limit`,
структурные логи без PII, простые тесты.

## Запуск

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Откройте: http://127.0.0.1:8000/ping

## Тесты

```bash
pytest -q
```

## Полезные маршруты
- `POST /notes` — создать заметку (`title`, `body`, `tags[]`)
- `GET /notes?limit=10&offset=0` — список с пагинацией (без поля `body` в ответе)

В каждом ответе заголовок `X-Request-ID`. Ошибки — в формате `application/problem+json`.
