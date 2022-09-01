import operator as op
import typing as t
from datetime import date

from hubstats.hubstaff_client import models

__all__ = ("DailyActivityMap", "build_activity_map")

UserId = int
ProjectId = int


class DailyActivityMap(t.TypedDict):
    activity_date: date
    projects: t.List[models.Project]
    users: t.List[models.User]
    activity_map: t.Dict[t.Tuple[UserId, ProjectId], models.DailyActivity]


def build_activity_map(activities: models.DailyActivitiesResponse, dt: date) -> DailyActivityMap:
    return {
        "activity_date": dt,
        "projects": sorted(activities.projects, key=op.attrgetter("created_at")),
        "users": sorted(activities.users, key=op.attrgetter("name")),
        "activity_map": {(a.user_id, a.project_id): a for a in activities.daily_activities}
    }
