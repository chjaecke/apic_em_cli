#!/usr/bin/env python
#
#   apic_cmd
#       v0.1
#
#   Christian Jaeckel (chjaecke@cisco.com)
#       October 2016
#
#   Main class to enter APIC-EM CLI.
#
#   REQUIREMENTS:
#       - requests
#       - cmd2
#
#   WARNING:
#       Any use of these scripts and tools is at
#       your own risk. There is no guarantee that
#       they have been through thorough testing in a
#       comparable environment and we are not
#       responsible for any damage or data loss
#       incurred with their use.

import os
import re
from cmd2 import Cmd, make_option, options
from library import Library
from wrapper_apic import ErrorAPIC
from wrapper_spark import WrapperSpark


class CmdAPIC(Cmd):
    prompt = 'apic_cmd# '
    intro = "Type 'help' to get a list of commands"

    @options([
        make_option('-m', '--max', type="int", help="Return only [n] devices"),
        make_option('-s', '--spark', action="store_true", help="Send messages to Spark room")
    ])
    def do_devices(self, args, opts=None):
        """
        Shows all network devices connected to the APIC-EM.

        Syntax: network_devices [options]
        Example:
            devices
            devices --spark --max=3
            devices -s -m 3
        """
        if opts.spark and not self.spark.validate_token():
            print("Verify that a Spark user token is set via 'sparkuser' and a room is selected via 'sparkrooms'.")
            return

        devices = self.lib.get_network_devices(max=opts.max)

        print(self.lib.cli_network_devices(devices))

        if opts.spark:
            self.spark.post_message(self.room, text=self.lib.spark_network_devices(devices))

        return

    @options([
        make_option('-i', '--teamid', type="int", help="Select only rooms from this team"),
        make_option('-m', '--max', type="int", help="Return only [n] rooms"),
        make_option('-t', '--type', type="str", help="Return only 'group' or 'direct' rooms")
    ])
    def do_sparkrooms(self, args, opts=None):
        """
         Lists all rooms that are connected to the current Spark user. You can also select a new room to post to Spark.

         Syntax: sparkrooms [options]
         Examples:
             sparkrooms
             sparkrooms -i MyTeamId -m 4 -t group
             sparkrooms --type=direct
             sparkrooms -t direct --max=2
        """
        if not self.spark.validate_token():
            print("Please set your Spark user token first with the 'sparkuser' command.")
            return

        if opts.teamid:
            team_id = str(opts.teamid)
        else:
            team_id = None

        if opts.max:
            rmax = int(opts.max)
        else:
            rmax = None

        if opts.type:
            rtype = str(opts.type)
        else:
            rtype = None

        req = self.spark.get_rooms(team_id, rmax, rtype)

        rooms = []

        for index, room in enumerate(req["items"], 1):
            room_line = {"index": index, "name": room["title"], "id": room["id"], "selected": ""}
            if self.room == room_line["id"]:
                room_line["selected"] = "XXXXXXXX"
            rooms.append(room_line)

        if self.room is not None:
            curr_room = self.spark.get_room(self.room)["title"]
        else:
            curr_room = "none"

        print("Numbers of rooms: {}".format(len(rooms)))
        print("Currently selected room: {}".format(curr_room))
        print()
        labels = ["Index", "Selected", "Room Name", "Room ID"]
        lines = [len(e) * "=" for e in labels]
        print("{:<8}{:<11}{:<22}{:<22}".format(*labels))
        print("{:<8}{:<11}{:<22}{:<22}".format(*lines))

        for room in rooms:
            # Fix encoding error of Windows CMD.
            room["name"] = str(room["name"]).encode('cp850','replace').decode('cp850')
            print("{:<8}{:<11}{:<22}{:<22}".format(room["index"], room["selected"], room["name"], room["id"]))

        print()
        response = self.query_yes_no("Do you want to select a new Spark room?")

        if response:

            index = int(input("Index of new room: ")) - 1

            if index < 0 or index > len(rooms) - 1:
                print("Please select a valid index from the list above.")
                return

            self.room = rooms[index]["id"]
            print("New room set to: {}".format(rooms[index]["name"]))

    def do_sparkuser(self, args):
        """
         Lists the current Spark user. You can also select a new user token to post to Spark.

         Syntax: sparkuser
         Example:
             sparkuser
        """
        curr_user = self.spark.get_people_me()

        if curr_user is not None:
            print("Spark Username: {}".format(curr_user["displayName"]))
            print("Spark User Email: {}".format(curr_user["emails"][0]))

        else:
            print("No valid Spark user token is set.")

        response = self.query_yes_no("Do you want to set a new Spark user token?")

        if response:
            token = input("New Spark Token: ")

            valid = self.spark.set_new_token(token)

            if valid:
                curr_user = self.spark.get_people_me()
                print("Spark Username: {}".format(curr_user["displayName"]))
                print("Spark User Email: {}".format(curr_user["emails"][0]))
            else:
                print("New Spark user token is not valid.")

    @options([
        make_option('-s', '--spark', action="store_true", help="Send messages to Spark room")
    ])
    def do_pathtrace(self, args, opts=None):
        """
         Performs a path trace between a source and a destination IP address.

         Syntax: pathtrace [options]
         Examples:
             pathtrace
             pathtrace -s
             pathtrace --spark
        """
        if opts.spark and not self.spark.validate_token():
            print("Verfiy that a Spark user token is set via 'sparkuser' and a room is selected via 'sparkrooms'.")
            return

        ip = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

        valid = False
        while not valid:

            src = input("Source IP: ")
            if not ip.match(src):
                print("Please enter a valid source IP address.")
            else:
                valid = True

        valid = False
        while not valid:

            dst = input("Destination IP: ")
            if not ip.match(dst):
                print("Please enter a valid destination IP address.")
            else:
                valid = True

        result_str = self.lib.pathtrace(src, dst)

        print(result_str)

        if opts.spark:
            self.spark.post_message(self.room, text=result_str)

    def precmd(self, line):
        print()
        return line

    def postcmd(self, stop, line):
        print()
        return False

    def query_yes_no(self, question, default="yes"):
        """
        Ask a yes/no question via input() and return their answer. 'question' is a string that is presented to the user.
        'default' is the presumed answer if the user just hits <Enter>. It must be 'yes' (the default), 'no' or None
        (meaning an answer is required of the user). The 'answer' return value is True for 'yes' or False for 'no'.
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("Invalid default answer: '%s'" % default)

        while True:
            print(question + prompt)
            choice = input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                print("Please respond with 'yes'/'y' or 'no'/'n'.\n")

    def preloop(self):

        print("##########################################")
        print("####                                  ####")
        print("####  APIC-EM CLI                     ####")
        print("####                                  ####")
        print("####  Version: 0.1                    ####")
        print("####  Date: 2016-10-07                ####")
        print("####  Developer: Christian Jaeckel    ####")
        print("####  Email: chjaecke@cisco.com       ####")
        print("####                                  ####")
        print("##########################################")
        print("")

        connected = False

        while not connected:
            print("Please enter your APIC-EM credentials.")
            apic_host = input("Host: ")
            apic_user = input("User: ")
            apic_pw = input("Password: ")

            try:
                self.lib = Library(apic_host, apic_user, apic_pw)
                self.spark = WrapperSpark(None)
                self.room = None

                connected = True
            except ErrorAPIC as e:
                print(str(e))
            finally:
                print()

        os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    CmdAPIC().cmdloop()
