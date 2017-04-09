CLIENT_NET=10.0.0.0/24
TABLE_ID=100
MARK=1

echo "$TABLE_ID     mitmproxy" >> /etc/iproute2/rt_tables
iptables -t mangle -A PREROUTING -d $CLIENT_NET -j MARK --set-mark $MARK
iptables -t nat -A PREROUTING -p tcp -s $CLIENT_NET --match multiport --dports 80,443 -j REDIRECT --to-port 8080

ip rule add fwmark $MARK lookup $TABLE_ID
ip route add local $CLIENT_NET dev lo table $TABLE_ID
