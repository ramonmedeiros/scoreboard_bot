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
        # connect
        try:
            result = urlparse(self.dbUrl)
            return psycopg2.connect(dbname=result.path[1:],
                                    user=result.username,
                                    password=result.password,
                                    host=result.hostname,
                                    port=result.port)
        except Exception as e:
            logging.error(f"Failed to login to database: {e}")

    def execute_query(self, query, params, select=False):
        try:
            with self.conn.cursor() as con:
                con.execute(query, params)

                # insert: assert success and return
                if select is False:
                    assert con.rowcount == 1, "Insert failed"
                    self.conn.commit()
                    return True

                # fetch data in case of query
                data = con.fetchall()
                description = [desc[0] for desc in con.description]
        except Exception as e:
            logging.error(f"Error while executing {query % params}: {e}")
            return False

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

    def get_games_per_channel(self, channel):
        query = "SELECT * FROM public.games WHERE channel=%s;"
        return self.execute_query(query=query, params=(channel,), select=True)

    def addGame(self, channel, player1, score1, player2, score2):
        query = 'INSERT INTO public.games("playerName1", "playerName2", score1, score2, channel) VALUES (%s, %s, %s, %s, %s);'
        return self.execute_query(query=query,
                                  params=(
                                      player1,
                                      player2,
                                      score1,
                                      score2,
                                      channel,
                                  ))
    def save_token(self, appid, token):
        query = 'INSERT INTO public.tokens(appid, token) VALUES (%(id)s, %(t)s) ON CONFLICT (appid) DO UPDATE SET token = %(t)s'
        return self.execute_query(query=query,
                                  params={"id": appid, "t": token})

    def get_token(self, appid):
        query = 'SELECT token from public.tokens WHERE appid=%s'
        return self.execute_query(query=query,
                                  params=(appid,))
