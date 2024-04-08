import json
import os
from pathlib import Path
import logging

from shutil import copytree
from fastapi import FastAPI
from huggingface_hub import snapshot_download

class Config:
    def __init__(self, config: dict) -> None:
        self.cache_dir = os.path.join(config["base_dir"], config["cache_dir"])
        self.finish_dir =os.path.join(config["base_dir"], config["finish_dir"])
        self.convert = config["convert"]

def load_config() -> Config:
    config_path = "./config.json"

    if not os.path.exists(config_path):
        logging.error("not find config")
        exit(1)
    else:
        with open(config_path, "r") as f:
            configs = json.load(f)

        return Config(configs)


def download_huggingface(repo_id: str, is_convert: bool, app: FastAPI):
    config = load_config()
    app.state.my_global_state["downloads"][repo_id]["status"] = "start"
    try:
        app.state.my_global_state["downloads"][repo_id]["status"] = "download"
        person, name = repo_id.split('/')
        path = snapshot_download(repo_id, cache_dir=config.cache_dir)
        logging.info("{} download success: {}".format(repo_id, path))
        app.state.my_global_state["downloads"][repo_id]["status"] = "handle"
    except Exception:
        app.state.my_global_state["downloads"][repo_id]["status"] = "derror"
        logging.error("{} download faild".format(repo_id))

    try:
        finish_dir_path = os.path.join(config.finish_dir, "{}-{}".format(person, name))
        if is_convert:
            convert_file_name = "{}-{}-f16.gguf".format(person, name, repo_id)
            finish_file_path = os.path.join(finish_dir_path, convert_file_name)
            os.system("{} {} {}".format(config.convert, path, finish_file_path))
        else:
            copytree(path, finish_dir_path)
            logging.info("copy finish: {}".format(finish_dir_path))

        app.state.my_global_state["downloads"][repo_id]["status"] = "finish"
    except Exception:
        app.state.my_global_state["downloads"][repo_id]["status"] = "herror"
        logging.error("handle download error: {}".format(path))
