#!/usr/bin/python3

import os
import sys
import time
import math
from datetime import datetime
from argparse import ArgumentParser, Namespace
from collections.abc import Iterable
from subprocess import Popen, PIPE

def make_rps_arg(rps: Iterable[int]):
    start, stop, step = rps
    return range(start, stop + step, step)

def run_tests(args: Namespace):
    rps = make_rps_arg(args.R)
    safe_url = args.url.replace(":", "_").replace("/", "_").replace(".", "_")

    for conn in args.c:
        output_file = f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}-{safe_url}-c{conn}.txt" 
        run_test(rps, conn, output_file, args)
    print("-------------------------------------------", end="\n")
    print("Done", end="\n")

def run_test(rps, conn, output_file, args: Namespace):
    with open(output_file, "w+") as f:
        for i, requested_rps in enumerate(rps):
            total_connections = len(args.c) * len(rps)
            total_runs = total_connections - i + 1
            estimated_time = (args.s + args.d) * total_runs / 60.0
            estimated_time = math.floor(estimated_time)

            print(f"Running test with {conn} connections and {requested_rps} RPS... ({estimated_time}m left)")
            run_wrk_command(requested_rps,conn, args, f)


def run_wrk_command(rps, connections, args: Namespace, file = None):
    exec = f"{args.p} -t{args.t} -c{connections} -d{args.d}s -R{rps} -L" 
                
    if args.S:
        exec = f"{exec} -s {args.S}"

    exec = f"{exec} {args.url}"

    if args.S and args.a:
        exec = exec.replace(args.url, "")
        exec = f"{exec} {args.url} -- {' '.join(args.a)}"

    print("Running: ", exec)
    
    if file:
        file.write(f"{exec}\n")
        file.flush()

    Process = Popen([exec], shell=True, stdin=PIPE, stderr=PIPE, stdout=file or PIPE) 
    _, stderr = Process.communicate()
    if stderr:
        print(stderr)

    if file:
        file.write("-------------------------------------------\n")
        file.flush()

    print("-------------------------------------------", end="\n")
    print(f"Done. Sleep {args.s}", end="\n")
    time.sleep(int(args.s))


def run_wrk_helper(args: Namespace):
    files_before = os.listdir('.')
    
    run_tests(args)

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
