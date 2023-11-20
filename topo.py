from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.node import Controller


def colored_text(text, color_code):
    return f"{color_code}{text}\033[0m"

class MyTopo( Topo ):
    "Custom topology"

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        h1 = self.addHost( 'h1' )
        h2 = self.addHost( 'h2' )
        h3 = self.addHost( 'h3' )
        h4 = self.addHost( 'h4' )
        h5 = self.addHost( 'h5' )
        h6 = self.addHost( 'h6' )
        h7 = self.addHost( 'h7' )
        h8 = self.addHost( 'h8' )
        h9 = self.addHost( 'h9' )
        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )
        s3 = self.addSwitch( 's3' )
        s4 = self.addSwitch( 's4' )

        # Add links
        self.addLink( s1, h1 )
        self.addLink( s1, h2 )
        self.addLink( s1, s2 )
        
        self.addLink( s2, h3 )
        self.addLink( s2, h4 )
        self.addLink( s2, s3 )
        
        self.addLink( s3, h5 )
        self.addLink( s3, h6 )
        self.addLink( s3, s4 )
        
        self.addLink( s4, h7 )
        self.addLink( s4, h8 )
        self.addLink( s4, h9 )

net = Mininet(topo=MyTopo(), controller=None, autoSetMacs=True)
net.start()

cli = CLI(net, script='script.sh')

print(colored_text('Getting interfaces information', "\033[31m"))
cli.do_net(_line=None)

print(colored_text('Getting IP address for all hosts interfaces', "\033[31m"))
cli.do_dump(_line=None)


print(colored_text('Getting MAC Address for all hosts interfaces', "\033[31m"))
for host_index in range(len(net.hosts)):
    cli.do_py(f'h{host_index+1}.MAC()')

print(colored_text('Getting MAC Address for all switches interfaces', "\033[31m"))
for switch_index in range(len(net.switches)):
    cli.do_py(f's{switch_index+1}.MAC()')

print(colored_text('Configuring switches to work normally', "\033[31m"))
for switch_index in range(len(net.switches)):
    net[f's{switch_index+1}'].cmd(f'ovs-ofctl add-flow s{switch_index+1} action=normal')

cli.do_pingallfull(_line=None)

print(colored_text('Configuring ARP', "\033[31m"))
# Generating a flood for ARP operation
for switch_index in range(len(net.switches)):
    net[f's{switch_index+1}'].cmd(f'ovs-ofctl del-flows s{switch_index+1}')
    net[f's{switch_index+1}'].cmd(f'ovs-ofctl add-flow s{switch_index+1} dl_type=0x806,nw_proto=1,action=flood')

print(colored_text('Adding rules for flow control', "\033[31m"))
# Creating rules for each switch
net['s1'].cmd('ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:02,actions=output:2')
net['s1'].cmd('ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:01,actions=output:1')

net['s1'].cmd('ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:04,actions=output:3')
net['s1'].cmd('ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:01,actions=output:1')
net['s2'].cmd('ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:04,actions=output:3')
net['s2'].cmd('ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:01,actions=output:1')

net['s1'].cmd('ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:04,actions=output:3')
net['s1'].cmd('ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:02,actions=output:2')
net['s2'].cmd('ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:04,actions=output:3')
net['s2'].cmd('ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:02,actions=output:1')

net.ping([net.hosts[0], net.hosts[1], net.hosts[3]])

net.stop()
