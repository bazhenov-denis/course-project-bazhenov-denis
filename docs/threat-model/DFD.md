Ниже — DFD уровня L1 для моего сервиса (контекст: веб-платформа квизов). Отмечены границы доверия и ключевые потоки `F1…F8`.

```mermaid
flowchart LR
  U[User/Client] -->|F1: HTTPS| BFF[Web/API]

  subgraph Edge[Trust Boundary: Edge]
    BFF -->|F2: mTLS/HTTPS| SVC[Quiz Service]
    BFF -->|F3: HTTPS| AUTH[Auth Service]
  end

  subgraph Core[Trust Boundary: Core]
    SVC -->|F4: TCP| DB[(PostgreSQL)]
    AUTH -->|F5: TCP| UDB[(Users DB)]
    SVC -->|F6: AMQP/Kafka| BUS[(Event Bus)]
  end

  subgraph External[Trust Boundary: External]
    MAIL[Email Provider]:::ext
    PAY[Payment/Billing]:::ext
  end

  BUS -->|F7: Outbound| MAIL
  BFF -->|F8: HTTPS admin| Admin[Admin UI]

  classDef ext fill:#444,stroke:#ccc,color:#fff;
  class MAIL,PAY ext;

```


| ID | Откуда → Куда              | Канал/протокол | Данные/PII              | Комментарий                |
| -- | -------------------------- | -------------- | ----------------------- | -------------------------- |
| F1 | User → Web/API             | HTTPS          | creds, cookies          | вход/регистрация/квиз      |
| F2 | Web/API → Quiz Service     | mTLS/HTTPS     | session, quiz data      | внутренний API             |
| F3 | Web/API → Auth             | HTTPS          | creds, tokens           | обмен токенами             |
| F4 | Quiz Service → PostgreSQL  | TCP            | quiz/answers/PII        | ORM/DRIVER                 |
| F5 | Auth → Users DB            | TCP            | password hash, PII      | хранение пользователей     |
| F6 | Quiz Service → Event Bus   | AMQP/Kafka     | events (PII минимально) | нотификации/аналитика      |
| F7 | Event Bus → Email Provider | HTTPS          | email, template vars    | внешняя интеграция         |
| F8 | Admin UI → Web/API         | HTTPS          | admin session           | управление курсами/квизами |
