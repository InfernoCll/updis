import psycopg2

DATABASE_CONFIG = {
    "dbname": "city_planning",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432"
}

try:
    conn = psycopg2.connect(**DATABASE_CONFIG)
    print("Database connected successfully!")
    conn.close()
except Exception as e:
    print("Database connection failed:", e)
