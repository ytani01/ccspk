"""ccspk のエントリポイント。サブコマンド hook・say・stop・status・summary・queue・translate・test・dict をまとめる。"""

import click

from . import __version__
from .check import demo as check_demo
from .click_utils import click_common_opts
from .hook import demo as hook_demo
from .hook import main as hook
from .hook import queue_, say, status, stop, summary, translate
from .mylog import getLogger, loggerInit
from .user_dict import demo as dict_demo
from .user_dict import dict_group

_log = getLogger("main")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click_common_opts(__version__)
def cli(ctx, debug):
    """Claude Code の返答を VOICEVOX で読み上げる。"""
    loggerInit(debug)
    _log.debug(f"debug={debug}")


@cli.command("test")
def test():
    """hook・dict・check の自己テストを走らせる。"""
    hook_demo()
    dict_demo()
    check_demo()


cli.add_command(hook, name="hook")
cli.add_command(say, name="say")
cli.add_command(stop, name="stop")
cli.add_command(status, name="status")
cli.add_command(summary, name="summary")
cli.add_command(queue_, name="queue")
cli.add_command(translate, name="translate")
cli.add_command(dict_group, name="dict")


if __name__ == "__main__":
    cli()
