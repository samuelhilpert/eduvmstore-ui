from django.views import generic
from django.utils.translation import gettext_lazy as _
from myplugin.content.eduvmstore.presets import preset_examples

class IndexView(generic.TemplateView):
    """
        View for displaying the tutorial index page and handling data retrieval from a backend API.
    """
    template_name = 'eduvmstore_dashboard/example/index.html'
    page_title = _("Example")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title

        # Add object to the context
        context["preset_examples"] = preset_examples

        # Add simple preset for the test.html fragment
        context["object"] = {"name": "Bob"}

        context["example_info"] = {
            "preset": preset_examples["ubuntu_linux"],
            "use_case_title": "Ubuntu Linux",
            "use_case_problem_question" : "How to set up simple Ubuntu Linux instances with SSH setup for users?",
            "use_case_description" : "This example demonstrates how lecturers can set up simple Ubuntu Linux instances with SSH setup for multiple users. Each user will have their own SSH key generated and securely stored.",
            "overview" : "Lecturers will create an AppTemplate that includes a cloud-init script to configure the Ubuntu Linux environment and automatically set up SSH access for users. This ensures a streamlined process for deploying and managing the instances.",
            "learning_objectives" : [
            "Create an AppTemplate tailored for the course requirements.",
            "Enable the \"Generate SSH setup for users\" option to automate the SSH setup.",
            "Launch and manage multiple instances of the Ubuntu Linux environment for their students."],
            "product_name" : "Ubuntu Linux",
            "product_url" : "https://ubuntu.com/",
            "image_name" : "Ubuntu 22.04",
            "security_group_instructions" : "For this example, select a security group that allows SSH access (port 22).",
            "instance_count": "1",
            "flavour" : "mb1.small",
            "instantiation_attribute_recommendation_values" : [],
            "link_id" : "ubuntu_linux",
        }

        return context