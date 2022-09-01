import typing as t
import weakref

from datetime import date
from vendor import httpx

from . import models, exceptions


class HubstaffClient(t.ContextManager["HubstaffClient"]):
    base_url: t.ClassVar[str] = "https://api.hubstaff.com"
    activities: "HubstaffActivities"

    def __init__(self, organization_id: str, auth: httpx.Auth = None):
        self.organization_id = organization_id
        self.auth = auth

    def __enter__(self):
        self.client = httpx.Client(auth=self.auth, base_url=self.base_url)
        self.client.__enter__()
        self.activities = HubstaffActivities(self)
        return self

    def __exit__(self, *exc_info):
        del self.activities
        return self.client.__exit__(*exc_info)


class HubstaffNamespace:
    owner: HubstaffClient

    def __init__(self, owner: HubstaffClient):
        self.owner = weakref.proxy(owner)


class HubstaffActivities(HubstaffNamespace):
    ExtraRecords = t.Union[
        t.Literal["users"],
        t.Literal["projects"],
        t.Literal["tasks"],
    ]
    daily_activities_path = "/v2/organizations/{org_id}/activities/daily"

    def daily_activities(
        self,
        start_date: date,
        stop_date: date,
        include: t.Collection[ExtraRecords] = (),
    ) -> models.DailyActivitiesResponse:
        params = {
            "date[start]": start_date.isoformat(),
            "date[stop]": stop_date.isoformat(),
            "include": ",".join(include),
        }

        url = self.daily_activities_path.format(org_id=self.owner.organization_id)
        resp = self.owner.client.get(url, params=params)
        if resp.is_error:
            raise exceptions.response_error(resp)

        return models.DailyActivitiesResponse.parse_obj(resp.json())
