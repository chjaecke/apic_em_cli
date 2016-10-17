APIC-EM CLI
===========

#### This projects implements a command-line interface to interact with the APIC-EM API. Optionally, all output of the CLI commands can also be posted in a Cisco Spark room. The idea of these scripts is to demonstrate the capabilities of the APIC-EM as well as the Cisco Spark API and how they can be used together to facilitate collaboration within distributed teams. 


## Table of Contents
  
  * [Requirements](#requirements)
  * [Installation](#installation)
  * [Getting Started](#getting-started)
  * [Descriptions](#descriptions)
  * [Contributing](#contributing)
  * [Changelog](#changelog)

  
# Requirements
All of these scripts habe been tested with [Python 3.5](https://www.python.org/) on Windows. Running on other platforms may require modification of the code.

You require the following Python modules:
* [requests](http://docs.python-requests.org/en/master/)
* [cmd2](https://pythonhosted.org/cmd2/)


# Installation

1. Download and install the most recent and stable version of Python 3:
https://www.python.org/downloads/

2. Use pip to install the `requests` and `cmd2` module for Python:
https://docs.python.org/3.6/installing/

3. Execute `apic_cmd.py`. Make sure that all Python files contained in this project are stored in the same folder.


# Getting Started

## Login
Enter your login credentials to access the CLI that is connected to your APIC-EM. Host information should be in the following format: `http(s)://my_apic_ip.com/`

You will be transfered to the CLI screen if the login is successful.


## Help
The `help` command shows you a list of commands that are implemented in the CLI. 
APIC-EM specific commands are `devices`, `pathtrace`, `sparkuser`, and `sparkrooms`. 

To get more information about each command, you can enter `help <cmd>` or `<cmd> -h`, e.g. `help devices`.
This help command shows you also all parameters that are required to execute a certain command.

Example:
```
apic_cmd# help devices


        Shows all network devices connected to the APIC-EM.

        Syntax: network_devices [options]
        Example:
            devices
            devices --spark --max=3
            devices -s -m 3

Usage: devices [options] arg

Options:
  -h, --help         show this help message and exit
  -m MAX, --max=MAX  Return only [n] devices
  -s, --spark        Send messages to Spark room
```

## Devices
The `devices` command lists all network devices that are connected to the APIC-EM. With the `max` option, you can limit results to certain number of devices.

Example: `apic_cmd# devices` | `apic_cmd# devices --max=3` | `apic_cmd# devices -m 5`

```
apic_cmd# devices

Device Name           IP Address            Up Time               Last Updated
===========           ==========            =======               ============
AP7081.059f.19ca      55.1.1.3              None                  2016-10-17 14:05:36
Branch-Access1        207.1.10.1            474 days, 6:22:19.43  2016-10-17 14:05:37
Branch-Router1        207.3.1.1             474 days, 6:00:26.48  2016-10-17 14:05:36
...					  ...					...					  ...
```


## Pathtrace
The `pathtrace` command performas a pathtrace from a source IP to a destination IP. Please note that 
the pathtrace requires a few seconds to finish. 

Example: 
```
apic_cmd# pathtrace

Source IP: 65.1.1.46
Destination IP: 207.1.10.20
Wait for pathtrace to finish.

Source: 65.1.1.46
(1) AP1
(2) CAMPUS-Access1
(3) CAMPUS-Dist1
(4) Campus-WLC-5508
(5) CAMPUS-Dist1
(6) CAMPUS-Core1
(7) CAMPUS-Router2
(8) UNKNOWN
(9) Branch-Router1
(10) Branch-Access1
Destination: 207.1.10.20
```

## Connecting to Spark
You can connect the APIC-EM CLI to your Spark user account and post the output of the CLI commands to a Spark room.
To do this, first you have to set your Spark user token and select a room where the output should be forwarded to.

### Get Spark User Token
Log in to https://developer.ciscospark.com/ and get your Spark user token. Click on your profile icon in the top right of the corner to view your token. DO NOT SHARE THIS TOKEN WITH ANYBODY ELSE!

### Set Spark User Token
Run the `sparkuser` command, enter yes to set a new token and paste your user token. If successful, the `sparkuser` command
should show your username and email attached to your account.

Example: 
```
apic_cmd# sparkuser

No valid Spark user token is set.
Do you want to set a new Spark user token? [Y/n]
y
New Spark Token: ***
Spark Username: John Doe
Spark User Email: johndoe@example.com

apic_cmd# sparkuser

Spark Username: John Doe
Spark User Email: johndoe@example.com
Do you want to set a new Spark user token? [Y/n]
n
```

### Set Spark Room
Run the `sparkrooms` command to select a room to which the CLI output should be forwarded. Please note that you have to set the Spark user token first. The command shows you a list of all rooms connected to your account as well as the currently selected room to forward the CLI output to. You can next choose another room by setting a new room index.

```
apic_cmd# sparkrooms

Numbers of rooms: 4
Currently selected room: Test Room

Index   Selected   Room Name             Room ID
=====   ========   =========             =======
1                  Project Foo           Y2lzY29zcGF***
2                  Alpha Beta          	 Y2lzY29zcGF***
3                  Jane Doe				 Y2lzY29zcGF***
4       XXXXXXXX   Test Room             Y2lzY29zcGF***

Do you want to select a new Spark room? [Y/n]
y
Index of new room: 1
New room set to: Project Foo
```

### Post to Spark
After setting the user token and selecting a Spark room, you can use the -s or --spark option of the APIC-EM commands to post the output to Spark.

Example: `devices -s` | `pathtrace --spark`


# Descriptions


| Script   | Description    |
|----------|----------------|
| apic_cmd.py  | Main file to start the APIC-EM CLI. |
| wrapper_apic.py | Wrapper class to facilitate access to the APIC-EM API through REST. This class can be easily reused in other projects as well. |
| wrapper_spark.py | Wrapper class to facilitate access to the Cisco Spark API through REST. This class can be easily reused in other projects as well. |
| library.py | Some outsourced methods to refactor interaction between the CLI and the APIC-EM API. |
| enums.py | Enumerations that are used in this project. |


# Contributing
All users are strongly encouraged to contribute patches, new scripts or ideas.
Please submit a pull request with your contribution and we will review, provide
feedback to you and if everything looks good, we'll merge it!


# Changelog

## v0.1 (2016-10-07)

Initial release
