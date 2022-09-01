from datetime import timedelta
import typing as t

from vendor import jinja2
from .models import DailyActivityMap


def fmt_timedelta(td, fmt):
    if isinstance(td, int):
        td = timedelta(seconds=td)

    hours, rem = divmod(td.total_seconds(), 3600)
    minutes, seconds = divmod(rem, 60)
    return fmt.format(h=int(hours), m=int(minutes), s=int(seconds))


env = jinja2.Environment(
    loader=jinja2.PackageLoader("hubstats.statstable", "templates"),
    autoescape=jinja2.select_autoescape(),
)
env.filters["fmt_timedelta"] = fmt_timedelta


def render_activity_table(activity_map: DailyActivityMap, out: t.TextIO) -> None:
    rendered_table = process_template("table.html", activity_map)
    out.write(rendered_table)


def process_template(template_name: str, context: DailyActivityMap, **kwctx):
    template = env.get_template(template_name)
    return template.render(context, **kwctx)
