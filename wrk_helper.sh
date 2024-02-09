#!/bin/bash

if [[ $1 = "-h" ]]; then
    echo "Usage: $0 -t <threads> -c <connections> -d <duration> -R <requests per second> <url>"
    exit 1
fi

SLEEP_DURATION=60
THREADS=
CONNECTIONS_VALUES=
DURATION=
RPS_VALUES=
URL=

while getopts ":t:c:d:R:" opt; do
    case $opt in
        t) THREADS=$OPTARG;;
        c) CONNECTIONS_VALUES=$OPTARG;;
        d) DURATION=$OPTARG;;
        R) RPS_VALUES=$OPTARG;;
        \?) echo "Invalid option: -$OPTARG" >&2; exit 1;;
        :)  echo "Option -$OPTARG requires an argument." >&2; exit 1;;
    esac
done

shift $((OPTIND -1))
URL=$1

if [ -z "$THREADS" ] || [ -z "$CONNECTIONS_VALUES" ] || [ -z "$DURATION" ] || [ -z "$RPS_VALUES" ] || [ -z "$URL" ]; then
    echo "All parameters are required."
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
    command="wrk -c $connections -t $THREADS -d $DURATION -L -R $rps $URL"
    echo "$command" >> "$OUTPUT_FILE"
    $command >> "$OUTPUT_FILE" 2>&1
    echo "-------------------------------------------" >> "$OUTPUT_FILE"
    echo "Test completed. Sleep $SLEEP_DURATION"
    sleep "$SLEEP_DURATION"
    echo "-------------------------------------------"
  done
done

echo "All tests completed."
