#!/bin/bash

DEFAULT_WRK_EXEC_PATH="wrk"
DEFAULT_SLEEP_DURATION=30
DEFAULT_THREADS=1
DEFAULT_CONNECTIONS_VALUES=1
DEFAULT_DURATION=30
DEFAULT_RPS_VALUES=100
DEFAULT_URL=

show_help() {
    cat <<EOF
Usage: $0 [OPTIONS] <url>

Options:
  -h             Display this help message
  -t <threads>   Number of threads (default: $DEFAULT_THREADS)
  -c <connections>  Number of connections (default: $DEFAULT_CONNECTIONS_VALUES)
  -R <RPS>       Requests per second (default: $DEFAULT_RPS_VALUES)
  -d <duration>  Test duration (default: $DEFAULT_DURATION)
  -s <sleep>     Sleep between iterations (default: $DEFAULT_SLEEP_DURATION)
  -p <path>      Path to wrk executable (default: $DEFAULT_WRK_EXEC_PATH)
EOF
}

wrk_exec_path="$DEFAULT_WRK_EXEC_PATH"
sleep_duration="$DEFAULT_SLEEP_DURATION"
threads="$DEFAULT_THREADS"
connections_values="$DEFAULT_CONNECTIONS_VALUES"
duration="$DEFAULT_DURATION"
rps_values="$DEFAULT_RPS_VALUES"
url="$DEFAULT_URL"

while getopts ":ht:t:c:d:R:s:p:" opt; do
    case $opt in
        h) show_help; exit 0 ;;
        t) threads=$OPTARG;;
        c) connections_values=$OPTARG;;
        d) duration=$OPTARG;;
        R) rps_values=$OPTARG;;
        s) sleep_duration=$OPTARG;;
        p) wrk_exec_path=$OPTARG;;
        \?) echo "Invalid option: -$OPTARG" >&2; exit 1;;
        :)  echo "Option -$OPTARG requires an argument." >&2; exit 1;;
    esac
done

shift $((OPTIND -1))
url=$1
if [ -z "$url" ]; then
    echo "Error: url is required." >&2
    show_help
    exit 1
fi

IFS=',' read -r -a connections_values <<< "$connections_values"
IFS=',' read -r -a rps_values <<< "$rps_values"

if [ ${#connections_values[@]} -eq 0 ] || [ ${#rps_values[@]} -eq 0 ]; then
    echo "Invalid array values. Please provide valid connections and RPS as arrays."
    exit 1
fi

safe_url=$(echo "$url" | sed 's/[^a-zA-Z0-9]/_/g')
for connections in "${connections_values[@]}"; do
  output_file="$(date '+%Y_%m_%d_%H_%M_%S')-$safe_url-c-$connections.txt"
  echo "$output_file"
  touch "$output_file"

  for rps in "${rps_values[@]}"; do
    echo "Running test with $connections connections and $rps RPS..."
    command="$wrk_exec_path -t$threads -c$connections -R$rps -d$duration -L $url"
    echo "$command" >> "$output_file"
    $command 2>&1 | tee -a "$output_file"
    echo "-------------------------------------------" >> "$output_file"
    echo "Test completed. Sleep $sleep_duration"
    sleep "$sleep_duration"
    echo "-------------------------------------------"
  done
done

echo "All tests completed."
