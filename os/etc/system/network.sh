#!/bin/bash

this_file_path=$(eval "realpath $0")
this_dir_path=$(eval "dirname $this_file_path")

for dev in $($this_dir_path/interface_list.sh eth | awk '{ print length(), $0 | "sort -n" }' | awk '{ print $2 }'); do
    dhclient -v $dev
    break
done
