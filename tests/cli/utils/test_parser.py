from typing import Tuple

import pytest
from propan.cli.utils.parser import parse_cli_args

APPLICATION = "module:app"

ARG1 = (
    "--k",
    "1",
)
ARG2 = (
    "-k2",
    "1",
)
ARG3 = ("--k3",)
ARG4 = ("--no-k4",)
ARG5 = (
    "--k5",
    "1",
    "1",
)
ARG6 = ("--some-key",)


@pytest.mark.parametrize(
    "args",
    (
        (APPLICATION, *ARG1, *ARG2, *ARG3, *ARG4, *ARG5, *ARG6),
        (*ARG1, APPLICATION, *ARG2, *ARG3, *ARG4, *ARG5, *ARG6),
        (*ARG1, *ARG2, APPLICATION, *ARG3, *ARG4, *ARG5, *ARG6),
        (*ARG1, *ARG2, *ARG3, APPLICATION, *ARG4, *ARG5, *ARG6),
        (*ARG1, *ARG2, *ARG3, *ARG4, APPLICATION, *ARG5, *ARG6),
        (*ARG1, *ARG2, *ARG3, *ARG4, *ARG5, APPLICATION, *ARG6),
        (*ARG1, *ARG2, *ARG3, *ARG4, *ARG5, *ARG6, APPLICATION),
    ),
)
def test_custom_argument_parsing(args: Tuple[str]):
    app_name, extra = parse_cli_args(*args)
    assert app_name == APPLICATION
    assert extra == {
        "k": "1",
        "k2": "1",
        "k3": True,
        "k4": False,
        "k5": ["1", "1"],
        "some_key": True,
    }
