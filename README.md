# Route Approval Check script
## Introduction
There is an Aviatrix feature called "BGP Route Approval" that could be enabled on Aviatrix Gateways ([Aviatrix Docs - BGP Route Approval](https://docs.aviatrix.com/documentation/latest/building-your-network/transit-bgp-route-approval.html?expand=true)).
The Route Approval feature maintains two lists of CIDRs: "Approved CIDR" list and "Pending CIDR" list:
- "Pending CIDR" list is a list of CIDRs that remote BGP Peer advertises to us but we do not have them installed/accepted on Aviatrix Gateway
- "Approved CIDR" list is a list of CIDRs that remote BGP Perr advertises to us nad we have accepted/installed on Aviatrix Gateway.

The purpose of the script is to validate whether the "Approved CIDR" list and the "Pending CIDR" list changed between today and tomorrow. 
The knowledge about whether those lists changed could be crucial if someone wants to monitor whether: 
a) there are new CIDRs that have been approved, 
b) there are some previously approved CIDRs that have been removed, 
c) there are new pending CIDRs, 
d) some pending CIDRs have been removed.

The script can be scheduled to be run every day. During the script execution the following files are created for each BGP connection:
- *transit-gw-name*_connection_*connection-name*_approved_cidr_list_date_*yyyy-mm-dd*.csv
  The purpose of the file is to keep a list of all approved CIDRs.
- *transit-gw-name*_connection_*connection-name*_pending_cidr_list_date_*yyyy-mm-dd*.csv
  The purpose of the file is to keep a list of all pending CIDRs.
- *transit-gw-name*_connection_*connection-name*_total_approved_cidr_date_*yyyy-mm-dd*.csv
  The purpose of the file is to keep the total number of approved CIDRs.
- *transit-gw-name*_connection_*connection-name*_total_pending_cidr_date_*yyyy-mm-dd*.csv
  The purpose of the file is to keep the total number of approved CIDRs.
By default, script generates and keeps these files in "/files/" folder.
## Requirements
The script uses .env file for keeping the information required to log in to the Aviatrix Controller and to send the email notifications.
The following variables must be updated by you before executing the script.
The content of .env file:
'''# Aviatrix Controller
CONTROLLER_IP = "IP-of-your-Aviatrix-Controller"
CONTROLLER_USER = "your-Aviatrix-Controller-Username"
CONTROLLER_PASSWORD = "your-Aviatrix-Controller-Username-Password"

# Email details
SENDER_EMAIL = "your-sender-email-address"
EMAIL_PASSWORD = "your-email-application-password"
RECEIVER_EMAIL = "your-receiver-email-address"'''

Please keep in mind that scrip only works for **Aviatrix Transit Gateways** that have "BGP Route Approval" feature enabled in **Connection-Mode**.
## Usage Example
Please be ware that you must pass the name of the Aviatrix Transit Gateway when executing the script.
Example:
'''python3 route_approval_check.py  *transit-70*'''
The transit-70 is a name of my Transit Gateway.
