import importlib.resources
from datetime import timedelta

from vendor import jinja2


def fmt_timedelta(td, fmt):
    if isinstance(td, int):
        td = timedelta(seconds=td)

    hours, rem = divmod(td.total_seconds(), 3600)
    minutes, seconds = divmod(rem, 60)
    return fmt.format(h=int(hours), m=int(minutes), s=int(seconds))


def load_template(template_name):
    return importlib.resources.read_text(__package__, template_name)


env = jinja2.Environment(
    loader=jinja2.FunctionLoader(load_template),
    autoescape=jinja2.select_autoescape(),
)
env.filters["fmt_timedelta"] = fmt_timedelta
