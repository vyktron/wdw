from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Column, Integer, String, Float
import schedule
import uvicorn
import asyncio
import json

# Configuration de la connexion à la base de données PostgreSQL
DATABASE_URL = "postgresql://root:admin@localhost:5432/wdw"  # Remplacez ceci par votre URL de connexion PostgreSQL
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, index=True)
    dad_name= Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# WebSocket pour la communication en temps réel
class WebSocketManager:
    def __init__(self):
        self.active_connections = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        await self.broadcast_data()

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_data(self, websocket: WebSocket = None):
        db = SessionLocal()
        locations = db.query(Location).all()
        db.close()

        data = {"locations": [(loc.dad_name, loc.latitude, loc.longitude) for loc in locations]}
        
        if websocket and websocket in self.active_connections:
            await websocket.send_json(data)
        else:
            for connection in self.active_connections:
                if connection in self.active_connections:  # Vérifier si la connexion est toujours active
                    await connection.send_json(data)

websocket_manager = WebSocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket_manager.connect(websocket)
    try:
        while True:
            if scheduled_job():
                await websocket_manager.broadcast_data(websocket)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        if websocket in websocket_manager.active_connections:
            websocket_manager.disconnect(websocket)
            await websocket_manager.broadcast_data()

# Tâche planifiée pour mettre à jour les données toutes les x secondes
def scheduled_job():
    for connection in websocket_manager.active_connections:
        connection.send_text(json.dumps({"locations": []}))  # Efface tous les marqueurs actuels

        db = SessionLocal()
        locations = db.query(Location).all()
        db.close()

        data = {"locations": [(loc.dad_name, loc.latitude, loc.longitude) for loc in locations]}
        for connection in websocket_manager.active_connections:
            connection.send_text(json.dumps(data))
    return True

schedule.every(10).seconds.do(scheduled_job)

# Route pour la page principale
@app.get("/", response_class=HTMLResponse)
def read_item():
    return HTMLResponse(content=open("templates/index.html").read(), status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
