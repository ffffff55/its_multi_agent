from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from config.settings import settings

# 硅基流动配置(主模型)
SF_API_KEY = settings.SF_API_KEY
SF_BASE_URL = settings.SF_BASE_URL
MAIN_MODEL_NAME = settings.MAIN_MODEL_NAME

# 阿里百炼配置(子模型)
AL_BAILIAN_API_KEY = settings.AL_BAILIAN_API_KEY
AL_BAILIAN_BASE_URL = settings.AL_BAILIAN_BASE_URL
SUB_MODEL_NAME = settings.SUB_MODEL_NAME

# 未配置的那一侧不能在导入时抛错，也不能拿空密钥去连真实地址。
_UNCONFIGURED_BASE_URL = "http://127.0.0.1:9/v1"
_UNCONFIGURED_API_KEY = "unconfigured"


def build_openai_client(base_url: str | None, api_key: str | None) -> AsyncOpenAI:
    """key 和 base url 都有才指向真实服务，否则用本机占位客户端。"""
    if api_key and base_url:
        return AsyncOpenAI(base_url=base_url, api_key=api_key)
    return AsyncOpenAI(base_url=_UNCONFIGURED_BASE_URL, api_key=_UNCONFIGURED_API_KEY)


# 创建模型客户端
# 主模型客户端(协调Agent使用)
main_model_client = build_openai_client(SF_BASE_URL, SF_API_KEY)
# 子模型客户端(干活的子Agent使用)
sub_model_client = build_openai_client(AL_BAILIAN_BASE_URL, AL_BAILIAN_API_KEY)




# 创建主调度模型
main_model = OpenAIChatCompletionsModel(
    model=MAIN_MODEL_NAME,
    openai_client=main_model_client)

# 创建子调度模型
sub_model = OpenAIChatCompletionsModel(
    model=SUB_MODEL_NAME,
    openai_client=sub_model_client)
