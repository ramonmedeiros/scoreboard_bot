import logging
import os
import psycopg2
from urllib.parse import urlparse

class Database():

    def __init__(self):
        # db auth
        self.dbUrl = os.environ.get("DATABASE_URL")
        self.conn = self.get_connection()

    def get_connection(self):
        result = urlparse(self.dbUrl)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        # connect
        try:
            conn = psycopg2.connect(dbname=database,
                                    user=username,
                                    password=password,
                                    host=hostname,
                                    port=port)
        except Exception as e:
            logging.error(f"Failed to login to database: {e}")


    def execute_query(self, query, params, select=False):

        try:
            with self.conn as con:
                con.execute(query, params)

                # fetch data in case of query
                if select is True:
                    data = con.fetchall()
                    description = [desc[0] for desc in curs.description]

        except Exception as e:
            logging.error(f"Error while executing {query}: {e}")

        # not select: just return
        if select is False:
            return True

        # return results in a dict with columns
        ret = []
        for row in data:

            # add result according to column
            rowData = {}
            for columnIndex in range(len(row)):
                rowData[description[columnIndex]] = row[columnIndex]
            ret.append(rowData)

        # no results: false
        if len(ret) == 0: return False
        return ret


    def addGame(self, channel, player1, score1, player2, score2):
        query = "INSERT INTO public.games(playerName1, playerName2, score1, score2) VALUES (%s, %s, %s, %s);"
        return self.execute_query(query, (player1, player2, score1, score2))
