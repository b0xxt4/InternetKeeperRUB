import utility.helpers as hlp
import yaml
import os
import requests

cred_pth = os.path.dirname(__file__)+'/credentials.yaml'
cron_pth = os.path.dirname(__file__)+'/cron.yaml'
python_pth = os.path.dirname(__file__)+'/.venv/bin/python'
exec_pth = os.path.dirname(__file__)+'/main.py'

def main():

    #check if credentials already exist
    if not os.path.exists(cred_pth):
        hlp.run_credential_gui()

    #posting request based on entered values
    response = hlp.request_poster(cred_pth)

    
    check = hlp.check_login(response)
   
    #20 attempts max for entering fitting credits
    for i in range(0, 20):
        if check:
            break
        else:
            hlp.run_credential_gui()
            response = hlp.request_poster(cred_pth)
            check = hlp.check_login(response)

    #check if cron already defined
    if not os.path.exists(cron_pth):
        hlp.get_login_and_interval()

    #create cronjob for relevant logintime
    if check:
        hlp.cron_job(python_pth, exec_pth, cron_path = cron_pth)

if __name__ == '__main__':
    main()