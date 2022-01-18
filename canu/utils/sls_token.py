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
import json
import sys

from kubernetes import client, config
import requests
import urllib3


def sls_token():
    """Query API-GW and retrieve token.

    Args:
        None.

    Returns:
        API token.
    """
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
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        secret_obj = v1.list_namespaced_secret(
            "default",
            field_selector="metadata.name=admin-client-auth",
        )
        secret_dict = secret_obj.to_dict()
        secret_base64_str = secret_dict["items"][0]["data"]["client-secret"]
        on_debug(debug, "base64 secret from Kubernetes is {}".format(secret_base64_str))
        secret = base64.b64decode(secret_base64_str.encode("utf-8"))
        on_debug(debug, "secret from Kubernetes is {}".format(secret))
    except Exception as err:
        print("Error collecting secret from Kubernetes: {}".format(err))
        sys.exit(1)

    #
    # Get an auth token by using the secret
    #
    token = None
    try:
        token_url = "https://api-gw-service-nmn.local/keycloak/realms/shasta/protocol/openid-connect/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": "admin-client",
            "client_secret": secret,
        }
        token_request = remote_request("POST", token_url, data=token_data, debug=debug)
        token = token_request["access_token"]
        on_debug(
            debug=debug,
            message="Auth Token from keycloak (first 50 char): {}".format(token[:50]),
        )
        return token
    except Exception as err:
        print("Error obtaining keycloak token: {}".format(err))
        sys.exit(1)
