from pydantic import BaseModel, FilePath, FileUrl
from pathlib import Path

class Config(BaseModel):
    config_group:set[str] = {808080}