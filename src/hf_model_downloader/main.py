from logging import debug
from typing import Union

import uvicorn
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

from download import download_huggingface, load_config

app = FastAPI()

app.state.my_global_state = {"downloads": {}}

class AddModel(BaseModel):
    path: str
    is_convert: bool = False

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/huggingface/download")
def huggingface_download(huggingface_model: AddModel, background_tasks: BackgroundTasks):
    app.state.my_global_state["downloads"][huggingface_model.path] = { "status": "start" }
    background_tasks.add_task(download_huggingface, huggingface_model.path, huggingface_model.is_convert, app)
    return {"code": 200, "msg": "success add", "data": True}

@app.get("/huggingface/status")
def huggingface_status(path: str):
    status = app.state.my_global_state["downloads"][path]["status"]
    return {"code": 200, "msg": "success get", "data": status}


if __name__ == "__main__":
    load_config()
    uvicorn.run("main:app", host="0.0.0.0", port=24440, reload=False)
