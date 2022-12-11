import requests
import urllib3
from surething.sureThing_pb2 import *
import time

urllib3.disable_warnings(urllib3.exceptions.SecurityWarning)

url = "https://localhost:8443/api/v1/ledger"
headers_proto = {"content-type":"application/x-protobuf", "Accept": "application/x-protobuf", "charset": "utf-8"}
server_cert = './ledger.crt'
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def serialize(protoClass):
    return protoClass.SerializeToString()


def createLocationProof(id, geolocation, proverId, verifierId, ca, timestamp, evidence):
    lp = LocationProofProto()
    lp.id = id
    lp.geolocation = geolocation
    lp.proverId = proverId
    lp.verifierId = verifierId
    lp.ca = ca
    lp.timestamp = timestamp
    lp.evidence = evidence
    return lp


def post(proto, url):
    r = requests.post(url, data=serialize(proto), headers=headers_proto, verify=server_cert)
    return r

def postLocationProof():
    lp = createLocationProof(2, 'IST', 33, 44, 22, round(time.time() * 1000), 'evidenceM')
    return post(lp, url)

def initiate():
    postLocationProof()


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    r = requests.post('https://xkcd.com/1906/')
    print(r.status_code)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    response = postLocationProof()
    if(response.status_code == 200):
        print('The Location Proof was successfully submitted!')
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
