
from sear import sear

# Import argparse for custom commandline flags
import argparse

# Import pathlib to load list of resource profiles
from pathlib import Path

parser = argparse.ArgumentParser(
    prog="RACF resource profile cleanup utility",
    description="This program allows you to mass delete resource profiles",
)

parser.add_argument("-l", "--list", help="File with RACF resource profiles to ingest", default=None)
parser.add_argument("-c", "--class-name", help="RACF class name", default=None)

args = parser.parse_args()

class_name = args.class_name or None
resource_list_path = args.list or None

def remove_resource_profile(class_name: str, profile_name: str):
    """Deletes a resource profile"""
    result = sear(
        {
            "operation": "delete",
            "admin_type": "resource",
            "resource": profile_name,
            "class": class_name,
        },
    )

    return result.result["return_codes"]["racf_return_code"]

# Error handling
if class_name is not None and resource_list_path is not None:
    # Load list of resource profiles
    resource_list_file = Path(resource_list_path)

    with resource_list_file.open(mode="r") as f:
        resource_profiles = f.readlines()

    for resource_profile in resource_profiles:
        resource_profile = resource_profile.rstrip()
        
        return_code = remove_resource_profile(class_name,resource_profile)
        if  return_code == 0:
            # Prints colored output to the terminal
            print(f"\033[91mDeleted\033[00m {resource_profile} in class {class_name}!")
        else:
            print(f"Error! Return code {return_code}")