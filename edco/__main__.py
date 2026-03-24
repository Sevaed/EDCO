from . import commands as cmd
from . import tui
from . import data
import click
import sys

CONTEXT_SETTINGS = dict(
    token_normalize_func=lambda x: x.lower(), help_option_names=["-h", "--help"]
)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("app_name", required=False)
@click.option(
    "-e",
    "--editor",
    "editor",
    type=str,
    help="editor to use, for example: nvim, /usr/sbin/vim",
    metavar="<editor>",
)
@click.option(
    "-c",
    "--cat",
    "cat",
    type=str,
    help="shows you content of given config",
    metavar="<app_name>",
)
@click.option(
    "-p",
    "--path",
    "path",
    type=str,
    help="shows you path of given config",
    metavar="<app_name>",
)
@click.option("-l", "--list", "list", is_flag=True, help="shows you yours added apps")
@click.option(
    "-d",
    "--delete",
    "delete",
    type=str,
    help="deletes yours app from apps_list",
    metavar="<app_name>",
)
@click.option(
    "-dg",
    "--delete-group",
    "delete_group",
    type=str,
    help="deletes all apps in group <group> from apps_list",
    metavar="<group_name>",
)
@click.option(
    "-a",
    "--add",
    "add",
    type=(click.Path(), str),
    help="adds <path> as <name> into yours apps_list",
    metavar="<app_config_path> <app_name>",
)
@click.option(
    "-g",
    "--group",
    "group",
    type=str,
    help="provides group for --add if needed",
    metavar="<group_name>",
)
def main(app_name, editor, cat, path, list, delete, delete_group, add, group):
    """
    (Better help in future)\n
    Use without arguments to summon TUI, use with app_name to edit config for given app
    """
    sum_of_options = sum(
        map(
            bool,
            [app_name, editor, cat, path, list, delete, delete_group, add, group],
        )
    )
    if sum_of_options == 0:
        tui.run_tui()
    elif sum_of_options > 2:
        raise click.UsageError("Too many options")
    elif sum_of_options == 1:
        if group:
            raise click.UsageError(
                "--group cannot be used without --add, use --help for usage"
            )
        if editor:
            raise click.UsageError(
                "specify which app config you want to edit, use --help for usage"
            )
        if app_name:
            cmd.edit_app_config(app_name)
        if cat:
            cmd.cat(cat)
        if path:
            cmd.path(path)
        if list:
            cmd.print_names()
        if delete:
            cmd.del_elements("name", delete)
        if delete_group:
            cmd.del_elements("group", delete_group)
        if add:
            cmd.add_app(add[1], add[0])
    else:
        if app_name and editor:
            cmd.edit_app_config(app_name, editor)
        elif add and group:
            cmd.add_app(add[1], add[0], group)


if __name__ == "__main__":
    main()
