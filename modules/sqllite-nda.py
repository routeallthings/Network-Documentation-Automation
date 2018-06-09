import sqlite3
from sqlite3 import Error
 
 
def create_connection():
    """ create a database connection to a database that resides
        in the memory
    """
    try:
        conn = sqlite3.connect(':memory:')
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        conn.close()

def create_database():
    sql = 'create table if not exists ' + table_name + ' (id integer)'
    c.execute(sql)
    conn.commit()




if __name__ == '__main__':
    create_connection()