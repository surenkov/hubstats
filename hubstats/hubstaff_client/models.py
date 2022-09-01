import typing as t
from datetime import date, datetime

from vendor import pydantic

__all__ = (
    "DailyActivity",
    "User",
    "Project",
    "DailyActivitiesResponse",
)

class ResponseEntity(pydantic.BaseModel):
    id: int

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        return NotImplemented

    def __hash__(self):
        return hash(self.id)


class NullDefaultModel(pydantic.BaseModel):
    @pydantic.validator("*", pre=True)
    def replace_none_with_default(cls, value, field):
        if value is None:
            return field.get_default()
        return value


class DailyActivity(ResponseEntity, NullDefaultModel):
    activity_date: t.Optional[date] = pydantic.Field(default=None, alias="date")
    user_id: t.Optional[int] = None
    project_id: t.Optional[int] = None
    task_id: t.Optional[int] = None
    keyboard: int = 0
    mouse: int = 0
    overall: int = 0
    tracked: int = 0
    input_tracked: int = 0
    manual: int = 0
    idle: int = 0
    resumed: int = 0
    billable: int = 0
    created_at: datetime = pydantic.Field(default_factory=datetime.utcnow)
    updated_at: datetime = pydantic.Field(default_factory=datetime.utcnow)


class User(ResponseEntity, NullDefaultModel):
    name: str = ""
    email: str = ""
    timezone: str = pydantic.Field(default="UTC", alias="time_zone")
    status: str = "active"
    created_at: datetime = pydantic.Field(default_factory=datetime.utcnow)
    updated_at: datetime = pydantic.Field(default_factory=datetime.utcnow)


class Project(ResponseEntity, NullDefaultModel):
    name: str = ""
    status: str = "active"
    billable: bool = True
    metadata: t.Dict[str, t.Any]
    created_at: datetime = pydantic.Field(default_factory=datetime.utcnow)
    updated_at: datetime = pydantic.Field(default_factory=datetime.utcnow)


class DailyActivitiesResponse(pydantic.BaseModel):
    daily_activities: t.List[DailyActivity]
    users: t.Set[User] = pydantic.Field(default_factory=set)
    projects: t.Set[Project] = pydantic.Field(default_factory=set)

    def extend(self, other: "DailyActivitiesResponse"):
        self.daily_activities.extend(other.daily_activities)
        self.users.update(other.users)
        self.projects.update(other.projects)
