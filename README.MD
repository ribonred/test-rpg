### getting started

copy env file
```
cp example.env .env
```

run in docker compose
```
docker compose up --build --remove-orphans --force-recreate
```

### service

- provider -> http://127.0.0.1:8000

- dashboard -> http://127.0.0.1:8000

### to run test

- provider

```
pytest
```

- dashboard

```
cd dashboard_app

pytest
```

### this project using poetry to manage dependency

poetry version 1.4.2

[poetry docs](https://python-poetry.org/docs/)
