import typing as t

from datetime import timedelta

from .models import DailyActivityMap
from .loader import env



def render_activity_table(activity_map: DailyActivityMap, out: t.TextIO) -> None:
    rendered_table = process_template("table.html", activity_map)
    out.write(rendered_table)


def process_template(template_name: str, context: DailyActivityMap, **kwctx):
    template = env.get_template(template_name)
    return template.render(context, **kwctx)
