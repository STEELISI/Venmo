#!/bin/bash
while true
do
    echo "Executing..."
    python3 get_intermediate_outputs.py intermediate_results
    sleep 86400
done
