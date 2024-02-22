#!/bin/bash

DEFAULT_WRK_EXEC_PATH="wrk"
DEFAULT_SLEEP_DURATION=30
DEFAULT_THREADS=1
DEFAULT_CONNECTIONS_VALUES=1
DEFAULT_DURATION=30
DEFAULT_RPS_VALUES=100
DEFAULT_URL=
DEFAULT_VERBOSE=0

show_help() {
    cat <<EOF
Usage: $0 [OPTIONS] <url>

Options:
  -h                Display this help message
  -t <threads>      Number of threads (default: $DEFAULT_THREADS)
  -c <connections>  Array of numbers of connections (eg: "50,100,1000") (default: $DEFAULT_CONNECTIONS_VALUES)
  -R <RPS>          Array of requests per second (eg: "50,100,1000") (default: $DEFAULT_RPS_VALUES)
  -d <duration>     Test duration (default: $DEFAULT_DURATION)
  -s <sleep>        Sleep between iterations (default: $DEFAULT_SLEEP_DURATION)
  -p <exec path>    Path to wrk executable (default: $DEFAULT_WRK_EXEC_PATH)
  -v <verbose>      Duplicate wrk output to console
EOF
}

wrk_exec_path="$DEFAULT_WRK_EXEC_PATH"
sleep_duration="$DEFAULT_SLEEP_DURATION"
threads="$DEFAULT_THREADS"
connections_values="$DEFAULT_CONNECTIONS_VALUES"
duration="$DEFAULT_DURATION"
rps_values="$DEFAULT_RPS_VALUES"
url="$DEFAULT_URL"
verbose="$DEFAULT_VERBOSE"

while getopts ":ht:t:c:d:R:s:p:vt:" opt; do
    case $opt in
        h) show_help; exit 0 ;;
        t) threads=$OPTARG;;
        c) connections_values=$OPTARG;;
        d) duration=$OPTARG;;
        R) rps_values=$OPTARG;;
        s) sleep_duration=$OPTARG;;
        p) wrk_exec_path=$OPTARG;;
        v) verbose=1;;
        \?) echo "Invalid option: -$OPTARG" >&2; exit 1;;
        :)  echo "Option -$OPTARG requires an argument." >&2; exit 1;;
    esac
done

shift $((OPTIND -1))
url=$1
if [ -z "$url" ]; then
    echo "Error: URL is required." >&2
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
i=0
for connections in "${connections_values[@]}"; do
  output_file="$(date '+%Y_%m_%d_%H_%M_%S')-$safe_url-c$connections.txt"
  echo -e "\n$output_file\n------------"

  for rps in "${rps_values[@]}"; do
    ((i++))
    estTimeM=$(echo "scale=2; (($duration + $sleep_duration) * ((${#connections_values[@]} * ${#rps_values[@]}) - $i + 1) - $sleep_duration) / 60" | bc)
    estTimeM=$(echo "$estTimeM" | awk '{printf "%g", $0}')
    echo -e "$i/$((${#connections_values[@]} * ${#rps_values[@]})): Running test with $connections connections and $rps RPS... (all tests will end in ${estTimeM}m)"

    command="$wrk_exec_path -t$threads -c$connections -R$rps -d$duration -L $url"
    echo "$command" >> "$output_file"

    if [ "$verbose" = "1" ]; then
      $command 2>&1 | tee -a "$output_file"
    else
      output=$($command 2>&1)
      if [ $? -ne 0 ]; then
        echo "$output"
        echo "$output" >> "$output_file"
      else
        echo "$output" >> "$output_file"
      fi
    fi
    echo "-------------------------------------------" >> "$output_file"

    if [ "$i" -ne "$(( ${#connections_values[@]} * ${#rps_values[@]}))" ]; then
      echo "Done. Sleep $sleep_duration"
      sleep "$sleep_duration"
    else
      echo "Done"
    fi
  done
done

echo -e "\nAll tests completed."
