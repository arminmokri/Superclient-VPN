#!/bin/bash

memory_path="/memory"

swap_enable="no"
swapfile_path="/mnt/swapfile"
if [[ $swap_enable == "yes" ]]; then
    ### Wait For swapon tmpfs
    for i in {1..300}
    do
        ### check memory storage Mount
        echo "check swapon tmpfs Mount try($i)"
        if [ -n "$(swapon --show | grep $swapfile_path)" ]; then
            break
        fi
    
    ### sleep
    sleep 1
    done
fi

if [[ ! -e $memory_path ]]; then
    mkdir -p $memory_path
fi

mount -t tmpfs -o size=8M,mode=0755 tmpfs $memory_path
