#!/usr/bin/python3

import os
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

    Process = Popen(
        [f"./wrk_helper.sh -t{args.t} -c{connections} -R{rps} -d{args.d} {args.url}"],
        shell=True, stdin=PIPE, stderr=PIPE)
    Process.communicate()


def run_wrk_parser():
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    reports = list(filter(
        lambda x: x.endswith(".txt"), files
    ))

    for report in reports:
        Process = Popen(
            [f"python ./wrk_parser.py {report}"],
            shell=True, stdin=PIPE, stderr=PIPE)
        Process.communicate()


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
        "-c",
        type=int,
        nargs="+",
        help="connections, eg -c 512 1024"
    )

    parser.add_argument(
        "url",
        type=str,
        help="Url"
    )

    args = parser.parse_args()

    run_wrk_helper(args)
    run_wrk_parser()


if __name__ == "__main__":
    main()
