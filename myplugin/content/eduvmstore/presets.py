# presets.py

preset_examples = {
    "ubuntu_linux": {
        "name": "Ubuntu Linux",
        "short_description": "Ubuntu for teaching",
        "description": "This template provides a base Ubuntu setup with SSH access.",
        "instantiation_notice": "",
        "fixed_ram_gb": "2",
        "fixed_disk_gb": "20",
        "fixed_cores": "2",
        "volume_size_gb": "0",
        "per_user_ram_gb": "0.5",
        "per_user_disk_gb": "5",
        "per_user_cores": "1",
        "public": False,
        "instantiation_attributes": [{"name": "version"}, {"name": "packages"}],
        "account_attributes": [{"name": "username"}, {"name": "password"}],
        "script": "runcmd:\r\n  - |\r\n    # Create directory for private keys\r\n    "
                  "mkdir -p /home/ubuntu/user_keys\r\n    chmod 700 /home/ubuntu/user_keys\r\n  "
                  "  chown ubuntu:ubuntu /home/ubuntu/user_keys\r\n\r\n  "
                  "  while IFS=: read -r username password; do\r\n   "
                  "   # Create users\r\n      if ! id \"$username\" &>/dev/null; then\r\n   "
                  "     useradd -m -s /bin/bash \"$username\"\r\n    "
                  "    echo \"$username:$password\" | chpasswd\r\n      fi\r\n\r\n  "
                  "    # Create SSH directory and key\r\n    "
                  "  sudo -u \"$username\" mkdir -p /home/\"$username\"/.ssh\r\n    "
                  "  chmod 700 /home/\"$username\"/.ssh\r\n\r\n      # Generate SSH key\r\n    "
                  "  sudo -u \"$username\" ssh-keygen -t rsa -b 2048 -f "
                  "/home/\"$username\"/.ssh/id_rsa -N \"\"\r\n\r\n   "
                  "   # Set Public Key as authorized_key\r\n    "
                  "  cat /home/\"$username\"/.ssh/id_rsa.pub >> "
                  "/home/\"$username\"/.ssh/authorized_keys\r\n  "
                  "    chmod 600 /home/\"$username\"/.ssh/authorized_keys\r\n    "
                  "  chown -R \"$username:$username\" /home/\"$username\"/.ssh\r\n\r\n    "
                  "  # Secure private keys for the admin & Ubuntu user\r\n   "
                  "   cp /home/\"$username\"/.ssh/id_rsa /home/ubuntu/user_keys/\"$username\"_id_rsa\r\n   "
                  "   chmod 600 /home/ubuntu/user_keys/\"$username\"_id_rsa\r\n  "
                  "    chown ubuntu:ubuntu /home/ubuntu/user_keys/\"$username\"_id_rsa\r\n  "
                  "  done < /etc/users.txt\r\n\r\n    # SSH configuration: Disable password login\r\n "
                  "   sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication no/'"
                  " /etc/ssh/sshd_config\r\n   "
                  " sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin prohibit-password/'"
                  " /etc/ssh/sshd_config\r\n    systemctl restart ssh"
    },
    "gitlab_server": {
        "name": "GitLab Server",
        "short_description": "GitLab for software engineering course",
        "description": "This template provides a GitLab server preconfigured for classroom use. The specified users get access to this gitlab server.",
        "instantiation_notice": "",
        "fixed_ram_gb": "4",
        "fixed_disk_gb": "50",
        "fixed_cores": "4",
        "volume_size_gb": "10",
        "per_user_ram_gb": "1",
        "per_user_disk_gb": "10",
        "per_user_cores": "1",
        "public": False,
        "instantiation_attributes": [],
        "account_attributes": [
            {"name": "username"},
            {"name": "password"},
            {"name": "firstname"},
            {"name": "lastname"},
            {"name": "email"},
        ],
        "script":"packages:\r\n  - curl\r\n  - openssh-server\r\n  - ca-certificates\r\n "
                 " - tzdata\r\n  - postfix\r\n  - jq\r\n\r\nruncmd:\r\n  - cat /etc/users.txt >"
                 " /etc/testtesttest\r\n  - |\r\n    FIRST_USER=$(head -n 1 /etc/users.txt | "
                 "cut -d':' -f1)\r\n    while IFS=':' read -r username password firstname "
                 "lastname email; do\r\n      if ! id \"$username\" &>/dev/null; then\r\n   "
                 "     useradd -m -s \"/bin/bash\" \"$username\"\r\n      "
                 "  echo \"$username:$password\" | chpasswd\r\n      "
                 "  if [ \"$username\" = \"$FIRST_USER\" ]; then\r\n        "
                 "  usermod -aG sudo \"$username\"\r\n        fi\r\n      fi\r\n   "
                 " done < /etc/users.txt\r\n\r\n  # Install GitLab \r\n  - apt-get update\r\n "
                 " - DEBIAN_FRONTEND=noninteractive apt-get install -y curl openssh-server "
                 "ca-certificates tzdata postfix jq\r\n  - curl -fsSL "
                 "https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh"
                 " | bash\r\n  - apt-get install -y gitlab-ce\r\n "
                 " - gitlab-ctl reconfigure\r\n  - gitlab-ctl restart\r\n\r\n  "
                 "# Wait until GitLab starts\r\n  - sleep 60\r\n\r\n  "
                 "# Generate Root-Token for API\r\n  - |\r\n    "
                 "export GITLAB_ROOT_TOKEN=$(openssl rand -hex 20)\r\n    "
                 "gitlab-rails runner \"token = User.find_by(username: "
                 "'root').personal_access_tokens.create(scopes:"
                 " ['api'], name: 'root-token', expires_at: 1.year.from_now); "
                 "token.set_token('$GITLAB_ROOT_TOKEN'); token.save!\"\r\n  "
                 "  echo \"$GITLAB_ROOT_TOKEN\" > /root/gitlab_token.txt\r\n\r\n  "
                 "# Create user in GitLab\r\n  - |\r\n   "
                 " export GITLAB_ROOT_TOKEN=$(cat /root/gitlab_token.txt)\r\n    "
                 "while IFS=':' read -r username password firstname lastname email; do\r\n   "
                 " response=$(curl --silent --header \"PRIVATE-TOKEN: $GITLAB_ROOT_TOKEN\""
                 " \"http://localhost/api/v4/users?username=$username\")\r\n   "
                 " user_exists=$(echo \"$response\" | jq -r 'if . == [] then 0 else 1"
                 " end')\r\n\r\n    if [ \"$user_exists\" -eq 0 ]; then\r\n     "
                 " curl --request POST --header \"PRIVATE-TOKEN: $GITLAB_ROOT_TOKEN\" \\\r\n    "
                 "    --data \"username=$username&name=$firstname "
                 "$lastname&email=$email&password=$password&skip_confirmation=true\" \\\r\n    "
                 "    \"http://localhost/api/v4/users\"\r\n    fi\r\n  "
                 "  done < /etc/users.txt\r\n\r\nfinal_message:"
                 " \"GitLab installation and user creation completed.\""

    },
    "jupyter_notebook": {
        "name": "Jupyter Notebook",
        "short_description": "Isolated Jupyter environment for each user",
        "description": "This template provides Jupyter Notebooks on separate ports for multiple users. The specified users get their own Jupyter environment on their own port.",
        "instantiation_notice": "",
        "fixed_ram_gb": "8",
        "fixed_disk_gb": "80",
        "fixed_cores": "4",
        "volume_size_gb": "50",
        "per_user_ram_gb": "2",
        "per_user_disk_gb": "10",
        "per_user_cores": "1",
        "public": False,
        "instantiation_attributes": [],
        "account_attributes": [
            {"name": "username"},
            {"name": "password"},
        ],
        "script":"packages:\r\n      - python3-pip\r\n      - python3-venv\r\n     "
                 " - curl\r\n\r\n    runcmd:\r\n      - |\r\n        PORT=8888\r\n      "
                 "  while IFS=':' read -r username password; do\r\n        "
                 "  if ! id \"$username\" &>/dev/null; then\r\n           "
                 " useradd -m -s \"/bin/bash\" \"$username\"\r\n            "
                 "echo \"$username:$password\" | chpasswd\r\n            "
                 "usermod -aG sudo \"$username\"\r\n          fi\r\n\r\n          "
                 "# Setup Jupyter environment\r\n          su - \"$username\" -c "
                 "\"python3 -m venv jupyter_env\"\r\n          "
                 "su - \"$username\" -c \"~/jupyter_env/bin/pip install --upgrade pip\"\r\n     "
                 "     su - \"$username\" -c \"~/jupyter_env/bin/pip install notebook\"\r\n\r\n"
                 "          # Generate Jupyter config\r\n          su - \"$username\" -c "
                 "\"~/jupyter_env/bin/jupyter notebook --generate-config\"\r\n    "
                 "      CONFIG_PATH=\"/home/$username/.jupyter/jupyter_notebook_config.py\"\r\n  "
                 "        echo \"c = get_config()\" >> \"$CONFIG_PATH\"\r\n         "
                 " echo \"c.NotebookApp.ip = '0.0.0.0'\" >> \"$CONFIG_PATH\"\r\n     "
                 "     echo \"c.NotebookApp.open_browser = False\" >> \"$CONFIG_PATH\"\r\n    "
                 "      echo \"c.NotebookApp.port = $PORT\" >> \"$CONFIG_PATH\"\r\n      "
                 "    echo \"c.NotebookApp.token = ''\" >> \"$CONFIG_PATH\"\r\n     "
                 "     echo \"c.NotebookApp.password = ''\" >> \"$CONFIG_PATH\"\r\n      "
                 "    chown \"$username:$username\" \"$CONFIG_PATH\"\r\n\r\n          "
                 "# Download sample notebook\r\n          "
                 "NOTEBOOK_URL="
                 "\"https://raw.githubusercontent.com/codebasics/py/master/Basics/test.ipynb\"\r\n"
                 "          NOTEBOOK_PATH=\"/home/$username/test.ipynb\"\r\n          "
                 "su - \"$username\" -c \"curl -o \\\"$NOTEBOOK_PATH\\\" \\\"$NOTEBOOK_URL\\\"\"\r\n"
                 "          chown \"$username:$username\" \"$NOTEBOOK_PATH\"\r\n\r\n          "
                 "# Create systemd service\r\n          echo \"[Unit]\r\n          "
                 "Description=Jupyter Notebook for $username\r\n          "
                 "After=network.target\r\n\r\n          [Service]\r\n          Type=simple\r\n "
                 "         User=$username\r\n          WorkingDirectory=/home/$username\r\n     "
                 "     ExecStart=/home/$username/jupyter_env/bin/jupyter-notebook\r\n        "
                 "  Restart=always\r\n\r\n          [Install]\r\n         "
                 " WantedBy=multi-user.target\" >"
                 " \"/etc/systemd/system/jupyter-$username.service\"\r\n\r\n         "
                 " systemctl daemon-reload\r\n          s"
                 "ystemctl enable \"jupyter-$username\"\r\n          "
                 "systemctl start \"jupyter-$username\"\r\n\r\n          "
                 "PORT=$((PORT + 1))\r\n\r\n        done < /etc/users.txt"
    }
}