from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi import WebSocket, WebSocketDisconnect
import schedule
import uvicorn
import asyncio

'''
# Configuration de la connexion à la base de données PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost/dbname"  # Remplacez ceci par votre URL de connexion PostgreSQL
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)

app = FastAPI()

# Route pour la page principale
@app.get("/", response_class=HTMLResponse)
def read_item():
    return HTMLResponse(content=open("index.html").read(), status_code=200)
'''
# Pour test
app = FastAPI()
fake_locations = [
    {"nom": "Jacques", "latitude": 43.2965, "longitude": -0.3700}
]
#

# WebSocket pour la communication en temps réel
class WebSocketManager:
    def __init__(self):
        self.active_connections = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        await self.broadcast_data()

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_data(self):
        db = SessionLocal()
        locations = db.query(Location).all()
        db.close()

        data = {"locations": [(loc.nom, loc.latitude, loc.longitude) for loc in locations]}
        for connection in self.active_connections:
            await connection.send_json(data)

websocket_manager = WebSocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            await schedule.run_pending()
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        await websocket_manager.broadcast_data()

# Tâche planifiée pour mettre à jour les données toutes les x secondes
'''
def scheduled_job():
    db = SessionLocal()
    locations = db.query(Location).all()
    db.close()
    data = {"locations": [(loc.nom, loc.latitude, loc.longitude) for loc in locations]}
    for connection in websocket_manager.active_connections:
        connection.send_json(data)
'''
#Pour test 
def scheduled_job():
    for connection in websocket_manager.active_connections:
        connection.send_json({"locations": [(loc["nom"], loc["latitude"], loc["longitude"]) for loc in fake_locations]})

schedule.every(10).seconds.do(scheduled_job)

@app.get("/", response_class=HTMLResponse)
def read_item():
    return HTMLResponse(content=open("templates/index.html").read(), status_code=200)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
