
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status

from psycopg.errors import UniqueViolation

from database import get_db_connection
from schemas import TransactionStatusResponse, TransactionWebhook


app = FastAPI()


@app.get("/")
def health_check():
    return {
        "status": "HEALTHY",
        "current_time": datetime.now(timezone.utc).isoformat(),
    }


@app.post(
    "/v1/webhooks/transactions",
    status_code=status.HTTP_202_ACCEPTED,
)
def receive_transaction(transaction: TransactionWebhook):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO public.transactions (
                        transaction_id,
                        source_account,
                        destination_account,
                        amount,
                        currency
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        transaction.transaction_id,
                        transaction.source_account,
                        transaction.destination_account,
                        transaction.amount,
                        transaction.currency,
                    ),
                )

    except UniqueViolation:
        # The transaction ID already exists.
        # Treat this request as a duplicate webhook.
        pass

    return {
        "message": "Transaction accepted",
        "transaction_id": transaction.transaction_id,
        "status": "PROCESSING",
    }


@app.get(
    "/v1/transactions/{transaction_id}",
    response_model=TransactionStatusResponse,
)
def get_transaction_status(transaction_id: str):
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    transaction_id,
                    status,
                    created_at,
                    processed_at
                FROM public.transactions
                WHERE transaction_id = %s
                """,
                (transaction_id,),
            )

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    return {
        "transaction_id": row[0],
        "status": row[1],
        "created_at": row[2],
        "processed_at": row[3],
    }
