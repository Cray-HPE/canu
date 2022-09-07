# MIT License
#
# (C) Copyright [2022] Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
"""Retrieve SLS token."""
import base64
from collections import defaultdict
import json
import sys
import os

from kubernetes import client, config
import requests
import urllib3


def pull_sls_networks(sls_file=None):
    """Query API-GW and retrieve token.

    Args:
        sls_file: generated sls json file.

    Returns:
        API token.
    """
    if sls_file:
        sls_networks = [
            network[x] for network in [sls_file.get("Networks", {})] for x in network
        ]
    if not sls_file:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        debug = False

        def on_debug(debug=False, message=None):
            if debug:
                print("DEBUG: {}".format(message))

        #
        # Convenience wrapper around remote calls
        #
        def remote_request(
            remote_type,
            remote_url,
            headers=None,
            data=None,
            verify=False,
            debug=False,
        ):
            remote_response = None
            while True:
                try:
                    response = requests.request(
                        remote_type,
                        url=remote_url,
                        headers=headers,
                        data=data,
                        verify=verify,
                    )
                    on_debug(debug, "Request response: {}".format(response.text))
                    response.raise_for_status()
                    remote_response = json.dumps({})
                    if response.text:
                        remote_response = response.json()
                    break
                except Exception as err:
                    message = "Error calling {}: {}".format(remote_url, err)
                    raise SystemExit(message) from err
            return remote_response

        #
        # Get the admin client secret from Kubernetes
        #
        secret = None
        cenv = os.getenv('CRAYENV')
        csm = 'csm'
        if cenv != csm:
            try:
                config.load_kube_config()
                v1 = client.CoreV1Api()
                secret_obj = v1.list_namespaced_secret(
                    "default",
                    field_selector="metadata.name=admin-client-auth",
                )
                secret_dict = secret_obj.to_dict()
                secret_base64_str = secret_dict["items"][0]["data"]["client-secret"]
                on_debug(
                    debug,
                    "base64 secret from Kubernetes is {}".format(secret_base64_str),
                )
                secret = base64.b64decode(secret_base64_str.encode("utf-8"))
                on_debug(debug, "secret from Kubernetes is {}".format(secret))
            except Exception as err:
                print("Error collecting secret from Kubernetes: {}".format(err))
                sys.exit(1)

        #
        # Get an auth token by using the secret
        #
        token = None
        if cenv != csm:
            try:
                token_url = "https://api-gw-service-nmn.local/keycloak/realms/shasta/protocol/openid-connect/token"
                token_data = {
                     "grant_type": "client_credentials",
                     "client_id": "admin-client",
                     "client_secret": secret,
                }
                token_request = remote_request(
                     "POST",
                     token_url,
                     data=token_data,
                     debug=debug,
                 )
                token = token_request["access_token"]
                on_debug(
                    debug=debug,
                    message="Auth Token from keycloak (first 50 char): {}".format(
                        token[:50],
                    ),
                )

            except Exception as err:
                print("Error obtaining keycloak token: {}".format(err))
                sys.exit(1)

        #
        # Get existing SLS data for comparison (used as a cache)
        #
        sls_cache = None
        if cenv == csm:
            sls_url = "http://cray-sls.services.svc.cluster.local/v1/networks"
        else:
            sls_url = "https://api-gw-service-nmn.local/apis/sls/v1/networks"
        auth_headers = {"Authorization": "Bearer {}".format(token)}
        try:
            sls_cache = remote_request(
                "GET",
                sls_url,
                headers=auth_headers,
                verify=False,
            )
            on_debug(
                debug=debug,
                message="SLS data has {} records".format(len(sls_cache)),
            )
        except Exception as err:
            print("Error requesting Networks from SLS: {}".format(err))
            sys.exit(1)
        on_debug(debug=debug, message="SLS records {}".format(sls_cache))

        sls_networks = sls_cache

    sls_variables = {
        "SWITCH_ASN": None,
        "CAN": None,
        "CAN_VLAN": None,
        "CMN": None,
        "CMN_VLAN": None,
        "HMN": None,
        "HMN_VLAN": None,
        "MTL": None,
        "MTL_VLAN": None,
        "NMN": None,
        "NMN_VLAN": None,
        "HMN_MTN": None,
        "NMN_MTN": None,
        "CAN_IP_GATEWAY": None,
        "CMN_IP_GATEWAY": None,
        "HSN_IP_GATEWAY": None,
        "HMN_IP_GATEWAY": None,
        "MTL_IP_GATEWAY": None,
        "NMN_IP_GATEWAY": None,
        "ncn_w001": None,
        "ncn_w002": None,
        "ncn_w003": None,
        "CAN_IP_PRIMARY": None,
        "CAN_IP_SECONDARY": None,
        "CMN_IP_PRIMARY": None,
        "CMN_IP_SECONDARY": None,
        "CAN_IPs": defaultdict(),
        "CMN_IPs": defaultdict(),
        "HMN_IPs": defaultdict(),
        "MTL_IPs": defaultdict(),
        "NMN_IPs": defaultdict(),
        "NMN_MTN_CABINETS": [],
        "HMN_MTN_CABINETS": [],
    }
    for sls_network in sls_networks:
        name = sls_network.get("Name", "")

        if name == "CAN":
            sls_variables["CAN"] = sls_network.get("ExtraProperties", {}).get(
                "CIDR",
                "",
            )
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                sls_variables["CAN_VLAN"] = subnets.get("VlanID", "")
                if subnets["Name"] == "bootstrap_dhcp":
                    sls_variables["CAN_IP_GATEWAY"] = subnets["Gateway"]
                    for ip in subnets["IPReservations"]:
                        if ip["Name"] == "can-switch-1":
                            sls_variables["CAN_IP_PRIMARY"] = ip["IPAddress"]
                        elif ip["Name"] == "can-switch-2":
                            sls_variables["CAN_IP_SECONDARY"] = ip["IPAddress"]

        if name == "CMN":
            sls_variables["CMN"] = sls_network.get("ExtraProperties", {}).get(
                "CIDR",
                "",
            )
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                sls_variables["CMN_VLAN"] = subnets.get("VlanID", "")
                if subnets["Name"] == "bootstrap_dhcp":
                    sls_variables["CMN_IP_GATEWAY"] = subnets["Gateway"]
                    for ip in subnets["IPReservations"]:
                        if ip["Name"] == "cmn-switch-1":
                            sls_variables["CMN_IP_PRIMARY"] = ip["IPAddress"]
                        elif ip["Name"] == "cmn-switch-2":
                            sls_variables["CMN_IP_SECONDARY"] = ip["IPAddress"]
                if subnets["Name"] == "network_hardware":
                    for ip in subnets["IPReservations"]:
                        if "sw" in ip["Name"]:
                            sls_variables["CMN_IPs"][ip["Name"]] = ip["IPAddress"]

        elif name == "HMN":
            sls_variables["HMN"] = sls_network.get("ExtraProperties", {}).get(
                "CIDR",
                "",
            )
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                sls_variables["HMN_VLAN"] = subnets.get("VlanID", "")
                if subnets["Name"] == "network_hardware":
                    sls_variables["HMN_IP_GATEWAY"] = subnets["Gateway"]
                    for ip in subnets["IPReservations"]:
                        sls_variables["HMN_IPs"][ip["Name"]] = ip["IPAddress"]

        elif name == "HSN":
            sls_variables["HSN"] = sls_network.get("ExtraProperties", {}).get(
                "CIDR",
                "",
            )
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                if subnets["Name"] == "hsn_base_subnet":
                    sls_variables["HSN_IP_GATEWAY"] = subnets["Gateway"]

        elif name == "MTL":
            sls_variables["MTL"] = sls_network.get("ExtraProperties", {}).get(
                "CIDR",
                "",
            )
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                sls_variables["MTL_VLAN"] = subnets.get("VlanID", "")
                if subnets["Name"] == "network_hardware":
                    sls_variables["MTL_IP_GATEWAY"] = subnets["Gateway"]
                    for ip in subnets["IPReservations"]:
                        sls_variables["MTL_IPs"][ip["Name"]] = ip["IPAddress"]

        elif name == "NMN":
            sls_variables["NMN"] = sls_network.get("ExtraProperties", {}).get(
                "CIDR",
                "",
            )
            sls_variables["SWITCH_ASN"] = sls_network.get("ExtraProperties", {}).get(
                "PeerASN",
                {},
            )
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                sls_variables["NMN_VLAN"] = subnets.get("VlanID", "")
                if subnets["Name"] == "bootstrap_dhcp":
                    for ip in subnets["IPReservations"]:
                        if ip["Name"] == "ncn-w001":
                            sls_variables["ncn_w001"] = ip["IPAddress"]
                        elif ip["Name"] == "ncn-w002":
                            sls_variables["ncn_w002"] = ip["IPAddress"]
                        elif ip["Name"] == "ncn-w003":
                            sls_variables["ncn_w003"] = ip["IPAddress"]
                elif subnets["Name"] == "network_hardware":
                    sls_variables["NMN_IP_GATEWAY"] = subnets["Gateway"]
                    for ip in subnets["IPReservations"]:
                        sls_variables["NMN_IPs"][ip["Name"]] = ip["IPAddress"]

        elif name == "NMN_MTN":
            sls_variables["NMN_MTN"] = sls_network.get("ExtraProperties", {}).get(
                "CIDR",
                "",
            )
            sls_variables["NMN_MTN_CABINETS"] = [
                list(sls_network.get("ExtraProperties", {}).get("Subnets", {})),
            ]
        elif name == "HMN_MTN":
            sls_variables["HMN_MTN"] = sls_network.get("ExtraProperties", {}).get(
                "CIDR",
                "",
            )
            sls_variables["HMN_MTN_CABINETS"] = [
                list(sls_network.get("ExtraProperties", {}).get("Subnets", {})),
            ]

    return sls_variables


def pull_sls_hardware(sls_file=None):
    """Query API-GW and retrieve token.

    Args:
        sls_file: generated sls json file.

    Returns:
        API token.
    """
    if sls_file:
        sls_hardware = [
            hardware[x] for hardware in [sls_file.get("Hardware", {})] for x in hardware
        ]
        return sls_hardware
    if not sls_file:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        debug = False

        def on_debug(debug=False, message=None):
            if debug:
                print("DEBUG: {}".format(message))

        #
        # Convenience wrapper around remote calls
        #
        def remote_request(
            remote_type,
            remote_url,
            headers=None,
            data=None,
            verify=False,
            debug=False,
        ):
            remote_response = None
            while True:
                try:
                    response = requests.request(
                        remote_type,
                        url=remote_url,
                        headers=headers,
                        data=data,
                        verify=verify,
                    )
                    on_debug(debug, "Request response: {}".format(response.text))
                    response.raise_for_status()
                    remote_response = json.dumps({})
                    if response.text:
                        remote_response = response.json()
                    break
                except Exception as err:
                    message = "Error calling {}: {}".format(remote_url, err)
                    raise SystemExit(message) from err
            return remote_response

        #
        # Get the admin client secret from Kubernetes
        #
        secret = None
        cenv = os.getenv('CRAYENV')
        csm = 'csm'
        if cenv != csm:
            try:
                config.load_kube_config()
                v1 = client.CoreV1Api()
                secret_obj = v1.list_namespaced_secret(
                    "default",
                    field_selector="metadata.name=admin-client-auth",
                )
                secret_dict = secret_obj.to_dict()
                secret_base64_str = secret_dict["items"][0]["data"]["client-secret"]
                on_debug(
                    debug,
                    "base64 secret from Kubernetes is {}".format(secret_base64_str),
                )
                secret = base64.b64decode(secret_base64_str.encode("utf-8"))
                on_debug(debug, "secret from Kubernetes is {}".format(secret))
            except Exception as err:
                print("Error collecting secret from Kubernetes: {}".format(err))
                sys.exit(1)

        #
        # Get an auth token by using the secret
        #
        token = None
        if cenv != csm:
            try:
                token_url = "https://api-gw-service-nmn.local/keycloak/realms/shasta/protocol/openid-connect/token"
                token_data = {
                    "grant_type": "client_credentials",
                    "client_id": "admin-client",
                    "client_secret": secret,
                }
                token_request = remote_request(
                    "POST",
                    token_url,
                    data=token_data,
                    debug=debug,
                )
                token = token_request["access_token"]
                on_debug(
                    debug=debug,
                    message="Auth Token from keycloak (first 50 char): {}".format(
                        token[:50],
                    ),
                )

            except Exception as err:
                print("Error obtaining keycloak token: {}".format(err))
                sys.exit(1)

        #
        # Get existing SLS data for comparison (used as a cache)
        #
        sls_cache = None
        if cenv == csm:
            sls_url = "http://cray-sls.services.svc.cluster.local/v1/hardware"
        else:
            sls_url = "https://api-gw-service-nmn.local/apis/sls/v1/hardware"
        auth_headers = {"Authorization": "Bearer {}".format(token)}
        try:
            sls_cache = remote_request(
                "GET",
                sls_url,
                headers=auth_headers,
                verify=False,
            )
            on_debug(
                debug=debug,
                message="SLS data has {} records".format(len(sls_cache)),
            )
        except Exception as err:
            print("Error requesting Networks from SLS: {}".format(err))
            sys.exit(1)
        on_debug(debug=debug, message="SLS records {}".format(sls_cache))

        return sls_cache
