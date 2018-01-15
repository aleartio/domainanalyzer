#!/usr/bin/env python
# coding=utf-8

import sys
import requests
import pythonwhois
import socket
import dns
from datetime import *
from dns import resolver , zone, query
import subprocess



# supress traceback information on errors
sys.tracebacklimit = 1

# TODO: Highlight important information
# TODO: This line is add from work to test conflict in git commits.

# get domain from input arguments
domain = sys.argv[1]

# strip extra domain information
if '//' in domain:
    domain = domain.split("//")[-1].split("/")[0]

# resolve against google server to get more accurate whois
res = resolver.Resolver()
resoving_nameserver = '8.8.8.8'
res.nameservers = [resoving_nameserver]


# init ip list for domain
ips = []

# if domain name is given
if len(sys.argv) > 1:

    # get whois
    whois = pythonwhois.get_whois(domain, True)

    # get php version
    r = requests.get('http://{}'.format(domain))
    try:
        php = r.headers['X-Powered-By']
    except:
        pass

    # calculate days left
    daysleft = (whois['expiration_date'][0].date() - datetime.now().date()).days
    exp = '' if daysleft > 66 else 'Exp ' + whois['expiration_date'][0].strftime("%Y-%m-%d") + ' (' + str(daysleft) + ' days left)'
# calculate hours ago
    try:
        hoursago = round((datetime.now().date() - whois['updated_date'][0].date()).total_seconds() / 3600)
        mod = '' if hoursago > 48 else 'Mod ' + whois['updated_date'][0].strftime("%Y-%m-%d") + " (%g hours ago)" % round(hoursago,0)
    except KeyError:
        mod = 'Mod: N/A'

    print('STATUS: {}'.format(' '.join(whois['status'])))
    if mod: print(mod)
    if exp: print(exp)
    print('REG: {}'.format(' '.join(whois['registrar'])))
    print('DNS: {}'.format(' '.join(whois['nameservers'])))
    print('PHP: {}'.format(php))

    # get ip from domain
    try:
        answers = res.query(domain)
        for rdata in answers:
            ips.append(rdata.address)
        print 'IP ' + ' / '.join(ips)

        # get host from ip
        try:
            host = socket.gethostbyaddr(ips[0])
            print 'HOST: ' + host[0]
        except socket.error:
            print 'HOST: N/A'
        pass

        # get name from ip
        print(ips[0])
        whois2 = pythonwhois.get_whois(ips[0], True) #nnetname??
        print('COMPANY: {}'.format(whois2['contacts']['registrant']['name']))
#       print(whois2)
#       if 'netname:' in str(whois2['raw']):
#           tail = str(whois2['raw']).split("netname:",1)
#           if tail:
#               tail = tail[1]
#               name=tail.split('\\')[0].strip()
#               print 'COMPANY: ' +name
#       else:
#           print 'COMPANY: N/A'
       

    except dns.resolver.NXDOMAIN:
        print 'No such domain resolving {} against {}'.format(domain,resoving_nameserver)
    except dns.resolver.Timeout:
        print 'Timed out while resolving {} against {}'.format(domain,resoving_nameserver)
    except dns.exception.DNSException:
        print 'Unhandled exception resolving {} against {}'.format(domain,resoving_nameserver)
        #https://stackoverflow.com/questions/9245067/is-it-reasonable-in-python-to-check-for-a-specific-type-of-exception-using-isins

    print('MX: {}'.format(subprocess.check_output(['dig','+noall', '+answer', 'MX', domain]).strip()))
    print('TXT: {}'.format(subprocess.check_output(['dig','+noall', '+answer', 'TXT', domain]).strip()))

    # open domain in browser
    #webbrowser.open('http://' + domain)
    #webbrowser.open('https://builtwith.com/' + domain)

# if you want to do anything cool with a keyword
if len(sys.argv) > 2:
   pass
