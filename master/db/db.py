import psycopg2
from psycopg2 import sql
from datetime import datetime
from pydantic import BaseModel
import random

class PostgresDB:
    def __init__(self, database_url):
        self.database_url = database_url
        self.conn = psycopg2.connect(self.database_url)

    def close_connection(self):
        self.conn.close(); 
    
    def create_table(self):
        cursor = self.conn.cursor()

        # Définition du schéma de la table
        table_schema = [
            ("id", "SERIAL", "PRIMARY KEY"),
            ("dad_name", "VARCHAR(255)", ""),
            ("latitude", "DOUBLE PRECISION", ""),
            ("longitude", "DOUBLE PRECISION", ""),
            ("timestamp", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "")
        ]

        # Création de la table
        table_creation_query = sql.SQL("CREATE TABLE IF NOT EXISTS locations ({})").format(
            sql.SQL(', ').join(sql.SQL("{} {} {}").format(
                sql.Identifier(col_name),
                sql.SQL(col_type),
                sql.SQL(col_options))
                for col_name, col_type, col_options in table_schema)
        )
        cursor.execute(table_creation_query)

        self.conn.commit()
        cursor.close()


    def insert_data(self, nom, latitude, longitude):
        cursor = self.conn.cursor()

        # Insertion des données
        insert_query = """
            INSERT INTO locations (dad_name, latitude, longitude, timestamp)
            VALUES (%s, %s, %s, %s)
        """
        timestamp = datetime.utcnow()
        cursor.execute(insert_query, (nom, latitude, longitude, timestamp))

        self.conn.commit()
        cursor.close()

    def print_data(self):
        cursor = self.conn.cursor()

        # Affichage des données
        select_query = """
            SELECT * FROM locations
        """
        cursor.execute(select_query)
        data = cursor.fetchall()

        # Récupération des noms de colonnes
        column_names = [desc[0] for desc in cursor.description]
        print(column_names)

        # Affichage des données
        for row in data:
            print(row)

        self.conn.commit()
        cursor.close()

    def delete_table(self):
        cursor = self.conn.cursor()

        # Suppression de la table
        delete_query = """
            DROP TABLE locations
        """
        cursor.execute(delete_query)

        self.conn.commit()
        cursor.close()

    def clear_table(self):
        cursor = self.conn.cursor()

        # Suppression de la table
        delete_query = """
            DELETE FROM locations
        """
        cursor.execute(delete_query)

        self.conn.commit()
        cursor.close()

class Location(BaseModel):
    """
    Classe de données pour la table "locations"
    
    Attributs:
    ----------
    dad_id : int
        Identifiant du papa perdu
    latitude: float
    longitude: float"""

    dad_id : int
    latitude: float
    longitude: float
    timestamp: str = datetime.utcnow().isoformat()

class Dad(BaseModel):
    """
    Classe de données pour la table "dads"
    
    Attributs:
    ----------
    name: str
        Nom du papa perdu
    ip: str
        Adresse IP
    latitude: float
        Dernière latitude connue
    longitude: float
        Dernière longitude connue
    timestamp: str
        Date et heure de la dernière position connue"""

    id: int
    name: str = random.choice(["Jacques", "Jean", "Paul", "Franck"])
    ip: str
    latitude: float
    longitude: float
    timestamp: str

# Exemple d'utilisation
if __name__ == "__main__":
    db = PostgresDB("postgresql://root:admin@localhost:5432/wdw")
    #db.delete_table()
    db.create_table()
    db.print_data()
    db.insert_data("Jacques", 43.2965, -0.300)
    #db.insert_data("Jean", 43.2965, -0.3700)
    #db.insert_data("Paul", 43.2965, -0.400)
    db.insert_data("Franck", 43.2965, -0.200)
    db.print_data()
    #db.clear_table()
    #db.print_data()
    db.close_connection()
