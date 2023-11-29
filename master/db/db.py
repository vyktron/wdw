import psycopg2
from psycopg2 import sql
from datetime import datetime

# Configuration de la connexion à la base de données PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost/dbname"  # Remplacez ceci par votre URL de connexion PostgreSQL

# Fonction pour créer la table dans la base de données
def create_table():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Définition du schéma de la table
    table_schema = [
        ("id", "SERIAL", "PRIMARY KEY"),
        ("Dad_name", "VARCHAR(255)"),
        ("Latitude", "DOUBLE PRECISION"),
        ("Longitude", "DOUBLE PRECISION"),
        ("Timestamp", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
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

    conn.commit()
    cursor.close()
    conn.close()

def insert_data(nom, latitude, longitude):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Insertion des données
    insert_query = """
        INSERT INTO locations (nom, latitude, longitude, timestamp)
        VALUES (%s, %s, %s, %s)
    """
    timestamp = datetime.utcnow()
    cursor.execute(insert_query, (nom, latitude, longitude, timestamp))

    conn.commit()
    cursor.close()
    conn.close()

# Exemple d'utilisation
if __name__ == "__main__":
    # Création de la table
    create_table()
