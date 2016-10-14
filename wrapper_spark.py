#!/usr/bin/env python
#
#   wrapper_spark
#       v0.1
#
#   Christian Jaeckel (chjaecke@cisco.com)
#       October 2016
#
#   This class provides methods to facilitate access
#   to the Cisco Spark API.
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
from enums import ApiRequest
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urlencode

"""
Default base URI of the Spark API
"""
DEFAULT_API_URI = "https://api.ciscospark.com/v1/people"


class ErrorSpark(Exception):
    """
    Generic error for Spark API
    """


class WrapperSpark(object):
    """"
    Cisco Spark API Wrapper class.
    """

    def __init__(self, token):
        """
        Create a new wrapper instance.

        :param token: Spark user token (without 'Bearer' prefix).
        """
        self.default_header = {'Content-type': 'application/json', 'Authorization': token}
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def set_new_token(self, token):
        """
        Set a new user token. If the new token is invalid, then the previous token is kept.

        :param token: New Spark user token (without 'Bearer' prefix).
        :return: True, if new user token was accepted.
        """
        old_token = self.default_header["Authorization"]
        self.default_header["Authorization"] = "Bearer " + token

        user = self.get_people_me()

        if user is not None:
            return True
        elif old_token is not None:
            self.default_header["Authorization"] = old_token

        return False

    def validate_token(self):
        """
        Validate if the current Spark user token is valid.

        :return: True, if user token is valid.
        """
        user = self.get_people_me()
        if user is not None:
            return True
        else:
            return False

    def get_people_me(self):
        """
        Shows the profile for the authenticated user.

        :return: API response in JSON.
        """
        try:
            return self._request_stub("people/me", ApiRequest.get)
        except ErrorSpark:
            return None

    def get_room(self, room_id):
        """
        Shows details for a room, by ID.

        :param room_id: The room ID.
        :return: API response in JSON.
        """
        return self._request_stub("rooms/" + room_id, ApiRequest.get)

    def get_rooms(self, team_id=None, max=None, type=None):
        """
        List rooms to which the authenticated user belongs.

        :param team_id: (Optional) Filter rooms by team ID.
        :param max: (Optional) Maximum amount of rooms returned.
        :param type: (Optional) Filter rooms by 'group' or 'direct' conversations.
        :return: API response in JSON.
        """
        params = {}
        if team_id is not None:
            params["teamID"] = team_id
        if max is not None:
            params["max"] = max
        if type is not None:
            params["type"] = type

        return self._request_stub("rooms", ApiRequest.get, query=params)

    def post_message(self, room_id=None, to_person_id=None, to_person_email=None, text=None, markdown=None, files=None):
        """
        Posts a plain text message, and optionally, a media content attachment, to a room.

        :param room_id: (Optional) The room ID.
        :param to_person_id: (Optional) The ID of the recipient when sending a private1:1 message.
        :param to_person_email: (Optional) The email address of the recipient when sendinga private 1:1 message.
        :param text: (Optional) The message, in plain text or in rich text if markdown is specified.
        :param markdown: (Optional) The message, in markdown format.
        :param files: (Optional) A URL reference for the message attachment.
        :return: API response in JSON.
        """
        params = {}
        if room_id is not None:
            params["roomId"] = room_id
        if to_person_id is not None:
            params["toPersonId"] = to_person_id
        if to_person_email is not None:
            params["toPersonEmail"] = to_person_email
        if text is not None:
            params["text"] = text
        if markdown is not None:
            params["markdown"] = markdown
        if files is not None:
            params["files"] = files

        return self._request_stub("messages", ApiRequest.post, payload=params)

    def _request_stub(self, resource_url, verb, query=None, payload=None):
        """
        Stub method for sending requests to the Cisco Spark API.

        :param resource_url: URI of the API method.
        :param verb: POST/GET/DELETE enum from ApiRequest.
        :param query: (Optional) Query parameters.
        :param payload: (Optional) Dictionary, bytes, or file-like object to send in the body to the API.
        :return: API response in JSON.
        """
        url = urlparse.urljoin(DEFAULT_API_URI, resource_url)

        if payload is not None:
            payload_json = json.dumps(payload)
        else:
            payload_json = None

        if query is not None:
            url_parts = list(urlparse.urlparse(url))
            curr_query = dict(urlparse.parse_qsl(url_parts[4]))
            curr_query.update(query)

            url_parts[4] = urlencode(curr_query)

            url = urlparse.urlunparse(url_parts)

        session = requests.Session()

        if verb == ApiRequest.post:
            response = session.request("POST", url, timeout=10, verify=False, data=payload_json,
                                       headers=self.default_header)
        elif verb == ApiRequest.get:
            response = session.request("GET", url, timeout=10, verify=False, data=payload_json,
                                       headers=self.default_header)
        else:
            raise ErrorSpark("Internal error")

        if response.status_code != 200:
            raise ErrorSpark("The following status code was returned: {}".format(response.status_code))

        return response.json()
