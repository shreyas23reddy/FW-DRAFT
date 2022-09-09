import requests
import json
from itertools import zip_longest
import difflib
import yaml
import re
import time


from auth_header import Authentication as auth
from operations import Operation
from getAndParseDATA import getData
from getAndParseDATA import parseData
from getAndParseDATA import deleteData
from createAndActivate import createSiteList
from createAndActivate import createPolicy

if __name__=='__main__':

    while True:

        """ open the yaml file where the constant data is stored"""

        with open("vmanage_login1.yaml") as f:
            config = yaml.safe_load(f.read())


        """ extracting info from Yaml file"""

        vmanage_host = config['vmanage_host']
        vmanage_port = config['vmanage_port']
        username = config['vmanage_username']
        password = config['vmanage_password']
        SiteListSiteID = config['SiteListSiteID']
        newActivevSmartpolicyId = config['newActivevSmartpolicyId']
        oldActivevSmartpolicyId = config['oldActivevSmartpolicyId']


        """ GET the TOKEN from Authnetication call"""
        header= auth.get_header(vmanage_host, vmanage_port,username, password)

        print(f"Reverting to OLD Policy")

        revertPolicy = createPolicy.activateNewCentralizedPolicy(vmanage_host, vmanage_port, oldActivevSmartpolicyId ,header)

        print('policy was activated waiting for the push to be completed')
        time.sleep(10)

        #revert the policy changes
        #vSmartpolicyId  de19531f-0008-4de0-94aa-8cddb22dd331
        #revertPolicy = createPolicy.activateNewCentralizedPolicy(vmanage_host, vmanage_port, vSmartpolicyId ,header)

        vSmartPolicy = getData.getVsmartPolicy(vmanage_host,vmanage_port,header)
        for vSmartActivePolicy in vSmartPolicy:
            if vSmartActivePolicy["isPolicyActivated"] == True:
                break
        vSmartPolicyActineNow = vSmartActivePolicy['policyId']

        while  vSmartPolicyActineNow != oldActivevSmartpolicyId:
            time.sleep(10)
            vSmartPolicy = getData.getVsmartPolicy(vmanage_host,vmanage_port,header)
            for vSmartActivePolicy in vSmartPolicy:
                if vSmartActivePolicy["isPolicyActivated"] == True:
                    vSmartPolicyActineNow = vSmartActivePolicy['policyId']
                    break

        print(f"vSmart Policy Active Now {vSmartPolicyActineNow} {vSmartActivePolicy['policyName']}")

        res = deleteData.deletevSmartPolicy(vmanage_host,vmanage_port,header,newActivevSmartpolicyId)
        print(f" Deleted FireWall Redirection centralized policy {newActivevSmartpolicyId} ") if res.status_code == 200 else print("unable to delete")

        for SiteID in SiteListSiteID:
            res = deleteData.deleteSiteList(vmanage_host,vmanage_port,header,SiteID['listId'])
            print(f" Deleted Site List creted for FireWall Redirection {SiteID['listId']} ") if res.status_code == 200 else print("unable to delete")

        exit()
