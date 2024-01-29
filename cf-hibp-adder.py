import requests
import configparser
import json

# Function to fetch the Zone ID
def fetch_zone_id(domain_name, email, key):
    url = f"https://api.cloudflare.com/client/v4/zones?name={domain_name}"
    headers = {"X-Auth-Email": email, "X-Auth-Key": key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        zone_data = response.json()
        if zone_data['result']:
            return zone_data['result'][0]['id']
    return None

# Function to add a DNS record
def add_dns_record(zone_id, payload, email, key):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {"Content-Type": "application/json", "X-Auth-Email": email, "X-Auth-Key": key}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()['result']
        print(f"Successfully added DNS record. Identifier: {result['id']}, Zone Identifier: {result['zone_id']}")
        return result['id']
    else:
        print(f"Failed to add DNS record: {response.text}")
        return None

# Function to delete a DNS record
def delete_dns_record(zone_id, record_id, email, key):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {"X-Auth-Email": email, "X-Auth-Key": key}
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        print("Successfully deleted DNS record.")
    else:
        print(f"Failed to delete DNS record: {response.text}")

# Read the config file for API credentials
config = configparser.ConfigParser()
with open("config.ini") as f:
    config.read_file(f)

auth_email = config["Cloudflare"]["email"]
auth_key = config["Cloudflare"]["key"]

# Get the domain name and TXT content from the user
domain_name = input("\n--> Enter the domain name: ")
txt_content = input("\n--> Enter the TXT record content: ")

# Fetch the Zone ID
zone_id = fetch_zone_id(domain_name, auth_email, auth_key)

if zone_id is None:
    print("Could not fetch Zone ID. Exiting.")
else:
    # Create the TXT record
    txt_record = {
        "type": "TXT",
        "name": domain_name,
        "content": txt_content,
        "ttl": 1
    }
    record_id = add_dns_record(zone_id, txt_record, auth_email, auth_key)

    # Ask to delete the DNS record
    if record_id:
        while True:
            print("\n✅ TXT record has been added. Verify on HIBP website.")
            delete_record = input("\n--> Do you want to delete this TXT record? (y/n): ")
            if delete_record.lower() == 'y':
                delete_dns_record(zone_id, record_id, auth_email, auth_key)
                break
            elif delete_record.lower() == 'n':
                print("TXT record will not be deleted.")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
