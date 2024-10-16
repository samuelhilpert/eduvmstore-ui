from asyncio import timeout
from http.client import responses

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic

import requests
from django.views.decorators.csrf import csrf_exempt


class IndexView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/tutorial/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.get_data_from_backend() 
        return context


    def get_data_from_backend(self):
        try:
            response = requests.get("http://localhost:8000/api/app-templates/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:  # Fix the typo here
            print(f"Error fetching images: {err}")
            return []
        except requests.exceptions.RequestException as e:  
            print(f"Request error: {e}")
            return []

    @method_decorator(csrf_exempt) 
    def post(self, request, *args, **kwargs):
        try:
            # Parse the JSON request body
            data = request.POST.get('name') 
            # Make a POST request to your backend API
            response = requests.post(
                "http://localhost:8000/api/app-templates/",
                json={"name": data}

            )
            response.raise_for_status()
            return JsonResponse({'message': 'Template added successfully!'})
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=400)




