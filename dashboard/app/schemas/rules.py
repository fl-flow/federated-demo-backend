from pydantic import BaseModel, validator


class CreateRules(BaseModel):
    modality: str
    bodyPart: str = None
    examItem: str
    algorithmCode: list

    @validator('algorithmCode')
    def check_algorithmCode(cls, v, values, **kwargs):
        if v:
            return str(v)


class UpdateRules(BaseModel):
    modality: str = None
    bodyPart: int = None
    examItem: str = None
    algorithmCode: list = None


class RulesList(BaseModel):
    modality: str
    examItem: str
