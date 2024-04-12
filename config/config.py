from pydantic import BaseSettings
import os
from utility.Utils import get_project_root
from resources.env import GLOBAL_CONFIG_ABSPATH, SECRET_CONFIG_ABSPATH

class SettingsSecrets(BaseSettings):

    ELASTICSEARCH_PSW: str
    ORACLEDB_PSW: str

    class Config:
        env_file = os.path.join(SECRET_CONFIG_ABSPATH)


class Settings(BaseSettings):
    UVICORN_HOST: str
    UVICORN_PORT: int
    MAPPING_FIELDS_PATH: str
    ORACLEDB_HOST: str
    ORACLEDB_PORT: str
    ORACLEDB_SERVICE: str
    ORACLEDB_USER: str
    ORACLE_SAMPLES_TABLE: str
    ORACLE_INTERVENTI_CLASSIFICATION_TABLE: str
    ORACLE_ODG_CLASSIFICATION_TABLE: str
    ELASTICSEARCH_HOST: str
    ELASTICSEARCH_PORT: str
    ELASTICSEARCH_HTTPS_FLAG: bool
    ELASTICSEARCH_USER: str
    TIMEOUT: int
    SCROLL_TIME: str
    DOC_SIZE: int
    ELASTICSEARCH_ML_INDEX: str
    ELASTICSEARCH_BI_INDEX: str
    ELASTICSEARCH_SAMPLES_ENTRIES_INDEX: str
    ES_INTERVENTI_SOURCE: str
    ES_ODG_SOURCE: str
    WEIGHT_SUPPORT: float
    WEIGHT_F1_SCORE: float

    class Config:
        env_file = os.path.join(GLOBAL_CONFIG_ABSPATH)
