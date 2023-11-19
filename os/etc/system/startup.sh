#!/bin/bash

my_print() {
   local message=$1
   local res=$2
   if [[ "$res" == "0" ]]; then
      echo "$message: Successed"
   else
      echo "$message: Failed"
   fi
}

### vars
this_file_path=$(eval "realpath $0")
this_dir_path=$(eval "dirname $this_file_path")

# dir var
disk_dir_path="/disk"
memory_dir_path="/memory"
tmp_dir_path="/tmp"

# rapo var
logo_path="$this_dir_path/logo"

#
repo_name=$(firmware --action get_repo_name --repo-name-path "${disk_dir_path}/name" | tr -d '\n')

# firmware var
firmware_dir_path="$disk_dir_path/firmware"
firmware_latest_path=$(firmware --action get_latest_firmware --repo-name-path "${disk_dir_path}/name" --firmware-dir-path "${firmware_dir_path}" | tr -d '\n')
firmware_app_unpack_path="$memory_dir_path"
firmware_os_unpack_path="$tmp_dir_path"
firmware_app_init_path="$firmware_app_unpack_path/bin/init.sh"
firmware_app_init_log="$tmp_dir_path/${repo_name}-init.log"


### Move Cursor Down And Print Logo
echo -e "\n\n\n\n\n\n"
cat $logo_path
echo -e "\n"

### Wait For Mount /memory
echo "Initial Storage... Started"
for i in {1..300}
do
   ### check memory storage Mount
   mountpoint -q $memory_dir_path
   res=$?
   my_print "check memory storage Mount try($i)" $res
   if [ $res -eq 0 ]; then
      break
   fi
   
   ### sleep Mount
   sleep 1
done
echo "Initial Storage... End"

### Application
echo "Initial Application... Start"
if [ -f "$firmware_latest_path" ]; then

   ### rm app files Application
   str_rm=$(rm -rf $firmware_app_unpack_path/*)
   res_rm=$?
   my_print "rm ${firmware_app_unpack_path}/* files" $res_rm

   str_app=$(firmware --action unpack_latest_firmware --repo-name-path "${disk_dir_path}/name" --firmware-dir-path "${firmware_dir_path}" --unpack-firmware-path "${firmware_app_unpack_path}" --unpack-firmware-exclude os)
   res_app=$?
   my_print "unpack Application files" $res_app

   str_os=$(firmware --action unpack_latest_firmware --repo-name-path "${disk_dir_path}/name" --firmware-dir-path "${firmware_dir_path}" --unpack-firmware-path "${firmware_os_unpack_path}" --unpack-firmware-include os)
   res_os=$?
   my_print "unpack OS files" $res_os

   ### run init app
   res_init=1
   if [[ "${res_app}" == "0" ]] && [[ "${res_os}" == "0" ]]; then
      $firmware_app_init_path &>$firmware_app_init_log &
      res_init=$?
   fi
   my_print "run Application init" $res_init

else
   my_print "No Firmware" 1
fi
echo "Initial Application... End"

exit 0
