import inspect
import os
from datetime import date
from typing import Any
from urllib.parse import urlencode

from jinja2 import pass_context
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from fastapi_admin import VERSION
from fastapi_admin.constants import BASE_DIR

class CompatibleTemplates(Jinja2Templates):
    def TemplateResponse(self, *args, **kwargs):
        # 1. Extract the name and context from the old fastapi-admin call pattern
        name = args[0] if len(args) > 0 else kwargs.get("name")
        context = kwargs.get("context") if "context" in kwargs else (args[1] if len(args) > 1 else {})
        request = context.get("request") if isinstance(context, dict) else None

        # 2. Dynamically check what signature the currently installed Starlette version expects
        sig = inspect.signature(super().TemplateResponse)
        
        if "request" in sig.parameters:
            # NEW Starlette behavior (FastAPI >= 0.104.0)
            # Filter out kwargs to avoid duplicate passing
            filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ("name", "context")}
            return super().TemplateResponse(
                request=request, 
                name=name, 
                context=context, 
                **filtered_kwargs
            )
        else:
            # OLD Starlette behavior (FastAPI <= 0.103.0)
            return super().TemplateResponse(name, context, **kwargs)

templates = CompatibleTemplates(directory=os.path.join(BASE_DIR, "templates"))
templates.env.globals["VERSION"] = VERSION
templates.env.globals["NOW_YEAR"] = date.today().year
templates.env.add_extension("jinja2.ext.i18n")


@pass_context
def current_page_with_params(context: dict, params: dict):
    request = context.get("request")  # type:Request
    full_path = request.scope["raw_path"].decode()
    query_params = dict(request.query_params)
    for k, v in params.items():
        query_params[k] = v
    return full_path + "?" + urlencode(query_params)


templates.env.filters["current_page_with_params"] = current_page_with_params


def set_global_env(name: str, value: Any):
    templates.env.globals[name] = value


def add_template_folder(*folders: str):
    for folder in folders:
        templates.env.loader.searchpath.insert(0, folder)
