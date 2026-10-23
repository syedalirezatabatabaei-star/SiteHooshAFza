# 🔐 Secrets with Infisical

This project no longer reads secrets from a local `.env` file. The run scripts
([run.sh](run.sh), [run.ps1](run.ps1)) fetch them from [Infisical](https://infisical.com)
at startup and inject them into the environment. Django, FastAPI and the Docker
containers keep reading the same variables (`SECRET_KEY`, `DB_PASSWORD`, `JWT_SECRET_KEY`, ...),
so no application code changes.

- `run.sh` and `run.ps1` wrap themselves with `infisical run` automatically.
- `.infisical.json` holds only the project link (no secrets) and is safe to commit.
- `.env` is ignored by git; after migration it is kept only as `.env.backup` and is no longer read.

## 1. Create the project and import the secrets

1. Sign up / log in at <https://app.infisical.com>.
2. `Secrets Management` → `+ Add New Project`. Name it after the service (e.g. `hooshafza`).
   Every project starts with `Development`, `Staging` and `Production`.
3. Open the project's `Secrets Overview` page and drag and drop the existing `.env` file
   onto it (or use `Paste Secrets`) to import everything at once. Delete the `.env`
   import afterwards so the values exist only in Infisical.

## 2. Install the CLI and link the project (local development)

```bash
# macOS
brew install infisical/get-cli/infisical
# Windows
winget install infisical
# Debian/Ubuntu
curl -1sLf 'https://artifacts-cli.infisical.com/setup.deb.sh' | sudo -E bash
sudo apt-get update && sudo apt-get install -y infisical

infisical login          # opens a browser
infisical login -i       # use this on a headless server, WSL 2, Codespaces or SSH

cd <project-root>
infisical init           # writes .infisical.json (no secrets, safe to commit)
```

For local development, run the stack with the `dev` environment:

```bash
INFISICAL_ENV=dev ./run.sh start      # Linux/macOS
$env:INFISICAL_ENV = 'dev'; .\run.ps1 start   # Windows
```

## 3. Server / production (non-interactive)

On a server, CI runner or any machine without a browser, do not use interactive
login. Create a **machine identity** and use **Universal Auth**:

1. In Infisical: `Access Control` → `Machine Identities` → `Create`.
2. Add a client secret under the identity's `Universal Auth` configuration.
3. Add the identity to the project (`Access Control` → `Machine Identities` →
   `Add Machine Identity to Project`) with the minimum role and environment it needs
   (for this service: `Production`).
4. On the server, provide these as real environment variables — from the platform's
   own secret store (systemd unit, Docker secret, CI secret), never in a committed file:

```bash
export INFISICAL_ENV=prod
export INFISICAL_PROJECT_ID=<project-id>                  # machine identities ignore .infisical.json
export INFISICAL_CLIENT_ID=<machine-identity-client-id>
export INFISICAL_CLIENT_SECRET=<machine-identity-client-secret>
```

For EU Cloud or self-hosting, also set `INFISICAL_DOMAIN` (e.g. `https://eu.infisical.com`).

Then start as usual; the script authenticates with the machine identity, gets a
short-lived token and injects the secrets:

```bash
./run.sh start        # Linux/macOS
.\run.ps1 start       # Windows
```

Alternatively, obtain a token yourself and the scripts will reuse it:

```bash
export INFISICAL_TOKEN=$(infisical login --method=universal-auth \
  --client-id=<id> --client-secret=<secret> --silent --plain)
./run.sh start
```

Reference: [machine identities](https://infisical.com/docs/documentation/platform/identities/machine-identities),
[universal auth](https://infisical.com/docs/documentation/platform/identities/universal-auth).

## 4. Verify the migration

```bash
# Secrets resolve from Infisical, not from disk:
mv .env .env.backup       # .env.backup is git-ignored and no longer read
./run.sh restart
docker exec hooshafza-backend python -c "import os; print('SECRET_KEY length:', len(os.environ['SECRET_KEY']))"
```

The command should print a length (never the value) and the stack should start
normally with `.env` renamed away.

## 5. If secrets were ever committed

Git history keeps values, so **rotate every credential that was committed**
(Django `SECRET_KEY`, `JWT_SECRET_KEY`, database passwords, payment and SpotPlayer
keys) after moving to Infisical. Scan the repository and its history with:

```bash
infisical scan git
```

See <https://infisical.com/docs/cli/scanning-overview>.

## 6. Server troubleshooting

**`Fatal glibc error: CPU does not support x86-64-v2`** — later MySQL 8.x images
are based on Oracle Linux 9 and require a newer CPU (x86-64-v2). The scripts now
default to `mysql:8.0.28`: it is the latest 8.0 line that still runs on
pre-x86-64-v2 CPUs (Oracle Linux 8 based). To use another image explicitly:

```bash
export MYSQL_IMAGE=mysql:8.0.28   # or any image your CPU supports
```

**`django.db.utils.NotSupportedError: MySQL 8.0.11 or later is required` (found
5.7.x)** — Django (>=5.0) rejects MySQL 5.7, so after switching to the 8.0.28
image a **new database** is created from scratch. Your data lives in the old
`mysql` 5.7 container; migrate it before bringing the stack up:

```bash
# 1) Dump the old MySQL 5.7 container (needs PORT 3306 not published, or use
#    an SSH tunnel / mysql client on the server)
docker exec mysql sh -c 'exec mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --databases hooshafza' > ./hooshafza-57.sql

# 2) Start the stack (a new mysql:8.0.28 container, named hooshafza-mysql).
./run.sh restart

# 3) Import the dump into the new 8.0.28 database
docker exec -i hooshafza-mysql sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD"' < ./hooshafza-57.sql
rm ./hooshafza-57.sql
```

**`django.db.utils.OperationalError: (2005, "Unknown server host 'hooshafza-mysql'")`** —
the app containers could not resolve the database hostname. Two ways to fix it:

1. **Preferred (automatic):** leave `DB_HOST` at its default (`hooshafza-mysql`) in
   Infisical. If a standalone `mysql` container is already running on the server
   and is version 8.0 or newer, the script reuses it, attaches it to
   `hooshafza-net` and points the app containers at it (`DB_HOST=mysql`).
2. **Manual:** set `DB_HOST` in Infisical to the real database host (e.g. the
   existing container's name `mysql`, or an external DB host). Any `DB_HOST`
   other than `hooshafza-mysql` is passed through untouched. The database must
   still be reachable from the app containers' Docker network
   (`docker network connect hooshafza-net mysql` attaches an existing container).

## Required variables

The run scripts refuse to start unless Infisical provides at least:

`SECRET_KEY`, `DEBUG`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_ROOT_PASSWORD`,
`JWT_SECRET_KEY`, `SITE_DOMAIN`.
