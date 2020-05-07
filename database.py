import logging
import os
import psycopg2


class Database():

    def __init__(self):
        # db auth
        self.user = os.environ.get("DB_USER")
        self.passwd = os.environ.get("DB_PASS")

        # db config
        self.host = os.environ.get("DB_HOST")
        self.port = os.environ.get("DB_PORT")
        self.dbName = os.environ.get("DB_NAME")
        self.conn = self.get_connection()

    def get_connection(self):

        # connect
        try:
            conn = psycopg2.connect(dbname=self.dbName,
                                    user=self.user,
                                    password=self.passwd,
                                    host=self.host,
                                    port=self.port)
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
