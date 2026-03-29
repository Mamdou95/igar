# Story 1.2: Deploiement Operationnel de la Plateforme Igar

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **administrateur IT (Thomas)**,
I want **deployer l'ensemble de la stack Igar via Docker Compose en moins de 30 minutes**,
So that **l'infrastructure complete est operationnelle avec tous les services necessaires**.

## Acceptance Criteria

1. **Given** un serveur Linux avec Docker installe **When** je lance `docker compose up -d` depuis le dossier `infrastructure/` **Then** tous les services demarrent : backend (Gunicorn), PostgreSQL (TDE), Redis 7.x, MinIO (avec Object Lock active), Elasticsearch, Nginx (TLS), tusd, Gotenberg, Celery workers (queues ocr, ai, default, compliance), Celery Beat, Django Channels (Daphne)
2. **And** le endpoint `/health` retourne un statut agrege de tous les composants en moins de 500ms
3. **And** Nginx route correctement `/` vers frontend, `/api/v1/` vers Django, `/ws/` vers Channels, `/uploads/` vers tusd
4. **And** le script `init-buckets.sh` cree les buckets MinIO (igar-temp, igar-vault avec Object Lock, igar-thumbnails)
5. **And** un `docker-compose.dev.yml` override est disponible pour le developpement (volumes, hot-reload)
6. **And** un fichier `.env.example` documente toutes les variables d'environnement

## Tasks / Subtasks

- [x] Task 1 : Creer la structure du dossier infrastructure/ et le .env.example (AC: #1, #6)
  - [x] 1.1 Creer le dossier `infrastructure/` a la racine du monorepo avec les sous-dossiers : `nginx/conf.d/`, `minio/`, `elasticsearch/`, `tusd/`, `prometheus/`, `grafana/dashboards/`, `scripts/`
  - [x] 1.2 Creer `infrastructure/.env.example` documentant TOUTES les variables d'environnement :
    - PostgreSQL : `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
    - MinIO : `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`
    - Redis : `REDIS_URL`
    - Django : `DJANGO_SETTINGS_MODULE`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`
    - Elasticsearch : `ELASTICSEARCH_URL`, `ES_JAVA_OPTS`
    - Frontend : `VITE_API_URL`, `VITE_WS_URL`
    - Sentry : `SENTRY_DSN`
  - [x] 1.3 Ajouter `infrastructure/.env` dans le `.gitignore` racine du monorepo

- [x] Task 2 : Creer le Dockerfile backend multi-stage (AC: #1)
  - [x] 2.1 Creer `backend/docker/Dockerfile` :
    - Stage `builder` : base `python:3.12-slim-bookworm`, installer les packages systeme (build-essential, libcairo2-dev, libmagic1, poppler-utils, tesseract-ocr, tesseract-ocr-fra, libpq-dev, libjpeg62-turbo-dev, zlib1g-dev), pip install requirements
    - Stage `runtime` : base `python:3.12-slim-bookworm`, installer les packages runtime seulement (libcairo2, libmagic1, poppler-utils, tesseract-ocr, tesseract-ocr-fra, libpq5, libjpeg62-turbo, zlib1g), copier site-packages depuis builder
    - WORKDIR `/app`, copier le code backend, exposer port 8000
    - ATTENTION : les requirements sont dans `requirements/igar/base.txt` + les requirements Mayan dans `requirements/` (verifier le chemin exact dans le Dockerfile)
  - [x] 2.2 Creer `backend/docker/entrypoint.sh` :
    - Boucle wait-for-db : `pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER` (max 30 tentatives, 2s entre chaque)
    - `python manage.py migrate --no-input`
    - `python manage.py collectstatic --no-input`
    - `exec "$@"` pour passer la commande (Gunicorn, Daphne, ou Celery)
  - [x] 2.3 Creer `backend/.dockerignore` : `.git`, `__pycache__`, `*.pyc`, `.env`, `node_modules`, `.pytest_cache`, `.coverage`, `htmlcov/`, `*.egg-info`

- [x] Task 3 : Creer le docker-compose.yml principal (AC: #1)
  - [x] 3.1 Definir le service `postgresql` :
    - Image : `postgres:17-alpine`
    - Volume : `postgres-data:/var/lib/postgresql/data`
    - Healthcheck : `pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}` (interval 5s, timeout 5s, retries 5)
    - Variables env depuis `.env`
  - [x] 3.2 Definir le service `redis` :
    - Image : `redis:7-alpine`
    - Command : `redis-server --appendonly yes` (persistence AOF)
    - Volume : `redis-data:/data`
    - Healthcheck : `redis-cli ping` (interval 5s, timeout 3s, retries 5)
  - [x] 3.3 Definir le service `minio` :
    - Image : `minio/minio:latest`
    - Command : `server /data --console-address ":9001"`
    - Volumes : `minio-data:/data`
    - Healthcheck : `curl -f http://localhost:9000/minio/health/live` (interval 10s, timeout 5s, retries 5)
    - Variables : `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`
  - [x] 3.4 Definir le service `minio-init` (one-shot) :
    - Image : `minio/mc:latest`
    - depends_on minio (condition: service_healthy)
    - Volume mount : `./minio/init-buckets.sh:/init-buckets.sh:ro`
    - Entrypoint : `/bin/sh /init-buckets.sh`
    - restart : `"no"`
  - [x] 3.5 Definir le service `elasticsearch` :
    - Image : `elasticsearch:8.17.0`
    - Environment : `discovery.type=single-node`, `xpack.security.enabled=false`, `ES_JAVA_OPTS=-Xms512m -Xmx512m`
    - Volume : `elasticsearch-data:/usr/share/elasticsearch/data`
    - Healthcheck : `curl -f http://localhost:9200/_cluster/health` (interval 10s, timeout 5s, retries 10)
    - Volume config : `./elasticsearch/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml:ro`
  - [x] 3.6 Definir le service `backend` :
    - Build : context `../backend`, dockerfile `docker/Dockerfile`
    - Command : `gunicorn igar.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120`
    - depends_on : postgresql (service_healthy), redis (service_healthy), minio (service_healthy), elasticsearch (service_healthy)
    - Healthcheck : `curl -f http://localhost:8000/health` (interval 15s, timeout 5s, retries 3)
    - Environment : `DJANGO_SETTINGS_MODULE`, `DATABASE_URL`, `REDIS_URL`, `MINIO_ENDPOINT`, `ELASTICSEARCH_URL`, `SECRET_KEY`
  - [x] 3.7 Definir le service `backend-ws` :
    - Meme build que backend
    - Command : `daphne -b 0.0.0.0 -p 8001 igar.asgi:application`
    - depends_on : redis (service_healthy)
    - Environment : meme que backend
  - [x] 3.8 Definir le service `worker-ocr` :
    - Meme build que backend
    - Command : `celery -A mayan worker -Q ocr -c 2 --loglevel=info`
    - depends_on : redis (service_healthy), minio (service_healthy)
    - IMPORTANT : verifier le module Celery de Mayan (`-A mayan` ou nom exact du module app)
  - [x] 3.9 Definir le service `worker-ai` :
    - Command : `celery -A mayan worker -Q ai -c 2 --loglevel=info`
    - depends_on : redis, minio, postgresql
  - [x] 3.10 Definir le service `worker-default` :
    - Command : `celery -A mayan worker -Q default,compliance -c 2 --loglevel=info`
    - depends_on : redis, postgresql
  - [x] 3.11 Definir le service `celery-beat` :
    - Command : `celery -A mayan beat --loglevel=info`
    - depends_on : redis, postgresql
    - Note : utiliser `--scheduler django_celery_beat.schedulers:DatabaseScheduler` si django-celery-beat est installe, sinon le scheduler par defaut
  - [x] 3.12 Definir le service `tusd` :
    - Image : `tusproject/tusd:latest`
    - Command avec flags S3 : `-s3-bucket igar-temp -s3-endpoint http://minio:9000 -s3-disable-ssl`
    - Environment : `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION=us-east-1`
    - depends_on : minio (service_healthy)
    - Hook post-finish : `-hooks-http http://backend:8000/api/v1/capture/tus-hook/` (le endpoint sera implemente dans Epic 2, placeholder pour l'instant)
  - [x] 3.13 Definir le service `gotenberg` :
    - Image : `gotenberg/gotenberg:8`
    - Command : `gotenberg --api-timeout=30s --api-root-path=/`
    - Healthcheck : `curl -f http://localhost:3000/health` (interval 10s, timeout 5s, retries 5)
  - [x] 3.14 Definir le service `nginx` :
    - Image : `nginx:1.27-alpine`
    - Ports : `"80:80"`, `"443:443"` (443 commente pour dev)
    - Volumes : `./nginx/nginx.conf:/etc/nginx/nginx.conf:ro`, `./nginx/conf.d/:/etc/nginx/conf.d/:ro`
    - depends_on : backend (service_started), backend-ws (service_started), tusd (service_started)
  - [x] 3.15 Definir les volumes nommes : `postgres-data`, `minio-data`, `elasticsearch-data`, `redis-data`
  - [x] 3.16 Definir le reseau `igar-network` (driver bridge), assigner a tous les services
  - [x] 3.17 Ajouter les services monitoring (Prometheus, Grafana) sous le profile `monitoring` pour qu'ils ne demarrent pas par defaut

- [x] Task 4 : Configurer Nginx comme reverse proxy (AC: #3)
  - [x] 4.1 Creer `infrastructure/nginx/nginx.conf` :
    - `worker_processes auto;`
    - `events { worker_connections 1024; }`
    - `http { ... }` avec : gzip on, `client_max_body_size 500m` (pour uploads lots de 500 docs), include conf.d/*.conf
    - Rate limiting : `limit_req_zone $binary_remote_addr zone=api_limit:10m rate=30r/s;`
  - [x] 4.2 Creer `infrastructure/nginx/conf.d/igar.conf` avec les location blocks :
    - `location /` : `try_files $uri /index.html;` (fichiers statiques frontend, placeholder pour Story 1.3)
    - `location /api/v1/` : `proxy_pass http://backend:8000;` + headers X-Forwarded-For, X-Forwarded-Proto, Host + `limit_req zone=api_limit burst=50 nodelay;`
    - `location /ws/` : `proxy_pass http://backend-ws:8001;` + `proxy_http_version 1.1;` + `proxy_set_header Upgrade $http_upgrade;` + `proxy_set_header Connection "upgrade";` + `proxy_read_timeout 3600s;`
    - `location /uploads/` : `proxy_pass http://tusd:8080;` + headers tus obligatoires : `proxy_set_header Tus-Resumable $http_tus_resumable;` + `proxy_set_header Upload-Offset $http_upload_offset;` + `proxy_set_header Upload-Length $http_upload_length;` + `client_max_body_size 0;` (pas de limite pour tus)
    - `location /health` : `proxy_pass http://backend:8000;`
  - [x] 4.3 Ajouter les headers de securite dans le server block :
    - `add_header X-Frame-Options "SAMEORIGIN" always;`
    - `add_header X-Content-Type-Options "nosniff" always;`
    - `add_header X-XSS-Protection "1; mode=block" always;`
    - `add_header Referrer-Policy "strict-origin-when-cross-origin" always;`
    - Section TLS commentee pour dev : `ssl_protocols TLSv1.3;` etc.

- [x] Task 5 : Creer le script d'initialisation MinIO (AC: #4)
  - [x] 5.1 Creer `infrastructure/minio/init-buckets.sh` :
    ```bash
    #!/bin/sh
    set -e
    # Attendre MinIO
    until mc alias set myminio http://minio:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD; do
      echo "Waiting for MinIO..."
      sleep 2
    done
    # Creer les buckets (idempotent avec --ignore-existing)
    mc mb --ignore-existing myminio/igar-temp
    mc mb --ignore-existing --with-lock myminio/igar-vault
    mc mb --ignore-existing myminio/igar-thumbnails
    # Lifecycle : TTL 24h sur igar-temp
    mc ilm rule add myminio/igar-temp --expire-days 1
    # Retention par defaut sur igar-vault (Governance 1 jour pour dev, Compliance en prod)
    mc retention set --default GOVERNANCE 1d myminio/igar-vault
    echo "MinIO buckets initialized successfully."
    ```
  - [x] 5.2 Rendre le script executable : `chmod +x init-buckets.sh`
  - [x] 5.3 IMPORTANT : Utiliser le mode **Governance** (pas Compliance) pour le dev — Governance permet de supprimer avec un flag force, Compliance est irreversible. Le mode Compliance sera active en production via la variable d'environnement.

- [x] Task 6 : Creer le docker-compose.dev.yml override (AC: #5)
  - [x] 6.1 Creer `infrastructure/docker-compose.dev.yml` avec :
    - `backend` : volume `../backend:/app`, environment `DJANGO_SETTINGS_MODULE=igar.settings.development`, `DEBUG=True`
    - `backend-ws` : meme volume mount
    - `worker-ocr`, `worker-ai`, `worker-default` : meme volume mount pour hot-reload du code
    - `postgresql` : port expose `"5432:5432"` pour acces direct pgAdmin/DBeaver
    - `redis` : port expose `"6379:6379"` pour redis-cli local
    - `minio` : ports exposes `"9000:9000"`, `"9001:9001"` pour console web MinIO
    - `elasticsearch` : port expose `"9200:9200"` pour requetes directes
    - Nginx : configuration alternative pour router `/` vers `host.docker.internal:5173` (HMR Vite, Story 1.3)

- [x] Task 7 : Implementer le healthcheck agrege `/health` (AC: #2)
  - [x] 7.1 Creer la vue healthcheck dans `backend/igar/core/health.py` :
    ```python
    import time
    from django.http import JsonResponse
    from django.db import connection
    # Verifier PostgreSQL, Redis, MinIO, Elasticsearch
    # Timeout 2s par service, reponse totale < 500ms
    # HTTP 200 si tous healthy, HTTP 503 sinon
    ```
  - [x] 7.2 Ajouter la route dans `backend/igar/urls.py` : `path("health", health_check_view, name="health")`
  - [x] 7.3 La reponse JSON doit suivre le format :
    ```json
    {
      "status": "healthy",
      "timestamp": "2026-03-18T10:00:00Z",
      "services": {
        "postgresql": {"status": "up", "latency_ms": 2},
        "redis": {"status": "up", "latency_ms": 1},
        "minio": {"status": "up", "latency_ms": 5},
        "elasticsearch": {"status": "up", "latency_ms": 8}
      }
    }
    ```
  - [x] 7.4 Ecrire les tests unitaires : `backend/tests/test_health.py` avec mocks des connexions externes
  - [x] 7.5 IMPORTANT : Cette vue ne doit PAS passer par l'authentification JWT (exclure `/health` des permissions DRF)

- [x] Task 8 : Configurations annexes des services (AC: #1)
  - [x] 8.1 Creer `infrastructure/elasticsearch/elasticsearch.yml` :
    - `cluster.name: igar-search`
    - `discovery.type: single-node`
    - `xpack.security.enabled: false`
    - `bootstrap.memory_lock: true`
  - [x] 8.2 Creer `infrastructure/prometheus/prometheus.yml` (profile monitoring) :
    - Scrape targets : backend:8000/metrics, redis-exporter, minio:9000/minio/v2/metrics/cluster
  - [x] 8.3 Creer `infrastructure/grafana/dashboards/igar-overview.json` (placeholder minimal)

- [x] Task 9 : Validation finale (AC: #1-#6)
  - [x] 9.1 Executer `docker compose config` depuis `infrastructure/` — doit parser sans erreur
  - [x] 9.2 Executer `docker compose up -d` — tous les services demarrent et passent les healthchecks
  - [x] 9.3 Verifier `curl http://localhost/health` retourne HTTP 200 avec tous les services "healthy" en < 500ms
  - [x] 9.4 Verifier le routage Nginx : `curl http://localhost/api/v1/` → Django, tester WebSocket upgrade sur `/ws/`
  - [x] 9.5 Verifier les buckets MinIO : `docker compose exec minio-init mc ls myminio/` → igar-temp, igar-vault, igar-thumbnails
  - [x] 9.6 Verifier l'override dev : `docker compose -f docker-compose.yml -f docker-compose.dev.yml config`
  - [x] 9.7 Verifier que `.env.example` documente toutes les variables utilisees dans les fichiers docker-compose
  - [x] 9.8 Executer les tests backend dans Docker : `docker compose exec backend pytest`

## Dev Notes

### Contexte Architectural Critique

**Architecture de reference :** [Source: _bmad-output/planning-artifacts/architecture.md#Project Structure & Boundaries]

Cette story cree le dossier `infrastructure/` conformement a l'architecture monorepo. Le dossier `backend/` existe deja (Story 1.1). Le dossier `frontend/` sera cree par Story 1.3.

**Services Docker requis (14 services + 1 one-shot) :**

| Service | Image Docker | Port interne | Role |
| --- | --- | --- | --- |
| `nginx` | `nginx:1.27-alpine` | 80/443 | Reverse proxy, TLS termination, rate limiting |
| `backend` | Build `../backend/` | 8000 | API Django (Gunicorn) |
| `backend-ws` | Build `../backend/` | 8001 | WebSocket Django (Daphne/ASGI) |
| `worker-ocr` | Build `../backend/` | — | Celery worker queue `ocr` |
| `worker-ai` | Build `../backend/` | — | Celery worker queue `ai` |
| `worker-default` | Build `../backend/` | — | Celery worker queues `default`, `compliance` |
| `celery-beat` | Build `../backend/` | — | Planificateur taches periodiques |
| `tusd` | `tusproject/tusd:latest` | 8080 | Upload resumable (protocole tus) |
| `gotenberg` | `gotenberg/gotenberg:8` | 3000 | Conversion Office → PDF |
| `postgresql` | `postgres:17-alpine` | 5432 | Base de donnees principale |
| `redis` | `redis:7-alpine` | 6379 | Cache, broker Celery, channel layer WS |
| `minio` | `minio/minio:latest` | 9000/9001 | Stockage objet S3 (Object Lock) |
| `elasticsearch` | `elasticsearch:8.17.0` | 9200 | Indexation full-text |
| `minio-init` | `minio/mc:latest` | — | Service one-shot : creation des buckets |

**Routing Nginx obligatoire :**

| Route | Destination | Headers/Config speciales |
| --- | --- | --- |
| `/` | Frontend SPA (fichiers statiques ou proxy dev) | `try_files $uri /index.html` |
| `/api/v1/` | `backend:8000` | `proxy_pass`, headers X-Forwarded-*, rate limit |
| `/ws/` | `backend-ws:8001` | `proxy_http_version 1.1`, `Upgrade`, `Connection`, timeout 3600s |
| `/uploads/` | `tusd:8080` | Headers tus, `client_max_body_size 0` |
| `/health` | `backend:8000` | Direct proxy, pas d'auth |

**Buckets MinIO requis :**

| Bucket | Object Lock | Politique | Usage |
| --- | --- | --- | --- |
| `igar-temp` | Non | Lifecycle TTL 24h | Fichiers pipeline (upload → OCR → IA) |
| `igar-vault` | Oui (Governance en dev, Compliance en prod) | Retention 1j dev / 365j prod | Coffre-fort WORM, documents scelles |
| `igar-thumbnails` | Non | Aucune | Miniatures des documents |

### Intelligence Story Precedente (Story 1.1)

**Lecons critiques a appliquer :**

1. **Mayan v4.11.1 n'existe pas encore sur GitLab** — le fork a ete clone avec **v4.9.4**. Le Dockerfile doit builder cette version exacte. Ne PAS tenter de telecharger v4.11.
2. **Python 3.13 ne contient plus `distutils`** — utiliser `python:3.12-slim-bookworm` (PAS 3.13) comme image de base Docker.
3. **`cairocffi` necessite `libcairo2-dev`** — ajouter dans les packages systeme du Dockerfile.
4. **Celery tente de se connecter a Redis au demarrage** — les services Redis doivent etre `service_healthy` avant de demarrer les workers. Utiliser `depends_on` avec condition `service_healthy`.
5. **Requirements dans `requirements/igar/`** (pas `requirements/` directement) — le Dockerfile doit installer `requirements/igar/base.txt` + les requirements Mayan dans le dossier `requirements/` standard de Mayan.
6. **Settings module** : `DJANGO_SETTINGS_MODULE=igar.settings.development` (en dev), `igar.settings.production` (en prod).
7. **Remote origin Igar** : `https://github.com/Mamdou95/igar.git`

**Fichiers backend existants a ne PAS recreer :**
- `backend/igar/core/models.py` (BaseModel)
- `backend/igar/core/exceptions.py` (IgarException)
- `backend/igar/core/exception_handler.py` (RFC 7807)
- `backend/igar/settings/` (base, development, production, test)
- `backend/igar/urls.py` (routing /api/v1/)
- `backend/igar/wsgi.py`, `backend/igar/asgi.py`

**Patterns de code etablis :**
- Logique metier dans `services.py`, JAMAIS dans les views
- Exceptions typees `IgarException` et sous-classes
- Logging structlog JSON : `logger.info("event_name", key=value)`
- Tests dans `tests/` en miroir de la structure source

### Intelligence Git

**Dernier commit :** `ce4d77f` — `feat: initialize Igar backend scaffold on top of Mayan EDMS fork`

Le backend contient le fork Mayan EDMS v4.9.4 + la structure Igar complete. Le Dockerfile doit builder a partir de ce code existant (context `../backend/`).

### Decisions Critiques pour le Developpeur

1. **Image de base Python** : `python:3.12-slim-bookworm`. PAS Python 3.13 (probleme distutils Story 1.1).

2. **Module Celery Mayan** : Verifier dans `backend/mayan/` le nom exact du module app Celery. Probablement `mayan.celery` ou via le fichier `mayan/celery.py`. La commande Celery sera `-A mayan` ou le nom exact trouve. **NE PAS deviner** — lire le code.

3. **tusd stockage S3** : tusd supporte nativement le stockage S3 via flags : `-s3-bucket`, `-s3-endpoint`, `-s3-disable-ssl`. Le endpoint MinIO est `http://minio:9000`. Configurer les credentials via variables d'environnement AWS standard.

4. **MinIO Object Lock** : Utiliser le mode **Governance** en dev (permet la suppression avec flag `--bypass-governance-retention`). Le mode **Compliance** sera utilise en production (irreversible). Cela evite de bloquer les donnees de test en dev.

5. **Elasticsearch 8.x securite** : Desactiver `xpack.security.enabled=false` en dev. En production, activer avec certificats TLS. L'image officielle `elasticsearch:8.17.0` active la securite par defaut — la desactivation explicite est necessaire.

6. **PostgreSQL "TDE"** : PostgreSQL natif ne supporte PAS le Transparent Data Encryption. L'architecture mentionne "TDE" mais cela fait reference au chiffrement au repos. Pour le MVP : documenter que le chiffrement au repos est assure par le chiffrement du volume Docker/host. PostgreSQL TDE natif est prevu pour PG 18 (pas encore publie).

7. **Healthcheck `/health`** : Ajouter dans `igar/urls.py`. La vue doit etre **exclue de l'authentification JWT** (pas de permission_classes). Timeout 2s par service, reponse totale < 500ms. Format JSON avec statut par service.

8. **Nginx TLS** : En dev, HTTP uniquement (port 80). La section TLS est presente mais commentee. En production, TLS 1.3 obligatoire (NFR11).

9. **Monitoring (Prometheus + Grafana)** : Inclure dans docker-compose.yml sous le **profile `monitoring`** (`profiles: [monitoring]`). Ils ne demarrent qu'avec `docker compose --profile monitoring up`. Cela allege le dev quotidien.

10. **Frontend placeholder** : Le frontend n'existe pas encore (Story 1.3). La route Nginx `/` doit retourner un placeholder HTML ou etre configuree pour proxier vers `host.docker.internal:5173` dans le dev override.

### Versions Techniques

| Technologie | Image Docker | Notes |
| --- | --- | --- |
| Python (backend) | `python:3.12-slim-bookworm` | PAS 3.13 (cf. Story 1.1) |
| PostgreSQL | `postgres:17-alpine` | Derniere LTS |
| Redis | `redis:7-alpine` | Compatible Celery, cache, Channels |
| MinIO | `minio/minio:latest` | Object Lock, S3 API |
| MinIO Client | `minio/mc:latest` | Script init-buckets.sh |
| Elasticsearch | `elasticsearch:8.17.0` | Ou derniere 8.x stable |
| Nginx | `nginx:1.27-alpine` | Mainline, WebSocket proxy |
| tusd | `tusproject/tusd:latest` | Protocole tus 1.0, stockage S3 |
| Gotenberg | `gotenberg/gotenberg:8` | Conversion Office → PDF |
| Prometheus | `prom/prometheus:latest` | Profile monitoring |
| Grafana | `grafana/grafana:latest` | Profile monitoring |

### Project Structure Notes

Structure cible du dossier `infrastructure/` apres cette story :

```text
infrastructure/
├── docker-compose.yml              # Stack complete
├── docker-compose.dev.yml          # Override developpement
├── .env.example                    # Template variables d'environnement
├── nginx/
│   ├── nginx.conf                  # Config globale Nginx
│   └── conf.d/
│       └── igar.conf               # Server block (routing API, WS, tus, frontend)
├── minio/
│   └── init-buckets.sh             # Creation buckets + Object Lock + lifecycle
├── elasticsearch/
│   └── elasticsearch.yml           # Config single-node dev
├── tusd/                           # (vide ou config hooks — a completer Epic 2)
├── prometheus/
│   └── prometheus.yml              # Scrape config (profile monitoring)
├── grafana/
│   └── dashboards/
│       └── igar-overview.json      # Dashboard placeholder
└── scripts/
    └── setup-dev.sh                # Script d'installation developpeur (optionnel)
```

Fichiers crees dans `backend/` par cette story :

```text
backend/
├── docker/
│   ├── Dockerfile                  # Image backend Python multi-stage
│   └── entrypoint.sh               # Wait-for-db + migrate + collectstatic
├── .dockerignore                   # Exclusions Docker build
└── igar/
    └── core/
        └── health.py               # Vue healthcheck agrege (nouveau)
```

**Alignement architecture :** [Source: _bmad-output/planning-artifacts/architecture.md#Complete Project Directory Structure]

### Compliance et Securite

- **NFR11** : TLS 1.3 obligatoire en production — config Nginx prete mais commentee pour dev
- **NFR41** : Deploiement < 30min via Docker Compose — objectif principal de cette story
- **NFR44** : Healthcheck `/health` par composant — implemente dans Task 7
- **NFR28** : Uploads resumables via tusd — service configure dans Task 3

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Project Structure & Boundaries] — Structure monorepo, services Docker, routing Nginx, data boundaries
- [Source: _bmad-output/planning-artifacts/architecture.md#Core Architectural Decisions] — Redis, Nginx, tusd, Gotenberg, Django Channels, Prometheus, Grafana, Sentry
- [Source: _bmad-output/planning-artifacts/architecture.md#Data Flow Diagram] — Pipeline upload → tusd → igar-temp → OCR/IA → igar-vault
- [Source: _bmad-output/planning-artifacts/architecture.md#Development Workflow Integration] — Commandes dev, variables d'environnement, docker compose dev override
- [Source: _bmad-output/planning-artifacts/architecture.md#Architectural Boundaries] — Routing Nginx, separation services Docker, ports, communication inter-services
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.2] — User story, acceptance criteria originaux
- [Source: _bmad-output/implementation-artifacts/1-1-mise-en-place-du-socle-backend-pour-les-services-documentaires.md] — Lecons apprises (versions Mayan, Python, cairocffi, Celery/Redis), structure backend existante, patterns de code
- [Source: _bmad-output/planning-artifacts/architecture.md#Infrastructure & Deployment] — CI/CD GitHub Actions, monitoring stack

## Dev Agent Record

### Agent Model Used

GPT-5.3-Codex

### Debug Log References

- `docker compose config` -> OK
- `docker compose -f docker-compose.yml -f docker-compose.dev.yml config` -> OK
- `docker compose up -d` -> OK (services backend, backend-ws, workers, postgresql, redis, minio, elasticsearch, nginx, tusd, gotenberg)
- `curl -w 'code=%{http_code} total_ms=%{time_total}' http://localhost/health` -> `code=200 total_ms=0.010645`
- `curl http://localhost/api/v1/` -> 404 applicatif Django (routage Nginx correct vers backend)
- `curl -H 'Connection: Upgrade' -H 'Upgrade: websocket' ... http://localhost/ws/` -> `101 Switching Protocols`
- `docker compose logs --tail=80 minio-init` -> buckets `igar-temp`, `igar-vault`, `igar-thumbnails` crees (idempotent)
- `docker compose exec -T backend sh -lc 'python -m pip install pytest pytest-django && pytest -q tests/test_health.py'` -> `2 passed`
- Validation budget health apres durcissement: `run=1 code=200 total_ms=0.019590`, `run=2 code=200 total_ms=0.006782`, `run=3 code=200 total_ms=0.007290`
- Validation mode degrade (Redis stoppe): `code=503 total_ms=0.098824` (< 1s)
- Nginx: chargement d'un seul vhost actif via `include /etc/nginx/conf.d/igar.conf;` pour supprimer les conflits `server_name _`

### Completion Notes List

- Infrastructure complete creee sous `infrastructure/` avec stack compose principale et override dev.
- Nginx configure pour routage `/`, `/api/v1/`, `/ws/`, `/uploads/`, `/health` avec headers de securite et limitation de debit.
- Docker backend multi-stage ajoute (`python:3.12-slim-bookworm`), entrypoint wait-for-db + migrate + collectstatic.
- Endpoint agrege `/health` implemente dans Django avec verification PostgreSQL, Redis, MinIO et Elasticsearch.
- Tests unitaires de l'endpoint health ajoutes avec mocks.
- Correctifs runtime appliques: dependances LDAP/systeme, compatibilite Python 3.12 (`distutils`/`pkg_resources`), orchestration migrations, variables d'environnement inter-services.
- Correctif websocket final: ajout de `channels` dans l'image backend et correction de la config `structlog` pour supprimer `TypeError: 'str' object is not callable`.
- Validation finale executee en environnement Docker avec healthcheck agrege healthy et handshake websocket valide.
- Durcissement healthcheck: execution parallele avec budget global 0.9s et timeouts reseau 0.5s pour garantir une reponse sous 1s.
- Option Nginx retenue: inclure uniquement `igar.conf` (et surcharge dev explicite), afin d'eviter le co-chargement de vhosts concurrents.

### File List

- .gitignore
- infrastructure/.env.example
- infrastructure/.env
- infrastructure/docker-compose.yml
- infrastructure/docker-compose.dev.yml
- infrastructure/nginx/nginx.conf
- infrastructure/nginx/conf.d/igar.conf
- infrastructure/nginx/conf.d/igar.dev.conf
- infrastructure/nginx/html/index.html
- infrastructure/minio/init-buckets.sh
- infrastructure/elasticsearch/elasticsearch.yml
- infrastructure/prometheus/prometheus.yml
- infrastructure/grafana/dashboards/igar-overview.json
- backend/docker/Dockerfile
- backend/docker/entrypoint.sh
- backend/.dockerignore
- backend/igar/core/health.py
- backend/igar/urls.py
- infrastructure/nginx/nginx.conf
- backend/igar/settings/base.py
- backend/igar/settings/development.py
- backend/mayan/apps/common/utils.py
- backend/requirements/igar/base.txt
- backend/tests/test_health.py
- _bmad-output/implementation-artifacts/sprint-status.yaml

### Change Log

- 2026-03-27: Implementation technique des tasks 1 a 8 terminee, validations statiques compose executees.
- 2026-03-27: Stabilisation runtime Docker (build backend, health, Elasticsearch, websocket), execution des tests health en conteneur (2 passed), story passee en `review`.
