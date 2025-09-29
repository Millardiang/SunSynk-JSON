#!/usr/bin/env python3
#############################################
# sunsynk_get.py — merged gettoken + getapi #
#############################################

def gettoken():
    import time
    import base64
    import json
    import requests
    import logging
    from io import StringIO
    from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
    from cryptography.hazmat.primitives.serialization import load_pem_public_key

    BearerToken = ""

    class ConsoleColor:    
        OKBLUE = "\033[34m"
        OKCYAN = "\033[36m"
        OKGREEN = "\033[32m"        
        MAGENTA = "\033[35m"
        WARNING = "\033[33m"
        FAIL = "\033[31m"
        ENDC = "\033[0m"
        BOLD = "\033[1m" 

    with open('options.json') as options_file:
       json_settings = json.load(options_file)

    # Get key to encode token with
    response = requests.get(
        'https://api.sunsynk.net/anonymous/publicKey',
        params={
            'source': 'sunsynk',
            'nonce': int(time.time() * 1000)
        }
    )

    # Write public key file
    from io import StringIO
    public_key_file = StringIO()
    public_key_file.writelines(
        [
            '-----BEGIN PUBLIC KEY-----',
            response.json()['data'],
            '-----END PUBLIC KEY-----'
        ]
    )
    public_key_file.seek(0)

    # Load public key
    public_key = load_pem_public_key(
        bytes(public_key_file.read(), encoding='utf-8'),
    )

    encrypted_password = base64.b64encode(public_key.encrypt(
        json_settings['sunsynk_pass'].encode('utf-8'),
        PKCS1v15()
    )).decode('utf-8')

    # API URL
    url = f'https://{json_settings["API_Server"]}/oauth/token/new'
    # Prepare request payload
    payload = {
        "areaCode": "sunsynk",
        "client_id": "csp-web",
        "grant_type": "password",
        "password": encrypted_password,
        "source": "sunsynk",
        "username": json_settings['sunsynk_user']
    }
    # Headers
    headers = {"Content-Type": "application/json"}    
    try:
        # Send POST request with timeout (10s)
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        # Raise an exception for HTTP errors (4xx, 5xx)
        response.raise_for_status()

        # Parse response
        parsed_login_json = response.json()

        # Check login status
        if parsed_login_json.get('msg') == "Success":
            print("Sunsynk Login: " + ConsoleColor.OKGREEN + parsed_login_json['msg'] + ConsoleColor.ENDC)
            BearerToken = parsed_login_json['data']['access_token']
            return BearerToken
        else:
            print("Sunsynk Login: " + ConsoleColor.FAIL + parsed_login_json['msg'] + ConsoleColor.ENDC)
            return BearerToken

    except requests.exceptions.Timeout:
        print(ConsoleColor.FAIL + "Error: Request timed out while connecting to Sunsynk API." + ConsoleColor.ENDC)
        return BearerToken

    except requests.exceptions.RequestException as e:
        print(ConsoleColor.FAIL + f"Error: Failed to connect to Sunsynk API. {e}" + ConsoleColor.ENDC)
        return BearerToken

    except json.JSONDecodeError:
        print(ConsoleColor.FAIL + "Error: Failed to parse Sunsynk API response." + ConsoleColor.ENDC)
        return BearerToken



import json
import requests
from datetime import datetime

class ConsoleColor:    
    OKBLUE = "\033[34m"
    OKCYAN = "\033[36m"
    OKGREEN = "\033[32m"        
    MAGENTA = "\033[35m"
    WARNING = "\033[33m"
    FAIL = "\033[31m"
    ENDC = "\033[0m"
    BOLD = "\033[1m" 

# Load settings from JSON file
try:
    with open('options.json') as options_file:
        json_settings = json.load(options_file)
        api_server = json_settings['API_Server']
except Exception as e:
    logging.error(f"Failed to load settings: {e}")
    print(ConsoleColor.FAIL + "Error loading settings.json. Ensure the file exists and is valid JSON." + ConsoleColor.ENDC)
    exit()
    
def GetInverterInfo(Token,Serial):    
    global api_server         
    # Inverter URL
    inverter_url = f"https://{api_server}/api/v1/inverter/{Serial}"
    # Headers (Fixed Bearer token format)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Token}"
    }

    try:
        # Corrected to use GET request
        response = requests.get(inverter_url, headers=headers, timeout=10)
        response.raise_for_status()

        parsed_inverter_json = response.json()

        if parsed_inverter_json.get('msg') == "Success":
            print("Inverter fetch response: " + ConsoleColor.OKGREEN + parsed_inverter_json['msg'] + ConsoleColor.ENDC)
            #print(parsed_inverter_json);            
            print("Inverter Etotal: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['etotal']) + ConsoleColor.ENDC)
            print("Inverter Emonth: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['emonth']) + ConsoleColor.ENDC)
            print("Inverter Etoday: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['etoday']) + ConsoleColor.ENDC)
            print("Inverter Eyear: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['eyear']) + ConsoleColor.ENDC)
            print("Inverter Sn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sn']) + ConsoleColor.ENDC)
            print("Inverter Alias: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['alias']) + ConsoleColor.ENDC)
            print("Inverter Gsn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['gsn']) + ConsoleColor.ENDC)
            print("Inverter Status: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['status']) + ConsoleColor.ENDC)
            print("Inverter RunStatus: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['runStatus']) + ConsoleColor.ENDC)
            print("Inverter Type: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['type']) + ConsoleColor.ENDC)
            print("Inverter ThumbUrl: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['thumbUrl']) + ConsoleColor.ENDC)
            print("Inverter Opened: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['opened']) + ConsoleColor.ENDC)
            print("Inverter MasterVer: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['version']['masterVer']) + ConsoleColor.ENDC)
            print("Inverter SoftVer: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['version']['softVer']) + ConsoleColor.ENDC)
            print("Inverter HardVer: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['version']['hardVer']) + ConsoleColor.ENDC)
            print("Inverter HmiVer: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['version']['hmiVer']) + ConsoleColor.ENDC)
            print("Inverter BmsVer: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['version']['bmsVer']) + ConsoleColor.ENDC)
            print("Inverter CommVer: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['version']['commVer']) + ConsoleColor.ENDC)
            print("Inverter Id: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['plant']['id']) + ConsoleColor.ENDC)
            print("Inverter Name: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['plant']['name']) + ConsoleColor.ENDC)
            print("Inverter Type: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['plant']['type']) + ConsoleColor.ENDC)
            print("Inverter Master: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['plant']['master']) + ConsoleColor.ENDC)
            print("Inverter Installer: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['plant']['installer']) + ConsoleColor.ENDC)
            print("Inverter Email: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['plant']['email']) + ConsoleColor.ENDC)
            print("Inverter Phone: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['plant']['phone']) + ConsoleColor.ENDC)
            print("Inverter CustCode: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['custCode']) + ConsoleColor.ENDC)
            print("Inverter CommType: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['commType']) + ConsoleColor.ENDC)
            print("Inverter Pac: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['pac']) + ConsoleColor.ENDC)
            print("Inverter UpdateAt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['updateAt']) + ConsoleColor.ENDC)
            print("Inverter RatePower: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['ratePower']) + ConsoleColor.ENDC)
            print("Inverter Brand: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['brand']) + ConsoleColor.ENDC)
            print("Inverter Address: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['address']) + ConsoleColor.ENDC)
            print("Inverter Model: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['model']) + ConsoleColor.ENDC)
            print("Inverter ProtocolIdentifier: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['protocolIdentifier']) + ConsoleColor.ENDC)
            print("Inverter EquipType: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['equipType']) + ConsoleColor.ENDC)
            print("Inverter Id: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['user']['id']) + ConsoleColor.ENDC)
            print("Inverter Nickname: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['user']['nickname']) + ConsoleColor.ENDC)
            print("Inverter Mobile: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['user']['mobile']) + ConsoleColor.ENDC)
            print("Inverter Email: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['user']['email']) + ConsoleColor.ENDC)

        else:
            print("Inverter fetch response: " + ConsoleColor.FAIL + parsed_inverter_json['msg'] + ConsoleColor.ENDC)

    except requests.exceptions.Timeout:
        print(ConsoleColor.FAIL + "Error: Request timed out while connecting to Service Provider API." + ConsoleColor.ENDC)

    except requests.exceptions.RequestException as e:
        print(ConsoleColor.FAIL + f"Error: Failed to connect to Service Provider API. {e}" + ConsoleColor.ENDC)
        return parsed_inverter_json
    except json.JSONDecodeError:
        print(ConsoleColor.FAIL + "Error: Failed to parse Service Provider API response." + ConsoleColor.ENDC)
        return {}

def GetInverterSettingsData(Token,Serial):    
    global api_server    
    # Inverter URL
    #curl -s -k -X GET -H "Content-Type: application/json" -H "authorization: Bearer $ServerAPIBearerToken" https://{api_server}/api/v1/inverter/$inverter_serial/realtime/input
    #inverter_url = f"https://{api_server}/api/v1/inverter/{Serial}/realtime/input"
    inverter_url = f"https://{api_server}/api/v1/common/setting/{Serial}/read"
    
    # Headers (Fixed Bearer token format)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Token}"
    }

    try:
        # Corrected to use GET request
        response = requests.get(inverter_url, headers=headers, timeout=10)
        response.raise_for_status()

        parsed_inverter_json = response.json()

        if parsed_inverter_json.get('msg') == "Success":           
            print(ConsoleColor.BOLD + "PV data fetch response: " + ConsoleColor.OKGREEN + parsed_inverter_json['msg'] + ConsoleColor.ENDC)
            #print(parsed_inverter_json);
            #print("PV Pac: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['pac']) + ConsoleColor.ENDC)
            print("Inverter Setting sellTime1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime1']))
            print("Inverter Setting genTime2on: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genTime2on']))
            print("Inverter Setting beep: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['beep']))
            print("Inverter Setting sellTime2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime2']))
            print("Inverter Setting wattOverExitFreqStopDelay: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattOverExitFreqStopDelay']))
            print("Inverter Setting sellTime5: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime5']))
            print("Inverter Setting sellTime6: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime6']))
            print("Inverter Setting sellTime3: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime3']))
            print("Inverter Setting sellTime4: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime4']))
            print("Inverter Setting exMeterCtSwitch: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['exMeterCtSwitch']))
            print("Inverter Setting sdChargeOn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sdChargeOn']))
            print("Inverter Setting lockInVoltVar: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['lockInVoltVar']))
            print("Inverter Setting time2on: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['time2on']))
            print("Inverter Setting batWarn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batWarn']))
            print("Inverter Setting wattVarEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattVarEnable']))
            print("Inverter Setting reconnMinVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['reconnMinVolt']))
            print("Inverter Setting caFStart: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['caFStart']))
            print("Inverter Setting pvMaxLimit: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['pvMaxLimit']))
            print("Inverter Setting sensorsCheck: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sensorsCheck']))
            print("Inverter Setting underFreq2Delay: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['underFreq2Delay']))
            print("Inverter Setting varQac2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['varQac2']))
            print("Inverter Setting varQac3: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['varQac3']))
            print("Inverter Setting varQac1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['varQac1']))
            print("Inverter Setting wattUnderExitFreq: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattUnderExitFreq']))
            print("Inverter Setting overVolt1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['overVolt1']))
            print("Inverter Setting overVolt2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['overVolt2']))
            print("Inverter Setting varQac4: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['varQac4']))
            print("Inverter Setting genPeakPower: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genPeakPower']))
            print("Inverter Setting meterB: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['meterB']))
            print("Inverter Setting eeprom: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['eeprom']))
            print("Inverter Setting meterA: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['meterA']))
            print("Inverter Setting comSet: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['comSet']))
            print("Inverter Setting caVoltPressureEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['caVoltPressureEnable']))
            print("Inverter Setting meterC: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['meterC']))
            print("Inverter Setting wattUnderFreq1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattUnderFreq1']))
            print("Inverter Setting solarMaxSellPower: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['solarMaxSellPower']))
            print("Inverter Setting acCoupleOnGridSideEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['acCoupleOnGridSideEnable']))
            print("Inverter Setting thursdayOn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['thursdayOn']))
            print("Inverter Setting time3On: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['time3On']))
            print("Inverter Setting batteryRestartCap: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryRestartCap']))
            print("Inverter Setting overFreq1Delay: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['overFreq1Delay']))
            print("Inverter Setting bmsErrStop: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['bmsErrStop']))
            print("Inverter Setting checkTime: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['checkTime']))
            print("Inverter Setting acOutputPowerLimit: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['acOutputPowerLimit']))
            print("Inverter Setting atsSwitch: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['atsSwitch']))
            print("Inverter Setting pv1SelfCheck: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['pv1SelfCheck']))
            print("Inverter Setting acCurrentUp: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['acCurrentUp']))
            print("Inverter Setting rsd: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['rsd']))
            print("Inverter Setting batteryOn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryOn']))
            print("Inverter Setting genTime1on: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genTime1on']))
            print("Inverter Setting volt12: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['volt12']))
            print("Inverter Setting volt10: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['volt10']))
            print("Inverter Setting volt11: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['volt11']))
            print("Inverter Setting time1on: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['time1on']))
            print("Inverter Setting wattUnderFreq1StartDelay: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattUnderFreq1StartDelay']))
            print("Inverter Setting rcd: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['rcd']))
            print("Inverter Setting chargeVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['chargeVolt']))
            print("Inverter Setting wednesdayOn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wednesdayOn']))
            print("Inverter Setting mpptMulti: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['mpptMulti']))
            print("Inverter Setting floatVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['floatVolt']))
            print("Inverter Setting workState: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['workState']))
            print("Inverter Setting loadMode: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['loadMode']))
            print("Inverter Setting sysWorkMode: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sysWorkMode']))
            print("Inverter Setting sn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sn']))
            print("Inverter Setting genCoolingTime: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genCoolingTime']))
            print("Inverter Setting genPeakShaving: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genPeakShaving']))
            print("Inverter Setting offGridImmediatelyOff: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['offGridImmediatelyOff']))
            print("Inverter Setting sellTime3Volt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime3Volt']))
            print("Inverter Setting sellTime2Pac: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime2Pac']))
            print("Inverter Setting current12: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['current12']))
            print("Inverter Setting time2On: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['time2On']))
            print("Inverter Setting current10: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['current10']))
            print("Inverter Setting current11: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['current11']))
            print("Inverter Setting batteryEfficiency: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryEfficiency']))
            print("Inverter Setting genAndGridSignal: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genAndGridSignal']))
            print("Inverter Setting pv3SelfCheck: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['pv3SelfCheck']))
            print("Inverter Setting wattV4: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattV4']))
            print("Inverter Setting acFreqLow: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['acFreqLow']))
            print("Inverter Setting wattV2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattV2']))
            print("Inverter Setting wattV3: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattV3']))
            print("Inverter Setting wattV1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattV1']))
            print("Inverter Setting batteryEmptyV: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryEmptyV']))
            print("Inverter Setting open: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['open']))
            print("Inverter Setting reconnMaxFreq: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['reconnMaxFreq']))
            print("Inverter Setting standard: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['standard']))
            print("Inverter Setting wattVarReactive2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattVarReactive2']))
            print("Inverter Setting disableFloatCharge: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['disableFloatCharge']))
            print("Inverter Setting inverterType: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['inverterType']))
            print("Inverter Setting wattVarReactive3: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattVarReactive3']))
            print("Inverter Setting wattVarReactive4: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattVarReactive4']))
            print("Inverter Setting solarPSU: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['solarPSU']))
            print("Inverter Setting fridayOn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['fridayOn']))
            print("Inverter Setting wattVarReactive1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattVarReactive1']))
            print("Inverter Setting time4on: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['time4on']))
            print("Inverter Setting cap6: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['cap6']))
            print("Inverter Setting generatorForcedStart: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['generatorForcedStart']))
            print("Inverter Setting overLongVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['overLongVolt']))
            print("Inverter Setting cap4: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['cap4']))
            print("Inverter Setting cap5: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['cap5']))
            print("Inverter Setting batteryChargeType: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryChargeType']))
            print("Inverter Setting genOffVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genOffVolt']))
            print("Inverter Setting cap2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['cap2']))
            print("Inverter Setting cap3: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['cap3']))
            print("Inverter Setting absorptionVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['absorptionVolt']))
            print("Inverter Setting genToLoad: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genToLoad']))
            print("Inverter Setting mpptNum: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['mpptNum']))
            print("Inverter Setting underFreq2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['underFreq2']))
            print("Inverter Setting underFreq1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['underFreq1']))
            print("Inverter Setting wattPfEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattPfEnable']))
            print("Inverter Setting remoteLock: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['remoteLock']))
            print("Inverter Setting generatorStartCap: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['generatorStartCap']))
            print("Inverter Setting batteryMaxCurrentCharge: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryMaxCurrentCharge']))
            print("Inverter Setting overFreq1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['overFreq1']))
            print("Inverter Setting tuesdayOn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['tuesdayOn']))
            print("Inverter Setting genOnVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genOnVolt']))
            print("Inverter Setting overFreq2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['overFreq2']))
            print("Inverter Setting solar2WindInputEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['solar2WindInputEnable']))
            print("Inverter Setting caVStop: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['caVStop']))
            print("Inverter Setting time5On: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['time5On']))
            print("Inverter Setting battMode: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['battMode']))
            print("Inverter Setting allowRemoteControl: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['allowRemoteControl']))
            print("Inverter Setting genOnCap: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genOnCap']))
            print("Inverter Setting gridAlwaysOn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['gridAlwaysOn']))
            print("Inverter Setting batteryLowVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryLowVolt']))
            print("Inverter Setting acFreqUp: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['acFreqUp']))
            print("Inverter Setting cap1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['cap1']))
            print("Inverter Setting chargeLimit: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['chargeLimit']))
            print("Inverter Setting generatorStartVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['generatorStartVolt']))
            print("Inverter Setting overVolt1Delay: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['overVolt1Delay']))
            print("Inverter Setting sellTime1Pac: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime1Pac']))
            print("Inverter Setting californiaFreqPressureEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['californiaFreqPressureEnable']))
            print("Inverter Setting activePowerControl: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['activePowerControl']))
            print("Inverter Setting batteryRestartVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryRestartVolt']))
            print("Inverter Setting zeroExportPower: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['zeroExportPower']))
            print("Inverter Setting overVolt2Delay: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['overVolt2Delay']))
            print("Inverter Setting equChargeCycle: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['equChargeCycle']))
            print("Inverter Setting dischargeCurrent: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['dischargeCurrent']))
            print("Inverter Setting solarSell: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['solarSell']))
            print("Inverter Setting mpptVoltLow: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['mpptVoltLow']))
            print("Inverter Setting time3on: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['time3on']))
            print("Inverter Setting wattVoltEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattVoltEnable']))
            print("Inverter Setting caFwEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['caFwEnable']))
            print("Inverter Setting maxOperatingTimeOfGen: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['maxOperatingTimeOfGen']))
            print("Inverter Setting micExportGridOff: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['micExportGridOff']))
            print("Inverter Setting importPower: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['importPower']))
            print("Inverter Setting pvLine: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['pvLine']))
            print("Inverter Setting three41: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['three41']))
            print("Inverter Setting caVwEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['caVwEnable']))
            print("Inverter Setting batteryShutdownVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryShutdownVolt']))
            print("Inverter Setting volt3: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['volt3']))
            print("Inverter Setting volt4: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['volt4']))
            print("Inverter Setting volt1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['volt1']))
            print("Inverter Setting volt2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['volt2']))
            print("Inverter Setting startVoltUp: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['startVoltUp']))
            print("Inverter Setting volt7: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['volt7']))
            print("Inverter Setting volt8: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['volt8']))
            print("Inverter Setting volt5: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['volt5']))
            print("Inverter Setting sellTime6Pac: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime6Pac']))
            print("Inverter Setting volt6: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['volt6']))
            print("Inverter Setting time4On: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['time4On']))
            print("Inverter Setting sellTime4Volt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime4Volt']))
            print("Inverter Setting volt9: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['volt9']))
            print("Inverter Setting facLowProtect: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['facLowProtect']))
            print("Inverter Setting wattOverFreq1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattOverFreq1']))
            print("Inverter Setting wattPf4: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattPf4']))
            print("Inverter Setting lowNoiseMode: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['lowNoiseMode']))
            print("Inverter Setting tempco: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['tempco']))
            print("Inverter Setting arcFactFrz: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['arcFactFrz']))
            print("Inverter Setting wattPf1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattPf1']))
            print("Inverter Setting wattPf2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattPf2']))
            print("Inverter Setting wattPf3: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattPf3']))
            print("Inverter Setting meterSelect: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['meterSelect']))
            print("Inverter Setting genChargeOn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genChargeOn']))
            print("Inverter Setting externalCtRatio: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['externalCtRatio']))
            print("Inverter Setting gridMode: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['gridMode']))
            print("Inverter Setting sellTime5Pac: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime5Pac']))
            print("Inverter Setting lowThrough: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['lowThrough']))
            print("Inverter Setting drmEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['drmEnable']))
            print("Inverter Setting pv2SelfCheck: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['pv2SelfCheck']))
            print("Inverter Setting underFreq1Delay: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['underFreq1Delay']))
            print("Inverter Setting energyMode: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['energyMode']))
            print("Inverter Setting ampm: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['ampm']))
            print("Inverter Setting gridPeakShaving: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['gridPeakShaving']))
            print("Inverter Setting time6on: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['time6on']))
            print("Inverter Setting fac: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['fac']))
            print("Inverter Setting vacLowProtect: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['vacLowProtect']))
            print("Inverter Setting chargeCurrentLimit: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['chargeCurrentLimit']))
            print("Inverter Setting caLv3: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['caLv3']))
            print("Inverter Setting sundayOn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sundayOn']))
            print("Inverter Setting genTime6on: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genTime6on']))
            print("Inverter Setting batteryImpedance: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryImpedance']))
            print("Inverter Setting safetyType: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['safetyType']))
            print("Inverter Setting varVolt4: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['varVolt4']))
            print("Inverter Setting varVolt3: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['varVolt3']))
            print("Inverter Setting varVolt2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['varVolt2']))
            print("Inverter Setting specialFunction: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['specialFunction']))
            print("Inverter Setting varVolt1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['varVolt1']))
            print("Inverter Setting mondayOn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['mondayOn']))
            print("Inverter Setting commAddr: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['commAddr']))
            print("Inverter Setting saturdayOn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['saturdayOn']))
            print("Inverter Setting dischargeLimit: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['dischargeLimit']))
            print("Inverter Setting atsEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['atsEnable']))
            print("Inverter Setting exMeterCt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['exMeterCt']))
            print("Inverter Setting overFreq2Delay: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['overFreq2Delay']))
            print("Inverter Setting phase: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['phase']))
            print("Inverter Setting autoDim: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['autoDim']))
            print("Inverter Setting batteryWorkStatus: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryWorkStatus']))
            print("Inverter Setting genToLoadOn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genToLoadOn']))
            print("Inverter Setting timeSync: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['timeSync']))
            print("Inverter Setting wattOverWgralFreq: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattOverWgralFreq']))
            print("Inverter Setting sdBatteryCurrent: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sdBatteryCurrent']))
            print("Inverter Setting peakAndVallery: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['peakAndVallery']))
            print("Inverter Setting batteryEmptyVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryEmptyVolt']))
            print("Inverter Setting batteryLowCap: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryLowCap']))
            print("Inverter Setting underVolt2Delay: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['underVolt2Delay']))
            print("Inverter Setting equChargeTime: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['equChargeTime']))
            print("Inverter Setting battType: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['battType']))
            print("Inverter Setting gridPeakPower: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['gridPeakPower']))
            print("Inverter Setting reset: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['reset']))
            print("Inverter Setting vacHighProtect: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['vacHighProtect']))
            print("Inverter Setting genTime5on: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genTime5on']))
            print("Inverter Setting deyeGenPowerDoubleFlag: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['deyeGenPowerDoubleFlag']))
            print("Inverter Setting pwm: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['pwm']))
            print("Inverter Setting time5on: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['time5on']))
            print("Inverter Setting highThrough: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['highThrough']))
            print("Inverter Setting lockOutVoltVar: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['lockOutVoltVar']))
            print("Inverter Setting lockInWattPF: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['lockInWattPF']))
            print("Inverter Setting caVStart: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['caVStart']))
            print("Inverter Setting acVoltUp: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['acVoltUp']))
            print("Inverter Setting wattFreqEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattFreqEnable']))
            print("Inverter Setting wattOverExitFreq: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattOverExitFreq']))
            print("Inverter Setting sellTime5Volt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime5Volt']))
            print("Inverter Setting caFStop: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['caFStop']))
            print("Inverter Setting lowPowerMode: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['lowPowerMode']))
            print("Inverter Setting varVoltEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['varVoltEnable']))
            print("Inverter Setting acCoupleFreqUpper: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['acCoupleFreqUpper']))
            print("Inverter Setting impedanceLow: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['impedanceLow']))
            print("Inverter Setting acType: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['acType']))
            print("Inverter Setting facHighProtect: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['facHighProtect']))
            print("Inverter Setting recoveryTime: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['recoveryTime']))
            print("Inverter Setting underVolt2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['underVolt2']))
            print("Inverter Setting lithiumMode: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['lithiumMode']))
            print("Inverter Setting underVolt1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['underVolt1']))
            print("Inverter Setting gridSignal: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['gridSignal']))
            print("Inverter Setting wattOverFreq1StartDelay: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattOverFreq1StartDelay']))
            print("Inverter Setting testCommand: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['testCommand']))
            print("Inverter Setting time6On: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['time6On']))
            print("Inverter Setting signalIslandModeEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['signalIslandModeEnable']))
            print("Inverter Setting upsStandard: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['upsStandard']))
            print("Inverter Setting reconnMinFreq: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['reconnMinFreq']))
            print("Inverter Setting parallelRegister2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['parallelRegister2']))
            print("Inverter Setting parallelRegister1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['parallelRegister1']))
            print("Inverter Setting startVoltLow: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['startVoltLow']))
            print("Inverter Setting smartLoadOpenDelay: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['smartLoadOpenDelay']))
            print("Inverter Setting genTime4on: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genTime4on']))
            print("Inverter Setting sellTime1Volt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime1Volt']))
            print("Inverter Setting wattVarActive4: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattVarActive4']))
            print("Inverter Setting wattVarActive3: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattVarActive3']))
            print("Inverter Setting genConnectGrid: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genConnectGrid']))
            print("Inverter Setting flag2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['flag2']))
            print("Inverter Setting softStart: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['softStart']))
            print("Inverter Setting lockOutWattPF: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['lockOutWattPF']))
            print("Inverter Setting sdStartCap: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sdStartCap']))
            print("Inverter Setting current4: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['current4']))
            print("Inverter Setting current3: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['current3']))
            print("Inverter Setting current2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['current2']))
            print("Inverter Setting current1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['current1']))
            print("Inverter Setting gfdi: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['gfdi']))
            print("Inverter Setting current8: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['current8']))
            print("Inverter Setting current7: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['current7']))
            print("Inverter Setting current6: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['current6']))
            print("Inverter Setting current5: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['current5']))
            print("Inverter Setting checkSelfTime: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['checkSelfTime']))
            print("Inverter Setting limit: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['limit']))
            print("Inverter Setting wattW3: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattW3']))
            print("Inverter Setting wattVarActive2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattVarActive2']))
            print("Inverter Setting wattW4: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattW4']))
            print("Inverter Setting wattVarActive1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattVarActive1']))
            print("Inverter Setting externalCurrent: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['externalCurrent']))
            print("Inverter Setting wattW1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattW1']))
            print("Inverter Setting wattW2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattW2']))
            print("Inverter Setting vnResponseTime: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['vnResponseTime']))
            print("Inverter Setting batteryShutdownCap: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryShutdownCap']))
            print("Inverter Setting wattUnderExitFreqStopDelay: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattUnderExitFreqStopDelay']))
            print("Inverter Setting offset: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['offset']))
            print("Inverter Setting sellTime4Pac: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime4Pac']))
            print("Inverter Setting wattActivePf1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattActivePf1']))
            print("Inverter Setting current9: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['current9']))
            print("Inverter Setting dischargeVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['dischargeVolt']))
            print("Inverter Setting qvResponseTime: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['qvResponseTime']))
            print("Inverter Setting wattActivePf4: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattActivePf4']))
            print("Inverter Setting time1On: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['time1On']))
            print("Inverter Setting wattActivePf2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattActivePf2']))
            print("Inverter Setting four19: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['four19']))
            print("Inverter Setting wattActivePf3: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattActivePf3']))
            print("Inverter Setting micExportAll: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['micExportAll']))
            print("Inverter Setting batteryMaxCurrentDischarge: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryMaxCurrentDischarge']))
            print("Inverter Setting isletProtect: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['isletProtect']))
            print("Inverter Setting lockOutChange: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['lockOutChange']))
            print("Inverter Setting californiaVoltPressureEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['californiaVoltPressureEnable']))
            print("Inverter Setting equVoltCharge: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['equVoltCharge']))
            print("Inverter Setting batteryCap: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryCap']))
            print("Inverter Setting genOffCap: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genOffCap']))
            print("Inverter Setting genTime3on: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genTime3on']))
            print("Inverter Setting sellTime6Volt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime6Volt']))
            print("Inverter Setting sellTime3Pac: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime3Pac']))
            print("Inverter Setting acCoupleOnLoadSideEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['acCoupleOnLoadSideEnable']))
            print("Inverter Setting sdStartVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sdStartVolt']))
            print("Inverter Setting generatorBatteryCurrent: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['generatorBatteryCurrent']))
            print("Inverter Setting reconnMaxVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['reconnMaxVolt']))
            print("Inverter Setting modbusSn: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['modbusSn']))
            print("Inverter Setting inverterOutputVoltage: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['inverterOutputVoltage']))
            print("Inverter Setting chargeCurrent: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['chargeCurrent']))
            print("Inverter Setting solar1WindInputEnable: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['solar1WindInputEnable']))
            print("Inverter Setting dcVoltUp: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['dcVoltUp']))
            print("Inverter Setting parallel: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['parallel']))
            print("Inverter Setting limter: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['limter']))
            print("Inverter Setting batErr: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batErr']))
            print("Inverter Setting backupDelay: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['backupDelay']))
            print("Inverter Setting dischargeCurrentLimit: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['dischargeCurrentLimit']))
            print("Inverter Setting arcFactT: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['arcFactT']))
            print("Inverter Setting wattUnderWgalFreq: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['wattUnderWgalFreq']))
            print("Inverter Setting commBaudRate: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['commBaudRate']))
            print("Inverter Setting equipMode: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['equipMode']))
            print("Inverter Setting gridSideINVMeter2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['gridSideINVMeter2']))
            print("Inverter Setting underVolt1Delay: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['underVolt1Delay']))
            print("Inverter Setting arcFaultType: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['arcFaultType']))
            print("Inverter Setting arcFactB: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['arcFactB']))
            print("Inverter Setting normalUpwardSlope: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['normalUpwardSlope']))
            print("Inverter Setting arcFactC: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['arcFactC']))
            print("Inverter Setting pf: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['pf']))
            print("Inverter Setting arcFactD: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['arcFactD']))
            print("Inverter Setting genMinSolar: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genMinSolar']))
            print("Inverter Setting sellTime2Volt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['sellTime2Volt']))
            print("Inverter Setting arcFactF: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['arcFactF']))
            print("Inverter Setting arcFactI: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['arcFactI']))
            print("Inverter Setting acVoltLow: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['acVoltLow']))
            print("Inverter Setting genSignal: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['genSignal']))
             
            print(ConsoleColor.OKGREEN + "Inverter Settings fetch complete" + ConsoleColor.ENDC)
       
            

        else:
            print("PV data fetch response: " + ConsoleColor.FAIL + parsed_inverter_json['msg'] + ConsoleColor.ENDC)

    except requests.exceptions.Timeout:
        print(ConsoleColor.FAIL + "Error: Request timed out while connecting to Service Provider API." + ConsoleColor.ENDC)

    except requests.exceptions.RequestException as e:
        print(ConsoleColor.FAIL + f"Error: Failed to connect to Service Provider API. {e}" + ConsoleColor.ENDC)
        return parsed_inverter_json
    except json.JSONDecodeError:
        print(ConsoleColor.FAIL + "Error: Failed to parse Service Provider API response." + ConsoleColor.ENDC)  
        return {}

def GetPvData(Token,Serial):    
    global api_server    
    # Inverter URL
    #curl -s -k -X GET -H "Content-Type: application/json" -H "authorization: Bearer $ServerAPIBearerToken" https://{api_server}/api/v1/inverter/$inverter_serial/realtime/input
    inverter_url = f"https://{api_server}/api/v1/inverter/{Serial}/realtime/input"
    # Headers (Fixed Bearer token format)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Token}"
    }

    try:
        # Corrected to use GET request
        response = requests.get(inverter_url, headers=headers, timeout=10)
        response.raise_for_status()

        parsed_inverter_json = response.json()

        if parsed_inverter_json.get('msg') == "Success":           
            print(ConsoleColor.BOLD + "PV data fetch response: " + ConsoleColor.OKGREEN + parsed_inverter_json['msg'] + ConsoleColor.ENDC)
            #print(parsed_inverter_json);
            print("PV Pac: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['pac']) + ConsoleColor.ENDC)
            print("PV Grid_tip_power: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['grid_tip_power']) + ConsoleColor.ENDC)
            print("PV Etoday: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['etoday']) + ConsoleColor.ENDC)
            print("PV Etotal: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['etotal']) + ConsoleColor.ENDC)
            
            print(ConsoleColor.WARNING + str(len(parsed_inverter_json['data']['pvIV'])) + ConsoleColor.ENDC +  " MPPTs detected.")
            #Loop through MPPTS
            for x in range(len(parsed_inverter_json['data']['pvIV'])): 
                currentmppt = str(x)
                print(f"PV MPPT {currentmppt} Power: " + ConsoleColor.OKCYAN + parsed_inverter_json['data']['pvIV'][x]['ppv'] + ConsoleColor.ENDC)
                print(f"PV MPPT {currentmppt} Voltage: " + ConsoleColor.OKCYAN + parsed_inverter_json['data']['pvIV'][x]['vpv'] + ConsoleColor.ENDC)
                print(f"PV MPPT {currentmppt} Current: " + ConsoleColor.OKCYAN + parsed_inverter_json['data']['pvIV'][x]['ipv'] + ConsoleColor.ENDC)
            
            print(ConsoleColor.OKGREEN + "PV fetch complete" + ConsoleColor.ENDC)
       
            

        else:
            print("PV data fetch response: " + ConsoleColor.FAIL + parsed_inverter_json['msg'] + ConsoleColor.ENDC)

    except requests.exceptions.Timeout:
        print(ConsoleColor.FAIL + "Error: Request timed out while connecting to Service Provider API." + ConsoleColor.ENDC)

    except requests.exceptions.RequestException as e:
        print(ConsoleColor.FAIL + f"Error: Failed to connect to Service Provider API. {e}" + ConsoleColor.ENDC)
        return parsed_inverter_json
    except json.JSONDecodeError:
        print(ConsoleColor.FAIL + "Error: Failed to parse Service Provider API response." + ConsoleColor.ENDC)        
        return {}

def GetGridData(Token,Serial):    
    global api_server   
    inverter_url = f"https://{api_server}/api/v1/inverter/grid/{Serial}/realtime?sn={Serial}"
    # Headers (Fixed Bearer token format)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Token}"
    }

    try:
        # Corrected to use GET request
        response = requests.get(inverter_url, headers=headers, timeout=10)
        response.raise_for_status()

        parsed_inverter_json = response.json()

        if parsed_inverter_json.get('msg') == "Success": 
            #print(parsed_inverter_json)
            print(ConsoleColor.BOLD + "Grid data fetch response: " + ConsoleColor.OKGREEN + parsed_inverter_json['msg'] + ConsoleColor.ENDC)
            print(ConsoleColor.WARNING + str(len(parsed_inverter_json['data']['vip'])) + ConsoleColor.ENDC +  " Phase(s) detected.")
            #Loop through phases
            for x in range(len(parsed_inverter_json['data']['vip'])):
                currentphase = str(x)
                print(f"Grid Phase {currentphase} Voltage: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['vip'][x]['volt']) + ConsoleColor.ENDC)
                print(f"Grid Phase {currentphase} Current: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['vip'][x]['current']) + ConsoleColor.ENDC)
                print(f"Grid Phase {currentphase} Power: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['vip'][x]['power']) + ConsoleColor.ENDC)
                
            print("Grid Pac: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['pac']) + ConsoleColor.ENDC)
            print("Grid Qac: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['qac']) + ConsoleColor.ENDC)
            print("Grid Fac: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['fac']) + ConsoleColor.ENDC)
            print("Grid Pf: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['pf']) + ConsoleColor.ENDC)
            print("Grid Status: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['status']) + ConsoleColor.ENDC)
            print("Grid AcRealyStatus: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['acRealyStatus']) + ConsoleColor.ENDC)
            print("Grid EtodayFrom: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['etodayFrom']) + ConsoleColor.ENDC)
            print("Grid EtodayTo: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['etodayTo']) + ConsoleColor.ENDC)
            print("Grid EtotalFrom: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['etotalFrom']) + ConsoleColor.ENDC)
            print("Grid EtotalTo: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['etotalTo']) + ConsoleColor.ENDC)
            print("Grid LimiterPowerArr: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['limiterPowerArr']) + ConsoleColor.ENDC)
            print("Grid LimiterTotalPower: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['limiterTotalPower']) + ConsoleColor.ENDC)
            
            print(ConsoleColor.OKGREEN + "Grid fetch complete" + ConsoleColor.ENDC)

            
            

        else:
            print("Grid data fetch response: " + ConsoleColor.FAIL + parsed_inverter_json['msg'] + ConsoleColor.ENDC)

    except requests.exceptions.Timeout:
        print(ConsoleColor.FAIL + "Error: Request timed out while connecting to Service Provider API." + ConsoleColor.ENDC)

    except requests.exceptions.RequestException as e:
        print(ConsoleColor.FAIL + f"Error: Failed to connect to Service Provider API. {e}" + ConsoleColor.ENDC)
        return parsed_inverter_json
    except json.JSONDecodeError:
        print(ConsoleColor.FAIL + "Error: Failed to parse Service Provider API response." + ConsoleColor.ENDC)                
        return {}

def GetBatteryData(Token,Serial):  
    global api_server  
    inverter_url = f"https://{api_server}/api/v1/inverter/battery/{Serial}/realtime?sn={Serial}&lan=en"
    # Headers (Fixed Bearer token format)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Token}"
    }

    try:
        # Corrected to use GET request
        response = requests.get(inverter_url, headers=headers, timeout=10)
        response.raise_for_status()

        parsed_inverter_json = response.json()

        if parsed_inverter_json.get('msg') == "Success": 
            #print(parsed_inverter_json)
            print("Battery Time: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['time']) + ConsoleColor.ENDC)
            print("Battery EtodayChg: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['etodayChg']) + ConsoleColor.ENDC)
            print("Battery EtodayDischg: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['etodayDischg']) + ConsoleColor.ENDC)
            print("Battery EmonthChg: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['emonthChg']) + ConsoleColor.ENDC)
            print("Battery EmonthDischg: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['emonthDischg']) + ConsoleColor.ENDC)
            print("Battery EyearChg: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['eyearChg']) + ConsoleColor.ENDC)
            print("Battery EyearDischg: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['eyearDischg']) + ConsoleColor.ENDC)
            print("Battery EtotalChg: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['etotalChg']) + ConsoleColor.ENDC)
            print("Battery EtotalDischg: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['etotalDischg']) + ConsoleColor.ENDC)
            print("Battery Type: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['type']) + ConsoleColor.ENDC)
            print("Battery Power: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['power']) + ConsoleColor.ENDC)
            print("Battery Capacity: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['capacity']) + ConsoleColor.ENDC)
            print("Battery CorrectCap: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['correctCap']) + ConsoleColor.ENDC)
            print("Battery BmsSoc: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['bmsSoc']) + ConsoleColor.ENDC)
            print("Battery BmsVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['bmsVolt']) + ConsoleColor.ENDC)
            print("Battery BmsCurrent: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['bmsCurrent']) + ConsoleColor.ENDC)
            print("Battery BmsTemp: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['bmsTemp']) + ConsoleColor.ENDC)
            print("Battery Current: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['current']) + ConsoleColor.ENDC)
            print("Battery Voltage: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['voltage']) + ConsoleColor.ENDC)
            print("Battery Temp: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['temp']) + ConsoleColor.ENDC)
            print("Battery Soc: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['soc']) + ConsoleColor.ENDC)
            print("Battery ChargeVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['chargeVolt']) + ConsoleColor.ENDC)
            print("Battery DischargeVolt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['dischargeVolt']) + ConsoleColor.ENDC)
            print("Battery ChargeCurrentLimit: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['chargeCurrentLimit']) + ConsoleColor.ENDC)
            print("Battery DischargeCurrentLimit: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['dischargeCurrentLimit']) + ConsoleColor.ENDC)
            print("Battery MaxChargeCurrentLimit: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['maxChargeCurrentLimit']) + ConsoleColor.ENDC)
            print("Battery MaxDischargeCurrentLimit: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['maxDischargeCurrentLimit']) + ConsoleColor.ENDC)
            print("Battery Bms1Version1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['bms1Version1']) + ConsoleColor.ENDC)
            print("Battery Bms1Version2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['bms1Version2']) + ConsoleColor.ENDC)
            print("Battery Current2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['current2']) + ConsoleColor.ENDC)
            print("Battery Voltage2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['voltage2']) + ConsoleColor.ENDC)
            print("Battery Temp2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['temp2']) + ConsoleColor.ENDC)
            print("Battery Soc2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['soc2']) + ConsoleColor.ENDC)
            print("Battery ChargeVolt2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['chargeVolt2']) + ConsoleColor.ENDC)
            print("Battery DischargeVolt2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['dischargeVolt2']) + ConsoleColor.ENDC)
            print("Battery ChargeCurrentLimit2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['chargeCurrentLimit2']) + ConsoleColor.ENDC)
            print("Battery DischargeCurrentLimit2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['dischargeCurrentLimit2']) + ConsoleColor.ENDC)
            print("Battery MaxChargeCurrentLimit2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['maxChargeCurrentLimit2']) + ConsoleColor.ENDC)
            print("Battery MaxDischargeCurrentLimit2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['maxDischargeCurrentLimit2']) + ConsoleColor.ENDC)
            print("Battery Bms2Version1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['bms2Version1']) + ConsoleColor.ENDC)
            print("Battery Bms2Version2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['bms2Version2']) + ConsoleColor.ENDC)
            print("Battery Status: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['status']) + ConsoleColor.ENDC)
            print("Battery BatterySoc1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batterySoc1']) + ConsoleColor.ENDC)
            print("Battery BatteryCurrent1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryCurrent1']) + ConsoleColor.ENDC)
            print("Battery BatteryVolt1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryVolt1']) + ConsoleColor.ENDC)
            print("Battery BatteryPower1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryPower1']) + ConsoleColor.ENDC)
            print("Battery BatteryTemp1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryTemp1']) + ConsoleColor.ENDC)
            print("Battery BatteryStatus2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryStatus2']) + ConsoleColor.ENDC)
            print("Battery BatterySoc2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batterySoc2']) + ConsoleColor.ENDC)
            print("Battery BatteryCurrent2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryCurrent2']) + ConsoleColor.ENDC)
            print("Battery BatteryVolt2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryVolt2']) + ConsoleColor.ENDC)
            print("Battery BatteryPower2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryPower2']) + ConsoleColor.ENDC)
            print("Battery BatteryTemp2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batteryTemp2']) + ConsoleColor.ENDC)
            print("Battery NumberOfBatteries: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['numberOfBatteries']) + ConsoleColor.ENDC)
            print("Battery Batt1Factory: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batt1Factory']) + ConsoleColor.ENDC)
            print("Battery Batt2Factory: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['batt2Factory']) + ConsoleColor.ENDC)
            
            print(ConsoleColor.OKGREEN + "Battery fetch complete" + ConsoleColor.ENDC)
            
        else:
            print("Battery data fetch response: " + ConsoleColor.FAIL + parsed_inverter_json['msg'] + ConsoleColor.ENDC)

    except requests.exceptions.Timeout:
        print(ConsoleColor.FAIL + "Error: Request timed out while connecting to Service Provider API." + ConsoleColor.ENDC)

    except requests.exceptions.RequestException as e:
        print(ConsoleColor.FAIL + f"Error: Failed to connect to Service Provider API. {e}" + ConsoleColor.ENDC)
        return parsed_inverter_json
    except json.JSONDecodeError:
        print(ConsoleColor.FAIL + "Error: Failed to parse Service Provider API response." + ConsoleColor.ENDC)         
        
        return {}
def GetLoadData(Token,Serial): 
    global api_server    
    inverter_url = f"https://{api_server}/api/v1/inverter/load/{Serial}/realtime?sn={Serial}"
    # Headers (Fixed Bearer token format)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Token}"
    }

    try:
        # Corrected to use GET request
        response = requests.get(inverter_url, headers=headers, timeout=10)
        response.raise_for_status()

        parsed_inverter_json = response.json()

        if parsed_inverter_json.get('msg') == "Success":           
            print(ConsoleColor.BOLD + "Load data fetch response: " + ConsoleColor.OKGREEN + parsed_inverter_json['msg'] + ConsoleColor.ENDC)
            #print(parsed_inverter_json)            
            print(ConsoleColor.WARNING + str(len(parsed_inverter_json['data']['vip'])) + ConsoleColor.ENDC +  " Load(s) detected.")
            #Loop through Load Phases            
            for x in range(len(parsed_inverter_json['data']['vip'])): 
                currentloadphase = str(x)
                print(f"Load {currentloadphase} Volt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['vip'][x]['volt']) + ConsoleColor.ENDC)
                print(f"Load {currentloadphase} Current: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['vip'][x]['current']) + ConsoleColor.ENDC)
                print(f"Load {currentloadphase} Power: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['vip'][x]['power']) + ConsoleColor.ENDC)    
            
            print("Load totalUsed: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['totalUsed']) + ConsoleColor.ENDC)
            print("Load smartLoadStatus: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['dailyUsed']) + ConsoleColor.ENDC)                
            print("Load totalPower: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['totalPower']) + ConsoleColor.ENDC)
            print("Load smartLoadStatus: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['smartLoadStatus']) + ConsoleColor.ENDC)
            print("Load loadFac: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['loadFac']) + ConsoleColor.ENDC)
            print("Load upsPowerL1: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['upsPowerL1']) + ConsoleColor.ENDC)
            print("Load upsPowerL2: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['upsPowerL2']) + ConsoleColor.ENDC)
            print("Load upsPowerL3: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['upsPowerL3']) + ConsoleColor.ENDC)
            print("Load upsPowerTotal: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['upsPowerTotal']) + ConsoleColor.ENDC)

            print(ConsoleColor.OKGREEN + "Load fetch complete" + ConsoleColor.ENDC) 
            
        else:
            print("Load data fetch response: " + ConsoleColor.FAIL + parsed_inverter_json['msg'] + ConsoleColor.ENDC)

    except requests.exceptions.Timeout:
        print(ConsoleColor.FAIL + "Error: Request timed out while connecting to Service Provider API." + ConsoleColor.ENDC)

    except requests.exceptions.RequestException as e:
        print(ConsoleColor.FAIL + f"Error: Failed to connect to Service Provider API. {e}" + ConsoleColor.ENDC)
        return parsed_inverter_json
    except json.JSONDecodeError:
        print(ConsoleColor.FAIL + "Error: Failed to parse Service Provider API response." + ConsoleColor.ENDC)          
        
        return {}
def GetOutputData(Token,Serial):
    global api_server   
    inverter_url = f"https://{api_server}/api/v1/inverter/{Serial}/realtime/output"
    # Headers (Fixed Bearer token format)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Token}"
    }

    try:
        # Corrected to use GET request
        response = requests.get(inverter_url, headers=headers, timeout=10)
        response.raise_for_status()

        parsed_inverter_json = response.json()

        if parsed_inverter_json.get('msg') == "Success":           
            print(ConsoleColor.BOLD + "Output data fetch response: " + ConsoleColor.OKGREEN + parsed_inverter_json['msg'] + ConsoleColor.ENDC)
            #print(parsed_inverter_json)            
            print(ConsoleColor.WARNING + str(len(parsed_inverter_json['data']['vip'])) + ConsoleColor.ENDC +  " Output Phase(es) detected.")
            #Loop through Load Phases            
            for x in range(len(parsed_inverter_json['data']['vip'])): 
                currentOutput = str(x) 
                print(f"Output {currentOutput} Volt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['vip'][x]['volt']) + ConsoleColor.ENDC)
                print(f"Output {currentOutput} Current: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['vip'][x]['current']) + ConsoleColor.ENDC)
                print(f"Output {currentOutput} Power: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['vip'][x]['power']) + ConsoleColor.ENDC)
            
            print("Inverter totalPower: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['pInv']) + ConsoleColor.ENDC)
            print("Inverter Power AC: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['pac']) + ConsoleColor.ENDC)                
            print("Inverter Frequency: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['fac']) + ConsoleColor.ENDC) 

            print(ConsoleColor.OKGREEN + "Output fetch complete" + ConsoleColor.ENDC)
                
            
        else:
            print("Output data fetch response: " + ConsoleColor.FAIL + parsed_inverter_json['msg'] + ConsoleColor.ENDC)

    except requests.exceptions.Timeout:
        print(ConsoleColor.FAIL + "Error: Request timed out while connecting to Service Provider API." + ConsoleColor.ENDC)

    except requests.exceptions.RequestException as e:
        print(ConsoleColor.FAIL + f"Error: Failed to connect to Service Provider API. {e}" + ConsoleColor.ENDC)
        return parsed_inverter_json
    except json.JSONDecodeError:
        print(ConsoleColor.FAIL + "Error: Failed to parse Service Provider API response." + ConsoleColor.ENDC)         
        return {}

def GetDCACTemp(Token,Serial):    
    global api_server       
    VarCurrentDate = datetime.today().strftime('%Y-%m-%d')
    #print(VarCurrentDate)
    inverter_url = f"https://{api_server}/api/v1/inverter/{Serial}/output/day?lan=en&date={VarCurrentDate}&column=dc_temp,igbt_temp"
    # Headers (Fixed Bearer token format)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Token}"
    }

    try:
        # Corrected to use GET request
        response = requests.get(inverter_url, headers=headers, timeout=10)
        response.raise_for_status()

        parsed_inverter_json = response.json()

        if parsed_inverter_json.get('msg') == "Success":           
            print(ConsoleColor.BOLD + "Inverter data fetch response: " + ConsoleColor.OKGREEN + parsed_inverter_json['msg'] + ConsoleColor.ENDC)
            #print(str(parsed_inverter_json))
            #DC Temp              
            LastRecNum=len(parsed_inverter_json['data']['infos'][0]['records'])-1
            print(f"Inverter Temp UOM: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['infos'][0]['unit']) + ConsoleColor.ENDC) 
            print(f"Inverter DC Temp Volt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['infos'][0]['records'][LastRecNum]['value']) + ConsoleColor.ENDC)            
            print(f"Inverter AC Temp Volt: " + ConsoleColor.OKCYAN + str(parsed_inverter_json['data']['infos'][1]['records'][LastRecNum]['value']) + ConsoleColor.ENDC)   
            
            print(ConsoleColor.OKGREEN + "DC/AC Temperature fetch complete" + ConsoleColor.ENDC)
            
        else:
            print("Inverter data fetch response: " + ConsoleColor.FAIL + parsed_inverter_json['msg'] + ConsoleColor.ENDC)

    except requests.exceptions.Timeout:
        print(ConsoleColor.FAIL + "Error: Request timed out while connecting to Service Provider API." + ConsoleColor.ENDC)

    except requests.exceptions.RequestException as e:
        print(ConsoleColor.FAIL + f"Error: Failed to connect to Service Provider API. {e}" + ConsoleColor.ENDC)
        return parsed_inverter_json
    except json.JSONDecodeError:
        print(ConsoleColor.FAIL + "Error: Failed to parse Service Provider API response." + ConsoleColor.ENDC)         







        return {}
