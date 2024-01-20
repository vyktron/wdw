import psycopg2
from psycopg2 import sql
from datetime import datetime
from pydantic import BaseModel
import random
from datetime import datetime

class Location(BaseModel):
    """
    Base model for the "locations" table
    
    Attributes:
    ----------
    dad_id : int
        Id of the lost dad
    latitude: float
    longitude: float
    timestamp: str
    """
    dad_id: int
    latitude: float
    longitude: float
    timestamp: str = datetime.utcnow().isoformat()

class Dad(BaseModel):
    """
    Base model for the "dads" table
    
    Attributes:
    ----------
    name: str
    ip: str
    latitude: float
        Last known latitude
    longitude: float
        Last known longitude
    timestamp: str
        Timestamp of the last known location
    """

    name: str = random.choice(["Jacques", "Jean", "Paul", "Franck"])
    ip: str
    latitude: float
    longitude: float
    timestamp: str = datetime.utcnow().isoformat()

class PostgresDB:
    def __init__(self, database_url):
        self.database_url = database_url
        self.conn = psycopg2.connect(self.database_url)
        self.locations = "locations"
        self.dads = "dads"

        # Create tables if they don't exist
        self.create_tables()

    def close_connection(self):
        self.conn.close(); 
    
    def create_tables(self):
        cursor = self.conn.cursor()

        # Location table schema
        location_table_schema = [
            ("id", "SERIAL", "PRIMARY KEY"),
            ("dad_id", "SERIAL", "REFERENCES dads(id)"),
            ("latitude", "DOUBLE PRECISION", ""),
            ("longitude", "DOUBLE PRECISION", ""),
            ("timestamp", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "")
        ]

        # Dad table schema
        dad_table_schema = [
            ("id", "SERIAL", "PRIMARY KEY"),
            ("name", "VARCHAR(255)", ""),
            ("ip", "VARCHAR(255)", ""),
            ("latitude", "DOUBLE PRECISION", ""),
            ("longitude", "DOUBLE PRECISION", ""),
            ("timestamp", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "")
        ]

        # Tables creation
        for table in [self.dads, self.locations]:
            table_creation_query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
                sql.Identifier(table),
                sql.SQL(', ').join(sql.SQL("{} {} {}").format(
                    sql.Identifier(col_name),
                    sql.SQL(col_type),
                    sql.SQL(col_options))
                for col_name, col_type, col_options in (location_table_schema if table == self.locations else dad_table_schema))
            )
            cursor.execute(table_creation_query)

        self.conn.commit()
        cursor.close()
    
    def get_dad_by_ip(self, ip : str) -> tuple:

        """
        Get the dad from the database from its IP address
        
        Parameters
        ----------
        ip : str
            The IP address of the dad
        
        Returns
        -------
        tuple[int, Dad] or tuple[int, None]
            The dad id and the dad if it exists, -1 and None otherwise
        """

        cursor = self.conn.cursor()

        # Fecthing dad id by IP
        select_query = f"""
            SELECT * FROM {self.dads} WHERE ip = %s
        """
        cursor.execute(select_query, (ip,))
        dad = cursor.fetchone()
        self.conn.commit()
        cursor.close()

        if dad is None:
            return -1, None
        else:
            print([col[0] for col in cursor.description])
            return dad[0], Dad(**dict(zip([col[0] for col in cursor.description[1:-1]], dad[1:-1])), timestamp=dad[-1].isoformat())
    
    def update_dad(self, dad_id, latitude : float, longitude : float) -> None:
            
            """
            Update the dad location and timestampin the database
            
            Parameters
            ----------
            dad_id : int
            latitude : float
                The new latitude
            longitude : float
                The new longitude
            """
    
            cursor = self.conn.cursor()
    
            # Updating dad location
            update_query = f"""
                UPDATE {self.dads} SET latitude = %s, longitude = %s, timestamp = CURRENT_TIMESTAMP WHERE id = %s
            """
            cursor.execute(update_query, (latitude, longitude, dad_id))
            self.conn.commit()
            cursor.close()

    def get_dads(self) -> list :

        """
        Get all dads from the database
        
        Returns
        -------
        list[Dad]
            The list of all dads
        """

        cursor = self.conn.cursor()

        # Fecthing all dads
        select_query = f"""
            SELECT * FROM {self.dads}
        """
        cursor.execute(select_query)
        dads = cursor.fetchall()
        self.conn.commit()
        cursor.close()

        return [[dad[0], Dad(**dict(zip([col[0] for col in cursor.description[1:-1]], dad[1:-1])), timestamp=dad[-1].isoformat()).model_dump()] for dad in dads]

    def insert_data(self, data : Location or Dad) -> int:

        """
        Insert data into the database

        Parameters
        ----------
        data : Location or Dad
            The data to insert
        
        Returns
        -------
        int :
            The inserted id (or existing id if the data is a dad  that is already in the database)
        """

        cursor = self.conn.cursor()
        table = self.locations if isinstance(data, Location) else self.dads

        # Data insertion query
        insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING id").format(
            sql.Identifier(table),
            sql.SQL(', ').join(sql.Identifier(col_name) for col_name in data.model_fields.keys()),
            sql.SQL(', ').join(sql.Placeholder() * len(data.model_fields.keys()))
        )
        cursor.execute(insert_query, [getattr(data, col_name) for col_name in data.model_fields.keys()])

        inserted_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()

        return inserted_id

    def print_data(self):
        cursor = self.conn.cursor()

        # Data printing query
        for table in [self.locations, self.dads]:
            select_query = f"""
                SELECT * FROM {table}
            """
            cursor.execute(select_query)

            print_size = (16 + len(table))
            print(print_size*"=")
            print(7*"-", table, 7*"-")
            for row in cursor.fetchall():
                print(row)
            print(print_size*"=")

    def delete_table(self, table_name):
        cursor = self.conn.cursor()
        # Deleting query
        delete_query = f"""
            DROP TABLE {table_name}
        """
        cursor.execute(delete_query)
        self.conn.commit()
        cursor.close()

    def clear_table(self):        
        for table in [self.locations, self.dads]:
            self.delete_table(table)


# Exemple d'utilisation
if __name__ == "__main__":
    db = PostgresDB("postgresql://root:admin@localhost:5432/wdw")
    #db.delete_table()
    #db.create_tables()
    dad1 = Dad(ip="175.5.0.2", latitude=43.2965, longitude=-0.300)
    dad2 = Dad(ip="172.6.0.52", latitude=47.5, longitude=-2.756)
    #db.insert_data(dad1)
    #db.insert_data(dad2)
    db.print_data()
    db.clear_table()
    #db.print_data()
    db.close_connection()
