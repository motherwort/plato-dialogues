import json
from typing import Literal
from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import markdown

templates = Jinja2Templates(directory="src/templates")

def respond404(request):
    return templates.TemplateResponse("404.j2", {"request": request}, 404)

app = FastAPI(title="Plato")

DIALOGUE_FILENAME = {
    "gorgias": "src/content/gorgias.json",
}

def get_dialogue_content(dialogue: str):
    filename = DIALOGUE_FILENAME.get(dialogue, None)
    if filename is None:
        return None

    with open(filename, "r") as f:
        return json.load(f)


def find_item(dialogue: str, search: str):
    dialogue_content = get_dialogue_content(dialogue)
    if dialogue_content is None:
        return None
    for i, dialogue_item in enumerate(dialogue_content["dialogue"], start=1):
        if search in dialogue_item["speech"]:
            return i
    return None


def get_dialogue_item_context(dialogue: str, item: int):
    if item < 0:
        return None

    dialogue_content = get_dialogue_content(dialogue)
    if dialogue_content is None:
        return None

    last_item = len(dialogue_content["dialogue"])

    if item > last_item:
        return None
    
    dialogue_item = dialogue_content["dialogue"][item - 1]
    dialogue_item["speech"] = markdown.markdown(dialogue_item["speech"])
    return {
        "title": dialogue_content["title"],
        "dialogue_item": dialogue_item,
        "item": item,
        "last_item": last_item,
        "hx_get_prev": f"/api/{dialogue}/item/{item - 1}/" if item > 1 else None,
        "hx_get_prev_replace_url": f"?item={item - 1}" if item > 1 else None,
        "hx_get_next": f"/api/{dialogue}/item/{item + 1}/" if item < last_item else None,
        "hx_get_next_replace_url": f"?item={item + 1}" if item < last_item else None,
    }


@app.get("/")
def main(request: Request):
    return templates.TemplateResponse(
        "main.j2",
        {
            "dialogues": [
                {
                    "title": "Горгий",
                    "url": "/gorgias"
                }
            ],
            "request": request,
        }
    )


@app.get("/{dialogue}/info")
def dialogue_info(request: Request, dialogue: str):
    dialogue_content = get_dialogue_content(dialogue)
    if dialogue_content is None:
        return respond404(request=request)

    context = {
        "request": request,
        "title": dialogue_content["title"],
        "bibliography": dialogue_content["bibliography"],
        "characters": dialogue_content["characters"],
        "read_href": f"/{dialogue}",
    }

    return templates.TemplateResponse(
        "dialogue_info.j2",
        context
    )


@app.get("/{dialogue}/")
def dialogue(request: Request, response: Response, dialogue: str, item: int | Literal[""] = None, search: str = None):
    if search:
        item = find_item(dialogue=dialogue, search=search)
        if item is None:
            return respond404(request=request)
        return RedirectResponse(f"?item={item}")

    if item is None or item == "":
        item = request.cookies.get("item", 1)
        return RedirectResponse(f"?item={item}")

    dialogue_item_context = get_dialogue_item_context(dialogue=dialogue, item=item)
    if dialogue_item_context is None:
        return respond404(request=request)
    
    context = {"request": request}
    context.update(dialogue_item_context)


    response = templates.TemplateResponse(
        "dialogue.j2",
        context
    )
    response.set_cookie("item", item, path=f"/{dialogue}")
    return response


@app.get("/api/{dialogue}/item/{item}/")
def dialogue_item(request: Request, response: Response, dialogue: str, item: int):
    dialogue_item_context = get_dialogue_item_context(dialogue=dialogue, item=item)
    if dialogue_item_context is None:
        return respond404(request=request)
    
    context = {"request": request}
    context.update(dialogue_item_context)

    response = templates.TemplateResponse(
        "dialogue_item.j2",
        context
    )
    response.set_cookie("item", item, path=f"/{dialogue}")
    return response
