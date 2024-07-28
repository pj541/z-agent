import argparse
from .web_sockets import SocketConnector
from getpass import getpass
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--command", help="It defines the command that needs to be executed", required=True)
    parser.add_argument("-u", "--username", help="username to log into the server", required=True)
    parser.add_argument("-s", "--host", help="host to connect to by default it is localhost")
    args = parser.parse_args()
    password = getpass()
    try:
        socks = SocketConnector(host=args.host, port='1463', username=args.username, password=password)
        exit_code = socks.run(args.command)
        if exit_code.get("status"):
            exit_code = socks.pull_proc_info(procid=exit_code.get("id"),wait_for_output=True)
        print(exit_code)
    except Exception as E:
        print(f"{E}")
    # if exit_code == '0':
    #     print(f'Successfully executed command \'{args.command}\'')
    # else:
    #     print(f'Could not execute command \'{args.command}\'')
    #     #raise Exception(f'Could not execute command \'{args.command}\'')

if __name__ == "__main__":
    main()