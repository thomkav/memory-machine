from __future__ import annotations

import rio
import asyncio

from ..common import (
    make_button,
    make_text,
)


@rio.page(
    name="Asynchronous Retrieval",
    url_segment="demo/asynchronous_retrieval",
)
class AsyncRetrievalDemo(rio.Component):

    content: str | None = None

    @rio.event.on_populate
    async def load_content(self) -> None:
        # Fetch your content here. This could be from a database, via HTTP, or
        # any other method.
        self.content = None
        self.force_refresh()
        await asyncio.sleep(1)
        self.content = "Hello, World!"
        self.force_refresh()

    def build(self) -> rio.Component:

        text = make_text(
            text=self.content or "Click the button to retrieve content.",
            justify="center",
        )
        button = make_button(
            "Retrieve Content",
            on_press=self.load_content,
        )
        progress_circle = rio.ProgressCircle(
            align_x=0.5,
            align_y=0.5,
        )

        if self.content is None:
            return rio.Column(text, button, progress_circle)
        else:
            return rio.Column(text, button)
