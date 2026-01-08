#!/usr/bin/env python3
import sys

CAT_LOGOGRAM = r"""
             /\_/\ 
            ( o.o )
             > ^ <
  Hi, I'm Mimi. How can I assist you today?
""".strip(
    "\n"
)

CSI = "\x1b["


def cyan(text: str) -> str:
    # Bright cyan (common across terminals): 96m
    return f"{CSI}96m{text}{CSI}0m"


def showIntro() -> None:
    out = CAT_LOGOGRAM

    # Only colorize when printing to an interactive terminal
    if sys.stdout.isatty():
        out = cyan(out)

    print(out)
