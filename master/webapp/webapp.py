from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import schedule
import uvicorn
import asyncio
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db import PostgresDB, Location, Dad

# Configuration de la connexion à la base de données PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL') 
db = PostgresDB(DATABASE_URL)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
                # send pong
                await websocket.send_text("pong")
                if self.map_connection:
                    try :
                        await self.map_connection.send_text(message)
                    except Exception as e:
                        print("Message not sent to map : ", e)
        except Exception:
            websocket_manager.disconnect(websocket)
    
    async def handle_map_connection(self, websocket: WebSocket):
        try :
            await websocket_manager.map_connect(websocket)
            # Maintain connection with the map
            message = json.loads(await websocket.receive_text())
            if message["get"] == "dads":
                dads = db.get_dads()
                await websocket.send_json({"dads": dads})
            while True:
                await asyncio.sleep(10)
                await websocket.send_json({"ping": "ping"})
                await websocket.receive_text()
        except Exception as e:
            print("close map connection : ", e, flush=True)
            websocket_manager.disconnect(websocket)

websocket_manager = WebSocketManager()

# Route websocket pour la communication en temps réel avec le consumer Kafka
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await asyncio.create_task(websocket_manager.handle_connections(websocket))
    
@app.websocket("/mapws")
async def mapws_endpoint(websocket: WebSocket):
    # Terminate an eventual task named "mapws"
    for task in asyncio.all_tasks():
        if task.get_name() == "mapws":
            task.cancel()
    # Run handle_map_connection in a new task
    try :
        await asyncio.create_task(websocket_manager.handle_map_connection(websocket), name="mapws")
    except asyncio.exceptions.CancelledError:
        print("Map connection closed", flush=True)
    except Exception as e:
        print("Unexpected : ", e, flush=True)

# Route pour la page principale
@app.get("/")
def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)