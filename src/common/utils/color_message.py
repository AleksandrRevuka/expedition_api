import click


def color_message(message: str, status: str) -> str:
    if status == "started":
        color_message = click.style(message, fg="green", italic=True)
    elif status == "error":
        color_message = click.style(message, fg="red", italic=True)
    elif status == "warning":
        color_message = click.style(message, fg="yellow", italic=True)
    elif status == "time":
        color_message = click.style(message, fg="bright_yellow", italic=True)
    elif status == "stopped":
        color_message = click.style(message, fg="bright_yellow", italic=True)
    elif status == "header":
        color_message = click.style(message, fg="cyan", italic=True)
    else:
        color_message = click.style(message, fg="blue", italic=True)
    return color_message
