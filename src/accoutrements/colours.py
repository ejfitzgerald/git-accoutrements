from colored import fg, attr


def _wrapper(text, code):
    return fg(code) + text + attr(0)


def red(text):
    return _wrapper(text, 1)


def green(text):
    return _wrapper(text, 2)


def yellow(text):
    return _wrapper(text, 3)


def blue(text):
    return _wrapper(text, 4)
