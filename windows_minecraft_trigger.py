import os
import subprocess
import argparse

from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

TRIGGER_TOKEN = os.getenv("MINECRAFT_TRIGGER_TOKEN", "CHANGE_ME")
TASK_NAME = os.getenv("MINECRAFT_TASK_NAME", "MinecraftStart")
BIND_HOST = os.getenv("MINECRAFT_TRIGGER_HOST", "0.0.0.0")
BIND_PORT = int(os.getenv("MINECRAFT_TRIGGER_PORT", "8787"))


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "task": TASK_NAME}


@app.post("/start-minecraft")
def start_minecraft(x_auth: str = Header(default="")) -> dict:
    if x_auth != TRIGGER_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")

    result = subprocess.run(
        ["schtasks", "/Run", "/TN", TASK_NAME],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to run scheduled task",
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            },
        )

    return {"status": "ok", "message": "Minecraft task started"}


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=BIND_HOST)
    parser.add_argument("--port", type=int, default=BIND_PORT)
    parser.add_argument("--token", default=TRIGGER_TOKEN)
    parser.add_argument("--task-name", default=TASK_NAME)
    args = parser.parse_args()

    TRIGGER_TOKEN = args.token
    TASK_NAME = args.task_name

    uvicorn.run(app, host=args.host, port=args.port)
