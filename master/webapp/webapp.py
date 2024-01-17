from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import schedule
import uvicorn
import asyncio
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db import PostgresDB, Location, Dad

# Configuration de la connexion à la base de données PostgreSQL
DATABASE_URL = "postgresql://root:admin@localhost:5432/wdw" #os.environ.get('DATABASE_URL')
db = PostgresDB(DATABASE_URL)

app = FastAPI()

# WebSocket pour la communication en temps réel
class WebSocketManager:
    def __init__(self):
        self.consumer_connections = set()
        self.map_connection = None

    async def consumer_connect(self, websocket: WebSocket):
        await websocket.accept()
        self.consumer_connections.add(websocket)
    
    async def map_connect(self, websocket: WebSocket):
        await websocket.accept()
        self.map_connection = websocket

    def disconnect(self, websocket: WebSocket):
        if websocket in self.consumer_connections:
            self.consumer_connections.remove(websocket)
        else :
            self.map_connection = None
    
    async def handle_connections(self, websocket: WebSocket):
        await self.consumer_connect(websocket)
        try:
            while True:
                # Listen for new messages from Kafka
                message = await websocket.receive_text()
                print(f"Received message: {message}")
                # Send good news to the client
                await websocket.send_json({"msg": "Message received!"})
                if self.map_connection:
                    print(message)
                    await self.map_connection.send_text(message)
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket)

    """
    async def broadcast_data(self, websocket: WebSocket = None):
        locations = db.query(Location).all()
        db.close()

        data = {"locations": [(loc.dad_name, loc.latitude, loc.longitude) for loc in locations]}
        
        if websocket:
            await websocket.send_json(data)
        else:
            for connection in self.active_connections:
                await connection.send_json(data)
    """
    

websocket_manager = WebSocketManager()

# Route websocket pour la communication en temps réel avec le consumer Kafka
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket_manager.handle_connections(websocket)
    

@app.websocket("/mapws")
async def mapws_endpoint(websocket: WebSocket):
    await websocket_manager.map_connect(websocket)
    # Maintain connection with the map
    while True:
        await asyncio.sleep(30)
        await websocket.send_json({"healthcheck": "Connection maintained"})

# Route pour la page principale
@app.get("/", response_class=HTMLResponse)
def read_item():
    return HTMLResponse(content=open("templates/index.html").read(), status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)