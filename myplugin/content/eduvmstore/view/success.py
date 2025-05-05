from django.views import generic
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
import io
import zipfile
from django.http import HttpResponse
from myplugin.content.eduvmstore.utils import generate_pdf, generate_ssh_instructions_pdf

class InstanceSuccessView(generic.TemplateView):
    template_name = "eduvmstore_dashboard/eduvmstore/success.html"
    page_title = _("Success")

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to render the success template.

        :param request: The incoming HTTP GET request.
        :type request: HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: Rendered HTML response.
        :rtype: HttpResponse
        """
        context = self.get_context_data(**kwargs)

        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        num_instances = int(self.request.session.get("num_instances", 1))
        separate_keys = self.request.session.get("separate_keys", False)
        ssh_user_requested = self.request.session.get('ssh_user_requested', False)
        context['ssh_user_requested'] = ssh_user_requested
        context['page_title'] = self.page_title
        context['instances'] = []

        for i in range(1, num_instances + 1):
            instance_name = self.request.session.get(f"names_{i}", "unknown")
            ip_address = self.request.session.get(f"ip_addresses_{i}", "unknown")

            if separate_keys:
                key_file = self.request.session.get(f"keypair_name_{i}", "unknown") + ".pem"
            else:
                key_file = self.request.session.get("keypair_name", "unknown") + ".pem"

            context['instances'].append({
                'name': instance_name,
                'ip': ip_address,
                'key': key_file,
            })

        return context



    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to generate and return a ZIP file containing PDFs with
        instance user account information and private keys (either one shared key or
        separate keys per instance).

        :param request: The incoming HTTP request.
        :type request: HttpRequest
        :param args: Additional positional arguments.
        :type args: tuple
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: An HTTP response with the generated ZIP file.
        :rtype: HttpResponse
        """
        num_instances = int(request.session.get("num_instances", 1))
        separate_keys = request.session.get("separate_keys", False)
        base_name = request.session.get("base_name", "instance")

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

            for i in range(1, num_instances + 1):
                accounts = request.session.get(f"accounts_{i}", [])
                name = request.session.get(f"names_{i}", f"Instance-{i}")
                app_template = request.session.get("app_template", "Unknown")
                created = request.session.get("created", "Unknown Date")
                instantiation = request.session.get(f"instantiations_{i}", [])
                ip_adr = request.session.get(f"ip_addresses_{i}", [])

                if accounts or instantiation:
                    pdf_content = generate_pdf(accounts, name, app_template, created, instantiation, ip_adr)
                    zip_file.writestr(f"{name}.pdf", pdf_content)

                if request.session.get('ssh_user_requested', False):
                    instances = []
                    for i in range(1, num_instances + 1):
                        name = request.session.get(f"names_{i}", "unknown")
                        ip = request.session.get(f"ip_addresses_{i}", "unknown")

                        if separate_keys:
                            key_file = request.session.get(f"keypair_name_{i}", "unknown") + ".pem"
                        else:
                            key_file = request.session.get("keypair_name", "unknown") + ".pem"

                        instances.append({'name': name, 'ip': ip, 'key': key_file})

                    ssh_pdf_content = generate_ssh_instructions_pdf(instances)
                    zip_file.writestr("ssh_instructions.pdf", ssh_pdf_content)

            if not separate_keys:
                private_key = request.session.get("private_key")
                keypair_name = request.session.get("keypair_name", "shared_instance_key")
                if private_key:
                    zip_file.writestr(f"{keypair_name}.pem", private_key)


            else:
                for i in range(1, num_instances + 1):
                    private_key = request.session.get(f"private_key_{i}")
                    keypair_name = request.session.get(f"keypair_name_{i}", f"instance_key_{i}")
                    if private_key:
                        zip_file.writestr(f"{keypair_name}.pem", private_key)

        zip_buffer.seek(0)

        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{base_name}_data.zip"'

        for i in range(1, num_instances + 1):
            request.session.pop(f"accounts_{i}", None)
            request.session.pop(f"instantiations_{i}", None)
            request.session.pop(f"names_{i}", None)
            request.session.pop(f"private_key_{i}", None)
            request.session.pop(f"keypair_name_{i}", None)
            request.session.pop(f"ip_addresses_{i}", None)

        request.session.pop("private_key", None)
        request.session.pop("keypair_name", None)
        request.session.pop("separate_keys", None)
        request.session.pop("num_instances", None)
        request.session.pop("app_template", None)
        request.session.pop("created", None)
        request.session.pop("base_name", None)

        return response