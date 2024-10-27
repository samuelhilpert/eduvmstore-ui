import requests
import socket
from django.views import generic

 # Retrieve the host IP address
def get_host_ip():
    """
        Retrieve the IP address of the host.

        :return: The IP address of the host.
        :rtype: str
    """
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
    """
        View for displaying the admin index page with user details and admin status.
    """
    template_name = 'eduvmstore_dashboard/admin/index.html'

    def get_context_data(self, **kwargs):
        """
            Add user details, authentication token, and admin status to the context.

            :param kwargs: Additional context parameters.
            :return: Context dictionary with user-specific details and content visibility.
            :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        token_id = None


        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id

        context['username'] = user.username
        context['auth_token'] = token_id
        context['admin'] = user.is_superuser
        context['show_content'] = False
        context['user_id'] = user.id

        if user.is_superuser:
            context['show_content'] = True
        else:
            context['show_content'] = False


        return context




