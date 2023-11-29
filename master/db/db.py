from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from model import DatabaseModel

# Utilisation de sqlalchemy.orm.declarative_base() au lieu de declarative_base()
Base = declarative_base()

class SQLAlchemyModel(Base):
    __tablename__ = 'your_table_name'

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime)

# Configuration de la connexion à la base de données PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost/dbname"  # Remplacez ceci par votre URL de connexion PostgreSQL
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

# Création d'une session SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fonction pour insérer des données dans la base de données
def create_database_entry(database_entry: DatabaseModel):
    db_entry = SQLAlchemyModel(**database_entry.dict())
    db = SessionLocal()
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    db.close()

# Exemple d'utilisation
if __name__ == "__main__":
    data = {
        "id": 1,
        "nom": "Exemple",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timestamp": datetime.utcnow(),
    }

    create_database_entry(DatabaseModel(**data))
