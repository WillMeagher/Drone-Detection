import termios, tty, sys, select

CHARACTER_MAPPINGS = {
    "esc": "\x1B"
}

# Save terminal settings
old = termios.tcgetattr(0)
# Disable buffering
tty.setcbreak(0)


def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def check(input_val = "esc"):
    if isData():
        if input_val in CHARACTER_MAPPINGS:
            input_val = CHARACTER_MAPPINGS[input_val]

        return sys.stdin.read(1) == input_val
    else:
        return False


def exit():
    termios.tcsetattr(0, termios.TCSANOW, old)