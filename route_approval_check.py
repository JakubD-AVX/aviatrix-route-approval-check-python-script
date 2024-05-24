import requests                        # required by Rest API
# import warnings
# import contextlib
from urllib3.exceptions import InsecureRequestWarning # to disable SSL certificate check
import os
import urllib3
# import json                            # required by Content-type
from pathlib import Path               # required to read the env variables
from dotenv import load_dotenv         # required to read the env variables
# import re                              # regex
from datetime import datetime, timedelta # required to create a file name with a timestamp and also required to check today's and yesterday's date
# Libraries required to send an email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv # required to work with csv files
import sys # required to pass variable for transit gateway name from command line

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# The values for the following variables are taken from ".env" file located in the same directory/folder as this Python script.
# Please update your ".env" file before executing the script.
dotenv_path = Path('.env')             # path to .env file with crecentials
load_dotenv(dotenv_path=dotenv_path)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

controller_ip = os.getenv('CONTROLLER_IP')
controller_user = os.getenv('CONTROLLER_USER')
controller_password = os.getenv('CONTROLLER_PASSWORD')

api_url = f"https://{controller_ip}/v1/api"

# Email configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587
sender_email = os.getenv('SENDER_EMAIL')
receiver_email = os.getenv('RECEIVER_EMAIL')
password = os.getenv('EMAIL_PASSWORD')
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#--------------- API Call Class ---------------#
def api_call():
  get_cid = {'action': 'login', 'password' : controller_password, 'username' : controller_user }
  response_api_call = requests.get(api_url, get_cid, verify=False)
  return response_api_call.json()

#--------------- Get Approval Info ---------------#
def get_approval_info(get_cid, gateway_name):
  get_approval_info = {"action": "show_transit_learned_cidrs_approval_info", "CID": get_cid, "gateway_name": gateway_name}
  response_get_sapproval_info_call = requests.get(api_url, get_approval_info, verify=False)
  return response_get_sapproval_info_call.json()

#--------------- Check Transit Gateway Name ---------------#
def get_transit_gateway_list(get_cid, gateway_name):
  get_list_of_transit_gws = {"action": "list_aviatrix_transit_gateways", "CID": get_cid}
  response_get_list_of_tgws = requests.get(api_url, get_list_of_transit_gws, verify=False)
  trgw_list = response_get_list_of_tgws.json()
  trgw_list = trgw_list['results']
  number_of_trgws = len(trgw_list)
  for i in range(number_of_trgws):
    #print(trgw_list[i]['name'])
    transit_gw_names_list.append(trgw_list[i]['name'])
  if gateway_name in transit_gw_names_list:
    print("------------------------------------------------------------------------------------------------------------------------")
    print(f"The Transit Gateway '{gateway_name}' is present / exists.")
    print("------------------------------------------------------------------------------------------------------------------------")
    trgw_check = True
  else:
    print("------------------------------------------------------------------------------------------------------------------------")
    print(f"The Transit Gateway '{gateway_name}' is not present / does not exist.")
    print("------------------------------------------------------------------------------------------------------------------------")
    trgw_check = False
  return trgw_check

#--------------- Send E-mail ---------------#
def send_email(gateway_name, connection_name_email, total_cidrs_yesterday, total_cidrs_today, ra_cidrs_type):
  # Create the email
  message = MIMEMultipart()
  message['From'] = sender_email
  message['To'] = receiver_email

  # Email body
  if ra_cidrs_type == "approved_ra":
    message['Subject'] = "Aviatrix - Route Approval - Approved CIDRs changed notification"
    body1 = "Total number of approved CIDRs changed for gateway: " + gateway_name + " and connection: " + connection_name_email + ".\n\n"
    body2 = "Total number of approved CIDRs today: " + total_cidrs_today + ".\n"
    body3 = "Total number of approved CIDRs yesterday: " + total_cidrs_yesterday + "."
    body4 = "\n\nPlease check the files for appropriate dates and compare the differences."
  elif ra_cidrs_type == "pending_ra":
    message['Subject'] = "Aviatrix - Route Approval - Pending CIDRs changed notification"
    body1 = "Total number of pending CIDRs changed for gateway: " + gateway_name + " and connection: " + connection_name_email + ".\n\n"
    body2 = "Total number of pending CIDRs today: " + total_cidrs_today + ".\n"
    body3 = "Total number of pending CIDRs yesterday: " + total_cidrs_yesterday + "."
    body4 = "\n\nPlease check the files for appropriate dates and compare the differences."   
  
  body = body1 + body2 + body3 + body4
  message.attach(MIMEText(body, 'plain'))

  # Sending the email
  try:
    # Connect to the server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Secure the connection
    server.login(sender_email, password)
    
    # Send the email
    text = message.as_string()
    server.sendmail(sender_email, receiver_email, text)
    print("Email sent successfully!")
  except Exception as e:
    print(f"Error: {e}")
  finally:
    # Disconnect from the server
    server.quit()

#--------------- CSV File Creation ---------------#
def csv_file_creation(file_option, gateway_name, file_data, connection_name):
  # get current date and time
  #current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  current_datetime = datetime.now().strftime("%Y-%m-%d")
  # convert datetime obj to string
  str_current_datetime = str(current_datetime)
  folder = "files/"

  if file_option == "approved_cidr_list":
    csv_filename = gateway_name+"_connection_"+connection_name+"_approved_cidr_list_date_"+str_current_datetime+".csv"
    file_path = os.path.join(folder, csv_filename)
    file_header = "Approved CIDRs List:\n"     
    with open(file_path, 'w', encoding='UTF8', newline='') as f:
      f.writelines(file_header)
      f.writelines(file_data)
      print("File " +csv_filename+ " has been created")
  elif file_option == "total_approved_cidr":
    csv_filename = gateway_name+"_connection_"+connection_name+"_total_approved_cidr_date_"+str_current_datetime+".csv"
    file_path = os.path.join(folder, csv_filename)
    #file_header = "Total number of Approved CIDRs:\n"     
    with open(file_path, 'w', encoding='UTF8', newline='') as f:
      #f.writelines(file_header)
      f.writelines(file_data)
      print("File " +csv_filename+ " has been created")
  elif file_option == "pending_cidr_list":
    csv_filename = gateway_name+"_connection_"+connection_name+"_pending_cidr_list_date_"+str_current_datetime+".csv"
    file_path = os.path.join(folder, csv_filename)
    file_header = "Pending CIDRs List:\n"     
    with open(file_path, 'w', encoding='UTF8', newline='') as f:
      f.writelines(file_header)
      f.writelines(file_data)
      print("File " +csv_filename+ " has been created")
  elif file_option == "total_pending_cidr":
    csv_filename = gateway_name+"_connection_"+connection_name+"_total_pending_cidr_date_"+str_current_datetime+".csv"
    file_path = os.path.join(folder, csv_filename)
    #file_header = "Total number of Pending CIDRs:\n"     
    with open(file_path, 'w', encoding='UTF8', newline='') as f:
      #f.writelines(file_header)
      f.writelines(file_data)
      print("File " +csv_filename+ " has been created")

#--------------- Check Whether Total Number of Approved CIDRs changed ---------------#
def check_total_approved(gateway_name, list_of_connections, count_number_of_connections):
  # Check the current number of Approved CIDRs as of today and yesterday
  for conn_name in range(count_number_of_connections):
    print("------------------------------------------------------------------------------------------------------------------------")
    print("Connection name: ", list_of_connections[conn_name])
    # Define the file path
    file_path = "files/" + gateway_name + "_connection_" + list_of_connections[conn_name] + "_total_approved_cidr_date_" + formatted_current_date + ".csv"
    # Open the CSV file and read the number of total approved CIDRs
    # for Today
    with open(file_path, 'r') as csvfile:
      csvreader = csv.reader(csvfile)
      for row in csvreader:
        # Assuming the number is in the first cell of the first row
        today_approved_number = row[0]
        print("The number of approved CIDRs in the CSV file for TODAY:", today_approved_number)
        break  # Exit after reading the first row

    # for Yesterday
    file_path = "files/" + gateway_name + "_connection_" + list_of_connections[conn_name] + "_total_approved_cidr_date_" + formatted_yesterday_date + ".csv"
    # Check whether the file for yesterday exists
    if os.path.exists(file_path):
      # Open the CSV file and read the number of total approved CIDRs
      with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
          # Assuming the number is in the first cell of the first row
          yesterday_approved_number = row[0]
          print("The number of approved CIDRs in the CSV file for YESTERDAY:", yesterday_approved_number)
          break  # Exit after reading the first row
    else:
      print("File from yesterday " + file_path + " for approved CIDRs does not exist.")

    # Checking for each connection whether the total approved CIDR changed compared to yesterday 
    if os.path.exists(file_path):
      if today_approved_number > yesterday_approved_number:
        print("Total approved CIDR number is greater than yesterday for connection: ", list_of_connections[conn_name])
        send_email(gateway_name, list_of_connections[conn_name], yesterday_approved_number, today_approved_number, "approved_ra")
      elif today_approved_number < yesterday_approved_number:
        print("Total approved CIDR number is lower than yesterday for connection: ", list_of_connections[conn_name])
        send_email(gateway_name, list_of_connections[conn_name], yesterday_approved_number, today_approved_number, "approved_ra")
      else:
        print("Total approved CIDR number has not changed for connection: ", list_of_connections[conn_name])

#--------------- Check Whether Total Number of Pending CIDRs changed ---------------#
def check_total_pending(gateway_name, list_of_connections, count_number_of_connections):
  # Check the current number of Pending CIDRs as of today and yesterday
  for conn_name in range(count_number_of_connections):
    print("------------------------------------------------------------------------------------------------------------------------")
    print("Connection name: ", list_of_connections[conn_name])
    # Define the file path
    file_path = "files/" + gateway_name + "_connection_" + list_of_connections[conn_name] + "_total_pending_cidr_date_" + formatted_current_date + ".csv"
    # Open the CSV file and read the number of total pending CIDRs
    # for Today
    with open(file_path, 'r') as csvfile:
      csvreader = csv.reader(csvfile)
      for row in csvreader:
        # Assuming the number is in the first cell of the first row
        today_pending_number = row[0]
        print("The number of pending CIDRs in the CSV file for TODAY:", today_pending_number)
        break  # Exit after reading the first row

    # for Yesterday
    file_path = "files/" + gateway_name + "_connection_" + list_of_connections[conn_name] + "_total_pending_cidr_date_" + formatted_yesterday_date + ".csv"
    # Check whether the file for yesterday exists
    if os.path.exists(file_path):
      # Open the CSV file and read the number of total pending CIDRs
      with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
          # Assuming the number is in the first cell of the first row
          yesterday_pending_number = row[0]
          print("The number of pending CIDRs in the CSV file for YESTERDAY:", yesterday_pending_number)
          break  # Exit after reading the first row
    else:
      print("File from yesterday " + file_path + " for pending CIDRs does not exist.")

    # Checking for each connection whether the total approved CIDR changed compared to yesterday
    if os.path.exists(file_path):
      if today_pending_number > yesterday_pending_number:
        print("Total pending CIDR number is greater than yesterday for connection: ", list_of_connections[conn_name])
        send_email(gateway_name, list_of_connections[conn_name], yesterday_pending_number, today_pending_number, "pending_ra")
      elif today_pending_number < yesterday_pending_number:
        print("Total pending CIDR number is lower than yesterday for connection: ", list_of_connections[conn_name])
        send_email(gateway_name, list_of_connections[conn_name], yesterday_pending_number, today_pending_number, "pending_ra")
      else:
        print("Total pending CIDR number has not changed for connection: ", list_of_connections[conn_name])

##########################################################################################################################################################################################################
#--------------- Main Code: ---------------#

# Date operations
# Getting current date
current_datetime = datetime.now()
formatted_current_date = current_datetime.strftime("%Y-%m-%d")
#print(formatted_current_date)
# Getting yesterday's date
yesterday_date = current_datetime - timedelta(days=1)
formatted_yesterday_date = yesterday_date.strftime("%Y-%m-%d")
#print(formatted_yesterday_date)

# Check if an argument for transit gateway name is provided
if len(sys.argv) != 2:
  print("Please provide the transit gateway name. Example of usage: python script.py <value>")
  sys.exit(1)

  # Get the value from the command-line arguments
#gateway_name = "transit-90"
gateway_name = sys.argv[1]

# Execute an API call to the Controller to get CID
get_cid = api_call()['CID']

# Check whether the Transit Gateway with provided name exists
transit_gw_names_list = []
try:
  trgw_list = get_transit_gateway_list(get_cid, gateway_name)
except:
  print("The provided Transit Gateway name was incorrect. Exiting...")
  sys.exit(1)

# Get the details of the Transit Gateways Route Approval
if trgw_list == True:
  get_approval_info = get_approval_info(get_cid, gateway_name)

  # Count the number of connections
  list_of_connections = []
  number_of_connections = get_approval_info['results']['connection_learned_cidrs_approval_info']
  count_number_of_connections = len(number_of_connections)
  # For loop is required to iterate every single connection present on a selected Transit Gateway and to populate the
  for connection in range(count_number_of_connections):
    approved = get_approval_info['results']['connection_learned_cidrs_approval_info'][connection]['conn_approved_learned_cidrs']
    pending = get_approval_info['results']['connection_learned_cidrs_approval_info'][connection]['conn_pending_learned_cidrs']
    connection_name = get_approval_info['results']['connection_learned_cidrs_approval_info'][connection]['conn_name']
    list_of_connections.append(connection_name)

    #print(connection_name)
    #print(approved)
    # Some basic modifications to get a list of approved and pending CIDRs in the desired way.. I know.. it could be done probably much simpler... but anyway it works.. :)
    approved_mod = str(approved)
    approved_mod = approved_mod.replace("[", "")
    approved_mod = approved_mod.replace("]", "")
    approved_mod = approved_mod.replace("'", "")
    approved_mod = approved_mod.replace(" ", "")
    approved_mod = approved_mod.replace(",", "\n")
    #approved_mod = approved_mod + "\n"
    #print("String approved: ", approved_mod) 
    #print(pending)
    pending_mod = str(pending)
    pending_mod = pending_mod.replace("[", "")
    pending_mod = pending_mod.replace("]", "")
    pending_mod = pending_mod.replace("'", "")
    pending_mod = pending_mod.replace(" ", "")
    pending_mod = pending_mod.replace(",", "\n")

    approved_length = len(approved)
    pending_length = len(pending)

    #print(approved_length)
    #print(pending_length)

    # Create new files:
    # - one file with a full list of Approved CIDRs (one file per connection)
    # - one file with a total number of Approved CIDRs (one file per connection)
    # - one file with a full list of Pending CIDRs (one file per connection)
    # - one file with a total number of Pending CIDRs (one file per connection)
    csv_file_creation("approved_cidr_list", gateway_name, approved_mod, connection_name)
    csv_file_creation("total_approved_cidr", gateway_name, str(approved_length), connection_name)
    csv_file_creation("pending_cidr_list", gateway_name, pending_mod, connection_name)
    csv_file_creation("total_pending_cidr", gateway_name, str(pending_length), connection_name)

  # Check whether the total number of Approved CIDRs changed (compare today and yesterday count)
  # Check is executed outside of FOR loop but still inside IF statement
  #print(list_of_connections)
  check_total_approved(gateway_name, list_of_connections, count_number_of_connections)
  # Check whether the total number of Pending CIDRs changed (compare today and yesterday count)
  # Check is executed outside of FOR loop but still inside IF statement
  check_total_pending(gateway_name, list_of_connections, count_number_of_connections)
