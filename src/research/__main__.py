"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Re-Search."""


if __name__ == "__main__":
    main(prog_name="re-search")  # pragma: no cover
