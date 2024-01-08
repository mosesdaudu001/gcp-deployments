# Commands

## Cloud SQL pricing calculator

https://cloud.google.com/sql/pricing#cpu-mem-pricing

## cloud_sql_proxy
Tool used for tunneling from local machine

https://cloud.google.com/sql/docs/mysql/sql-proxy

Step 1:
    Create a mysql instance in google cloud mysql

Step 2:
    Create a database

Step 3:
    Create a user

Step 4:
    Add IAM role to service account for `Cloud Functions Service Agent` and enable `cloud sql admin API`

## Proxy from localhost
```
$ mkdir cloudsql
$ ./cloud_sql_proxy -instances=yt-py-345518:us-west4:vlad-postgres -dir=cloudsql
```

## Connect to the proxy
Connect to the socket using the MySQL client. 
You have to be in the same directory, or else adjust the path to the socket.

```
mysql -u root -p -S cloudsql/inspired-victor-367616\:us-west4\:test-mysql
```

## Python virtual environment
Create new virtual environment in Python and install requirements.

```
$ python3 -m venv my_env
$ my_env/bin/pip install -r requirements.txt
```