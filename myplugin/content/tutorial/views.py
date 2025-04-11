from http.client import responses

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.utils.translation import gettext_lazy as _

import requests
from django.views.decorators.csrf import csrf_exempt

#THIS CODE IS NOT USED AT THE MOMENT

class IndexView(generic.TemplateView):
    """
        View for displaying the tutorial index page and handling data retrieval from a backend API.
    """
    template_name = 'eduvmstore_dashboard/tutorial/index.html'
    page_title = _("About EduVMStore")

    def get_context_data(self, **kwargs):
        """
            Add backend app templates data to the context.

            :param kwargs: Additional context parameters.
            :return: Context dictionary with app template data under the 'images' key.
            :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        context['images'] = self.get_data_from_backend()
        return context

    def get_data_from_backend(self):
        """
            Fetch app templates from the backend API.

            :return: A list of app template data dictionaries if the request is successful,
                     otherwise an empty list.
            :rtype: list[dict]
        """
        try:
            response = requests.get("http://localhost:8000/api/app-templates/", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"Error fetching images: {err}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []


    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        """
            Handle POST requests to add a new app template by sending data to the backend API.

            :param HttpRequest request: The incoming HTTP POST request.
            :param args: Additional positional arguments.
            :param kwargs: Additional keyword arguments.
            :return: JsonResponse with success message if successful, or an error message
                    if a request error occurs.
            :rtype: Json
        """
        try:
            data = request.POST.get('name')
            response = requests.post(
                "http://localhost:8000/api/app-templates/",
                json={"name": data},
                timeout=10

            )
            response.raise_for_status()
            return JsonResponse({'message': 'Template added successfully!'})
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=400)


