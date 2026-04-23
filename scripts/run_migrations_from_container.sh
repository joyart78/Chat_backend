#!/bin/sh

cp ./alembic.ini.example ./alembic.ini
awk '{ sub("sqlalchemy.url = postgresql://local:local@localhost:5469/local", "sqlalchemy.url = postgresql://"ENVIRON["DB_USER"]":"ENVIRON["DB_PASSWORD"]"@"ENVIRON["DB_HOST"]":"ENVIRON["DB_PORT"]"/"ENVIRON["DB_NAME"]); print }' alembic.ini.example >alembic.ini
alembic upgrade head
