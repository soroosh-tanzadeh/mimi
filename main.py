import signal

from cli.agent import Agent


def handler(signum, frame):
    print("\n Use 'quit' command to exit.")


def main() -> None:
    agent = Agent("User> ")
    agent.run()


if __name__ == "__main__":
    # Set the signal handler
    signal.signal(signal.SIGINT, handler)
    main()
