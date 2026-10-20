
import time

from database import get_db_connection


def claim_pending_transaction():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
               
            """
            WITH next_transaction AS (
                SELECT transaction_id
                FROM public.transactions
                WHERE status = 'PROCESSING'
                AND processed_at IS NULL
                AND (
                    claimed_at IS NULL
                    OR claimed_at < NOW() - INTERVAL '5 minutes'
                )
                ORDER BY created_at
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            )
            UPDATE public.transactions AS transaction
            SET claimed_at = NOW()
            FROM next_transaction
            WHERE transaction.transaction_id = next_transaction.transaction_id
            RETURNING transaction.transaction_id;
            """

            )

            row = cursor.fetchone()
            return row[0] if row else None


def mark_transaction_processed(transaction_id):
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE public.transactions
                SET status = 'PROCESSED',
                    processed_at = NOW()
                WHERE transaction_id = %s
                  AND status = 'PROCESSING'
                  AND processed_at IS NULL
                """,
                (transaction_id,),
            )
            return cursor.rowcount == 1



def process_pending_transactions():
    print("Background worker started.")

    while True:
        try:
            transaction_id = claim_pending_transaction()

            if transaction_id is None:
                time.sleep(2)
                continue

            print(f"Processing transaction: {transaction_id}")
            print("Simulating external processing for 30 seconds...")

            time.sleep(30)

            if mark_transaction_processed(transaction_id):
                print(
                    f"Transaction {transaction_id} "
                    "processed successfully."
                )
            else:
                print(
                    f"Could not mark {transaction_id} as processed."
                )

        except Exception as error:
            print(
                f"Worker error: {type(error).__name__}: {error}"
            )
            time.sleep(2)


if __name__ == "__main__":
    process_pending_transactions()

