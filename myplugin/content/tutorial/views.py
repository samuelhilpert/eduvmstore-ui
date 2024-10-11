from django.views import generic
from horizon import exceptions
from openstack_dashboard.api import glance
import requests
from django.utils.translation import gettext_lazy as _


class IndexView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/tutorial/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        token_id = None

        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id

        context['username'] = user.username
        context['auth_token'] = token_id
        context['admin'] = user.is_superuser
        context['show_content'] = user.is_superuser

        # Funktion zur API-Abfrage von Benutzer- oder Projektnamen
        def get_keystone_entity_name(entity_id):
            keystone_url = self.request.user.endpoint
            headers = {
                'X-Auth-Token': self.request.user.token.id,
                'Content-Type': 'application/json'
            }

            # Versuche, die ID als Benutzer-ID zu behandeln
            user_url = f"{keystone_url}/v3/users/{entity_id}"
            user_response = requests.get(user_url, headers=headers)

            if user_response.status_code == 200:
                user_data = user_response.json()
                return user_data['user']['name']

            # Versuche, die ID als Projekt-ID zu behandeln
            project_url = f"{keystone_url}/v3/projects/{entity_id}"
            project_response = requests.get(project_url, headers=headers)

            if project_response.status_code == 200:
                project_data = project_response.json()
                return project_data['project']['name']

            # Fehler werfen, wenn weder Benutzer noch Projekt gefunden wurden
            raise exceptions.NotFound(f"ID {entity_id} is neither a valid user nor a project.")

        # Glance-Images abrufen
        try:
            filters = {}  # Hier kannst du nach Bedarf Filter hinzufügen
            images, has_more_data, has_prev_data = glance.image_list_detailed(
                self.request, filters=filters, paginate=True
            )

            # User- und Projekt-Namen für jedes Image umwandeln
            image_data = []
            for image in images:
                try:
                    owner_name = get_keystone_entity_name(image.owner)
                except exceptions.NotFound:
                    owner_name = _("Unknown")

                image_data.append({
                    'id': image.id,
                    'name': image.name,
                    'owner_name': owner_name,
                    'size': image.size,
                    'status': image.status,
                    'created_at': image.created_at,
                })

            context['images'] = image_data

        except Exception as e:
            context['error_message'] = _('Unable to retrieve images: %s') % str(e)

        return context
