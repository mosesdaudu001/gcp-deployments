import pymysql
import os

def get_products(data):
    connection = pymysql.connect(
        unix_socket='sql-server/random-developments:us-central1:game-instance',
        user='moses',
        password="poltxzhlcd",
        database='gaming',
        cursorclass=pymysql.cursors.DictCursor
        )
    with connection:
        with connection.cursor() as cursor:
            sql_query = "INSERT INTO games (name, system, date) VALUES (%s, %s, %s)"
            cursor.execute(sql_query, (data['name'], data['system'], data['date']))
        connection.commit()

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM `games`;")
            result = cursor.fetchall()
            result = [{"name": row["name"], "price": row["system"], "date": row["date"]} for row in result]
            return {"results": result}
data = {
    "name": "Example Game",
    "system": "Example System",
    "date": "2022-01-05"
}
if __name__ == "__main__":
    print(get_products(data))