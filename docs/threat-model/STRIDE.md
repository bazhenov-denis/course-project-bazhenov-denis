# P04 — STRIDE: Угрозы и контроли

| Поток/Элемент | Угроза (S/T/R/I/D/E) | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---|---|---|---|---|---|
| F1 /login | S (Spoofing) | Подмена пользователя (кража пароля/сессии) | MFA, rate limit, secure cookies (HttpOnly, SameSite), IP throttling | NFR-01, NFR-04 | e2e + ZAP baseline, негативные тесты |
| F1 | I (Information disclosure) | Утечка через подробные ошибки/трейсы | RFC7807, error sanitization | NFR-02 | Контрактные тесты ошибок |
| F2 | T (Tampering) | Подмена запросов между BFF и SVC | mTLS, strict schema validation | NFR-03 | Интеграционные тесты + проверка сертификатов |
| F3 | E (Elevation of privilege) | Получение токена выше прав | RBAC + scoped tokens, короткий TTL | NFR-05 | Unit тесты RBAC + jwt-lint |
| F4 | R (Repudiation) | Отказ от действий (нет трассируемости) | Audit log с целостностью (hash/append-only) | NFR-06 | Логи в SIEM, тест целостности |
| F4 | I | Утечка PII из БД | Encryption at rest + least privilege | NFR-07 | Политика KMS, миграция шифрования |
| F6 | T | Инъекция в события/очереди | Схемы/валидаторы, подписанные события | NFR-03 | Schema registry тесты |
| F7 | D (Denial of service) | Массовая рассылка/спам | Quotas, retry-policy с backoff | NFR-08 | Нагрузочные + chaos-тест |
| Edge boundary | D | DoS на публичный эндпоинт | WAF + rate limit на ingress | NFR-04 | k8s ingress аннотации, тест |
| Admin (F8) | E | Эскалация прав в админке | 2FA, отдельные роли, журнал действий | NFR-05, NFR-06 | e2e admin + аудит |
