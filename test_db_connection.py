
from database import get_db_connection


def test_database_connection():
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                result = cursor.fetchone()

                print("Database connection successful!")
                print("Query result:", result[0])

    except Exception as error:
        print("Database connection failed.")
        print("Error type:", type(error).__name__)
        print("Error details:", error)


if __name__ == "__main__":
    test_database_connection()
