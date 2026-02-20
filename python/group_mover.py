
from sear import sear

# Import argparse for command line flags and arguments
import argparse

# Import date time, for log names
from datetime import datetime

# Import the module for file management
from pathlib import Path

# Get date-time for log
date_time = datetime.now().strftime("group_mover_log-%d-%m-%Y-t-%H-%M")

parser = argparse.ArgumentParser(
    prog='Group mover',
    description=
    'Moves users from one group over to another and empties the original group'
    ,
)

log_entries = []

# Write to log function
def write_to_log_cache(log_entry: str):
    """Caches log entries in memory"""
    log_entries.append(log_entry)

def write_cache_to_disk():
    """Writes the cached log entries to disk"""

    # Log folder path
    log_folder_path_string = "./logs"
    log_folder_path = Path(log_folder_path_string)
    if not log_folder_path.exists():
        log_folder_path.mkdir()

    # Create log file for current session
    log_path = Path(f"{log_folder_path_string}/{date_time}")
    log_path.touch()

    for entry in log_entries:
        with log_path.open("a") as f:
            f.write(f"{entry}\n")

# Commandline flags and arguments
parser.add_argument('-d', '--destination')
parser.add_argument('-g', '--group')

args = parser.parse_args()

# The group users are being moved from
group = str(args.group) or None

# Destination group
destination_group = str(args.destination) or None

# Gets RACF users in the group
def get_racf_users(group: str) -> list[str]:
    """Gets RACF users connected to a group"""
    user_list = []
    raw_user_list = []

    result = sear(
        {
        "operation": "extract",
        "admin_type": "group",
        "group": group,
        },
    )

    if "base:connected_users" in result.result["profile"]["base"]:
        raw_user_list = result.result["profile"]["base"]["base:connected_users"]

    for user in raw_user_list:
        user_list.append(user["base:connected_userid"])

    return user_list

def move_groups(users: list[str], group: str, destination_group: str):
    for user in users:
        connect_result = sear(
            {
                "operation": "alter",
                "admin_type": "group-connection",
                "userid": user.strip(),
                "group": destination_group.strip(),
            },
        )
        delete_result = sear(
            {
                "operation": "delete",
                "admin_type": "group-connection",
                "userid": user.strip(),
                "group": group.strip(),
            },
        )
        write_to_log_cache(log_entry=f"{user} moved from {group} to {destination_group}")
    
    return True

if group is not None and destination_group is not None:
    users_list = get_racf_users(group)
    if move_groups(users_list, group, destination_group):
        write_cache_to_disk()
        print(f"Moved users from {group} to {destination_group}")
else:
    exit("No group(s) supplied, use -g to supply the group being from and -d to supply the destination group")
