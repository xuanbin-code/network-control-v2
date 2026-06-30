"""API 请求/响应 Pydantic 模型"""

from typing import List, Optional

from pydantic import BaseModel


class SetFilterRequest(BaseModel):
    mode: str
    targets: Optional[List[str]] = None


class RuleCreateRequest(BaseModel):
    domain: str


class SettingUpdateRequest(BaseModel):
    key: str
    value: str


class TestMessageRequest(BaseModel):
    message: str
    targets: Optional[List[str]] = None
