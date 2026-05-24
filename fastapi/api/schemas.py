from typing import List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class WorkoutCreate(BaseModel):
    name: str
    description: Optional[str] = None


class WorkoutRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None


class RoutineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    workouts: List[int] = Field(
        default_factory=list,
        validation_alias=AliasChoices("workouts", "workout_ids"),
    )

    @field_validator("workouts", mode="before")
    @classmethod
    def coerce_workout_ids(cls, value):
        if value is None:
            return []
        return [int(workout_id) for workout_id in value]


class RoutineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    workouts: List[WorkoutRead] = []
