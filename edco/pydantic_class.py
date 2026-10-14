from pydantic import BaseModel, ConfigDict, Field


class app(BaseModel):
    model_config = ConfigDict(extra="allow")
    __pydantic_extra__: dict[str, str] = Field(init=False)
    path: str


class backup_script(BaseModel):
    path: str


class backup_configs(BaseModel):
    script: backup_script


class backup(BaseModel):
    configs: backup_configs
    type: str


class config(BaseModel):
    apps: dict[str, app]
    backup: backup
