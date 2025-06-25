from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.room_connections: Dict[str, List[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            # Remove from all rooms
            for room, clients in self.room_connections.items():
                if client_id in clients:
                    clients.remove(client_id)
            logger.info(f"Client {client_id} disconnected")

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

    async def send_json_message(self, data: dict, client_id: str):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error sending JSON to {client_id}: {e}")
                self.disconnect(client_id)

    def join_room(self, client_id: str, room: str):
        if room not in self.room_connections:
            self.room_connections[room] = []
        if client_id not in self.room_connections[room]:
            self.room_connections[room].append(client_id)

    def leave_room(self, client_id: str, room: str):
        if room in self.room_connections and client_id in self.room_connections[room]:
            self.room_connections[room].remove(client_id)

    async def broadcast_to_room(self, message: str, room: str):
        if room in self.room_connections:
            for client_id in self.room_connections[room]:
                await self.send_personal_message(message, client_id)

    async def broadcast_json_to_room(self, data: dict, room: str):
        if room in self.room_connections:
            for client_id in self.room_connections[room]:
                await self.send_json_message(data, client_id)

    async def broadcast_to_all(self, message: str):
        for client_id in self.active_connections:
            await self.send_personal_message(message, client_id)

    async def broadcast_sensor_data(self, sensor_data: dict):
        """Broadcast sensor data to all connected clients"""
        message = {
            "type": "sensor_data",
            "data": sensor_data,
            "timestamp": sensor_data.get("timestamp")
        }
        await self.broadcast_json_to_room(message, "dashboard")

    async def broadcast_alert(self, alert_data: dict):
        """Broadcast alerts to all connected clients"""
        message = {
            "type": "alert",
            "data": alert_data,
            "severity": alert_data.get("severity", "info")
        }
        await self.broadcast_to_all(json.dumps(message)) 