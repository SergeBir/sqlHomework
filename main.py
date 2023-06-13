import psycopg2

conn = psycopg2.connect(database="clients_db", user="postgres", password="")


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            email VARCHAR(100),
            phones VARCHAR(255)[]);
            """)
    conn.commit()


def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clients (first_name, last_name, email, phones)
            VALUES (%s, %s, %s, %s);
        """, (first_name, last_name, email, phones))
    conn.commit()


def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE clients
            SET phones = array_append(phones, %s)
            WHERE id = %s;
        """, (phone, client_id))
    conn.commit()


def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        update_fields = []
        update_values = []
        if first_name:
            update_fields.append('first_name = %s')
            update_values.append(first_name)
        if last_name:
            update_fields.append('last_name = %s')
            update_values.append(last_name)
        if email:
            update_fields.append('email = %s')
            update_values.append(email)
        if phones:
            update_fields.append('phones = %s')
            update_values.append(phones)
        update_values.append(client_id)
        if update_fields:
            update_query = ', '.join(update_fields)
            cur.execute(f"""
                UPDATE clients
                SET {update_query}
                WHERE id = %s;
            """, tuple(update_values))
    conn.commit()


def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE clients
            SET phones = array_remove(phones, %s)
            WHERE id = %s;
        """, (phone, client_id))
    conn.commit()


def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM clients
            WHERE id = %s;
        """, (client_id,))
    conn.commit()


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        query = """
            SELECT * FROM clients
            WHERE 1=1
        """
        values = []

        if first_name:
            query += " AND first_name = %s"
            values.append(first_name)

        if last_name:
            query += " AND last_name = %s"
            values.append(last_name)

        if email:
            query += " AND email = %s"
            values.append(email)

        if phone:
            query += " AND %s = ANY (phone_numbers)"
            values.append(phone)

        cur.execute(query, tuple(values))
        result = cur.fetchall()
        return result


create_db(conn)
add_client(conn, "Ivar", "The Boneless", "ivar.theboneless@example.com", ["1234567891", "9876543211"])
add_phone(conn, 1, "1636656666")
change_client(conn, 1, first_name="Ragnar", last_name="Lothbrok")
# delete_phone(conn, 1, "1234567891")
# delete_client(conn, 1)
result = find_client(conn, first_name="Ivar")
print(result)

conn.close()
