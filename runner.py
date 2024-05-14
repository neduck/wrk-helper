#!/usr/bin/python3

import os
import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Iterable
from subprocess import Popen, PIPE


def make_rps_arg(rps: Iterable[int]) -> str:
    start, stop, step = rps
    args_list = [str(arg) for arg in range(start, stop + step, step)]
    return ",".join(args_list)


def run_wrk_helper(args: Namespace):
    rps = make_rps_arg(args.R)
    connections = args.c[0]
    if len(args.c) > 1:
        connections = ",".join(
            map(str, args.c)
        )

    files_before = os.listdir('.')

    exec = ""
    if args.p:
        exec = f"{os.path.dirname(os.path.abspath(sys.argv[0]))}/wrk_helper.sh -t{args.t} -c{connections} -R{rps} -d{args.d} -s{args.s} -p {args.p} {args.url}"
    else:
        exec = f"{os.path.dirname(os.path.abspath(sys.argv[0]))}/wrk_helper.sh -t{args.t} -c{connections} -R{rps} -d{args.d} -d{args.s} -p wrk {args.url}"

    print(exec)

    Process = Popen(
        [exec],
        shell=True, stdin=PIPE, stderr=PIPE)
    stdout, stderr = Process.communicate()
    if stderr:
        print(stderr)

    files_after = os.listdir('.')
    new_reports = [file for file in files_after if file not in files_before and file.endswith(".txt") and os.path.isfile(file)]
    return new_reports


def run_wrk_parser(new_reports):
    for report in new_reports:
        exec = f"{sys.executable} {os.path.dirname(os.path.abspath(sys.argv[0]))}/wrk_parser.py {report}"

        print(exec)

        Process = Popen(
            [exec],
            shell=True, stdin=PIPE, stderr=PIPE)
        stdout, stderr = Process.communicate()
        if stderr:
            print(stderr)


def main():
    parser = ArgumentParser(description="Helper for wrk")
    parser.add_argument(
        "-R",
        type=int,
        nargs=3,
        help=" RPS start stop step for generation RPS parameter string, eg -R 100 1000 200"
    )

    parser.add_argument(
        "-t",
        type=int,
        help="Number of threads (default: $DEFAULT_THREADS)"
    )

    parser.add_argument(
        "-d",
        type=int,
        help="Duration"
    )

    parser.add_argument(
        "-s",
        type=int,
        help="Sleep"
    )

    parser.add_argument(
        "-c",
        type=int,
        nargs="+",
        help="connections, eg -c 512 1024"
    )

    parser.add_argument(
        "-p",
        type=str,
        help="path to wrk script, eg -p /usr/local/bin/wrk (default: wrk)"
    )

    parser.add_argument(
        "url",
        type=str,
        help="Url"
    )

    args = parser.parse_args()

    new_reports = run_wrk_helper(args)
    run_wrk_parser(new_reports)


if __name__ == "__main__":
    main()
