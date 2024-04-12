import os
import sys
import time
import requests
from datetime import datetime
import json
from scrapli import Scrapli
import click

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)


def login(session, ip, username, password):
    url = f"https://{ip}/rest/v10.11/login"
    credentials = {"username": username, "password": password}
    try:
        response = session.post(url, data=credentials, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.secho(f"Error during login: {str(e)}", fg="red")
        sys.exit(1)


def start_dryrun(session, ip, input_file):
    url = f"https://{ip}/rest/v10.11/configs/running-config?dryrun"

    try:
        with open(input_file, "rb") as f:
            data = f.read()
        headers = {"Content-Type": "text/plain"}
        response = session.post(url, data=data, headers=headers, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.secho(f"Error starting dryrun: {str(e)}", fg="red")
        sys.exit(1)


def get_dryrun_results(session, ip):
    url = f"https://{ip}/rest/v10.11/configs/running-config?dryrun"
    try:
        while True:
            response = session.get(url, verify=False)
            response.raise_for_status()
            result = response.json()
            if result["state"] != "pending":
                break
            time.sleep(5)
        return result
    except requests.exceptions.RequestException as e:
        click.secho(f"Error getting dryrun results: {str(e)}", fg="red")
        sys.exit(1)


def clear_dryrun_results(session, ip):
    url = f"https://{ip}/rest/v10.11/configs/running-config?dryrun"
    try:
        response = session.delete(url, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.secho(f"Error clearing dryrun results: {str(e)}", fg="red")
        sys.exit(1)


def get_running_config(session, host):
    running_config_url = f"https://{host}/rest/v10.11/configs/running-config"
    response = session.get(running_config_url, verify=False)
    return response.json()


def update_config(config, mgmt_int, subsystems):
    config["System"]["mgmt_intf"] = mgmt_int
    config["System"]["subsystems"] = subsystems
    return config


def write_config_json(config, filename):
    with open(filename, "w") as file:
        json.dump(config, file, indent=4)


def upload_config_startup(session, host, config_json):
    configs_url = f"https://{host}/rest/v10.11/fullconfigs/startup-config"
    headers = {"Content-Type": "application/json"}
    data = config_json
    response = session.put(
        configs_url, json=data, headers=headers, verify=False, timeout=120
    )
    return response.status_code


def show_checkpoint_diff(ip, username, password):
    device = {
        "host": ip,
        "auth_username": username,
        "auth_password": password,
        "auth_strict_key": False,
        "platform": "aruba_aoscx",
    }

    conn = Scrapli(**device)
    conn.open()
    diff_output = conn.send_command("checkpoint diff startup-config running-config")
    return diff_output.result


def copy_startup_running(ip, username, password):
    device = {
        "host": ip,
        "auth_username": username,
        "auth_password": password,
        "auth_strict_key": False,
        "platform": "aruba_aoscx",
    }
    conn = Scrapli(**device)
    conn.open()
    output = conn.send_command("copy startup-config running-config")
    return output.result


def copy_running_startup(ip, username, password):
    device = {
        "host": ip,
        "auth_username": username,
        "auth_password": password,
        "auth_strict_key": False,
        "platform": "aruba_aoscx",
    }
    conn = Scrapli(**device)
    conn.open()
    output = conn.send_command("copy running-config startup-config")
    return output.result


def logout(session, ip):
    url = f"https://{ip}/rest/v10.11/logout"
    try:
        response = session.post(url, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        click.secho(f"Error during logout: {str(e)}", fg="red")
        sys.exit(1)


def main():
    session = requests.Session()
    ip = "10.102.193.4"
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    input_file = "/Users/lucasbates/canu-container/canu/canu/config/sw-leaf-bmc-001.cfg"
    checkpoint_name = f"ac_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
    validated_config_json = (
        f"{os.path.dirname(os.path.abspath(__file__))}/{ip}_{checkpoint_name}.json"
    )
    login(session, ip, username, password)
    start_dryrun(session, ip, input_file)
    result = get_dryrun_results(session, ip)
    if result["state"] == "error":
        click.secho("Dryrun failed.", fg="red")
        # Handle error parsing here
    else:
        click.secho("Dryrun Succeeded", fg="green")
        original_config = json.loads(result["configs"]["json"])
        running_config = get_running_config(session, ip)
        mgmt_int = running_config["System"]["mgmt_intf"]
        subsystems = running_config["System"]["subsystems"]
        updated_config = update_config(original_config, mgmt_int, subsystems)
        write_config_json(updated_config, validated_config_json)
        status_code = upload_config_startup(session, ip, updated_config)
        if status_code != 200:
            click.secho("Failed to upload the configuration.", fg="red")
            raise Exception("Failed to upload the configuration.")
        diff_output = show_checkpoint_diff(ip, username, password)
        print(diff_output)
        user_confirmation = input(
            "Do you want to replace the running config with the uploaded config? (y/n): "
        )
        if user_confirmation.lower() == "y":
            copy_startup_running(ip, username, password)
        else:
            # copy the running configuration back to the startup configuration
            copy_running_startup(ip, username, password)
    clear_dryrun_results(session, ip)
    logout(session, ip)


if __name__ == "__main__":
    main()
