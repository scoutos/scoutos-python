from pydantic import BaseModel, ConfigDict


class Channel(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    name: str
