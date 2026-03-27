# FastAPI Backend

Backend API built with FastAPI, SQLAlchemy, Alembic, and PostgreSQL.

This README is written for the FastAPI Backend project setup:

- FastAPI app entrypoint: `app.main:app`
- ORM: SQLAlchemy
- Migrations: Alembic
- Database: PostgreSQL
- Local config file: `.env.local`
- Docker config file: `.env.docker`
- Docker Compose files:
  - `docker-compose-dev.yml`
  - `docker-compose-wsl.yml`
- Production hosting: Render
- Production database: Neon
- Optional direct Neon URL for migrations: `DIRECT_DATABASE_URL`

---

## 1. What this project expects

This project is designed so that:

- local Python runs default to `.env.local`
- Docker containers receive environment variables from `.env.docker`
- Alembic can use `DIRECT_DATABASE_URL` for Neon migrations when provided
- the API uses `uvicorn` in development and `gunicorn` in production

## Configuration

This project uses a centralized `Settings` class in `config.py` to manage environment-based configuration.

The recommended pattern is:

- define all required application settings in one place
- load local development values from `.env.local`
- allow containerized environments to override values through injected environment variables
- support special cases such as tests or CI with an optional `ENV_FILE` override
- expose computed properties for derived values such as database URLs

### Behavior

With this setup:

- **Local development** defaults to `.env.local`
- **Docker Compose** can inject `.env.docker`, which overrides local values inside the container
- **Tests and CI** can set `ENV_FILE` to point to a different environment file when needed

### Notes

The configuration layer also supports:

- an optional direct database URL override for migrations or other non-standard environments
- automatic switching to a test database name when `testing=true`
- a separate resolved database URL for normal application use versus migrations

### Example workflow

- Run locally with the default local environment file:

  ```bash
  uvicorn app.main:app --reload
  ```

- Run in Docker with container-provided environment variables

- Run tests or CI with a custom environment file:
  ```bash
  ENV_FILE=.env.test pytest
  ```

### Why this approach

This keeps configuration:

- **consistent**, by defining settings in one place
- **flexible**, by supporting local, Docker, test, and CI environments
- **maintainable**, by avoiding repeated connection-string logic across the codebase

## The full implementation lives in `config.py`

## 2. Project structure

The project is organized as follows:

```text
.
├── .github/
│   └── workflows/
│       └── CI-CD.yml
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── app/
│   ├── routers/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── oauth2.py
│   ├── schemas.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_posts.py
│   ├── test_users.py
│   ├── test_utils.py
│   └── test_votes.py
├── .dockerignore
├── .env.docker
├── .env.local
├── .env.prod
├── .gitignore
├── alembic.ini
├── docker-compose-dev.yml
├── docker-compose-wsl.yml
├── Dockerfile
├── gunicorn.service
├── nginx.conf
└── requirements.txt
```

---

## 3. Environment files

Do **not** commit real secrets to GitHub.

Keep `.env.local`, `.env.docker`, and any production secrets out of version control unless they contain only placeholders.

### `.env.local`

Use this for local Python runs.

```env
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_NAME=fastapi
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=yourpassword

SECRET_KEY=replace_with_a_real_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### `.env.docker`

Use this for Docker containers.

```env
DATABASE_HOSTNAME=postgres
DATABASE_PORT=5432
DATABASE_NAME=fastapi
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=yourpassword

SECRET_KEY=replace_with_a_real_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Postgres container variables
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=fastapi
```

### Production environment variables (Render)

Set these in the Render dashboard, not in a committed file:

```env
DATABASE_HOSTNAME=...
DATABASE_PORT=5432
DATABASE_NAME=...
DATABASE_USERNAME=...
DATABASE_PASSWORD=...
DATABASE_SSLMODE=require

SECRET_KEY=replace_with_a_real_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

DIRECT_DATABASE_URL=postgresql://.../neondb?sslmode=require&channel_binding=require
```

---

## 4. First-time local setup

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Make sure your `.env.local` exists before starting the app.

---

## 5. Run locally with local PostgreSQL

Use this path if PostgreSQL is installed directly on your machine and `.env.local` points to it.

### Start the app

```bash
uvicorn app.main:app --reload
```

### Run migrations

```bash
alembic upgrade head
```

### Create a migration

```bash
alembic revision --autogenerate -m "describe your change"
```

### Roll back one migration

```bash
alembic downgrade -1
```

### Open Swagger docs

```text
http://127.0.0.1:8000/docs
```

---

## 6. Run everything with Docker (development)

Use this when both the API and PostgreSQL run in containers.

### Start containers

```bash
docker compose -f docker-compose-dev.yml up --build
```

### Start containers in detached mode

```bash
docker compose -f docker-compose-dev.yml up --build -d
```

### Stop containers

```bash
docker compose -f docker-compose-dev.yml down
```

### Stop containers and remove volumes

```bash
docker compose -f docker-compose-dev.yml down -v
```

### View logs

```bash
docker compose -f docker-compose-dev.yml logs -f
```

### Open a shell in the API container

```bash
docker compose -f docker-compose-dev.yml exec api sh
```

### Run migrations inside the API container

```bash
docker compose -f docker-compose-dev.yml exec api alembic upgrade head
```

### Create a migration inside the API container

```bash
docker compose -f docker-compose-dev.yml exec api alembic revision --autogenerate -m "describe your change"
```

### Run tests inside the API container

```bash
docker compose -f docker-compose-dev.yml exec api pytest -q
```

---

## 7. Run the WSL Docker environment

Use this if you want to run the WSL-specific Compose stack.

### Start services

```bash
docker compose -f docker-compose-wsl.yml up -d
```

### View logs

```bash
docker compose -f docker-compose-wsl.yml logs -f
```

### Stop services

```bash
docker compose -f docker-compose-wsl.yml down
```

### Stop services and remove volumes

```bash
docker compose -f docker-compose-wsl.yml down -v
```

### Run migrations inside the API container

```bash
docker compose -f docker-compose-wsl.yml exec api alembic upgrade head
```

### Run tests inside the API container

```bash
docker compose -f docker-compose-wsl.yml exec api pytest -q
```

### Important note for `docker-compose-wsl.yml`

-> Replace your own image name in the Compose file

---

## 8. Recommended Docker Compose files

This project uses separate Docker Compose files for different development and runtime workflows.

The full configuration should remain in the repository.

### `docker-compose-dev.yml`

Use this file as the default local development setup.

It is intended for a workflow where:

- PostgreSQL runs in Docker
- the FastAPI application also runs in Docker
- the application is built from the local source tree
- source code is mounted into the container
- the API runs with auto-reload enabled for development
- PostgreSQL is exposed on host port `5434`
- a dedicated Docker volume is used for development database persistence

This is the recommended option for everyday development when you want a fully containerized local environment.

### `docker-compose-wsl.yml`

Use this file for the WSL-based runtime setup.

It is intended for a workflow where:

- PostgreSQL runs in Docker
- the API runs from a prebuilt image instead of a local build
- the application is served with Gunicorn and Uvicorn workers
- PostgreSQL is exposed on host port `5433`
- the API is exposed on host port `8001`
- a separate Docker volume is used for database persistence in this environment

This makes it better suited for a more stable container-based runtime than the development Compose file.

### Container networking

When both services run inside Docker Compose, the API container should connect to PostgreSQL using the Compose service name and the container port:

```env
DATABASE_HOSTNAME=postgres
DATABASE_PORT=5432
```

Do not use `localhost` inside the API container, and do not use the published host port such as `5433` or `5434` for container-to-container communication.

### Host machine access

The published host ports are only for access from your machine:

- `5434` for PostgreSQL in `docker-compose-dev.yml`
- `5433` for PostgreSQL in `docker-compose-wsl.yml`

For example, if you run the FastAPI app locally instead of inside Docker, it should connect through the mapped host port, not the internal container port.

### Recommendation

Keep the full Docker Compose definitions in `docker-compose-dev.yml` and `docker-compose-wsl.yml`, and use the README to explain:

- what each file is for
- which workflow is the default
- how services communicate inside Docker
- which host ports are exposed externally

---

## 9. Testing

This project uses `pytest` for automated testing.

### Run all tests locally

```bash
pytest --disable-warnings -v -s -x
```

This is the main test command used in this project. It runs the full test suite with verbose output, shows standard output directly, suppresses warning noise, and stops on the first failure.

### Run all tests locally (quiet mode)

```bash
pytest -q
```

Use this when you want a shorter, less verbose test output.

### Run a single test file

```bash
pytest tests/test_users.py -q
```

### Run a single test file with verbose output

```bash
pytest tests/test_users.py -v
```

### Stop on the first failure

```bash
pytest -x
```

### Recommended test setup

Use a dedicated test database and enable testing mode before running the test suite.

With the current configuration, `TESTING=true` automatically makes the application use a database name with the `_test` suffix. In practice, that means:

- if `DATABASE_NAME=fastapi`, tests will use `fastapi_test`
- you should not usually set `DATABASE_NAME=fastapi_test` together with `TESTING=true`, because that would produce `fastapi_test_test`

A typical test configuration therefore looks like this:

```env
DATABASE_NAME=fastapi
TESTING=true
```

This helps keep test data isolated from your main development database.

### How tests work in this project

The test setup uses pytest fixtures to:

- enable testing mode automatically
- create a separate SQLAlchemy session for each test
- override the FastAPI database dependency
- create and clean up database tables for each test function
- generate test users, authentication tokens, and sample post data

This keeps tests isolated and reduces the risk of one test affecting another.

### CI test workflow

The CI pipeline follows the same general pattern in GitHub Actions:

- start a PostgreSQL service
- set `TESTING=true`
- run Alembic migrations
- execute the test suite with pytest

---

## 10. Alembic and migrations

This project uses Alembic to manage database schema changes.

### Create a migration

```bash
alembic revision --autogenerate -m "describe your change"
```

Use this after updating your SQLAlchemy models to generate a new migration script.

### Apply all migrations

```bash
alembic upgrade head
```

This applies all pending migrations to the current database.

### Roll back the most recent migration

```bash
alembic downgrade -1
```

Use this to undo the latest migration during development if needed.

### Show the current revision

```bash
alembic current
```

### Show migration history

```bash
alembic history
```

### Recommended Alembic setup

Alembic should use the same configuration source as the application instead of duplicating database connection logic.

In this project, the recommended pattern is:

- use the normal application database URL for standard migrations
- allow an optional `DIRECT_DATABASE_URL` override for environments that require a direct connection, such as certain hosted database providers (NEON)
- keep the database URL resolution in `config.py` and let Alembic read from that centralized settings layer

In practice, `alembic/env.py` should set Alembic's `sqlalchemy.url` from `settings.migration_database_url`.

This keeps migration behavior aligned with the application and avoids maintaining separate connection logic in multiple places.

### Why this approach is useful

This setup helps keep migrations:

- consistent, because both the app and Alembic rely on the same settings source
- flexible, because direct connection overrides remain available when required
- easier to maintain, because connection string logic lives in one place

````

---

## 11. Build and publish to Docker Hub

### Build the image

```bash
 docker image tag your-docker-image-name your-docker-hub-username/docker-hub-username:your-docker-image-name
````

### Log in to Docker Hub

```bash
docker login
```

### Push the image

```bash
docker push your-docker-hub-username/docker-hub-username:your-docker-image-name
```

### Optional versioned tag

```bash
docker build -t your-docker-hub-username/fastapi-backend:v1.0.0 .
docker push your-docker-hub-username/fastapi-backend:v1.0.0
```

### Pull and run the published image locally

```bash
docker pull your-docker-hub-username/fastapi-backend:latest
docker run --env-file .env.docker -p 8000:8000 your-docker-hub-username/fastapi-backend:latest
```

---

## 12. Production deployment with Render + Neon

### Production database

Use Neon as the hosted PostgreSQL database.

Recommended production variables:

```env
DATABASE_HOSTNAME=your-neon-host
DATABASE_PORT=5432
DATABASE_NAME=your_db_name
DATABASE_USERNAME=your_user
DATABASE_PASSWORD=your_password
DATABASE_SSLMODE=require

DIRECT_DATABASE_URL=postgresql://.../neondb?sslmode=require&channel_binding=require

SECRET_KEY=replace_with_a_real_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Deploy on Render from a Dockerfile

If Render builds your app from the repository Dockerfile:

1. Push your latest code to GitHub
2. Create a new Web Service on Render
3. Point Render to the repository
4. Choose Docker-based deploy
5. Set all environment variables in the Render dashboard
6. Deploy

### Deploy on Render from Docker Hub

If Render pulls a prebuilt image:

1. Build and push the Docker image to Docker Hub
2. Create a new Web Service on Render
3. Choose the option to deploy from an image/registry
4. Set the image, for example:

```text
yourdockerhubusername/fastapi-backend:latest
```

5. Set all environment variables in the Render dashboard
6. Deploy

### Production start command

If your deployment requires a command, use:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
```

### Run production migrations

Start Command
Render runs this command to start your app with each deploy:

```bash
bash -c "python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

If you run migrations against Neon, `DIRECT_DATABASE_URL` should point to the direct connection string.

## 13. Linux commands

1. WSL commands

List available WSL distributions:

```bash
wsl -l -v
```

Open Ubuntu 24.04 as root:

```bash
wsl -d Ubuntu-24.04 -u root
```

2. systemd service commands

Check service status:

```bash
sudo systemctl status api.service
```

Disable and stop the service:

```bash
sudo systemctl disable --now api.service
```

Enable and start the service:

```bash
sudo systemctl enable --now api.service
```

3. SSH key setup for GitHub Actions deploy

If you do not already have an SSH key, generate one on your local machine
(Linux, macOS, or WSL):

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keygen -t ed25519 -C "github-actions-deploy"
```

When prompted:

- Press Enter to use the default file path
- Press Enter for an empty passphrase
- Press Enter again to confirm

4. Show your SSH keys

Private key:

```bash
cat ~/.ssh/id_ed25519
```

Public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

Use them like this:

- Put the private key into the GitHub secret: PROD_SSH_PRIVATE_KEY
- Put the public key into the Ubuntu server file: ~/.ssh/authorized_keys

5. Add the public key to the Ubuntu server

Step 1: Show your public key on your current machine

```bash
cat ~/.ssh/id_ed25519.pub
```

It will print one long line similar to this:

ssh-ed25519 <generated-key-data> github-actions-deploy

Copy the entire line.

Step 2: Connect to the Ubuntu server

```bash
ssh your_username@your_server_ip
```

If this is your own PC, open its terminal directly.

Step 3: Create the SSH folder and authorized_keys file on the Ubuntu server

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

What these commands do:

- mkdir -p ~/.ssh -> creates the .ssh folder if it does not exist
- chmod 700 ~/.ssh -> makes the folder private
- touch ~/.ssh/authorized_keys -> creates the authorized_keys file if it does not exist
- chmod 600 ~/.ssh/authorized_keys -> makes the file private

Step 4: Add the public key to authorized_keys

Open the file:

```bash
nano ~/.ssh/authorized_keys
```

Paste the public key line you copied from:

```bash
cat ~/.ssh/id_ed25519.pub
```

Save and exit:

- Ctrl + O
- Enter
- Ctrl + X

6. Get the public IP from CLI

Option 1:

```bash
curl ifconfig.me
```

Option 2:

```bash
curl https://api.ipify.org
```

## 7. How the GitHub Actions runner works for this project

This project uses a self-hosted GitHub Actions runner for the Ubuntu / WSL deployment job.

How it works:

- GitHub matches the deploy job to a runner with the required labels
- the job runs directly on that runner machine
- the repository is checked out into the runner workspace
- deployment commands run locally on that same machine
- SSH is not required for deployment to the runner itself

If your workflow uses labels such as:

```yaml
runs-on: [self-hosted, linux, x64, ubuntu-wsl]
```

then the runner must have those labels to receive the job.

### Typical runner setup commands

GitHub provides the exact commands during runner setup in:

**Repository Settings > Actions > Runners > New self-hosted runner**

For the current setup, the runner is being used from WSL and is currently located here:

```bash
/mnt/c/Users/user/actions-runner
```

A setup for this project would look like this:

```bash
cd /mnt/c/Users/user
mkdir -p actions-runner
cd actions-runner
curl -o actions-runner-linux-x64-2.333.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.333.0/actions-runner-linux-x64-2.333.0.tar.gz
echo "<published-sha256-checksum>  actions-runner-linux-x64-2.333.0.tar.gz" | shasum -a 256 -c
tar xzf ./actions-runner-linux-x64-2.333.0.tar.gz
./config.sh --url https://github.com/ras-dec19/FastAPI-Project --token <generated-registration-token>
./run.sh
```

### Notes

- `./config.sh` registers the runner with your repository
- `./run.sh` starts the runner manually in the current shell session
- in this setup, running `cd actions-runner` worked because the runner folder is under `/mnt/c/Users/user/`, not under `~/actions-runner`
- the download URL, version, and registration token are generated by GitHub during setup and may change over time
- right now, the runner is not installed as a service yet, which is why you have to start it manually with `./run.sh`
- if you want the runner to start automatically when the WSL Ubuntu environment starts, you can install it as a service after configuration

### Optional service-based startup

If you install the runner as a Linux service, you can manage it with:

```bash
cd /mnt/c/Users/user/actions-runner
sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status
```

### WSL note

You only need to add the following if `systemctl` is not working in your WSL Ubuntu environment. If `systemctl` already works, you do not need to add this.

If `systemctl` is not working, fix WSL first:

```bash
sudo nano /etc/wsl.conf
```

Put in:

```ini
[boot]
systemd=true
```

Then from Windows PowerShell:

```powershell
wsl.exe --shutdown
```

For this project, the important point is that the deploy job runs on the self-hosted runner machine itself, so no SSH step is needed for deployment to that same machine.

## 14. Git ignore recommendation

Make sure `.gitignore` includes at least:

```gitignore
venv/
__pycache__/
.pytest_cache/
.env
.env.*
```

Make sure `.dockerignore` includes at least:

```dockerignore
__pycache__/
venv/
.pytest_cache
.env
.env.*
.gitignore
Dockerfile*
docker-compose*.yml
gunicorn.service
nginx.conf
```

---

## 15. Notes

- Use `.env.local` for local Python commands.
- Use `.env.docker` for Docker containers.
- Use `localhost` when the Python process runs on your machine.
- Use `postgres` when the Python process runs inside Docker Compose.
- Use `DIRECT_DATABASE_URL` for Neon migrations when available.
- Prefer a separate test database for `pytest`.
