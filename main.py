from router import route


def main():
    print("Query Router CLI — type 'exit' or 'quit' to stop.\n")
    while True:
        try:
            query = input("Query: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        response = route(query)
        print(response, "\n")


if __name__ == "__main__":
    main()
