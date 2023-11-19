#!/usr/bin/expect -f

log_user 1

set id [lindex $argv 0]
set username [lindex $argv 1]
set password [lindex $argv 2]

spawn nmcli connection up ${id} --ask

expect {
    "Enter 'yes' to accept, 'no' to abort; anything else to view:" {
        send -- "yes\r"
        exp_continue
    }
    "Username:" { 
        send -- "${username}\r"
        exp_continue
    }
    "Password:" { 
        send -- "${password}\r"
        exp_continue
    }
    "Gateway (vpn.secrets.gateway):" {
        send -- "\r"
        exp_continue
    }
    "Cookie (vpn.secrets.cookie):" {
        send -- "\r"
        exp_continue
    }
    "Gateway certificate hash (vpn.secrets.gwcert):" {
        send -- "\r"
        exp_continue
    }
}

exit
