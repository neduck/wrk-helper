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

    exec = f"{os.path.dirname(os.path.abspath(sys.argv[0]))}/wrk_helper.sh -t{args.t} -c{connections} -R{rps} -d{args.d} -s{args.s} -p {args.p} {args.url}"

    if args.S:
       exec = f"{os.path.dirname(os.path.abspath(sys.argv[0]))}/wrk_helper.sh -t{args.t} -c{connections} -R{rps} -d{args.d} -s{args.s} -p {args.p} -S {args.S} {args.url}"

    if args.S and args.a:
       exec = f"{os.path.dirname(os.path.abspath(sys.argv[0]))}/wrk_helper.sh -t{args.t} -c{connections} -R{rps} -d{args.d} -s{args.s} -p {args.p} -S {args.S} -a {','.join(args.a)} {args.url}"

    print("Running: ", exec)

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

        print("Running: ", exec)

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
        default=1,
        help="Number of threads (default: 1)"
    )

    parser.add_argument(
        "-d",
        type=int,
        default=15,
        help="Duration (default: 15)"
    )

    parser.add_argument(
        "-s",
        type=int,
        default=15,
        help="Sleep (default: 15)"
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
        default="wrk",
        help="path to wrk script, eg -p /usr/local/bin/wrk (default: wrk)"
    )

    parser.add_argument(
        "--with-graph",
        action='store_true',
        help="Generate graph"
    )

    parser.add_argument(
        "url",
        type=str,
        help="Url"
    )

    parser.add_argument(
        "-S",
        type=str,
        help="Lua script path for complicated cases loadtesting"
    )

    parser.add_argument(
       "-a",
       type=str,
       nargs="+",
       help="args for Lua script, eg -a foo bar" 
    )

    args = parser.parse_args()

    new_reports = run_wrk_helper(args)
    if args.with_graph:
        run_wrk_parser(new_reports)


if __name__ == "__main__":
    main()
