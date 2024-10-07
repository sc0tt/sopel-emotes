# sopel-emotes

This module searches for emotes in messages from multiple sources (7TV, BetterTTV, FrankerFaceZ). It searches for emotes in the format `:emote_name:` and looks them up from the available emote sources based on a configurable priority list. The emote size is also configurable.
    
Features:
- Configurable emote sources and search priority (7TV, BTTV, FFZ) via Sopel config.
- Configurable emote size (small, medium, large) via Sopel config.
- Handles multiple emotes in a single message with rate limiting delays.

Future Tasks:
- Caching


## Installing

Releases are hosted on PyPI, so after installing Sopel, all you need is `pip`:

```shell
$ pip install sopel-emotes
```

## Configuring

The easiest way to configure `sopel-emotes` is via Sopel's
configuration wizard—simply run `sopel-plugins configure emotes`
and enter the values for which it prompts you.

### Manual configuration

```ini
[emotes]
sources = bttv, ffz # Available options: [7tv, ffz, bttv]. Order determines priority.
size = large # small, medium, or large
```