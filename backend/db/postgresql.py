import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="test_db",
        user="test_user",
        password="testing",
        port="5432"
    )

    print("Connection Succesfull")

    cur = conn.cursor()
    cur.execute("SELECT version();")

    db_version = cur.fetchone()
    print("Version", db_version)

    cur.close()
    conn.close()

except Exception as e:
    print("Error: ", e)