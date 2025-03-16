from __future__ import annotations

import os
from pathlib import Path

import openai
import rio

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    message = """
This template requires an OpenAI API key to work

You can get your API key from [OpenAI's website](https://platform.openai.com/api-keys
Make sure to enter your key into the `__init__.py` file before trying to run the project
""".strip()

    print(message)
    raise RuntimeError(message)


def on_app_start(app: rio.App) -> None:
    # Create the OpenAI client and attach it to the app
    app.default_attachments.append(openai.AsyncOpenAI(api_key=OPENAI_API_KEY))

# Define a theme for Rio to use.
#
# You can modify the colors here to adapt the appearance of your app or website.
# The most important parameters are listed, but more are available! You can find
# them all in the docs
#
# https://rio.dev/docs/api/theme


THEME = rio.Theme.from_colors(
    primary_color=rio.Color.from_hex("01dffdff"),
    secondary_color=rio.Color.from_hex("0083ffff"),
    mode="light",
)


# Create the Rio app
app = rio.App(
    name='memory-machine-ui',
    on_app_start=on_app_start,
    theme=THEME,
    assets_dir=Path(__file__).parent / "assets",
)
