#!/usr/bin/env python

import re
import subprocess
import textwrap
from bottle import get, post, request, run, route, template, static_file

usb_count = 2
interfaces_file = '/etc/network/interfaces'
git_location = 'https://github.com/metanyx/metanyx.git'
allowed_subprocesses = ['service', 'ln', 'ifup', 'ifdown', 'iw', 'ifconfig']

def service(service, action):
    subprocess.call(['service', service, action])

def wlan_client_check(iface):
	try:
	    update = subprocess.check_output(["ifconfig", iface])
	    return 'wlan0'
	except subprocess.CalledProcessError as update_error:
	    return 'None'

def hostapd_config(iface, ssid, psk, card='edimax', hide_ssid=False):
    f = '/etc/hostapd/hostapd.conf'
    if card == 'edimax':
        driver = 'rtl871xdrv'
    else:
        driver = 'nl80211'
    config = textwrap.dedent("""\
    interface=%s
    ssid=%s
    wpa_passphrase=%s
    driver=%s
    hw_mode=g
    channel=6
    macaddr_acl=0
    auth_algs=1
    ignore_broadcast_ssid=0
    wpa=2
    wpa_key_mgmt=WPA-PSK
    wpa_pairwise=TKIP
    rsn_pairwise=CCMP
    """ % (iface, ssid, psk, driver))
    with open(f, "w") as conf:
        conf.write(config)

def dnsmasq_config(clients):
    config = '/etc/dnsmasq.conf'

    writing = True
    writing_conf = False
    with open(config, "r") as f:
        lines = f.readlines()
    with open(config, "w") as f:
        for line in lines:
            if writing:
                if "<IFACES>" in line:
                    writing_conf = True
                    f.write(line)
                    continue
                if writing_conf:
                    for c in clients: 
                        f.write('interface=%s\n' % c)
                    writing_conf = False
                    writing = False
                    continue
                f.write(line)
            if "</IFACES>" in line:
                writing = True
                f.write(line)

def iface_config(ssid, psk, eth_function, iface_eth='eth0', iface_client='wlan0', iface_ap='wlan1'):
    subprocess.call(["ifdown", iface_client])
    subprocess.call(["ifdown", iface_ap])
    if 'dhcp_client' in eth_function:
	    iface_conf = textwrap.dedent("""\
		# The loopback network interface
		auto lo
		iface lo inet loopback

		auto %s 
		allow-hotplug %s
		iface %s inet dhcp

		auto %s
		allow-hotplug %s
		iface %s inet dhcp
		    wpa-ssid %s
		    wpa-psk %s

		auto %s
		allow-hotplug %s
		iface %s inet static
		    address 192.168.5.1
		    netmask 255.255.255.0
	    """ % (iface_eth, iface_eth, iface_eth, iface_client, iface_client, 
		   iface_client, ssid, psk, iface_ap, iface_ap, iface_ap))
    else:
	    iface_conf = textwrap.dedent("""\
		# The loopback network interface
		auto lo
		iface lo inet loopback

		auto %s 
		allow-hotplug %s
		iface %s inet static
		    address 192.168.5.1
		    netmask 255.255.255.0
		    network 192.168.5.0

		auto %s
		allow-hotplug %s
		iface %s inet dhcp
		    wpa-ssid %s
		    wpa-psk %s

		auto %s
		allow-hotplug %s
		iface %s inet static
		    address 192.168.6.2
		    netmask 255.255.255.0
	    """ % (iface_eth, iface_eth, iface_eth, iface_client, iface_client, 
		   iface_client, ssid, psk, iface_ap, iface_ap, iface_ap))
    with open(interfaces_file, "w") as conf:
        conf.write(iface_conf)
    subprocess.call(["ifup", iface_client])
    subprocess.call(["ifup", iface_ap])

def tor_config(iface):
    f = '/etc/tor/torrc'
    return

def sys_symlink(src, dest):
    src = '/opt/metanyx/bin/hostapd_rtl8188'
    dest = '/usr/sbin/hostapd'
    subprocess.call(["ln", '-sf', src, dest])
    
def set_wifi_client(ssid, psk, iface='wlan0'):
    wpa_ssid = '    wpa-ssid ' + ssid
    wpa_psk = '    wpa-psk ' + psk
    subprocess.call(["ifdown", iface])
    with open(interfaces_file, "r") as interfaces:
        lines = interfaces.readlines()
    with open(interfaces_file, "w") as interfaces:
        for line in lines:
            interfaces.write(re.sub(r'^    wpa-ssid.*', wpa_ssid, line))
    with open(interfaces_file, "r") as interfaces:
        lines = interfaces.readlines()
    with open(interfaces_file, "w") as interfaces:
        for line in lines:
            interfaces.write(re.sub(r'^    wpa-psk.*', wpa_psk, line))
    subprocess.call(["ifup", iface])
    return True

@route('/')
@get('/setup') # or @route('/setup')
def setup():
    wlan_client = wlan_client_check('wlan0')
    return template('setup_template', usb_count=usb_count, wlan_client=wlan_client)

@route('/static/<filename>')
def server_static(filename):
        return static_file(filename, root='static')

@post('/setup')
def do_setup():

    enabled = request.forms.get('client_enable')

    client_enable = request.forms.get('client_enable')
    client_ssid = request.forms.get('client_ssid')
    client_psk = request.forms.get('client_psk')
    client_iface = request.forms.get('client_iface')

    ap_enable = request.forms.get('ap_enable')
    ap_ssid = request.forms.get('ap_ssid')
    ap_psk = request.forms.get('ap_psk')
    ap_iface = request.forms.get('ap_iface')

    eth_iface = 'eth0'
    eth_function = request.forms.get('eth_function')

    if not client_enable:
        client_ssid = "<SSID>"
        client_psk = "<PSK>"

    print 'Applying config changes. metanyx will reboot when complete'
    
    clients = []
    if ap_enable is '1':
        clients.append(ap_iface)
    else:
        subprocess.call(["systemctl", ",disable", "hostapd.service"])


    if 'dhcp_client' in eth_function:
        manage_iface = ap_iface
    else:
        manage_iface = eth_iface
        clients.append(eth_iface)

    hostapd_config(ap_iface, ap_ssid, ap_psk, 'edimax')
    dnsmasq_config(clients)
    subprocess.call(["/root/iptables.sh", eth_iface, client_iface, ap_iface, manage_iface ])
    iface_config(client_ssid, client_psk, eth_function, eth_iface, client_iface, ap_iface)
#    service('dnsmasq', 'restart')
    #if '1' in ap_enable:
    #    service('hostapd', 'restart')
    #else:
    #    service('hostapd', 'stop')
    #service('metanyx-manager', 'restart')
    subprocess.call(["/sbin/reboot"])
    #return '<p>Config complete. <a href="setup">Menu</a></p>'

@get('/status')
def status():
    tor_status = 'ControlPort <port>'
    batt_status = open('/sys/bus/i2c/devices/0-0034/axp20-supplyer.28/power_supply/battery/status').read()
    batt_capacity = open('/sys/bus/i2c/devices/0-0034/axp20-supplyer.28/power_supply/battery/capacity').read()

    return template ('status_template', {'batt_status':batt_status, 'batt_capacity':batt_capacity})

@get('/update')
def update():
        return template('<p>Sorry. Not yet working. <a href="setup">Menu</a></p><p></p>')
    #try:
    #    update = subprocess.check_output(["bash", "/opt/metanyx/src/ansible/run_update.sh"])
    #    return template('<p>Update complete. <a href="setup">Menu</a></p><p> {{ update }} </p>', update=update)
    #except subprocess.CalledProcessError as update_error:
    #    return template('<p>Update failure. <a href="setup">Menu</a></p><p>{{ error }}</p>', error=update_error)


@get('/shutdown')
def shutdown():
    subprocess.call(["shutdown", "now", "-h"])
    return "<p>Shuting down system now</p>"

@get('/reboot')
def reboot():
    subprocess.call(["reboot"])
    return "<p>Rebooting system now</p>"

@get('/service')
def servicer(service='tor', state='restart'):
    service('tor', 'restart')
    return "<p>%sing %s now</p>" % (state, service)

run(host='192.168.5.1', port=80, debug=True)
