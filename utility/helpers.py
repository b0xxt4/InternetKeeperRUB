import requests
import os
import yaml
import tkinter as tk
from tkinter import messagebox
from crontab import CronTab
import datetime
from time import sleep

tk.TK_SILENCE_DEPRECIATION=1


def request_poster(path):
    cred = yaml.safe_load(open(path))
    web_address = cred['web_address']
    login_id = cred['login_id']
    password = cred['password']

    values = {'loginid' : login_id,
            'password' : password,
            'action': 'Login'}

    r = requests.post(web_address, data=values)
    return r

def run_credential_gui():
    def submit_credentials():
        web_address = entry_web.get()
        login_id = entry_login.get()
        password = entry_password.get()
        # You can handle the credentials here (e.g., save to file or use securely)
        data = dict(
            web_address = web_address,
            login_id = login_id,
            password = password
        )
        with open('credentials.yaml', 'w') as outputfile:
            yaml.dump(data, outputfile, default_flow_style=False)

        messagebox.showinfo("Success", "Credentials saved")
        root.destroy()


    # Create main window
    root = tk.Tk()
    root.title("Credential Entry")
    root.geometry("300x500")

    # Web address label and entry
    label_web = tk.Label(root, text="Web Address:")
    label_web.pack(pady=(10, 0))
    entry_web = tk.Entry(root, width=40)
    entry_web.insert(0, "https://login.ruhr-uni-bochum.de/cgi-bin/laklogin")  # Default value
    entry_web.pack()

    # Login ID label and entry
    label_login = tk.Label(root, text="Login ID:")
    label_login.pack(pady=(10, 0))
    entry_login = tk.Entry(root, width=40)
    entry_login.pack()

    # Password label and entry
    label_password = tk.Label(root, text="Password:")
    label_password.pack(pady=(10, 0))
    entry_password = tk.Entry(root, width=40, show="*")
    entry_password.pack()

    # Submit button
    submit_btn = tk.Button(root, text="Submit", command=submit_credentials)
    submit_btn.pack(pady=15)

    # Run the application
    root.lift()
    root.mainloop()

def get_login_and_interval():
    def on_submit():
        login_time = entry_login_time.get()
        check_interval = entry_interval.get()
        data = dict(
            login_time=login_time,
            check_interval = check_interval
        )
        print(f"Login Time: {login_time}, Check Interval: {check_interval} minutes")
        with open('time.yaml', 'w') as outputfile:
            yaml.dump(data, outputfile, default_flow_style=False)
        
        window.destroy()

    window = tk.Tk()
    window.title("Login and Interval")
    window.geometry("300x150")

    label_login_time = tk.Label(window, text="Login Time (HH:MM):")
    label_login_time.pack(pady=(10, 0))
    entry_login_time = tk.Entry(window, width=30)
    entry_login_time.pack()

    label_interval = tk.Label(window, text="Check Interval (minutes):")
    label_interval.pack(pady=(10, 0))
    entry_interval = tk.Entry(window, width=30)
    entry_interval.pack()

    submit_button = tk.Button(window, text="OK", command=on_submit)
    submit_button.pack(pady=15)

    window.lift()
    window.mainloop()


def check_login(response) -> bool:
    root = tk.Tk()
    root.wm_attributes("-topmost", 1)
    root.withdraw()
    if response.status_code == 200:
        messagebox.showinfo(
            'Success', 
            'The login works and can be used!',
            parent=root
            )
        return True
    else:
        messagebox.showinfo(
        'Failed',
        'The login did not work. Check the entered credentials!',
        parent=root
        )
        return False
    root.destroy()

def cron_job(python_pth, exec_pth, cron_path):
    root = tk.Tk()
    root.wm_attributes("-topmost", 1)
    root.withdraw()
    cron_data = yaml.safe_load(open(cron_path))
    #sleep(5) #wait 5 seconds
    login_time = cron_data['login_time']
    time = datetime.time(hour=int(str(login_time)[0:1]), minute=int(str(login_time)[3:4]))
    check_interval = cron_data['check_interval']
    cron = CronTab()
    job = cron.new(command = 'source' + python_pth + ' '+ exec_pth)
    job.minute.every(check_interval)
    job.setall(time)
    #job.write()
    job.enable()
    messagebox.showinfo('Success', 'Automization installed!', parent=root)

    
def checkConnection(response)->bool:
    if response.status_code == 200:
        return True
    else:
        return False

def looper(response, interval_mins, cred_pth):
    while True:
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M:%S")
        sleep(int(interval_mins)*60)
        print(time + " connected")
        if not checkConnection(response):
            print(time +  " connection interruptet. Reconnecting")
            response = hlp.request_poster(cred_pth)
            if response.status_code == 200:
                print (time + " reconnected")    