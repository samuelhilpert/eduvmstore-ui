import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from an explicit path (parent directory of the current file's directory)
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(env_path)

# Get the BASE_URL from the environment
BASE_URL = os.getenv('BASE_URL')

if not BASE_URL:
    raise ValueError("BASE_URL is not set in the environment variables.")

# API endpoints for the EduVM Store backend
API_ENDPOINTS = {
    'app_templates': BASE_URL + 'app-templates/',  # For app template list
    'app_templates_update': BASE_URL + 'app-templates/{template_id}/', # For updating an app template
    'app_template_detail': BASE_URL + 'app-templates/{template_id}/',  # For a specific app template
    'app_template_delete': BASE_URL + 'app-templates/{template_id}', # For deleting an app template
    'instances_launch': BASE_URL + 'instances/launch/',  # For instance launch
    'user_list': BASE_URL + 'users/',  # For user list
    'roles_list': BASE_URL + 'roles',  # For roles list
    'get_to_approve': BASE_URL + 'app-templates/?public=True&approved=False', #  approving app templates
    'check_name': BASE_URL + 'app-templates/name/',  # For checking if a name is valid
    'favorite': BASE_URL + 'app-templates/favorites',  # For favoring app templates
    'to_be_favorite': BASE_URL + 'favorites/',  # For getting an app template favored
    'delete_favorite': BASE_URL + 'favorites/delete_by_app_template/', #  deleting favored app template
}