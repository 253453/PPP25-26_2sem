from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio

from app.ws_manager import manager

router = APIRouter()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):

    await manager.connect(client_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()

            if data == "start":
                await run_fake_task(client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)


async def run_fake_task(client_id: str):

    await manager.send(client_id, {
        "status": "queued"
    })

    await asyncio.sleep(1)

    await manager.send(client_id, {
        "status": "running",
        "progress": 30
    })

    await asyncio.sleep(1)

    await manager.send(client_id, {
        "status": "running",
        "progress": 70
    })

    await asyncio.sleep(1)

    await manager.send(client_id, {
        "status": "finished",
        "progress": 100
    })