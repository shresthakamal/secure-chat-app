import click


@click.command()
@click.option("-p", help="Poison", default=False, is_flag=True)
@click.option("-up", help="Client Side Communication", default=False, is_flag=True)
def main(p, up):
    if up:
        with open("secure_chat_app.py", "r") as chat_file:
            handler = chat_file.read()

        handler = handler.replace("172.31.0.4", "172.31.0.3")

        with open("secure_chat_app.py", "w") as chat_file:
            chat_file.write(handler)

    if p:
        with open("secure_chat_app.py", "r") as chat_file:
            handler = chat_file.read()

        handler = handler.replace("172.31.0.3", "172.31.0.4")

        with open("secure_chat_app.py", "w") as chat_file:
            chat_file.write(handler)


if __name__ == "__main__":
    main()
