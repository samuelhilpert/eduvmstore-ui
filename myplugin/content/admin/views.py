import requests
import socket
from django.views import generic

def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:

        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        raise RuntimeError("Failed to retrieve host IP address") from e
    finally:
        s.close()
    return ip

class IndexView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/admin/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        token_id = None


        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id

        context['username'] = user.username
        context['auth_token'] = token_id
        context['admin'] = user.is_superuser
        context['show_content'] = False

        if user.is_superuser:
            context['show_content'] = True
        else:
            context['show_content'] = False


        return context




