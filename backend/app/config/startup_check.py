"""启动前配置检查。

只读取 ``settings`` 上已经加载完成的字段，不改动任何加载顺序或加载方式。
所有提示只写「字段名」，不写字段值，避免 API Key 出现在报错、终端或日志里。
"""
from __future__ import annotations

from typing import Any, NamedTuple

# 至少要有完整的一套 AI 服务，这句话是原有启动校验的语义，保持不变。
AI_SERVICE_REQUIREMENT = "必须配置至少一个 AI 服务 (硅基流动 或 阿里百炼)"


class ProviderSpec(NamedTuple):
    """一套 AI 服务需要的字段：API Key、Base URL，以及它实际使用的模型名称。"""

    label: str
    key_field: str
    url_field: str
    model_field: str


AI_PROVIDERS: tuple[ProviderSpec, ...] = (
    ProviderSpec("硅基流动", "SF_API_KEY", "SF_BASE_URL", "MAIN_MODEL_NAME"),
    ProviderSpec("阿里百炼", "AL_BAILIAN_API_KEY", "AL_BAILIAN_BASE_URL", "SUB_MODEL_NAME"),
)

_ERROR_HEADER = "启动前配置检查未通过，缺少以下配置："
_ERROR_FOOTER = "请参考 backend/app/.env.example 补齐后重新启动；这里只报字段名，不打印密钥值。"


def _text(config: Any, field: str) -> str:
    value = getattr(config, field, None)
    return "" if value is None else str(value).strip()


def has_value(config: Any, field: str) -> bool:
    """字段是否有值（None、空串、纯空白都算没配）。"""
    return bool(_text(config, field))


def is_provider_configured(config: Any, spec: ProviderSpec) -> bool:
    return has_value(config, spec.key_field) and has_value(config, spec.url_field)


def configured_provider_labels(config: Any) -> list[str]:
    return [spec.label for spec in AI_PROVIDERS if is_provider_configured(config, spec)]


def missing_configuration_problems(config: Any) -> list[str]:
    """返回逐项列出的缺失配置，每项只说字段名。

    - 一套完整的 AI 服务都没有时，先给出总体要求，再按服务列出缺的字段。
    - 已配置的那一套缺模型名称时，单独指出是哪个模型字段。
    硅基流动未配置完整、但阿里百炼完整时不算启动失败，
    这与 README「只配一套也能起来」的约定一致。
    """
    incomplete: list[tuple[ProviderSpec, list[str]]] = []
    missing_model_names: list[str] = []
    complete_count = 0

    for spec in AI_PROVIDERS:
        missing_fields = [
            field
            for field in (spec.key_field, spec.url_field)
            if not has_value(config, field)
        ]
        if missing_fields:
            incomplete.append((spec, missing_fields))
            continue

        complete_count += 1
        if not has_value(config, spec.model_field):
            missing_model_names.append(f"{spec.model_field}（{spec.label} 已配置，模型名称为空）")

    problems: list[str] = []

    if complete_count == 0:
        problems.append(AI_SERVICE_REQUIREMENT)
        for spec, missing_fields in incomplete:
            problems.append(f"{spec.label}：缺少 {' 和 '.join(missing_fields)}")

    for item in missing_model_names:
        problems.append(f"缺少模型名称 {item}")

    return problems


def startup_configuration_error_message(problems: list[str]) -> str:
    lines = [_ERROR_HEADER]
    lines.extend(f"- {problem}" for problem in problems)
    lines.append(_ERROR_FOOTER)
    return "\n".join(lines)


def startup_configuration_summary(config: Any) -> str:
    """启动成功后打印的一行摘要：只说明哪套服务已配置、模型名称是什么，不含密钥值。"""
    labels = configured_provider_labels(config)
    providers = "、".join(labels) if labels else "无"
    return (
        "启动前配置检查通过：已配置 AI 服务 = "
        f"{providers}（API Key 只报是否设置，不打印值）；"
        f"MAIN_MODEL_NAME={_text(config, 'MAIN_MODEL_NAME') or '未设置'}，"
        f"SUB_MODEL_NAME={_text(config, 'SUB_MODEL_NAME') or '未设置'}"
    )
