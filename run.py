import os
import psycopg2
import apis.rates

from datetime import datetime, timedelta
from flask import Flask
from flask import request


app = Flask(__name__)


# Connect to db
def get_db_connection():
    dbconn = psycopg2.connect(host='0.0.0.0',
                            database='postgres',
                            user=os.environ['PGUSERNAME'],
                            password=os.environ['PGPASSWORD'])
    return dbconn


@app.route("/rates")
def rates():
    source: str = request.args.get("origin")
    destination: str = request.args.get("destination")
    date_from: str = request.args.get("date_from")
    date_to: str = request.args.get("date_to")
    date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    date_from = datetime.strptime(date_from, '%Y-%m-%d').date()

    conn = get_db_connection()
    cur = conn.cursor()

    rate_list = apis.rates.get_rates(source, destination, date_from, date_to, cur)
    cur.close()

    return rate_list


if __name__ == "__main__":
    app.run(debug=True)


