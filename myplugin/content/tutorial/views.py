from http.client import responses

from django.views import generic

import requests


class IndexView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/tutorial/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.get_data_from_backend()  # Pass the fetched data to the template
        return context


    def get_data_from_backend(self):
        try:
            response = requests.get("http://localhost:8000/api/app-templates")
            response.raise_for_status()
            return response.json().get("images", [])
        except requests.exceptions.HTTPError as err:  # Fix the typo here
            print(f"Error fetching images: {err}")
            return []
        except requests.exceptions.RequestException as e:  # Catch any other exceptions from requests
            print(f"Request error: {e}")
            return []





