#!/usr/bin/python

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import Node
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.util import pmonitor
from signal import SIGINT
from mininet.node import Controller
from time import time
import os
from os import environ

POXDIR = environ[ 'HOME' ] + '/pox'

class POX( Controller ):
    def __init__( self, name, cdir=POXDIR,
                  command='python pox.py',
                  cargs=( 'openflow.of_01 --port=%s '
                          'forwarding.l2_learning' ),
                  **kwargs ):
        Controller.__init__( self, name, cdir=cdir,
                             command=command,
                             cargs=cargs, **kwargs )

controllers={ 'pox': POX }
 
def routerNet():
    # Run Mininet
    net = Mininet( link=TCLink )
    value = 0
    
    # Add Router
    r1 = net.addHost('r1')
    r2 = net.addHost('r2')
    r3 = net.addHost('r3')
    r4 = net.addHost('r4')
    
    # Add Host
    ha = net.addHost('ha')
    hb = net.addHost('hb')
    
    # Bandwidth
    bw1={'bw':1}
    bw2={'bw':0.5}

    # Add Link
    net.addLink(r1, ha, max_queue_size = 100, use_htb = True, intfName1 = 'r1-eth0', intfName2 = 'ha-eth0', cls=TCLink, **bw1) 
    net.addLink(r2, ha, max_queue_size = 100, use_htb = True, intfName1 = 'r2-eth1', intfName2 = 'ha-eth1', cls=TCLink, **bw1) 
    net.addLink(r3, hb, max_queue_size = 100, use_htb = True, intfName1 = 'r3-eth0', intfName2 = 'hb-eth0', cls=TCLink, **bw1)
    net.addLink(r4, hb, max_queue_size = 100, use_htb = True, intfName1 = 'r4-eth1', intfName2 = 'hb-eth1', cls=TCLink, **bw1)
    net.addLink(r1, r3, max_queue_size = 100, use_htb = True, intfName1 = 'r1-eth1', intfName2 = 'r3-eth1', cls=TCLink, **bw2) 
    net.addLink(r1, r4, max_queue_size = 100, use_htb = True, intfName1 = 'r1-eth2', intfName2 = 'r4-eth2', cls=TCLink, **bw1) 
    net.addLink(r2, r4, max_queue_size = 100, use_htb = True, intfName1 = 'r2-eth0', intfName2 = 'r4-eth0', cls=TCLink, **bw2)
    net.addLink(r2, r3, max_queue_size = 100, use_htb = True, intfName1 = 'r2-eth2', intfName2 = 'r3-eth2', cls=TCLink, **bw1)
    net.build()

    #Host Configuration
    ha.cmd("ifconfig ha-eth0 0")
    ha.cmd("ifconfig ha-eth1 0")
    ha.cmd("ifconfig ha-eth0 192.168.50.1 netmask 255.255.255.0")
    ha.cmd("ifconfig ha-eth1 192.168.57.2 netmask 255.255.255.0")
    
    hb.cmd("ifconfig hb-eth0 0")
    hb.cmd("ifconfig hb-eth1 0")
    hb.cmd("ifconfig hb-eth0 192.168.53.2 netmask 255.255.255.0")
    hb.cmd("ifconfig hb-eth1 192.168.55.1 netmask 255.255.255.0")
	
    #Router Configuration
    r1.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
    r2.cmd("echo 2 > /proc/sys/net/ipv4/ip_forward")
    r3.cmd("echo 3 > /proc/sys/net/ipv4/ip_forward")
    r4.cmd("echo 4 > /proc/sys/net/ipv4/ip_forward")
    
    r1.cmd("ifconfig r1-eth0 0")
    r1.cmd("ifconfig r1-eth1 0")
    r1.cmd("ifconfig r1-eth2 0")
    r1.cmd("ifconfig r1-eth0 192.168.50.2 netmask 255.255.255.0")
    r1.cmd("ifconfig r1-eth1 192.168.51.1 netmask 255.255.255.0")
    r1.cmd("ifconfig r1-eth2 192.168.52.1 netmask 255.255.255.0")
    
    r2.cmd("ifconfig r2-eth0 0")
    r2.cmd("ifconfig r2-eth1 0")
    r2.cmd("ifconfig r2-eth2 0")
    r2.cmd("ifconfig r2-eth0 192.168.56.2 netmask 255.255.255.0")
    r2.cmd("ifconfig r2-eth1 192.168.57.1 netmask 255.255.255.0")
    r2.cmd("ifconfig r2-eth2 192.168.54.2 netmask 255.255.255.0")
    
    r3.cmd("ifconfig r3-eth0 0")
    r3.cmd("ifconfig r3-eth1 0")
    r3.cmd("ifconfig r3-eth2 0")
    r3.cmd("ifconfig r3-eth0 192.168.53.1 netmask 255.255.255.0")
    r3.cmd("ifconfig r3-eth1 192.168.51.2 netmask 255.255.255.0")
    r3.cmd("ifconfig r3-eth2 192.168.54.1 netmask 255.255.255.0")
    
    r4.cmd("ifconfig r4-eth0 0")
    r4.cmd("ifconfig r4-eth1 0")
    r4.cmd("ifconfig r4-eth2 0")
    r4.cmd("ifconfig r4-eth0 192.168.56.1 netmask 255.255.255.0")
    r4.cmd("ifconfig r4-eth1 192.168.55.2 netmask 255.255.255.0")
    r4.cmd("ifconfig r4-eth2 192.168.52.2 netmask 255.255.255.0")
    
    #Static Routing Host
    ha.cmd("ip rule add from 192.168.50.1 table 1")
    ha.cmd("ip rule add from 192.168.57.2 table 2")
    ha.cmd("ip rule add 192.168.50.0/24 dev ha-eth0 scope link table 1")
    ha.cmd("ip rule add default via 192.168.50.2 dev ha-eth0 table 1")
    ha.cmd("ip rule add 192.168.57.0/24 dev ha-eth1 scope link table 2")
    ha.cmd("ip rule add default via 192.168.57.1 dev ha-eth1 table 2")
    ha.cmd("ip rule add default scope global nexthop via 192.168.50.2 dev ha-eth0")
    ha.cmd("ip rule add default scope global nexthop via 192.168.57.1 dev ha-eth1")
    ha.cmd("route add default gw 192.168.50.2 dev ha-eth0")
    ha.cmd("route add default gw 192.168.57.1 dev ha-eth1")
    
    hb.cmd("ip rule add from 192.168.53.2 table 3")
    hb.cmd("ip rule add from 192.168.55.1 table 4")
    hb.cmd("ip rule add 192.168.53.0/24 dev hb-eth0 scope link table 1")
    hb.cmd("ip rule add default via 192.168.53.1 dev hb-eth0 table 1")
    hb.cmd("ip rule add 192.168.55.0/24 dev hb-eth1 scope link table 2")
    hb.cmd("ip rule add default via 192.168.55.2 dev hb-eth1 table 2")
    hb.cmd("ip rule add default scope global nexthop via 192.168.53.1 dev hb-eth0")
    hb.cmd("ip rule add default scope global nexthop via 192.168.55.2 dev hb-eth1")
    hb.cmd("route add default gw 192.168.53.1 dev hb-eth0")
    hb.cmd("route add default gw 192.168.55.2 dev hb-eth1")
    
    #Static Routing Router
    r1.cmd("route add -net 192.168.53.0/24 gw 192.168.51.2")
    r1.cmd("route add -net 192.168.54.0/24 gw 192.168.51.2")
    r1.cmd("route add -net 192.168.55.0/24 gw 192.168.52.2")
    r1.cmd("route add -net 192.168.56.0/24 gw 192.168.52.2")
    r1.cmd("route add -net 192.168.57.0/24 gw 192.168.51.2")
    
    r2.cmd("route add -net 192.168.50.0/24 gw 192.168.54.1")
    r2.cmd("route add -net 192.168.52.0/24 gw 192.168.56.1")
    r2.cmd("route add -net 192.168.55.0/24 gw 192.168.56.1")
    r2.cmd("route add -net 192.168.51.0/24 gw 192.168.54.1")
    r2.cmd("route add -net 192.168.53.0/24 gw 192.168.54.1")
    
    r3.cmd("route add -net 192.168.50.0/24 gw 192.168.51.1")
    r3.cmd("route add -net 192.168.55.0/24 gw 192.168.54.2")
    r3.cmd("route add -net 192.168.57.0/24 gw 192.168.54.2")
    r3.cmd("route add -net 192.168.52.0/24 gw 192.168.51.1")
    r3.cmd("route add -net 192.168.56.0/24 gw 192.168.54.2")
    
    r4.cmd("route add -net 192.168.57.0/24 gw 192.168.56.2")
    r4.cmd("route add -net 192.168.50.0/24 gw 192.168.52.1")
    r4.cmd("route add -net 192.168.54.0/24 gw 192.168.56.2")
    r4.cmd("route add -net 192.168.53.0/24 gw 192.168.52.1")
    r4.cmd("route add -net 192.168.51.0/24 gw 192.168.52.1")
    
    # Iperf
    hb.cmd('iperf -s &')
    ha.cmd('iperf -t 10 -B 192.168.50.1 -c 192.168.53.2 &')
    ha.cmd('iperf -t 10 -B 192.168.57.2 -c 192.168.53.2 &')
    
    # Start Network
    CLI(net)
    
    # Ping All Host
    info( '\n', net.ping() ,'\n' )

    # Stop Network
    net.stop()

if __name__ == '__main__':
    os.system('mn -c')
    os.system( 'clear' )
    setLogLevel( 'info' )
    routerNet()
