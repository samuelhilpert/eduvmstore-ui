
# Base URL for the Backend API
BASE_URL = "http://localhost:8000/api/"


# Define your API endpoints in a dictionary or as constants
API_ENDPOINTS = {
    'app_templates': BASE_URL + 'app-templates/',  # For app template list
    'app_template_detail': BASE_URL + 'app-templates/{template_id}/',  # For a specific app template
    'instances_launch': BASE_URL + 'instances/launch/',  # For instance launch
    'user_list': BASE_URL + 'users/',  # For user list
    'roles_list': BASE_URL + 'roles',  # For roles list
    'get_to_approve': BASE_URL + 'app-templates/?public=True&approved=False', # For approving app templates
    'check_name': BASE_URL + 'app-templates/name/',  # For checking if a name is valid
}
