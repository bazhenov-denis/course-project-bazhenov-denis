# C1: Docker Production Build Report

## 1. Описание

В проекте используется **multi-stage build** для создания продакшн-образа Python приложения на FastAPI.  
Основные цели:

- Минимизация размера образа.
- Удаление dev-зависимостей из финального образа.
- Оптимизация слоёв с кэшированием pip.
- Запуск приложения под непривилегированным пользователем `appuser`.

---

## 2. Проверка истории слоёв (`docker history myapp:prod`)

```text
IMAGE          CREATED         CREATED BY                                      SIZE      COMMENT
83eca628cde0   2 minutes ago   CMD ["uvicorn" "app.main:app" "--host" "0.0.…   0B        buildkit.dockerfile.v0
<missing>      2 minutes ago   USER appuser                                    0B        buildkit.dockerfile.v0
<missing>      2 minutes ago   HEALTHCHECK &{["CMD-SHELL" "curl -f http://l…   0B        buildkit.dockerfile.v0
<missing>      2 minutes ago   EXPOSE map[8000/tcp:{}]                         0B        buildkit.dockerfile.v0
<missing>      2 minutes ago   ENV PYTHONUNBUFFERED=1                          0B        buildkit.dockerfile.v0
<missing>      2 minutes ago   COPY . . # buildkit                             164kB     buildkit.dockerfile.v0
<missing>      2 minutes ago   COPY /usr/local/bin /usr/local/bin # buildkit   20.5MB    buildkit.dockerfile.v0
<missing>      2 minutes ago   COPY /usr/local/lib/python3.11 /usr/local/li…   54.2MB    buildkit.dockerfile.v0
<missing>      3 minutes ago   RUN /bin/sh -c useradd -m appuser # buildkit    69.6kB    buildkit.dockerfile.v0
```
Из истории видно, что слои для dev-зависимостей остаются только в build stage, а runtime-слои минимальны.

## 3. Итоговый размер образа (docker images myapp:prod)
```text 
REPOSITORY   TAG       IMAGE ID       CREATED         SIZE
myapp        prod      83eca628cde0   2 minutes ago   315MB
```

# C2: Безопасность контейнера

## 1. Описание

Цель: обеспечить безопасный продакшн-контейнер для Python приложения на FastAPI.  

- Контейнер **не запускается под root**, используется непривилегированный пользователь `appuser`.  
- Настроен `HEALTHCHECK` для проверки доступности сервиса.  
- Файловая система приложения при возможности **read-only**.  
- Ограничены системные привилегии: `no-new-privileges`, seccomp профиль по умолчанию.  

---

## 2. Изменения в Dockerfile / Compose

### Основные улучшения безопасности

- `USER appuser` — запуск контейнера под непривилегированным пользователем.  
- `HEALTHCHECK` — проверка доступности `http://localhost:8000/health`.  
- Минимизация пакетов и слоёв для уменьшения поверхности атаки.  
- В Compose можно добавить:
```yaml
read_only: true
security_opt:
  - no-new-privileges:true
  - seccomp:default.json
```

запуск:
```bash
docker run -d \
  --name myapp_prod \
  --read-only \
  --security-opt no-new-privileges:true \
  --security-opt seccomp=default.json \
  -p 8000:8000 \
  myapp:prod
```
## 3. Проверка безопасности (docker inspect)
Пользователь контейнера
```
docker inspect myapp_prod --format '{{.Config.User}}'
```

Вывод:
```
appuser
```

Подтверждает, что контейнер не запускается под root.

Ограничения безопасности
```
docker inspect myapp_prod --format '{{.HostConfig.SecurityOpt}}'
```

Вывод:
```
[no-new-privileges:true seccomp:default.json]
```

# C3 Compose/локальный запуск


Файл compose.yml — в проекте

Лог запуска контейнеров:

$ docker compose ps
```text
NAME      IMAGE         COMMAND                  SERVICE   CREATED          STATUS                      PORTS
myapp     myapp:prod    "uvicorn app.main:ap…"   app       2 minutes ago    Up 57 seconds (unhealthy)   0.0.0.0:8000->8000/tcp
mydb      postgres:15   "docker-entrypoint.s…"   db        58 seconds ago   Up 57 seconds               0.0.0.0:5433->5432/tcp
myredis   redis:8       "docker-entrypoint.s…"   redis     4 minutes ago    Up 2 minutes                0.0.0.0:6379->6379/tcp
```

Лог healthcheck (через curl):

```
$ curl http://localhost:8000/health

{"status":"ok"}
```