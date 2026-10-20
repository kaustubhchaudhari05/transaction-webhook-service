# Transaction Webhook Service

A Python backend service that accepts transaction webhooks, stores transactions in PostgreSQL, and processes them asynchronously using a background worker.

## Features

- REST API built with FastAPI.
- PostgreSQL persistence.
- Duplicate transaction protection using a unique transaction ID.
- Asynchronous transaction processing using a background worker.
- Simulated 30-second processing delay.
- Transaction status endpoint.
- Health-check endpoint.
- Automatic recovery of stale worker claims.

## Technology Stack

- Python
- FastAPI
- PostgreSQL (Supabase)
- Psycopg
- Pydantic

## Project Structure

```text
transaction-webhook-service/
├── main.py
├── worker.py
├── database.py
├── schemas.py
├── test_db_connection.py
├── .env
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.11 or compatible version
- PostgreSQL database
- pip

## Configuration

Create a `.env` file in the project root:

```env
DATABASE_URL=your_postgresql_connection_string
```

Do not commit `.env` or expose database credentials.

## Installation

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows Command Prompt:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install fastapi uvicorn "psycopg[binary]" python-dotenv
```

## Database Setup

Create the `public.transactions` table in PostgreSQL with the required transaction fields, status, timestamps, and uniqueness constraint on `transaction_id`.

Ensure the database schema matches the application's SQL queries.

## Run the API

```bash
uvicorn main:app --reload
```

API documentation:

http://127.0.0.1:8000/docs

## Run the Background Worker

Open a second terminal, activate the virtual environment, and run:

```bash
python worker.py
```

Keep the worker running while testing transaction processing.

## API Endpoints

### Health Check

`GET /`

Returns the service health status and current timestamp.

### Receive Transaction

`POST /v1/webhooks/transactions`

Example request:

```json
{
  "transaction_id": "txn_001",
  "source_account": "ACC_1001",
  "destination_account": "ACC_2002",
  "amount": 2500.00,
  "currency": "INR"
}
```

Expected response: `202 Accepted`.

### Get Transaction Status

`GET /v1/transactions/{transaction_id}`

Returns the transaction's status, creation timestamp, and processing timestamp.

Possible statuses:

- `PROCESSING`
- `PROCESSED`

Unknown transaction IDs return `404 Not Found`.

## Processing Flow

1. The API validates the incoming webhook.
2. The transaction is stored in PostgreSQL.
3. The API responds with `202 Accepted`.
4. The background worker claims pending transactions.
5. The worker simulates external processing with a 30-second delay.
6. The worker updates the transaction status and processing timestamp.

## Reliability

The database's unique transaction ID prevents duplicate rows. Worker claims use timestamps so stale claims can become eligible for recovery after five minutes.

The external processing step is currently simulated. Production integrations would require additional safeguards against repeated external side effects.

## Security

- Keep database credentials in environment variables.
- Never commit `.env`.
- Use HTTPS for public deployments.
- Configure production secrets and database access appropriately.
