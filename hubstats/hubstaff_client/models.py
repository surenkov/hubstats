import typing as t

from datetime import date, datetime
from zoneinfo import ZoneInfo

from vendor import pydantic


class NullDefaultModel(pydantic.BaseModel):
    @pydantic.validator("*", pre=True)
    def replace_none_with_default(cls, value, field):
        if value is None:
            return field.get_default()
        return value


class DailyActivity(NullDefaultModel):
    id: int
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


class User(NullDefaultModel):
    id: int
    name: str = ""
    email: str = ""
    timezone: str = pydantic.Field(default="UTC", alias="time_zone")
    status: str = "active"
    created_at: datetime = pydantic.Field(default_factory=datetime.utcnow)
    updated_at: datetime = pydantic.Field(default_factory=datetime.utcnow)

    def tzinfo(self):
        return ZoneInfo(self.timezone)


class Project(NullDefaultModel):
    id: int
    name: str = ""
    status: str = "active"
    billable: bool = True
    metadata: t.Dict[str, t.Any]
    created_at: datetime = pydantic.Field(default_factory=datetime.utcnow)
    updated_at: datetime = pydantic.Field(default_factory=datetime.utcnow)


class DailyActivitiesResponse(pydantic.BaseModel):
    daily_activities: t.List[DailyActivity]
    users: t.Optional[t.List[User]] = None
    projects: t.Optional[t.List[Project]] = None
