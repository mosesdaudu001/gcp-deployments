import pymysql
import os

def get_products(data):
  connection = pymysql.connect(
    unix_socket='/cloudsql/random-developments:us-central1:game-instance', # gcp recognises cloudsql as the source
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

def hello_world(request):
  request_json = request.get_json()
  return get_products(request_json)
