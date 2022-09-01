import typing as t
import weakref

from datetime import date
from vendor import httpx

from . import models, exceptions, auth


class HubstaffClient(t.ContextManager["HubstaffClient"]):
    base_url: t.ClassVar[str] = "https://api.hubstaff.com"
    activities: "HubstaffActivities"

    def __init__(self, organization_id: str, token_mgr: auth.AbcTokenManager):
        self.organization_id = organization_id
        self.auth = auth.HubstaffAuth(token_mgr)

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

    def get_next_page(self, response_data: t.Dict[str, t.Any]) -> t.Optional[int]:
        try:
            return response_data["pagination"]["next_page_start_id"]
        except KeyError:
            return None


class HubstaffActivities(HubstaffNamespace):
    ExtraRecords = t.Union[
        t.Literal["users"],
        t.Literal["projects"],
        t.Literal["tasks"],
    ]
    daily_activities_path = "/v2/organizations/{org_id}/activities/daily"

    def daily_activities(
        self,
        start: date,
        stop: date,
        include: t.Collection[ExtraRecords] = (),
        _offset: int = None,
    ) -> models.DailyActivitiesResponse:
        params: t.Dict[str, t.Any] = {
            "date[start]": start.isoformat(),
            "date[stop]": stop.isoformat(),
            "include": ",".join(set(include)),
        }
        if _offset is not None:
            params["page_start_id"] = _offset

        url = self.daily_activities_path.format(org_id=self.owner.organization_id)
        resp = self.owner.client.get(url, params=params)
        if resp.is_error:
            raise exceptions.response_error(resp)

        data = resp.json()
        activities = models.DailyActivitiesResponse.parse_obj(data)

        next_page = self.get_next_page(data)
        if next_page is not None:
            next_activities = self.daily_activities(start, stop, include, next_page)
            activities.extend(next_activities)

        return activities
