#!/usr/bin/env python
#
#   wrapper_apic
#       v0.1
#
#   Christian Jaeckel (chjaecke@cisco.com)
#       October 2016
#
#   This class provides methods to facilitate access
#   to the APIC-EM API.
#
#   REQUIREMENTS:
#       - requests
#
#   WARNING:
#       Any use of these scripts and tools is at
#       your own risk. There is no guarantee that
#       they have been through thorough testing in a
#       comparable environment and we are not
#       responsible for any damage or data loss
#       incurred with their use.

import json
import requests
import urllib.parse as urlparse
import xml.etree.ElementTree as et
from enums import ApiEncoding
from enums import ApiRequest
from requests.packages.urllib3.exceptions import InsecureRequestWarning

"""
Default base URI of the APIC-EM API
"""
DEFAULT_API_URI = "/api/v1/"


class ErrorAPIC(Exception):
    """
    Generic error raised by the APIC-EM API module.
    """


class WrapperAPIC(object):
    """
    APIC-EM API Wrapper class.
    """

    def __init__(self, url, username, password):
        """
        Create a new wrapper instance.

        :param url: URL/Host to APIC-EM.
        :param username: Username to access API.
        :param password: Password to access API.
        """
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.base_url = urlparse.urljoin(url, DEFAULT_API_URI)
        self.username = username
        self.password = password
        self.token = None
        self.login()

    def login(self):
        """
        Login to APIC-EM API. Posts user credentials and retrieves a service ticket to post requests to the APIC-EM API.
        """

        try:
            login_data = {"username": self.username, "password": self.password}
            json_login = json.dumps(login_data)
            headers = {"content-type": "application/json"}

            session = requests.Session()
            response = session.request("POST", self.base_url + "ticket", timeout=10, verify=False, data=json_login, headers=headers)

            if response.status_code != 200:
                raise Exception

            self.token = response.json()["response"]["serviceTicket"]

        except Exception:
            raise ErrorAPIC("Connection to APIC-EM API failed. Please verify user credentials.")

    def send_request(self, resource_url, verb, payload=None, enc=ApiEncoding.json, relogin=False):
        """
        Sends a requests to the APIC-EM API.

        :param resource_url: URI of the API method.
        :param verb: POST/GET/DELETE enum from ApiRequest.
        :param payload: (Optional) Dictionary, bytes, or file-like object to send in the body to the API.
        :param enc: (Optional) XML or JSON enum from ApiEncoding. Default is JSON.
        :param relogin: (Optional) Perform a relogin to the API to get a new session ticket first.
        :return: API response in JSON or XML.
        """

        if relogin:
            self.login()

        session = requests.Session()
        headers = {"x-auth-token": self.token}

        if enc == ApiEncoding.xml:
            headers["content-type"] = "application/xml"
        else:
            headers["content-type"] = "application/json"

        if verb == ApiRequest.get:
            response = session.request("GET", self.base_url + resource_url, timeout=10, verify=False, headers=headers)
        elif verb == ApiRequest.post:
            response = session.request("POST", self.base_url + resource_url, timeout=10, verify=False, headers=headers,
                                   data=payload)
        else:
            raise ErrorAPIC("Internal error")

        if response.status_code == 401:
            self.send_request(resource_url, verb, payload, enc, relogin=True)
        elif response.status_code != 200 and response.status_code != 202:
            raise ErrorAPIC("The following status code was returned: {}".format(response.status_code))

        if enc == ApiEncoding.xml:
            return et.fromstring(response.content)
        elif enc == ApiEncoding.json:
            return response.json()
        else:
            raise ErrorAPIC("Internal error")