import ivyhandler as ivyh
import json
import os

# ANSI COLORS
GREEN = "\033[32m"
LIME = "\033[38;5;154m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
RESET = "\033[0m"

def clear():
    if os.name == 'nt':
        os.system("cls")
    else:
        os.system("clear")

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

while True:
    clear()

    inp = input(f"{BOLD}{ITALIC}{GREEN}Command:{RESET} ").strip()

    if inp == "":
        continue

    if inp.startswith("/ask "):
        question = inp[len("/ask "):]

        print(f"{BOLD}{ITALIC}{LIME}Ivy:{RESET} ", end="")

        buffer = ""

        # Stream and buffer to avoid word-by-word output
        for chunk in ivyh.completion_stream(config["llms"]["grok-4.1-fast"]["url"], question):
            buffer += chunk + " "
            if len(buffer) > 50:  # tuning size
                print(buffer, end="", flush=True)
                buffer = ""

        # Print leftover
        if buffer:
            print(buffer, end="", flush=True)

        print("\n")
        input("Press Enter...")

    elif inp.lower() in ("/quit", "/exit"):
        print(f"{BOLD}\033[31mExiting...{RESET}")
        break

    else:
        print(f"\033[33mUnknown command:\033[0m {inp}")
