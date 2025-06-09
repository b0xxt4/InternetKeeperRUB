import utility.helpers as hlp
import yaml
import os
import requests

cred_pth = os.path.dirname(__file__)+'/credentials.yaml'
wifi_pth = os.path.dirname(__file__)+'/wifi_credentials.yaml'
time_pth = os.path.dirname(__file__)+'/time.yaml'

def main():

    #check if credentials already exist
    if not os.path.exists(cred_pth):
        hlp.run_credential_gui()

    #check if wifi is already defined
    if not os.path.exists(wifi_pth):
        hlp.save_multiple_wifi_credentials()

    #posting request based on entered values
    check = hlp.intialRequest(cred_pth)
    
    #20 attempts max for entering fitting credits
    for i in range(0, 20):
        if check:
            print("Connected")
            break
        else:
            hlp.run_credential_gui()
            check  = hlp.intialRequest(cred_pth)

    #check if time already defined
    if not os.path.exists(time_pth):
        hlp.get_login_and_interval()

    time_input = yaml.safe_load(open(time_pth))
    interval_mins = time_input['check_interval']

    hlp.looper(interval_mins, cred_pth)
    
if __name__ == '__main__':
    main()