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
#       - None
#
#   WARNING:
#       Any use of these scripts and tools is at
#       your own risk. There is no guarantee that
#       they have been through thorough testing in a
#       comparable environment and we are not
#       responsible for any damage or data loss
#       incurred with their use.

import io
import json
import time
from enums import ApiRequest
from wrapper_apic import WrapperAPIC


class Library(object):
    """
    Library to bundle APIC-EM API requests and process responses to hand over to the CLI.
    """

    def __init__(self, apic_host, apic_user, apic_pw):
        """
        Create a new Library instance.

        :param apic_host: URL/Host to APIC-EM.
        :param apic_user: Username to access API.
        :param apic_pw: Password to access API.
        """
        self.apic = WrapperAPIC(apic_host, apic_user, apic_pw)

    def get_network_devices(self, max=None):
        """
        Fetch list of network devices from APIC-EM.

        :param max: Maximum number of returned devices.
        :return: List of network devices.
        """
        uri = "network-device"
        if max is not None:
            uri += "?limit=%s" % max

        res = self.apic.send_request(uri, ApiRequest.get)

        devices = []

        for device in res["response"]:
            device_info = {
                "Device Name": device["hostname"],
                "IP Address": str(device["managementIpAddress"]),
                "Up Time": str(device["upTime"]),
                "Last Updated": str(device["lastUpdated"])
            }
            devices.append(device_info)

        return devices

    def cli_network_devices(self, devices):
        """
        Format a list of network devices to print out on the CLI.

        :param devices: List of network devices from 'get_network_devices'.
        :return: String formatted to print devices on the CLI.
        """
        result_str = io.StringIO()

        labels = ["Device Name", "IP Address", "Up Time", "Last Updated"]
        lines = [len(e) * "=" for e in labels]

        print("{:<22}{:<22}{:<22}{:<22}".format(*labels), file=result_str)
        print("{:<22}{:<22}{:<22}{:<22}".format(*lines), file=result_str)

        for device in devices:
            print("{:<22}{:<22}{:<22}{:<22}".format(
                device['Device Name'], device['IP Address'], device['Up Time'],
                device['Last Updated']),
                file=result_str
            )

        res = result_str.getvalue()
        result_str.close()

        return res

    def spark_network_devices(self, devices):
        """
        Format a list of network devices to print out in a Spark room.

        :param devices: List of network devices from 'get_network_devices'.
        :return: String formatted to print devices in a Spark room.
        """
        result_str = io.StringIO()
        ctr = 1
        labels = ["Device Name", "IP Address", "Up Time", "Last Updated"]

        for device in devices:
            print(file=result_str)
            print("[Device #%i]" % ctr, file=result_str)

            for l in labels:
                print("{}: {}".format(l, device[l]), file=result_str)

            ctr += 1

        res = result_str.getvalue()
        result_str.close()

        return res

    def pathtrace(self, src, dst):
        """
        Perform a path trace.

        :param src: Source IP address.
        :param dst: Destination IP address.
        :return: String formatted to print path trace on the CLI and in a Spark room.
        """
        result_str = io.StringIO()

        uri = "flow-analysis"
        tmp_data = tmp_data = json.dumps({'sourceIP': src, 'destIP': dst})

        res = self.apic.send_request(uri, ApiRequest.post, tmp_data)

        flow_id = res['response']['flowAnalysisId']
        print("Wait for pathtrace to finish.")
        print()

        time.sleep(10)

        uri = 'flow-analysis/' + flow_id
        res = self.apic.send_request(uri, ApiRequest.get)

        path_nodes = res['response']['networkElementsInfo']

        nodes = []

        for index, node in enumerate(path_nodes):
            if index == 0:
                nodes.append("Source: {}".format(node.get('ip')))
            elif index == len(path_nodes) - 1:
                nodes.append("Destination: {}".format(node.get('ip')))
            else:
                nodes.append("({}) {}".format(index, node.get('name', '???')))

        if res['response']['request']['status'] == 'FAILED':
            print(res['response']['request']['failureReason'], file=result_str)
        else:
            for node in nodes:
                print(node, file=result_str)

        result = result_str.getvalue()
        result_str.close()

        return result
