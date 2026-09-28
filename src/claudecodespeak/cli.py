"""claudecodespeak のエントリポイント。サブコマンド hook と add-word をまとめる。"""

import click

from . import __version__
from .add_word import main as add_word
from .click_utils import click_common_opts
from .hook import main as hook
from .mylog import getLogger, loggerInit

_log = getLogger("main")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click_common_opts(__version__)
def cli(ctx, debug):
    """Claude Code の返答を VOICEVOX で読み上げる。"""
    loggerInit(debug)
    _log.debug(f"debug={debug}")


cli.add_command(hook, name="hook")
cli.add_command(add_word, name="add-word")


if __name__ == "__main__":
    cli()
