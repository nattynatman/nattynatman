#!/usr/bin/env python3
"""
Competitor Insights Agent for Relevance AI
==========================================
A CLI tool that surfaces competitive intelligence about the AI agent/automation market.
"""

import sys
import os
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule

# Load .env if present
load_dotenv(Path(__file__).parent / ".env")

from agent import run_agent

app = typer.Typer(
    name="competitor-insights",
    help="Surface competitor insights for Relevance AI.",
    add_completion=False,
)
console = Console()

EXAMPLE_QUERIES = [
    "What are the top 5 competitors to Relevance AI right now, and how do they differentiate?",
    "Compare Relevance AI vs Voiceflow on features, pricing, and positioning",
    "What's the latest news or funding activity for n8n, Flowise, and Dify?",
    "What features are competitors offering that Relevance AI doesn't have yet?",
    "How does Relevance AI's pricing compare to Make.com and Zapier?",
    "What are enterprise buyers saying about Relevance AI vs alternatives?",
    "Summarise the AI agent builder market landscape in 2025",
]


def print_banner():
    console.print(
        Panel.fit(
            "[bold cyan]Competitor Insights Agent[/bold cyan]\n"
            "[dim]Powered by Claude · Focused on Relevance AI[/dim]",
            border_style="cyan",
        )
    )


@app.command()
def query(
    question: str = typer.Argument(
        None,
        help="Your competitive intelligence question. If omitted, enters interactive mode.",
    ),
    examples: bool = typer.Option(
        False, "--examples", "-e", help="Show example queries and exit."
    ),
):
    """
    Ask the agent a competitive intelligence question about the AI automation market.

    Examples:\n
        python main.py "Compare Relevance AI vs Voiceflow"\n
        python main.py "What's new with n8n and Flowise?"\n
        python main.py  # interactive mode
    """
    if examples:
        console.print("\n[bold]Example queries:[/bold]\n")
        for i, q in enumerate(EXAMPLE_QUERIES, 1):
            console.print(f"  [cyan]{i}.[/cyan] {q}")
        console.print()
        raise typer.Exit()

    print_banner()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print(
            "[red]Error:[/red] ANTHROPIC_API_KEY is not set.\n"
            "Set it in your environment or create a [bold].env[/bold] file:\n\n"
            "  [dim]ANTHROPIC_API_KEY=sk-ant-...[/dim]\n"
        )
        raise typer.Exit(1)

    # Interactive mode if no question provided
    if not question:
        console.print("\n[dim]Tip: run with --examples to see sample queries[/dim]")
        console.print("[dim]Type 'quit' or press Ctrl+C to exit[/dim]\n")

        while True:
            try:
                question = Prompt.ask("[bold cyan]Your question[/bold cyan]").strip()
            except (KeyboardInterrupt, EOFError):
                console.print("\n[dim]Goodbye.[/dim]")
                raise typer.Exit()

            if question.lower() in {"quit", "exit", "q"}:
                console.print("[dim]Goodbye.[/dim]")
                raise typer.Exit()

            if not question:
                continue

            _run_and_display(question)
            console.print()
    else:
        _run_and_display(question)


def _run_and_display(question: str):
    """Run the agent for a question and pretty-print the result."""
    console.print(f"\n[bold]Q:[/bold] {question}\n")
    console.print(Rule(style="dim"))

    try:
        answer = run_agent(question)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        return
    except Exception as e:
        console.print(f"\n[red]Agent error:[/red] {e}")
        return

    console.print(Rule(style="dim"))
    console.print(Markdown(answer))


if __name__ == "__main__":
    app()
