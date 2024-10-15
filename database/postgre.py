import psycopg2
from database.configurationparser import config

class postgreConnection(object):
    def __init__(self, section):
        self.section = section
        sid = ['local']
        
        if section in sid:
            self.get_conection()

    def get_conection(self):
        try:
            params = config(section=self.section)
            self.connection = psycopg2.connect(**params)
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
                
    def db_select(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        return cursor.fetchall()  
    
    
if __name__ == "__main__":
    SECTION = 'local'
    postgrecon = postgreConnection(SECTION)
    postgrecon.connect()