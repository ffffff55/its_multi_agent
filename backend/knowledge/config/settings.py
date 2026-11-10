from pydantic_settings import BaseSettings,SettingsConfigDict
import os

class Settings(BaseSettings):
    # 缺省用空字符串。类体里写 os.environ.get 时，没配变量就是 None，导入阶段会校验失败。
    # 环境变量和 .env 仍会覆盖这些空字符串。
    API_KEY: str = ""
    BASE_URL: str = ""
    MODEL: str = ""
    EMBEDDING_MODEL: str = ""

    
    # knowledge/config
    KNOWLEDGE_BASE_URL: str = ""

    _current_dir = os.path.dirname(os.path.abspath(__file__))
    # knowledge
    _project_root = os.path.dirname(_current_dir)
    
    VECTOR_STORE_PATH: str = os.path.join(_project_root, "chroma_kb1")
    
    # Default directories
    CRAWL_OUTPUT_DIR: str = os.path.join(_project_root, "data", "crawl")
    # Using 'data/crawl' as the default location for markdown files
    MD_FOLDER_PATH: str = CRAWL_OUTPUT_DIR
    TMP_MD_FOLDER_PATH:str= os.path.join(_project_root, "data", "tmp")
    # Text splitting configuration
    CHUNK_SIZE: int = 3000
    CHUNK_OVERLAP: int = 200

    # Retrieval configuration
    TOP_ROUGH: int = 50
    TOP_FINAL: int = 5

    model_config = SettingsConfigDict(
        env_file=os.path.join(_project_root, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

# 必须要实例化
settings = Settings()
