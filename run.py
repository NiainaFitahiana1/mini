import click
from app.main import app
from app.cli.commands import cli as cli_group

@click.group()
def main():
    pass

@main.command("run")
def run_server():
    debug=False
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)

# Accroche les commandes custom (init-db, set-user)
main.add_command(cli_group)

if __name__ == "__main__":
    main()
