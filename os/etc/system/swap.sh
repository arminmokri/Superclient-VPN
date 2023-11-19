#!/bin/bash

swap_enable="yes"
swapfile_path="/mnt/swapfile"
swap_size=512 # MB

if [[ $swap_enable == "yes" ]]; then
    flag=0
    if [[ ! -f $swapfile_path ]]; then
        flag=1
        echo "swap file $swapfile_path not exist."
    else
        current_swapfile_size=$(stat -c %s $swapfile_path)
        swapfile_size=$(($swap_size * 1048576))
        if [[ $current_swapfile_size -ne $swapfile_size ]]; then
            flag=1
            echo "swap file $swapfile_path size changed."
        fi
    fi

    if [[ $flag -eq "1" ]]; then
        dd if=/dev/zero of=$swapfile_path bs=1024 count=$(($swap_size * 1024))
        chmod 600 $swapfile_path
        mkswap $swapfile_path
        echo "swap file $swapfile_path created."
    fi

    if [ -z "$(swapon --show | grep $swapfile_path)" ]; then
        swapon $swapfile_path
        echo "swap file $swapfile_path mounted."
    else
        echo "swap file $swapfile_path is already mount."
    fi
else
    echo "swap is disabled."
fi
