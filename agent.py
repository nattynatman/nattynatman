"""Core competitor insights agent powered by Claude."""

import os
import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.markdown import Markdown

from tools import TOOL_SCHEMAS, execute_tool

console = Console()

SYSTEM_PROMPT = """You are a strategic competitive intelligence analyst specialising in the AI automation and agent-builder market. Your focus company is **Relevance AI** — a no-code/low-code platform for building and deploying AI agents and multi-agent workflows.

## Relevance AI context (your baseline):
- Platform for building AI agents (no-code + API)
- Multi-agent "teams" that can collaborate on tasks
- Pre-built agent templates for sales, support, research, operations
- Integrations with major LLMs (OpenAI, Anthropic, Google, etc.)
- Target market: SMBs to mid-market, primarily B2B SaaS teams
- Key value prop: speed-to-deploy for non-technical business users
- Pricing: usage-based credits model, free tier available

## Your job:
When asked about competitors or the competitive landscape, you will:
1. **Search** for up-to-date information using your tools — don't rely on stale knowledge alone
2. **Synthesise** findings into structured, actionable insights
3. **Highlight** what matters most: feature gaps, pricing differences, positioning shifts, funding/growth signals, and customer sentiment
4. **Recommend** strategic implications for Relevance AI where relevant

## Key competitors to monitor:
- **Workflow/automation**: Make.com, Zapier, n8n, Tray.ai
- **Agent builders**: Voiceflow, Botpress, Flowise, Dify.ai, Stack AI
- **Dev-focused frameworks**: LangChain/LangSmith, CrewAI, AutoGen, LlamaIndex
- **Enterprise AI platforms**: Vertex AI Agent Builder, Azure AI Foundry, AWS Bedrock Agents
- **Horizontal AI**: OpenAI (GPTs/Assistants), Cohere, Dust.tt, Beam.ai

## Output style:
- Use markdown with clear headers and bullet points
- Lead with the most strategically important finding
- Include source URLs where helpful
- Be direct and opinionated — flag what actually matters, not just a summary
- When comparing, use a structured format (feature table, pros/cons, etc.)
"""


def run_agent(user_query: str, max_turns: int = 10) -> str:
    """
    Run the competitor insights agent for a given query.
    Returns the final assistant response as a string.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Please set it before running the agent."
        )

    client = anthropic.Anthropic(api_key=api_key)
    messages = [{"role": "user", "content": user_query}]

    final_response = ""

    for turn in range(max_turns):
        with Live(
            Spinner("dots", text=f"[cyan]Agent thinking (turn {turn + 1})…[/cyan]"),
            console=console,
            transient=True,
        ):
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOL_SCHEMAS,
                messages=messages,
            )

        # Collect any text content from this turn
        text_blocks = [b.text for b in response.content if b.type == "text"]
        if text_blocks:
            final_response = "\n".join(text_blocks)

        # If the model is done, return
        if response.stop_reason == "end_turn":
            break

        # Handle tool calls
        if response.stop_reason == "tool_use":
            tool_blocks = [b for b in response.content if b.type == "tool_use"]

            # Append assistant message with all content blocks
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool and collect results
            tool_results = []
            for tool_block in tool_blocks:
                console.print(
                    f"  [dim]→ Calling tool:[/dim] [yellow]{tool_block.name}[/yellow] "
                    f"[dim]{dict(list(tool_block.input.items())[:2])}[/dim]"
                )
                result = execute_tool(tool_block.name, tool_block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result,
                })

            messages.append({"role": "user", "content": tool_results})
        else:
            # Unexpected stop reason — bail out
            break

    return final_response
