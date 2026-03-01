#!/usr/bin/env python3
"""Entry point: python run_jobs.py [--port 8080]"""
import typer
import uvicorn

app = typer.Typer(add_completion=False)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to listen on"),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload on file changes"),
):
    """Start the JobRadar web server."""
    typer.echo(f"\n  JobRadar running at http://localhost:{port}\n")
    uvicorn.run("jobs.app:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
