# Route Approval Check script
## Introduction
There is an Aviatrix feature called "BGP Route Approval" that could be enabled on Aviatrix Gateways ([Aviatrix Docs - BGP Route Approval](https://docs.aviatrix.com/documentation/latest/building-your-network/transit-bgp-route-approval.html?expand=true)).
The Route Approval feature maintains two lists of CIDRs: "Approved CIDR" list and "Pending CIDR" list:
- "Pending CIDR" list is a list of CIDRs that remote BGP Peer advertises to us but we do not have them installed/accepted on Aviatrix Gateway yet,
- "Approved CIDR" list is a list of CIDRs that remote BGP Peer advertises to us nad we have accepted/installed on Aviatrix Gateway.

The purpose of the script is to validate whether the "Approved CIDR" list and the "Pending CIDR" list changed between today and tomorrow. 
The knowledge about whether those lists changed could be crucial if someone wants to monitor whether: 
- there are new CIDRs that have been approved, 
- there are some previously approved CIDRs that have been removed, 
- there are new pending CIDRs advertised from BGP Peer, 
- some pending CIDRs have been removed.

The script can be scheduled to be run every day. During the script execution the following 4 files are created for each BGP connection:
- transit-gw-name_connection_connection-name_approved_cidr_list_date_yyyy-mm-dd.csv
  The purpose of the file is to keep a list of all approved CIDRs.
- transit-gw-name_connection_connection-name_pending_cidr_list_date_yyyy-mm-dd.csv
  The purpose of the file is to keep a list of all pending CIDRs.
- transit-gw-name_connection_connection-name_total_approved_cidr_date_yyyy-mm-dd.csv
  The purpose of the file is to keep the total number of approved CIDRs.
- transit-gw-name_connection_connection-name_total_pending_cidr_date_yyyy-mm-dd.csv
  The purpose of the file is to keep the total number of approved CIDRs.

By default, script generates and keeps these files in "/files/" folder.
## Requirements
Please keep in mind that script only works for **Aviatrix Transit Gateways** that have "BGP Route Approval" feature enabled in **Connection-Mode**.
The script uses .env file for keeping the information required to log in to the Aviatrix Controller and to send the email notifications.
The following variables must be updated by you before executing the script.
The content of .env file:

```
# Aviatrix Controller
CONTROLLER_IP = "IP-of-your-Aviatrix-Controller"
CONTROLLER_USER = "your-Aviatrix-Controller-Username"
CONTROLLER_PASSWORD = "your-Aviatrix-Controller-Username-Password"

# Email details
SENDER_EMAIL = "your-sender-email-address"
EMAIL_PASSWORD = "your-email-application-password"
RECEIVER_EMAIL = "your-receiver-email-address"
```

## Usage Example
Please be ware that you must pass the name of the Aviatrix Transit Gateway when executing the script.
Example:
```
$ python3 route_approval_check.py transit-70
```
The *transit-70* is a name of my Transit Gateway.

## Output
Besides the files that are created by the script, the script also generates some outputs and sends notification e-mails.
The script generates the outputs that show the following pieces of information:
- name of the Aviatrix Transit Gateway that has been checked
- name of each connection
- for each connection: number of approved CIDRs for today and yesterday
- for each connection: number of pending CIDRs for today and yesterday

In case the number of CIDRs (either approved or pending) between today and yesterday is not equal -> script sends a notification e-mail(s).
### Executing the script for the first time
Once the script is executed for the first time you do not have any files generated a day before.
Therefore script cannot compare the data gathered today against the data from yesterday.
However, the script will still generate the files for today.
### Executing the script for the second+ time
Example of the output of executing the script for the existing Transit Gateway (in case the data/files for yesterday exist):
```
$ python3 route_approval_check.py  transit-90
------------------------------------------------------------------------------------------------------------------------
The Transit Gateway 'transit-90' is present / exists.
------------------------------------------------------------------------------------------------------------------------
File transit-90_connection_t90-t80_approved_cidr_list_date_2024-05-24.csv has been created
File transit-90_connection_t90-t80_total_approved_cidr_date_2024-05-24.csv has been created
File transit-90_connection_t90-t80_pending_cidr_list_date_2024-05-24.csv has been created
File transit-90_connection_t90-t80_total_pending_cidr_date_2024-05-24.csv has been created
File transit-90_connection_fake_approved_cidr_list_date_2024-05-24.csv has been created
File transit-90_connection_fake_total_approved_cidr_date_2024-05-24.csv has been created
File transit-90_connection_fake_pending_cidr_list_date_2024-05-24.csv has been created
File transit-90_connection_fake_total_pending_cidr_date_2024-05-24.csv has been created
File transit-90_connection_fake2_approved_cidr_list_date_2024-05-24.csv has been created
File transit-90_connection_fake2_total_approved_cidr_date_2024-05-24.csv has been created
File transit-90_connection_fake2_pending_cidr_list_date_2024-05-24.csv has been created
File transit-90_connection_fake2_total_pending_cidr_date_2024-05-24.csv has been created
File transit-90_connection_tr90-tr70_approved_cidr_list_date_2024-05-24.csv has been created
File transit-90_connection_tr90-tr70_total_approved_cidr_date_2024-05-24.csv has been created
File transit-90_connection_tr90-tr70_pending_cidr_list_date_2024-05-24.csv has been created
File transit-90_connection_tr90-tr70_total_pending_cidr_date_2024-05-24.csv has been created
------------------------------------------------------------------------------------------------------------------------
Connection name:  t90-t80
The number of approved CIDRs in the CSV file for TODAY: 1
The number of approved CIDRs in the CSV file for YESTERDAY: 2
Total approved CIDR number is lower than yesterday for connection:  t90-t80
Email sent successfully!
------------------------------------------------------------------------------------------------------------------------
Connection name:  fake
The number of approved CIDRs in the CSV file for TODAY: 1
The number of approved CIDRs in the CSV file for YESTERDAY: 1
Total approved CIDR number has not changed for connection:  fake
------------------------------------------------------------------------------------------------------------------------
Connection name:  fake2
The number of approved CIDRs in the CSV file for TODAY: 1
The number of approved CIDRs in the CSV file for YESTERDAY: 1
Total approved CIDR number has not changed for connection:  fake2
------------------------------------------------------------------------------------------------------------------------
Connection name:  tr90-tr70
The number of approved CIDRs in the CSV file for TODAY: 3
The number of approved CIDRs in the CSV file for YESTERDAY: 1
Total approved CIDR number is greater than yesterday for connection:  tr90-tr70
Email sent successfully!
------------------------------------------------------------------------------------------------------------------------
Connection name:  t90-t80
The number of pending CIDRs in the CSV file for TODAY: 2
The number of pending CIDRs in the CSV file for YESTERDAY: 1
Total pending CIDR number is greater than yesterday for connection:  t90-t80
Email sent successfully!
------------------------------------------------------------------------------------------------------------------------
Connection name:  fake
The number of pending CIDRs in the CSV file for TODAY: 0
The number of pending CIDRs in the CSV file for YESTERDAY: 0
Total pending CIDR number has not changed for connection:  fake
------------------------------------------------------------------------------------------------------------------------
Connection name:  fake2
The number of pending CIDRs in the CSV file for TODAY: 0
The number of pending CIDRs in the CSV file for YESTERDAY: 0
Total pending CIDR number has not changed for connection:  fake2
------------------------------------------------------------------------------------------------------------------------
Connection name:  tr90-tr70
The number of pending CIDRs in the CSV file for TODAY: 0
The number of pending CIDRs in the CSV file for YESTERDAY: 2
Total pending CIDR number is lower than yesterday for connection:  tr90-tr70
Email sent successfully!
```
### Executing the script for not existing Transit Gateway
Example of the output of executing the script for the non-existing Transit Gateway:
```
$ python3 route_approval_check.py  transit-1234
------------------------------------------------------------------------------------------------------------------------
The Transit Gateway 'transit-1234' is not present / does not exist.
------------------------------------------------------------------------------------------------------------------------
```
### E-mail notifications
In case the number of CIDRs (either approved or pending) between today and yesterday is not equal -> script sends a notification e-mail(s).
Example of the e-mail message (e-mail title: Aviatrix - Route Approval - Pending CIDRs changed notification):
```
Total number of pending CIDRs changed for gateway: transit-90 and connection: t90-t80.

Total number of pending CIDRs today: 2.
Total number of pending CIDRs yesterday: 1.

Please check the files for appropriate dates and compare the differences.
```
