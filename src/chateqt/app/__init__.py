"""Init app module."""

import typer

from .offline import app as offline_app
from .online import app as online_app

cli = typer.Typer()


cli.add_typer(offline_app, name="offline")
cli.add_typer(online_app, name="online")
