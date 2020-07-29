from .feature import parse_commandline, create_new_branch


def main():
    args = parse_commandline()
    create_new_branch('feature', args)
