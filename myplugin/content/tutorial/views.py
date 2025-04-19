from http.client import responses

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.utils.translation import gettext_lazy as _

import requests
from django.views.decorators.csrf import csrf_exempt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from io import BytesIO
from django.http import HttpResponse



class IndexView(generic.TemplateView):
    """
        View for displaying the tutorial index page and handling data retrieval from a backend API.
    """
    template_name = 'eduvmstore_dashboard/tutorial/index.html'
    page_title = _("About EduVMStore")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context

    def post(self, request, *args, **kwargs):
        pdf_bytes = generate_eduvmstore_pdf()
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="EduVMStore.pdf"'
        return response

def generate_eduvmstore_pdf():
    """
    Erstellt ein PDF mit Text- und Code-Inhalten und gibt es als Bytes zurück.
    Ideal für Webanwendungen (z. B. Flask/FastAPI).
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterHeading', parent=styles['Heading1'], alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='CodeBlock', fontName='Courier', fontSize=9, leading=12, spaceBefore=6, spaceAfter=6))

    elements = []

    # Beispielinhalte – hier kannst du deinen echten Text einsetzen
    sections = [
        {
            "title": "About EduVMStore",
            "text": """This section provides background information, frequently asked questions, and contact details for EduVMStore.

---

**Manual**

You can download the official user manual for EduVMStore directly from the dashboard by clicking the "Download Manual" button.

---

**FAQ**

**What is the EduVMStore?**  
EduVMStore is a platform designed for managing and provisioning virtual machines in an educational context. It integrates with OpenStack to simplify the creation, configuration, and management of VMs, enabling users such as students and educators to deploy customized learning environments quickly. The platform supports various VM configurations and resource allocations, making it suitable for classroom and research purposes.

**Who created the EduVMStore?**  
The EduVMStore was developed by students of the DHBW Mannheim, Germany. The project was part of the Bachelor's degree program in Business Informatics. The team includes Valentin Czekalla, Jared Heinrich, Marian Rickert, Emese Racz, Monika Bircic, and Samuel Hilpert.

**Who can use EduVMStore?**  
EduVMStore is designed for students, educators, lecturers, and IT administrators in the DHBW who require virtualized environments for teaching, learning, and research.

**What happens if I exceed my resource quota?**  
If you exceed your resource quota, you will not be able to create new instances or allocate additional resources until the quota is increased or existing resources are freed. In such cases, contact your administrator or IT department.

**Can I share my AppTemplates with other users?**  
Yes, you can share your AppTemplates with other users by selecting the "Available for everyone" option during the creation process. See the documentation section "Publish a private AppTemplate" for details.

---

**Contact**

Email: admin@eduVMStore.com  
Phone: +49 123 456 7890"""
        },
        {
            "title": "Script Tutorial",
            "text": """Cloud-init scripts are used to automate the configuration of virtual machines during their initialization.
In EduVMStore, these scripts are essential for setting up AppTemplates, allowing you to define user accounts, install software, configure services, and more.

This tutorial provides a structured guide to writing effective cloud-init scripts using YAML.

Step-by-step instructions:

1. Start with the shebang line to indicate script type.
2. Use the 'write_files' section to create or modify files.
3. Use the 'packages' section to install software.
4. Use 'runcmd' to run commands during initialization.
5. Use 'users' to define user accounts.
6. Use 'final_message' to print something at the end.

Instantiation and Account Attributes:
Account attributes (e.g. username:password) can be read and used in your cloud-init script logic.

Best Practices:
- Test scripts in dev before production.
- Comment each section meaningfully.
- Avoid duplicating 'write_files' or 'runcmd'.
- Validate uploaded CSVs.

Tips and Tricks:
- Use LLMs to generate cloud-init.
- Combine 'write_files' and 'runcmd' for automation.
- Provide meaningful final messages.
- Use placeholders/variables for flexibility.

Common Pitfalls:
- Wrong indentation (YAML-sensitive).
- Not escaping special characters.
- Repeating 'write_files' or 'runcmd'.
- Invalid CSV header or content.
- Missing adjustments for dynamic file paths.
- Forgetting to update user counts.""",

            "code": [
                "#cloud-config",

                """write_files:
          - path: /etc/motd
            content: |
              Welcome to your new instance!
              Managed by EduVMStore.""",

                """packages:
          - curl
          - git
          - python3""",

                """runcmd:
          - apt-get update
          - apt-get install -y nginx""",

                """users:
          - name: student
            groups: sudo
            shell: /bin/bash
            sudo: ['ALL=(ALL) NOPASSWD:ALL']
            lock_passwd: false
            passwd: $6$rounds=4096$randomsalt$hashedpassword""",

                """final_message: "Instance setup is complete. Enjoy your environment!\"""",

                """while IFS=: read -r username password; do
            # Create users
            if ! id "$username" &>/dev/null; then
                useradd -m -s /bin/bash "$username"
                echo "$username:$password" | chpasswd
            fi
        done < /etc/users.txt"""
            ]
        }, {
            "title": "Instructions",
            "text": """This section provides a visual guide using interactive tiles. Each tile explains a major function within the EduVMStore interface.

---

**Create AppTemplate**

1. Open the EduVMStore dashboard.
2. Click ‘Create AppTemplate’.
3. Select an image from the dropdown.
4. Enter a name for the template.
5. Provide a short and detailed description.
6. Add an instantiation notice (optional).
7. Set availability: Everyone or Creator only.
8. Select one or more fitting security groups.
9. Define minimal system requirements for the template.
10. Set instantiation and account attributes.
11. Upload or write the cloud-init script.
12. Click ‘Create’ to finalize.

---

**Launch Instance**

1. Open the EduVMStore dashboard.
2. Navigate to the AppTemplate Overview page.
3. Click on the 'Launch' button.
4. Enter a custom name for the instance (optional).
5. Select the number of instances.
6. Choose one or separate keys for the templates.
7. Decide if instances should be identical.
8. Modify template properties if not identical.
9. Enter instantiation attributes.
10. Add users via attribute fields or CSV upload.
11. Click 'Launch Instance' to start.

---

**Publish a private AppTemplate**

1. Open the EduVMStore dashboard.
2. Search for your private AppTemplate.
3. Open the dropdown next to 'Launch' and click 'Edit AppTemplate'.
4. Change "Available for" to "Everyone".
5. Click 'Create'.
6. The AppTemplate will await admin approval before publishing.

---

**Clone AppTemplate**

1. Open the EduVMStore dashboard.
2. Search for the AppTemplate you want to clone.
3. Use the dropdown next to the launch button and select "Clone AppTemplate".
4. Enter a new name for the cloned template.
5. Adjust settings or configurations as needed.
6. Click "Create" to finalize the clone.
"""
        }, {
            "title": "Examples",
            "text": """This section contains full example scenarios on how to set up different environments using EduVMStore.

---

**Use Case: Ubuntu Linux**

Goal: Set up simple Ubuntu instances with SSH access per user.

Steps:
- Create an AppTemplate (Ubuntu base image, security groups, minimal resources).
- Enable "Generate SSH setup for users".
- Define instantiation and account attributes (e.g., username:password).
- The SSH setup script is automatically included.
- Launch multiple instances and configure shared or individual users and volumes.

---

**Use Case: GitLab Server**

Goal: Set up a GitLab server for a software engineering course.

Steps:
- Create an AppTemplate with GitLab-compatible base image and resources (e.g., 4 GB RAM, 50 GB Disk).
- Upload or write a cloud-init script that installs GitLab, sets up users, and generates a root token.
- Launch one instance and provide user details (username, password, firstname, lastname, email).

---

**Use Case: Jupyter Notebook**

Goal: Provide isolated Jupyter environments for multiple students on a single instance.

Steps:
- Create an AppTemplate with sufficient resources (e.g., 8 GB RAM, 80 GB Disk).
- Enable optional SSH setup.
- Upload or write a cloud-init script that installs Jupyter, assigns users, and runs instances on individual ports.
- Launch one instance, configure users with CSV or manual entry.
""",

            "code": [
                # Ubuntu Linux cloud-init
                """runcmd:
          - |
            # Create directory for private keys
            mkdir -p /home/ubuntu/user_keys
            chmod 700 /home/ubuntu/user_keys
            chown ubuntu:ubuntu /home/ubuntu/user_keys
        
            while IFS=: read -r username password; do
              # Create users
              if ! id "$username" &>/dev/null; then
                useradd -m -s /bin/bash "$username"
                echo "$username:$password" | chpasswd
              fi
        
              # Create SSH directory and key
              sudo -u "$username" mkdir -p /home/"$username"/.ssh
              chmod 700 /home/"$username"/.ssh
        
              # Generate SSH key
              sudo -u "$username" ssh-keygen -t rsa -b 2048 -f /home/"$username"/.ssh/id_rsa -N ""
        
              # Set Public Key as authorized_key
              cat /home/"$username"/.ssh/id_rsa.pub >> /home/"$username"/.ssh/authorized_keys
              chmod 600 /home/"$username"/.ssh/authorized_keys
              chown -R "$username:$username" /home/"$username"/.ssh
        
              # Secure private keys for the admin & Ubuntu user
              cp /home/"$username"/.ssh/id_rsa /home/ubuntu/user_keys/"$username"_id_rsa
              chmod 600 /home/ubuntu/user_keys/"$username"_id_rsa
              chown ubuntu:ubuntu /home/ubuntu/user_keys/"$username"_id_rsa
            done < /etc/users.txt
        
            # SSH configuration: Disable password login
            sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
            sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
            systemctl restart ssh""",

                # GitLab Server cloud-init
                """packages:
          - curl
          - openssh-server
          - ca-certificates
          - tzdata
          - postfix
          - jq
        
        runcmd:
          - cat /etc/users.txt > /etc/testtesttest
          - |
            FIRST_USER=$(head -n 1 /etc/users.txt | cut -d':' -f1)
            while IFS=':' read -r username password firstname lastname email; do
              if ! id "$username" &>/dev/null; then
                useradd -m -s "/bin/bash" "$username"
                echo "$username:$password" | chpasswd
                if [ "$username" = "$FIRST_USER" ]; then
                  usermod -aG sudo "$username"
                fi
              fi
            done < /etc/users.txt
        
          - apt-get update
          - DEBIAN_FRONTEND=noninteractive apt-get install -y curl openssh-server ca-certificates tzdata postfix jq
          - curl -fsSL https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | bash
          - apt-get install -y gitlab-ce
          - gitlab-ctl reconfigure
          - gitlab-ctl restart
          - sleep 60
        
          - |
            export GITLAB_ROOT_TOKEN=$(openssl rand -hex 20)
            gitlab-rails runner "token = User.find_by(username: 'root').personal_access_tokens.create(scopes: ['api'], name: 'root-token', expires_at: 1.year.from_now); token.set_token('$GITLAB_ROOT_TOKEN'); token.save!"
            echo "$GITLAB_ROOT_TOKEN" > /root/gitlab_token.txt
        
          - |
            export GITLAB_ROOT_TOKEN=$(cat /root/gitlab_token.txt)
            while IFS=':' read -r username password firstname lastname email; do
            response=$(curl --silent --header "PRIVATE-TOKEN: $GITLAB_ROOT_TOKEN" "http://localhost/api/v4/users?username=$username")
            user_exists=$(echo "$response" | jq -r 'if . == [] then 0 else 1 end')
        
            if [ "$user_exists" -eq 0 ]; then
              curl --request POST --header "PRIVATE-TOKEN: $GITLAB_ROOT_TOKEN" \
                --data "username=$username&name=$firstname $lastname&email=$email&password=$password&skip_confirmation=true" \
                "http://localhost/api/v4/users"
            fi
            done < /etc/users.txt
        
        final_message: "GitLab installation and user creation completed.""",

                # Jupyter Notebook cloud-init
                """packages:
          - python3-pip
          - python3-venv
          - curl
        
        runcmd:
          - |
            PORT=8888
            while IFS=':' read -r username password; do
              if ! id "$username" &>/dev/null; then
                useradd -m -s "/bin/bash" "$username"
                echo "$username:$password" | chpasswd
                usermod -aG sudo "$username"
              fi
        
              su - "$username" -c "python3 -m venv jupyter_env"
              su - "$username" -c "~/jupyter_env/bin/pip install --upgrade pip"
              su - "$username" -c "~/jupyter_env/bin/pip install notebook"
        
              su - "$username" -c "~/jupyter_env/bin/jupyter notebook --generate-config"
              CONFIG_PATH="/home/$username/.jupyter/jupyter_notebook_config.py"
              echo "c = get_config()" >> "$CONFIG_PATH"
              echo "c.NotebookApp.ip = '0.0.0.0'" >> "$CONFIG_PATH"
              echo "c.NotebookApp.open_browser = False" >> "$CONFIG_PATH"
              echo "c.NotebookApp.port = $PORT" >> "$CONFIG_PATH"
              echo "c.NotebookApp.token = ''" >> "$CONFIG_PATH"
              echo "c.NotebookApp.password = ''" >> "$CONFIG_PATH"
              chown "$username:$username" "$CONFIG_PATH"
        
              NOTEBOOK_URL="https://raw.githubusercontent.com/codebasics/py/master/Basics/test.ipynb"
              NOTEBOOK_PATH="/home/$username/test.ipynb"
              su - "$username" -c "curl -o \"$NOTEBOOK_PATH\" \"$NOTEBOOK_URL\""
              chown "$username:$username" "$NOTEBOOK_PATH"
        
              echo "[Unit]
              Description=Jupyter Notebook for $username
              After=network.target
        
              [Service]
              Type=simple
              User=$username
              WorkingDirectory=/home/$username
              ExecStart=/home/$username/jupyter_env/bin/jupyter-notebook
              Restart=always
        
              [Install]
              WantedBy=multi-user.target" > "/etc/systemd/system/jupyter-$username.service"
        
              systemctl daemon-reload
              systemctl enable "jupyter-$username"
              systemctl start "jupyter-$username"
        
              PORT=$((PORT + 1))
        
            done < /etc/users.txt"""
            ]
        }



    ]

    for section in sections:
        elements.append(Paragraph(section['title'], styles['CenterHeading']))
        elements.append(Spacer(1, 12))

        if "text" in section:
            for line in section["text"].split('\n'):
                elements.append(Paragraph(line.strip(), styles['Normal']))
                elements.append(Spacer(1, 6))

        if "code" in section:
            for code_block in section["code"]:
                elements.append(Preformatted(code_block.strip(), styles['CodeBlock']))
                elements.append(Spacer(1, 12))


        elements.append(PageBreak())

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()