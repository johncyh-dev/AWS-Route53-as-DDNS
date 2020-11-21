#!bin/python3

import json
import urllib.request
import re
import sys
import subprocess
import time
from configparser import ConfigParser

def get_local_IP():
    currentIP = urllib.request.urlopen('https://api.ipify.org').read().decode('utf-8')
    if not re.match('^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', currentIP): 
        sys.exit('Invalid IP address: %s' % currentIP)
    return currentIP

def make_payload(name, resourceRecord):
    with open('route53-crud-sample.json') as sample,\
         open('route53-update.json', 'w') as output:
        data = json.load(sample) 
        change = data["Changes"][0]
        change["Action"] = "UPSERT"
        change["ResourceRecordSet"]["Name"] = name
        change["ResourceRecordSet"]["ResourceRecords"] = resourceRecord
        json.dump(data, output)

def put_record(hostedZoneID):
    updateRecordCmd = ['aws', 'route53', 'change-resource-record-sets', 
                       '--hosted-zone-id', hostedZoneID, 
                       '--change-batch', 'file://route53-update.json']
    updateRecordProcess = subprocess.Popen(updateRecordCmd,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, 
                                           universal_newlines=True)
    stdout, stderr = updateRecordProcess.communicate()
    print(stdout)
    print(stderr)
    response = json.loads(stdout)
    id = response['ChangeInfo']['Id']
    return id

def get_update_status(id):
    enquireStatusCmd = ['aws', 'route53', 'get-change', '--id', id]
    enquireStatusProcess = subprocess.Popen(enquireStatusCmd,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            universal_newlines=True)
    stdout, stderr = enquireStatusProcess.communicate()
    print(stdout)
    print(stderr)
    response = json.loads(stdout)
    status = response['ChangeInfo']['Status']
    return status

def main(timeoutInMin=10):
    config = ConfigParser()
    config.read('.env')
    _hostedZoneID = config['DEFAULT']['HostedZoneID']
    _domainName = config['DEFAULT']['DomainName']
    currentIP = get_local_IP()
    make_payload(_domainName, [{ "Value": currentIP}])
    print('Calling Route53 Change-resource-record-sets API...')
    id = put_record(_hostedZoneID)
   
    interval = 15
    time.sleep(interval)
    counter = 1
    maximum = timeoutInMin * 60 / interval
    while counter < maximum:
        print('%s Attempt to enquire the status...' % counter)        
        status = get_update_status(id)
        if status == 'INSYNC':
            print('Update completed')
            break
        counter += 1
        time.sleep(interval)
    else: 
        print('Update incomplete, timed out upon %s' % timeoutInMin)

if __name__ == '__main__':
    main()
