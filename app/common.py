# This file contains the standard components used in the UI
import rio

DONT_GROW_CENTER_ALIGN = {
    "grow_x": False,
    "grow_y": False,
    "align_x": 0.5,
    "align_y": 0.5,
}

BUTTON_DEFAULTS = {
    "is_sensitive": True,
}


def make_text(
    text: str,
    **kwargs,
):
    return rio.Text(
        text=text,
        **kwargs,
    )


def make_button(
    content: str,
    **kwargs,
) -> rio.Button:

    kwargs = kwargs
    kwargs.update(DONT_GROW_CENTER_ALIGN)
    kwargs.update(BUTTON_DEFAULTS)

    return rio.Button(
        content=content,
        **kwargs,
    )
