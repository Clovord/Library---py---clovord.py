# clovord

A Python SDK for interacting with the Clovord Gateway and REST API.

## Installation

```bash
pip install .
```

## Usage

```python
from clovord import Bot

bot = Bot()


@bot.event
async def on_ready() -> None:
    print("Bot is ready")


@bot.event
async def on_message(message) -> None:
    print(message.content)


bot.run("TOKEN")
```

## Overview

- `Bot` is the main entrypoint.
- The Gateway connection is handled internally with heartbeat and reconnect support.
- The REST client is asynchronous and available through `bot.http`.
