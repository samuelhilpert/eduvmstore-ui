
# Base URL for the API (if your endpoints share a common base)
# Change the BASE_URL if needed
BASE_URL = "http://localhost:8000/api/"


# Define your API endpoints in a dictionary or as constants
API_ENDPOINTS = {
    'app_templates': BASE_URL + 'app-templates/',  # For app template list
    'app_template_detail': BASE_URL + 'app-templates/{template_id}/',  # For a specific app template
    'instances_launch': BASE_URL + 'instances/launch/',  # For instance launch
}