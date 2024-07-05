import os
import sys
import time
import requests
from datetime import datetime
import json
from scrapli import Scrapli
import click
import logging

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def login(session, ip, username, password):
    url = f"https://{ip}/rest/v10.11/login"
    credentials = {"username": username, "password": password}
    try:
        response = session.post(url, data=credentials, verify=False)
        response.raise_for_status()
        logger.info(f"Successfully logged in to {ip}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during login: {str(e)}")
        sys.exit(1)


def start_dryrun(session, ip, input_file):
    url = f"https://{ip}/rest/v10.11/configs/running-config?dryrun"

    try:
        with open(input_file, "rb") as f:
            data = f.read()
        headers = {"Content-Type": "text/plain"}
        response = session.post(url, data=data, headers=headers, verify=False)
        response.raise_for_status()
        logger.info(f"Started dryrun on {ip}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error starting dryrun: {str(e)}")
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
        logger.info(f"Dryrun results obtained from {ip}")
        if result["state"] == "error":
            logger.error(f"Dryrun failed. Error details: {result['errors']}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting dryrun results: {str(e)}")
        sys.exit(1)


def clear_dryrun_results(session, ip):
    url = f"https://{ip}/rest/v10.11/configs/running-config?dryrun"
    try:
        response = session.delete(url, verify=False)
        response.raise_for_status()
        logger.info(f"Dryrun results cleared on {ip}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error clearing dryrun results: {str(e)}")
        sys.exit(1)


def get_running_config(session, host):
    running_config_url = f"https://{host}/rest/v10.11/configs/running-config"
    response = session.get(running_config_url, verify=False)
    logger.info(f"Running config obtained from {host}")
    return response.json()


def update_config(config, mgmt_int, subsystems):
    config["System"]["mgmt_intf"] = mgmt_int
    config["System"]["subsystems"] = subsystems
    logger.info("Config updated with mgmt_intf and subsystems")
    return config


def write_config_json(config, filename):
    with open(filename, "w") as file:
        json.dump(config, file, indent=4)
    logger.info(f"Config written to {filename}")


def upload_config_startup(session, host, config_json, force):
    if force:
        configs_url = f"https://{host}/rest/v10.11/fullconfigs/running-config"
        logger.info("Force flag enabled. Writing to running configuration.")
    else:
        configs_url = f"https://{host}/rest/v10.11/fullconfigs/startup-config"

    headers = {"Content-Type": "application/json"}
    data = config_json
    response = None  # Initialize response variable
    try:
        response = session.put(
            configs_url, json=data, headers=headers, verify=False, timeout=60
        )
        response.raise_for_status()
        if force:
            logger.info(f"Config uploaded to running-config on {host}")
        else:
            logger.info(f"Config uploaded to startup-config on {host}")
        return response.status_code, response
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Error uploading config to {'running-config' if force else 'startup-config'} on {host}: {str(e)}"
        )
        if response is not None:
            logger.error(f"Response content: {response.text}")
        return None, response


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
    logger.info(f"Checkpoint diff obtained from {ip}")
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
    logger.info(f"Copied startup-config to running-config on {ip}")
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


def set_checkpoint_timer(session, host, minutes):
    url = f"https://{host}/rest/v10.11/configs/autocheckpoint"
    headers = {"Content-Type": "application/json"}
    data = {"minutes": minutes}
    try:
        response = session.post(url, headers=headers, json=data, verify=False)
        response.raise_for_status()
        logger.info(f"Checkpoint timer set to {minutes} minutes on {host}")
    except requests.exceptions.RequestException as e:
        if (
            response.status_code == 400
            and "Checkpoint auto timer is already ON" in response.text
        ):
            logger.warning(
                f"Checkpoint auto timer is already ON on {host}. Acknowledging..."
            )
            acknowledge_autocheckpoint(session, host)
            logger.info(f"Acknowledged existing checkpoint on {host}")
            set_checkpoint_timer(
                session, host, minutes
            )  # Retry setting the checkpoint timer
        else:
            logger.error(f"Error setting checkpoint timer on {host}: {str(e)}")
            logger.error(f"Response content: {response.text}")
            raise


def acknowledge_autocheckpoint(session, host):
    url = f"https://{host}/rest/v10.11/configs/autocheckpoint"
    headers = {"Content-Type": "application/json"}
    try:
        response = session.put(url, headers=headers, verify=False)
        response.raise_for_status()
        logger.info(f"Acknowledged autocheckpoint on {host}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error acknowledging autocheckpoint on {host}: {str(e)}")
        logger.error(f"Response content: {response.text}")
        raise


def copy_running_to_checkpoint(session, host, checkpoint_name):
    url = f"https://{host}/rest/v10.11/fullconfigs/{checkpoint_name}?from=%2Frest%2Fv10.11%2Ffullconfigs%2Frunning-config"
    headers = {"accept": "*/*"}
    try:
        response = session.put(url, headers=headers, verify=False)
        response.raise_for_status()
        logger.info(
            f"Copied running configuration to checkpoint '{checkpoint_name}' on {host}"
        )
    except requests.exceptions.RequestException as e:
        if response.status_code == 400 and "already exists" in response.text:
            logger.warning(
                f"Checkpoint '{checkpoint_name}' already exists or a checkpoint with the same config on {host}. Skipping checkpoint creation."
            )
        else:
            logger.error(
                f"Error copying running configuration to checkpoint '{checkpoint_name}' on {host}: {str(e)}"
            )
            logger.error(f"Response content: {response.text}")
            raise


def verify_connectivity(ip, username, password, timeout=120, interval=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            device = {
                "host": ip,
                "auth_username": username,
                "auth_password": password,
                "auth_strict_key": False,
                "platform": "aruba_aoscx",
            }
            conn = Scrapli(**device)
            conn.open()
            logger.info(f"Successfully connected to {ip} after configuration change")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to {ip}: {str(e)}")
            time.sleep(interval)
    logger.error(f"Failed to connect to {ip} within the specified timeout")
    return False


def logout(session, ip):
    url = f"https://{ip}/rest/v10.11/logout"
    try:
        response = session.post(url, verify=False)
        response.raise_for_status()
        logger.info(f"Logged out from {ip}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during logout: {str(e)}")
        sys.exit(1)


@click.command()
@click.option("--log", is_flag=True, help="Enable logging")
@click.option("--ip", prompt="Enter switch IP", help="Switch IP address")
@click.option("--username", prompt="Enter your username", help="Username")
@click.option("--password", prompt="Enter your password", help="Password")
@click.option(
    "--config",
    prompt="Enter path to the config file",
    help="Path to the configuration file",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force write to running configuration. Needed for Aruba-CX virtual switch.",
)
def main(log, ip, username, password, config, force):
    if not log:
        logging.disable(logging.CRITICAL)

    session = requests.Session()
    checkpoint_name = f"ac_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
    validated_config_json = (
        f"{os.path.dirname(os.path.abspath(__file__))}/{ip}_{checkpoint_name}.json"
    )

    try:
        login_successful = False
        try:
            login(session, ip, username, password)
            login_successful = True
            start_dryrun(session, ip, config)
            result = get_dryrun_results(session, ip)
            if result["state"] == "error":
                logger.error(f"Dryrun failed. Error details: {result['errors']}")
            else:
                logger.info("Dryrun Succeeded")
                original_config = json.loads(result["configs"]["json"])
                running_config = get_running_config(session, ip)
                copy_running_to_checkpoint(session, ip, checkpoint_name)
                mgmt_int = running_config["System"]["mgmt_intf"]
                subsystems = running_config["System"]["subsystems"]
                updated_config = update_config(original_config, mgmt_int, subsystems)
                write_config_json(updated_config, validated_config_json)
                set_checkpoint_timer(session, ip, 2)
                status_code = None
                try:
                    # Other code...
                    status_code = upload_config_startup(
                        session, ip, updated_config, force
                    )
                    # Other code...
                except Exception as e:
                    logger.exception(
                        f"An error occurred during configuration upload: {str(e)}"
                    )
                    raise

                # Move the block outside of the try-except block
                if status_code is None:
                    logger.error(
                        "Uploaded configuration failed. Rolling back to the previous configuration."
                    )
                    if verify_connectivity(ip, username, password):
                        logger.info(
                            f"Roll Back Successful. Connection re-established with {ip}."
                        )
                    else:
                        logger.error(
                            f"Failed to re-establish connection with {ip}. Aborting configuration upload."
                        )
                        raise Exception("Failed to upload configuration")

                if not force:
                    diff_output = show_checkpoint_diff(ip, username, password)
                    print(diff_output)
                    user_confirmation = input(
                        "Do you want to replace the running config with the uploaded config? (y/n): "
                    )
                    if user_confirmation.lower() == "y":
                        copy_startup_running(ip, username, password)
                        if not verify_connectivity(ip, username, password):
                            logger.error(
                                "Uploaded configuration failed. Rolling back to the previous configuration."
                            )
                            copy_running_startup(ip, username, password)
                    else:
                        # Copy the running configuration to a checkpoint
                        copy_running_to_checkpoint(session, ip, checkpoint_name)
                else:
                    logger.info("Force flag enabled. Skipping user confirmation.")

                # Acknowledge autocheckpoint at the end of the "Dryrun Succeeded" block
                acknowledge_autocheckpoint(session, ip)

            clear_dryrun_results(session, ip)
        except Exception as e:
            logger.exception(f"An error occurred: {str(e)}")
            raise
    finally:
        if login_successful:
            logout(session, ip)


if __name__ == "__main__":
    main()
