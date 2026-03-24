import click

CONTEXT_SETTINGS = dict(token_normalize_func=lambda x: x.lower())


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("-c", "--cat", "cat", type=str)
@click.option("-p", "--path", "path", type=str)
@click.option("-l", "--list", "list", is_flag=True)
@click.option("-d", "--delete", "delete", type=str)
@click.option("-a", "--add", "add", type=(click.Path(), str))
@click.option("-g", "--group", "group", type=str)
@click.argument("sas", required=False)
def main(cat, path, list, delete, add, group, sas):
    click.echo([cat, path, list, delete, add, group, sas])
    click.echo(sum(map(bool, [cat, path, list, delete, add, group, sas])))


main()
