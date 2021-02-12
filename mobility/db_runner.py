import psycopg2


def run_sql(servers, sql):
    
    for server in servers:
        
        connection = psycopg2.connect(
            host = server['host'],
            database = server['db'],
            user = server['user'],
            password = server['password']
        )
        cursor= connection.cursor()
        
        for row in sql:
            cursor.execute(row)
        
        connection.commit()
        cursor.close()
        connection.close()


def get_once(server, sql):
    connection = psycopg2.connect(
        host = server['host'],
        database = server['db'],
        user = server['user'],
        password = server['password']
    )
    cursor= connection.cursor()
    cursor.execute(sql)

    records = cursor.fetchall()

    cursor.close()
    connection.close()
    
    return records
