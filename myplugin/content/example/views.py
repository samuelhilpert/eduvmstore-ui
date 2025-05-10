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

        context["example_infos"] = [
            {
                "preset": preset_examples["ubuntu_linux"],
                "use_case_title": "Ubuntu Linux",
                "use_case_problem_question": "How to set up simple Ubuntu Linux instances with SSH setup for users?",
                "use_case_description": "This example demonstrates how lecturers can set up simple Ubuntu Linux instances with SSH setup for multiple users. Each user will have their own SSH key generated and securely stored.",
                "overview": "Lecturers will create an AppTemplate that includes a cloud-init script to configure the Ubuntu Linux environment and automatically set up SSH access for users. This ensures a streamlined process for deploying and managing the instances.",
                "learning_objectives": [
                    "Create an AppTemplate tailored for the course requirements.",
                    'Enable the "Generate SSH setup for users" option to automate the SSH setup.',
                    "Launch and manage multiple instances of the Ubuntu Linux environment for their students.",
                ],
                "product_name": "Ubuntu Linux",
                "product_url": "https://ubuntu.com/",
                "image_name": "Ubuntu 22.04",
                "security_group_instructions": "For this example, select a security group that allows SSH access (port 22).",
                "instance_count": "1",
                "flavour": "mb1.small",
                "instantiation_attribute_recommendation_values": [],
                "link_id": "ubuntu_linux",
            },
            {
            "preset": preset_examples["gitlab_server"],
            "use_case_title": "GitLab Server",
            "use_case_problem_question": "How to set up a GitLab server for a software engineering course?",
            "use_case_description": "This example demonstrates how lecturers can set up a GitLab server for a software engineering course using the EduVMStore. The setup enables students to collaborate on projects and manage their code repositories effectively, providing a practical learning environment.",
            "overview": "Lecturers will create an AppTemplate that includes a cloud-init script to configure the GitLab server and add students with their access credentials. This ensures a streamlined process for deploying and managing the server.",
            "learning_objectives": [
                "Create an AppTemplate tailored for the course requirements.",
                "Write a configuration script to automate the setup of the GitLab server.",
                "Launch and manage an instance of the GitLab server for their students.",
            ],
            "product_name": "GitLab",
            "product_url": "https://about.gitlab.com/",
            "image_name": "Ubuntu 22.04",
            "security_group_instructions": "For this example, select a security group that allows HTTP access (port 80) and SSH access (port 22).",
            "instance_count": "1",
            "flavour": "mb1.medium",
            "instantiation_attribute_recommendation_values": [],
            "link_id": "gitlab_server",
            },
            {
                "preset": preset_examples["jupyter_notebook"],
                "use_case_title": "Jupyter Notebook",
                "use_case_problem_question": "How to set up a Jupyter Notebook instance with multiple user accounts?",
                "use_case_description": "This example demonstrates how lecturers can set up a Jupyter Notebook instance with multiple user accounts. Each user will have their own isolated Jupyter Notebook environment accessible on different ports of the instance.",
                "overview": "Lecturers will create an AppTemplate that includes a cloud-init script to configure the Jupyter Notebook environment and add students with their access credentials. This ensures a streamlined process for deploying and managing the instance.",
                "learning_objectives": [
                    "Create an AppTemplate tailored for the course requirements.",
                    "Write a configuration script to automate the setup of the Jupyter Notebook environment.",
                    "Launch and manage an instance of the Jupyter Notebook environment for their students.",
                ],
                "product_name": "Jupyter Notebook",
                "product_url": "https://jupyter.org/",
                "image_name": "Ubuntu 22.04",
                "security_group_instructions": "For this example, select a security group that allows HTTP access (ports 8888-8900).",
                "instance_count": "1",
                "flavour": "mb1.large",
                "instantiation_attribute_recommendation_values": [],
                "link_id": "jupyter_notebook",
            },
            {
                "preset": preset_examples["postgres"],
                "use_case_title": "Postgres Server",
                "use_case_problem_question": "How to set up a Postgres database server for a database course?",
                "use_case_description": "This example demonstrates how lecturers can set up a Postgres database server for teaching database concepts and SQL. Each student gets their own database account with appropriate permissions.",
                "overview": "Lecturers will create an AppTemplate that includes a cloud-init script to configure the Postgres server and add students with their own database accounts. This ensures a streamlined process for deploying and managing the database server.",
                "learning_objectives": [
                    "Create an AppTemplate tailored for database teaching.",
                    "Configure a Postgres server with multiple student accounts.",
                    "Launch and manage a database server instance for database courses.",
                ],
                "product_name": "PostgreSQL",
                "product_url": "https://www.postgresql.org/",
                "image_name": "Ubuntu 22.04",
                "security_group_instructions": "For this example, select a security group that allows PostgreSQL access (port 5432).",
                "instance_count": "1",
                "flavour": "mb1.medium",
                "instantiation_attribute_recommendation_values": [],
                "link_id": "postgres",
            },
        ]

        return context