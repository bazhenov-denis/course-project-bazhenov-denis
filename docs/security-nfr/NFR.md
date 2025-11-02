
# Нефункциональные требования (NFR)

| ID | Требование | Критерий приёмки |
|----|------------|------------------|
| NFR-01 | Единый конверт ошибок (Problem Details) + `correlation_id` | Любой 4xx/5xx → `application/problem+json` с полями `type,title,status,detail,instance,correlation_id`. Заголовок `X-Request-ID` присутствует. |
| NFR-02 | Пагинация и лимиты | `limit` по умолчанию ≤ 50; `limit > 200` → 422. Нет режима «выгрузи всё». |
| NFR-03 | Структурные логи без PII | В логах отсутствуют поля из deny-list (`password, token, body`). Логи содержат `ts, level, message, correlation_id`. |
| NFR-04 | Минимизация данных в ответах | Список заметок не содержит `body`; только whitelisted DTO (`id,title,tags`). |
| NFR-05 | Тесты на валидацию/ошибки | Есть `pytest`-тесты: валидация limit→422, конверт ошибок, отсутствие `body` в списке. |
| NFR-06 | CORS/политика доступа | Включён CORS (ограничения на методы/заголовки). |
| NFR-07 | Корреляция запросов | Во всех ответах присутствует `X-Request-ID`; в логах пишется `correlation_id`. |
| NFR-08 | Supply chain (план) | В CI добавить публикацию SBOM (CycloneDX) и SCA-гейтинг на High/Critical — запланировано. |
