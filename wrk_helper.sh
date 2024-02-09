#!/bin/bash

if [[ $1 = "-h" ]]; then
    echo "Usage: $0 -t <threads> -c <connections> -R <RPS> -d <duration> --sleep <iteration sleep> <url>"
    exit 1
fi

SLEEP_DURATION=30
THREADS=1
CONNECTIONS_VALUES=1
DURATION=30
RPS_VALUES=100
URL=

while getopts ":t:c:d:R:sleep:" opt; do
    case $opt in
        t) THREADS=$OPTARG;;
        c) CONNECTIONS_VALUES=$OPTARG;;
        d) DURATION=$OPTARG;;
        R) RPS_VALUES=$OPTARG;;
        sleep) SLEEP_DURATION=$OPTARG;;
        \?) echo "Invalid option: -$OPTARG" >&2; exit 1;;
        :)  echo "Option -$OPTARG requires an argument." >&2; exit 1;;
    esac
done

shift $((OPTIND -1))
URL=$1

if [ -z "$URL" ]; then
    echo "URL is required"
    exit 1
fi

IFS=',' read -r -a CONNECTIONS_VALUES <<< "$CONNECTIONS_VALUES"
IFS=',' read -r -a RPS_VALUES <<< "$RPS_VALUES"

if [ ${#CONNECTIONS_VALUES[@]} -eq 0 ] || [ ${#RPS_VALUES[@]} -eq 0 ]; then
    echo "Invalid array values. Please provide valid connections and RPS as arrays."
    exit 1
fi

for connections in "${CONNECTIONS_VALUES[@]}"; do
  safe_url=$(echo "$URL" | sed 's/[^a-zA-Z0-9]/_/g')
  OUTPUT_FILE="$(date '+%Y_%m_%d_%H_%M_%S')-$safe_url-c-$connections.txt"
  echo "$OUTPUT_FILE"
  touch "$OUTPUT_FILE"

  for rps in "${RPS_VALUES[@]}"; do
    echo "Running test with $connections connections and $rps RPS_VALUES..."
    command="wrk -t$THREADS -c$connections -R$rps -d$DURATION -L $URL"
    echo "$command" >> "$OUTPUT_FILE"
    $command >> "$OUTPUT_FILE" 2>&1
    echo "-------------------------------------------" >> "$OUTPUT_FILE"
    echo "Test completed. Sleep $SLEEP_DURATION"
    sleep "$SLEEP_DURATION"
    echo "-------------------------------------------"
  done
done

echo "All tests completed."
