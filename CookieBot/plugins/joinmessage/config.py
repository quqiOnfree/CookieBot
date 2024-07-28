from pydantic import BaseModel

class Config(BaseModel):
    config_group:set[str]