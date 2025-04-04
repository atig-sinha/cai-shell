import os
import sys
import shlex
import subprocess
import readline

# File to store command history
HISTORY_FILE = os.path.expanduser("~/.cai_history")

# Built-in commands
builtin_commands = {"echo", "exit", "type", "cd", "export", "unset"}

def load_history():
    """Load command history from a file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            for line in f:
                readline.add_history(line.strip())

def save_history():
    """Save command history to a file."""
    with open(HISTORY_FILE, "w") as f:
        for i in range(1, readline.get_current_history_length() + 1):
            f.write(readline.get_history_item(i) + "\n")

def execute_command(args):
    """Execute an external command."""
    try:
        os.execvp(args[0], args)
    except FileNotFoundError:
        print(f"{args[0]}: command not found")
        sys.exit(1)

def handle_builtin(command, args):
    """Handle built-in commands."""
    if command == "exit":
        save_history()  # Save history before exiting
        sys.exit(int(args[0]) if args else 0)
    elif command == "echo":
        print(" ".join(args))
    elif command == "cd":
        try:
            target_dir = args[0] if args else os.getenv("HOME")
            os.chdir(target_dir)
        except FileNotFoundError:
            print(f"cd: no such file or directory: {target_dir}")
        except IndexError:
            print("cd: missing argument")
    elif command == "type":
        if args[0] in builtin_commands:
            print(f"{args[0]} is a builtin command.")
        else:
            found = False
            for path in os.getenv("PATH").split(os.pathsep):
                if os.path.isdir(path):
                    for item in os.listdir(path):
                        if item == args[0]:
                            print(f"{args[0]} is {os.path.join(path, args[0])}")
                            found = True
                            break
                    if found:
                        break
            if not found:
                print(f"{args[0]}: command not found")
    elif command == "export":
        if args:
            key, value = args[0].split("=", 1)
            os.environ[key] = value
    elif command == "unset":
        if args:
            os.environ.pop(args[0], None)

def main():
    # Load command history
    load_history()

    while True:
        try:
            # Set up the prompt
            #{os.getcwd()}
            prompt = f"❰cai❱  ─► "
            # Use readline to handle input with history
            command = input(prompt)
            if not command.strip():
                continue

            # Add command to history
            readline.add_history(command)

            # Split the command into arguments
            args = shlex.split(command)
            command_name = args[0]

            if command_name in builtin_commands:
                handle_builtin(command_name, args[1:])
            else:
                # Handle external commands
                pid = os.fork()
                if pid == 0:
                    # Child process
                    execute_command(args)
                else:
                    # Parent process
                    os.waitpid(pid, 0)

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except EOFError:
            print("\nUse 'exit' to quit.")
            save_history()  # Save history before exiting
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()