#!/usr/bin/env python
#
#   enums
#       v0.1
#
#   Christian Jaeckel (chjaecke@cisco.com)
#       October 2016
#
#   This class provides some enumerations that are
#   used for this project.
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

from enum import Enum


class ApiEncoding(Enum):
    json = 1
    xml = 2


class ApiRequest(Enum):
    post = 1
    get = 2
    delete = 3
