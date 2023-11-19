#!/bin/bash

########################################################################
# Define various configuration parameters.
########################################################################

SUBNET_INTERFACE=${1}
SOCKS_PORT=${2}
SOCKS_IP="127.0.0.1"
SOCKS_SERVER_IP=${3}
SOCKS_SERVER_PORT=${4}
REDSOCKS_CONF=${5}
REDSOCKS_LOG=${6}
REDSOCKS_IP="0.0.0.0"
REDSOCKS_PORT_TCP=$(expr $SOCKS_PORT + 1)
REDSOCKS_PORT_UDP=$(expr $SOCKS_PORT + 1)
USE_DNS2SOCKS=${7}
DNSServer=${8}
DNS2SOCKS_LOG=${9}


########################################################################
# redsocks configuration
########################################################################

cat >$REDSOCKS_CONF <<EOF
base {
	// debug: connection progress
	log_debug = off;

	// info: start and end of client session
	log_info = on;

	/* possible 'log' values are:
	 *   stderr
	 *   "file:/path/to/file"
	 *   syslog:FACILITY  facility is any of "daemon", "local0"..."local7"
	 */
	// log = stderr;
	// log = "file:/path/to/file";
	// log = "syslog:local7";
	log = "file:$REDSOCKS_LOG";

	// detach from console
	// daemon = off;
	daemon = on;

	/* Change uid, gid and root directory, these options require root
	 * privilegies on startup.
	 * Note, your chroot may requre /etc/localtime if you write log to syslog.
	 * Log is opened before chroot & uid changing.
	 * Debian, Ubuntu and some other distributions use 'nogroup' instead of
	 * 'nobody', so change it according to your system if you want redsocks
	 * to drop root privileges.
	 */
	// user = nobody;
	// group = nobody;
	// chroot = "/var/chroot";

	/* possible 'redirector' values are:
	 *   iptables   - for Linux
	 *   ipf        - for FreeBSD
	 *   pf         - for OpenBSD
	 *   generic    - some generic redirector that MAY work
	 */
	redirector = iptables;

	/* Override per-socket values for TCP_KEEPIDLE, TCP_KEEPCNT,
	 * and TCP_KEEPINTVL. see man 7 tcp for details.
	 * 'redsocks' relies on SO_KEEPALIVE option heavily. */
	//tcp_keepalive_time = 0;
	//tcp_keepalive_probes = 0;
	//tcp_keepalive_intvl = 0;

	// Every 'redsocks' connection needs two file descriptors for sockets.
	// If 'splice' is enabled, it also needs four file descriptors for
	// pipes.  'redudp' is not accounted at the moment.  When max number of
	// connection is reached, redsocks tries to close idle connections. If
	// there are no idle connections, it stops accept()'ing new
	// connections, although kernel continues to fill listenq.

	// Set maximum number of open file descriptors (also known as 'ulimit -n').
	//  0 -- do not modify startup limit (default)
	// rlimit_nofile = 0;

	// Set maximum number of served connections. Default is to deduce safe
	// limit from 'splice' setting and RLIMIT_NOFILE.
	// redsocks_conn_max = 0;

	// Close connections idle for N seconds when/if connection count
	// limit is hit.
	//  0 -- do not close idle connections
	//  7440 -- 2 hours 4 minutes, see RFC 5382 (default)
	// connpres_idle_timeout = 7440;

	// 'max_accept_backoff' is a delay in milliseconds to retry 'accept()'
	// after failure (e.g. due to lack of file descriptors). It's just a
	// safety net for misconfigured 'redsocks_conn_max', you should tune
	// redsocks_conn_max if accept backoff happens.
	// max_accept_backoff = 60000;
	max_accept_backoff = 10;
}

redsocks {
	/* 'local_ip' defaults to 127.0.0.1 for security reasons,
	 * use 0.0.0.0 if you want to listen on every interface.
	 * 'local_*' are used as port to redirect to.
	 */
	local_ip = $REDSOCKS_IP;
	local_port = $REDSOCKS_PORT_TCP;

	// listen() queue length. Default value is SOMAXCONN and it should be
	// good enough for most of us.
	// listenq = 128; // SOMAXCONN equals 128 on my Linux box.

	// Enable or disable faster data pump based on splice(2) syscall.
	// Default value depends on your kernel version, true for 2.6.27.13+
	// splice = false;
	splice = true;

	// 'ip' and 'port' are IP and tcp-port of proxy-server
	// You can also use hostname instead of IP, only one (random)
	// address of multihomed host will be used.
	ip = $SOCKS_IP;
	port = $SOCKS_PORT;

	// known types: socks4, socks5, http-connect, http-relay
	type = socks5;

	// login = "foobar";
	// password = "baz";

	// known ways to disclose client IP to the proxy:
	//  false -- disclose nothing
	// http-connect supports:
	//  X-Forwarded-For  -- X-Forwarded-For: IP
	//  Forwarded_ip     -- Forwarded: for=IP # see RFC7239
	//  Forwarded_ipport -- Forwarded: for="IP:port" # see RFC7239
	// disclose_src = false;
	disclose_src = false;

	// various ways to handle proxy failure
	//  close -- just close connection (default)
	//  forward_http_err -- forward HTTP error page from proxy as-is
	// on_proxy_fail = close;
	on_proxy_fail = close;
}

redudp {
	// 'local_ip' should not be 0.0.0.0 as it's also used for outgoing
	// packets that are sent as replies - and it should be fixed
	// if we want NAT to work properly.
	local_ip = $REDSOCKS_IP;
	local_port = $REDSOCKS_PORT_UDP;

	// 'ip' and 'port' of socks5 proxy server.
	ip = $SOCKS_IP;
	port = $SOCKS_PORT;
	// login = username;
	// password = pazzw0rd;

	// redsocks knows about two options while redirecting UDP packets at
	// linux: TPROXY and REDIRECT.  TPROXY requires more complex routing
	// configuration and fresh kernel (>= 2.6.37 according to squid
	// developers[1]) but has hack-free way to get original destination
	// address, REDIRECT is easier to configure, but requires 'dest_ip' and
	// 'dest_port' to be set, limiting packet redirection to single
	// destination.
	// [1] http://wiki.squid-cache.org/Features/Tproxy4
	// dest_ip = 8.8.8.8;
	// dest_port = 53;

	// udp_timeout = 30;
	// udp_timeout_stream = 180;
	udp_timeout = 10;
	udp_timeout_stream = 10;
}

dnstc {
	// fake and really dumb DNS server that returns "truncated answer" to
	// every query via UDP, RFC-compliant resolver should repeat same query
	// via TCP in this case.
	// local_ip = 127.0.0.1;
	// local_port = 5300;
}

// you can add more 'redsocks' and 'redudp' sections if you need.

EOF

########################################################################
# start redsocks
########################################################################

if pgrep redsocks; then
    killall redsocks
    sleep 1
fi

redsocks -c $REDSOCKS_CONF &>/dev/null &

########################################################################
# start dns2socks
########################################################################

if pgrep DNS2SOCKS; then
    killall DNS2SOCKS
    sleep 1
fi

if [[ "$USE_DNS2SOCKS" == "True" ]]; then
	DNS2SOCKS $SOCKS_IP:$SOCKS_PORT $DNSServer 127.0.0.1:5300 /l:$DNS2SOCKS_LOG &>/dev/null &

	# iptables
	iptables -t nat -A OUTPUT -p tcp --dport 53 -j REDIRECT --to-port 5300
	iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-port 5300
fi

########################################################################
# iptables
########################################################################

#
sysctl -w net.ipv4.ip_forward=1
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A POSTROUTING -t nat -j MASQUERADE

##################### REDSOCKSTCP #####################
iptables -t nat -N REDSOCKSTCP

# please modify MyIP, MyPort, etc.
# ignore traffic sent to ss-server
iptables -t nat -A REDSOCKSTCP -p tcp -d $SOCKS_SERVER_IP --dport $SOCKS_SERVER_PORT -j RETURN

# ignore traffic sent to reserved addresses
iptables -t nat -A REDSOCKSTCP -p tcp -d 0.0.0.0/8          -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 10.0.0.0/8         -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 100.64.0.0/10      -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 127.0.0.0/8        -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 169.254.0.0/16     -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 172.16.0.0/12      -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 192.0.0.0/24       -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 192.0.2.0/24       -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 192.88.99.0/24     -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 192.168.0.0/16     -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 198.18.0.0/15      -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 198.51.100.0/24    -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 203.0.113.0/24     -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 224.0.0.0/4        -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 240.0.0.0/4        -j RETURN
iptables -t nat -A REDSOCKSTCP -p tcp -d 255.255.255.255/32 -j RETURN

#
iptables -t nat -A REDSOCKSTCP -p tcp -j REDIRECT --to-ports $REDSOCKS_PORT_TCP

#
iptables -t nat -A PREROUTING --in-interface $SUBNET_INTERFACE -p tcp -j REDSOCKSTCP

#
iptables -A INPUT -i $SUBNET_INTERFACE -p tcp --dport $REDSOCKS_PORT_TCP -j ACCEPT

#
iptables -t nat -nvL

##################### REDSOCKSUDP #####################
iptables -t mangle -N REDSOCKSUDP

# please modify MyIP, MyPort, etc.
# ignore traffic sent to ss-server
iptables -t mangle -A REDSOCKSUDP -p udp -d $SOCKS_SERVER_IP --dport $SOCKS_SERVER_PORT -j RETURN

# ignore traffic sent to reserved addresses
iptables -t mangle -A REDSOCKSUDP -p udp -d 0.0.0.0/8          -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 10.0.0.0/8         -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 100.64.0.0/10      -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 127.0.0.0/8        -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 169.254.0.0/16     -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 172.16.0.0/12      -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 192.0.0.0/24       -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 192.0.2.0/24       -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 192.88.99.0/24     -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 192.168.0.0/16     -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 198.18.0.0/15      -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 198.51.100.0/24    -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 203.0.113.0/24     -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 224.0.0.0/4        -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 240.0.0.0/4        -j RETURN
iptables -t mangle -A REDSOCKSUDP -p udp -d 255.255.255.255/32 -j RETURN

#
iptables -t mangle -A REDSOCKSUDP -p udp -j REDIRECT --to-ports $REDSOCKS_PORT_UDP

#
iptables -t mangle -A PREROUTING --in-interface $SUBNET_INTERFACE -p udp -j REDSOCKSUDP

#
iptables -A INPUT -i $SUBNET_INTERFACE -p udp --dport $REDSOCKS_PORT_UDP -j ACCEPT

#
iptables -t mangle -nvL

exit 0
