# AI-SQL

AI-SQL is a local natural language to SQL prototype. It uses a local LLM model to generate PostgreSQL `SELECT` queries from natural language questions.

This project is made for learning and thesis work. It is not production ready.

## Features

- Local LLM-based SQL generation
- PostgreSQL database
- FastAPI backend
- Flet user interface
- User login
- Admin-only user and database management
- Argon2 password hashing
- Basic SQL validation
- Docker support for backend and PostgreSQL

## Project structure

```text
backend/              FastAPI backend
core/                 Main application logic
ui/                   Flet user interface
logs/schema.json      Allowed schema file for the LLM
logs/sql_prompt.txt   Prompt file for SQL generation
Dockerfile
docker-compose.yaml
Main.py
requirements.txt
```

## Requirements

- Python 3.11 ->
- Docker
- Docker Compose
- Local GGUF model file

The project expects the model file in the project root:

```text
example.gguf
```

The model file may not be included in the repository because it can be large.

## Environment variables

The required environment variables can be defined either in a `.env` file or exported from the shell, for example from `~/.bashrc`.

Required variables:

```text
POSTGRES_USER
POSTGRES_PASSWORD
DB_READ_USER
DB_READ_PASS
DB_WRITE_USER
DB_WRITE_PASS
```

Example for `~/.bashrc`:

```bash
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres

export DB_READ_USER=postgres
export DB_READ_PASS=postgres

export DB_WRITE_USER=postgres
export DB_WRITE_PASS=postgres
```

After editing `~/.bashrc`, reload it:

```bash
source ~/.bashrc
```

For development, the same PostgreSQL user can be used for both read and write connections. For a more secure setup, separate read and write users should be created in PostgreSQL.

## Start backend and database

Start PostgreSQL and the FastAPI backend:

```bash
docker compose up --build
```

Backend runs at:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/health
```

Expected response:

```json
{
  "ok": true
}
```

## Create the first admin user

Create the first user inside the backend container:

```bash
docker compose exec backend python Main.py
```

If there are no users in the database, the program asks you to create the first user. The first user becomes an admin user.

After the user has been created, you can log in from the Flet user interface.

## Start the user interface

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Flet UI:

```bash
export API_BASE=http://localhost:8000
python -m ui.Window
```

On Windows PowerShell:

```powershell
$env:API_BASE="http://localhost:8000"
python -m ui.Window
```

## Basic usage

1. Start backend and PostgreSQL with Docker Compose.
2. Create the first admin user.
3. Start the Flet UI.
4. Log in.
5. Create a table from the `Database` view.
6. Ask a natural language question from the `Query` view.

Example row format in the `Database` view:

```text
Brake pad;BP-100;brake;29.90
Oil filter;OF-200;filter;12.50
Spark plug;SP-300;engine;8.90
```

Example question:

```text
Show all parts where category is brake
```

## API endpoints

```text
GET  /health
POST /login
POST /aisql
POST /add_user
POST /delete_user
POST /database
POST /delete_table
POST /delete_part
PUT  /update_part
PUT  /update_user
```

## Important files

The project uses these files from the `logs` folder:

```text
logs/schema.json
logs/sql_prompt.txt
```

`schema.json` defines the tables and columns that the LLM is allowed to use.

`sql_prompt.txt` defines the SQL generation instructions for the LLM.

## Security notes

This project includes basic security features:

- passwords are hashed with Argon2
- admin actions require admin rights
- the LLM query path uses a read-only database session
- generated SQL must start with `SELECT`
- SQL containing semicolons is rejected
- table identifiers are handled with `psycopg.sql.Identifier` in admin operations

This is not enough for production use. SQL validation is still basic and should be improved before using the system with sensitive data.

## Troubleshooting

### Backend does not start

Check that Docker is running and that the required environment variables are available:

```bash
echo $POSTGRES_USER
echo $DB_READ_USER
echo $DB_WRITE_USER
```

Also check that the model file exists in the project root:

```text
example.gguf
```

### SQL generation does not work

Check that these files exist:

```text
logs/schema.json
logs/sql_prompt.txt
```

Also check that the model file path in `docker-compose.yaml` matches the actual model filename.

### UI cannot connect to backend

Check that the backend is running:

```text
http://localhost:8000/health
```

Then check that `API_BASE` is set correctly:

```bash
export API_BASE=http://localhost:8000
```

### Login does not work

Create the first admin user:

```bash
docker compose exec backend python Main.py
```

## License

Apache-2.0
