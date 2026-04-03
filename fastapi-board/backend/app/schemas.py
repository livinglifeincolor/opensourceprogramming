from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=10)


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "PostUpdate":
        """title과 content 중 하나 이상이 요청에 포함되어야 한다.

        둘 다 생략하면 업데이트할 내용이 없으므로 422를 반환한다.
        """
        if not self.model_fields_set:
            raise ValueError("title 또는 content 중 하나 이상을 포함해야 합니다.")
        return self

    def apply_to(self, existing: dict) -> dict:
        """요청에 포함된 필드만 existing 값에 덮어씌워 반환한다.

        model_fields_set을 사용하므로 클라이언트가 명시적으로 보낸 필드만
        반영되고, 생략한 필드는 기존 값이 유지된다.
        """
        patch = self.model_dump(include=self.model_fields_set)
        return {**existing, **patch}


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SearchResponse(BaseModel):
    total: int
    results: list[PostResponse]
