#!/usr/bin/python3

# imports
import time

from .Router import *


# global
while_flag = True
load_vpn = True
parser = None
exit_code = 0


def usage():
    parser.print_help()
    return


def main():
    global parser
    global exit_code
    try:
        router = Router()
        while while_flag:

            if load_vpn:
                router.LoadVPN()
                load_vpn = False

            time.sleep(1)

    except Exception as e:
        print(e)
        usage()
    finally:
        exit(exit_code)


if __name__ == "__main__":
    main()
