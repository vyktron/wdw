import psycopg2
from psycopg2 import sql
from datetime import datetime

# Configuration de la connexion à la base de données PostgreSQL
DATABASE_URL = "postgresql://root:admin@localhost:5432/wdw"  # Remplacez ceci par votre URL de connexion PostgreSQL

# Fonction pour créer la table dans la base de données
def create_table():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

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

    conn.commit()
    cursor.close()
    conn.close()

def insert_data(nom, latitude, longitude):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Insertion des données
    insert_query = """
        INSERT INTO locations (dad_name, latitude, longitude, timestamp)
        VALUES (%s, %s, %s, %s)
    """
    timestamp = datetime.utcnow()
    cursor.execute(insert_query, (nom, latitude, longitude, timestamp))

    conn.commit()
    cursor.close()
    conn.close()


#afficher les données du tableau en mettant le nom des colonnes
def print_data():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

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

    conn.commit()
    cursor.close()
    conn.close()

def delete_table():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Suppression de la table
    delete_query = """
        DROP TABLE locations
    """
    cursor.execute(delete_query)

    conn.commit()
    cursor.close()
    conn.close()

def clear_table():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Suppression de la table
    delete_query = """
        DELETE FROM locations
    """
    cursor.execute(delete_query)

    conn.commit()
    cursor.close()
    conn.close()

# Exemple d'utilisation
if __name__ == "__main__":
    #delete_table()
    # Création de la table
    #create_table()

    # Insertion des données
    #insert_data("Jacques", 43.2965, -0.3700)
    #insert_data("Jean", 43.2965, -0.3700)
    #insert_data("Paul", 43.2965, -0.3700)
    print_data()
    clear_table()
    print_data()
