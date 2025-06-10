import requests
import os
import yaml
import tkinter as tk
from tkinter import messagebox
import datetime
from time import sleep
import subprocess

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

def connectionCheck() -> bool:
    try:
        response = requests.get("https://google.com", timeout=5)
        return repsonse.status_code == 200
    except requests.ConnectionError:
        return False


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
        root.update()
        return True
    else:
        messagebox.showinfo(
        'Failed',
        'The login did not work. Check the entered credentials!',
        parent=root
        )
        root.update()
        return False

def looper(interval_mins, cred_pth):
    while True:
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M:%S")
        sleep(int(interval_mins)*60)
        print(time + ": Internet connected")
        if not wifiConnected:
            print(time +  " connection interruptet. Reconnecting")
            
            with open("wifi_credentials.yaml", "r") as file:
                wifi_list = yaml.safe_load(file)
            
            for ssid, creds in wifi_list.items():
                if is_connected_to(ssid=ssid):
                    response = request_poster(cred_pth)
                    if response.status_code == 200:
                        print(time + ": " + ssid+" reconnected")
                        sleep(15)
                else:
                    connect_to(ssid=ssid, password = {creds['password']})
                    sleep(30)
                    response = request_poster(cred_pth)
                    if response.status_code == 200:
                        print (time + ": " + ssid + " reconnected")

def wifiConnected() -> bool:
    connection = False
    with open("wifi_credentials.yaml", "r") as file:
        wifi_list = yaml.safe_load(file)

    list_connected = list()
    for ssid, creds in wifi_list.items():
        if not is_connected_to(ssid=ssid):
            connect_to(ssid=ssid, password= {creds['password']})
            sleep(15)
            if connectionCheck:
                all_connected.append(True)
            else:
                all_connected.append(False)
    
    return all(x is True for x in list_connected)


def save_multiple_wifi_credentials():
    wifi_data = {}

    def add_entry():
        ssid = entry_ssid.get().strip()
        password = entry_password.get().strip()
        if not ssid:
            messagebox.showwarning("Input Error", "SSID cannot be empty.")
            return
        wifi_data[ssid] = {"password": password}
        entry_ssid.delete(0, tk.END)
        entry_password.delete(0, tk.END)
        messagebox.showinfo("Saved", f"Entry for '{ssid}' saved.")

    def finish():
        if os.path.exists("wifi_credentials.yaml"):
            with open("wifi_credentials.yaml", "r") as file:
                existing_data = yaml.safe_load(file) or {}
        else:
            existing_data = {}

        existing_data.update(wifi_data)

        with open("wifi_credentials.yaml", "w") as file:
            yaml.dump(existing_data, file)

        messagebox.showinfo("Done", "All entries saved to wifi_credentials.yaml")
        window.destroy()

    window = tk.Tk()
    window.title("WiFi Credentials")
    window.geometry("300x200")

    tk.Label(window, text="WiFi SSID:").pack(pady=(10, 0))
    entry_ssid = tk.Entry(window, width=30)
    entry_ssid.pack()

    tk.Label(window, text="WiFi Password:").pack(pady=(10, 0))
    entry_password = tk.Entry(window, width=30, show="*")
    entry_password.pack()

    tk.Button(window, text="Add Entry", command=add_entry).pack(pady=(10, 0))
    tk.Button(window, text="Finish & Save", command=finish).pack(pady=5)

    window.mainloop()

def intialRequest(cred_pth) -> bool:
    
    responses = list()
    with open("wifi_credentials.yaml", 'r') as file:
        wifis = yaml.safe_load(file)

    for ssid, creds in wifis.items():
        connect_to(ssid=ssid, password={creds['password']})
        sleep(15)
        response = request_poster(cred_pth)
        status_code = response.status_code
        if status_code == 200:
            print(ssid + ": Connection innitialized")
        else:
            print(ssid + ": Connection can't be innitialzied")
        responses.append(response.status_code)


    if sum(responses)/len(responses) == 200:
        return True
    else:
        return False

import subprocess

def what_wifi():
    process = subprocess.run(['nmcli', '-t', '-f', 'ACTIVE,SSID', 'dev', 'wifi'], stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip().split(':')[1]
    else:
        return ''

def is_connected_to(ssid: str):
    return what_wifi() == ssid

def scan_wifi():
    process = subprocess.run(['nmcli', '-t', '-f', 'SSID,SECURITY,SIGNAL', 'dev', 'wifi'], stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip().split('\n')
    else:
        return []
        
def is_wifi_available(ssid: str):
    return ssid in [x.split(':')[0] for x in scan_wifi()]

def connect_to(ssid: str, password: str):
    if not is_wifi_available(ssid):
        return False
    subprocess.call(['nmcli', 'd', 'wifi', 'connect', ssid, 'password', password])
    return is_connected_to(ssid)

def connect_to_saved(ssid: str):
    if not is_wifi_available(ssid):
        return False
    subprocess.call(['nmcli', 'c', 'up', ssid])
    return is_connected_to(ssid)
