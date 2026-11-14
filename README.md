# clovord

A Python SDK for interacting with the Clovord Gateway and REST API.

## Installation

```bash
pip install clovord
```

For local development:

```bash
pip install -e .[dev]
```

## Usage

```python
import clovord
import os
from clovord import Bot, Container, TextDisplay

intents = clovord.Intents.default()
intents.members = True
intents.messages = True
intents.presence = True

bot = Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.username}")

@bot.command(name="help")
async def help_command(ctx):
    await ctx.send(
        components=[
            Container(
                TextDisplay("**Help**"),
                TextDisplay("Use `!ping` or `/ping`."),
                accent_color=0x3FE0C5,
            )
        ]
    )

@bot.command()
async def ping(ctx):
    await ctx.send(f"pong · {round(bot.latency * 1000)} ms")

bot.run(os.environ["BOT_TOKEN"])
```

## Overview

- `Bot` is the main entrypoint.
- Prefix commands use `command_prefix` and `@bot.command`.
- Slash commands use `bot.tree` and `@bot.tree.command`.
- Rich layouts use Containers (`Container`, `TextDisplay`, …) via `components=`.
- The Gateway connection is handled internally with heartbeat and reconnect support.
- The REST client is asynchronous and available through `bot.http`.

## Extensions (Cogs-like)

`clovord.py` supports extension modules via `setup(bot)`.

```python
from clovord import Container, TextDisplay

def setup(bot):
    @bot.command(name="hello")
    async def hello(ctx):
        await ctx.send(
            components=[
                Container(
                    TextDisplay("Hello from an extension"),
                    accent_color=0x3FE0C5,
                )
            ]
        )
```

```python
from pathlib import Path
from clovord import Bot

bot = Bot(command_prefix="!")

bot.load_extension("mybot.handlers.message_create")

bot.load_extensions(
    "mybot.handlers.message_create",
    "mybot.handlers.ready",
)

bot.load_extensions_from_package("mybot.handlers")

bot.load_extensions_from_path(Path(__file__).parent / "handlers")
```

<!-- latest-release-notes:start -->
## Latest Release Notes
Version: `0.1.42`
Last commit: channel message pins

### Added
- `Message.pin`, `Message.unpin`, and `Channel.pins`

See full history in CHANGELOG.md.
<!-- latest-release-notes:end -->
