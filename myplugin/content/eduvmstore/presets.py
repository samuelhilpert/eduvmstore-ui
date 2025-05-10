# presets.py

preset_examples = {
    "ubuntu_linux": {
        "name": "Ubuntu Linux",
        "short_description": "Ubuntu for teaching",
        "description": "This template provides a base Ubuntu setup with SSH access.",
        "instantiation_notice": "",
        "fixed_ram_gb": "1",
        "fixed_disk_gb": "2",
        "fixed_cores": "1",
        "volume_size_gb": "0",
        "public": False,
        "instantiation_attributes": [],
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
        "description": "This template provides a GitLab server preconfigured for classroom use. "
                       "The specified users get access to this gitlab server.",
        "instantiation_notice": "",
        "fixed_ram_gb": "1",
        "fixed_disk_gb": "10",
        "fixed_cores": "1",
        "volume_size_gb": "0",
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
        "description": "This template provides Jupyter Notebooks on separate ports for multiple users. "
                       "The specified users get their own Jupyter environment on their own port.",
        "instantiation_notice": "",
        "fixed_ram_gb": "2",
        "fixed_disk_gb": "10",
        "fixed_cores": "1",
        "volume_size_gb": "0",
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
    },
    "postgres": {
        "name": "Postgres Server",
        "short_description": "A postgres server for database management",
        "description": "This AppTemplate can be used to teach DB Courses about Postgres and SQL.\n"
            "An example usage is to let students create a database and operate on it via SQL.\n"
            "The specified users get access to this postgres server.\n"
            "Students can Access the server via 'psql -h <ip-address> -U <username> -d <db_name>'\n"
            "Example requests could be:\n"
            "CREATE TABLE authors (\n"
            "  id SERIAL PRIMARY KEY,\n"
            "  name TEXT NOT NULL\n"
            ");\n"
            "\n"
            "CREATE TABLE books (\n"
            "  id SERIAL PRIMARY KEY,\n"
            "  title TEXT NOT NULL,\n"
            "  author_id INT REFERENCES authors(id),\n"
            "  year_published INT\n"
            ");\n"
            "\n"
            "CREATE TABLE borrowings (\n"
            "  id SERIAL PRIMARY KEY,\n"
            "  book_id INT REFERENCES books(id),\n"
            "  borrower TEXT NOT NULL,\n"
            "  borrowed_on DATE DEFAULT CURRENT_DATE\n"
            ");\n"
            "\n"       
            "-- Insert authors\n"
            "INSERT INTO authors (name) VALUES ('George Orwell'), ('Haruki Murakami');\n"
            "\n"
            "-- Insert books\n"
            "INSERT INTO books (title, author_id, year_published) VALUES\n"
            "('1984', 1, 1949),\n"
            "('Norwegian Wood', 2, 1987),\n"
            "('Kafka on the Shore', 2, 2002);\n"
            
            "-- Insert borrowings\n"
            "INSERT INTO borrowings (book_id, borrower) VALUES\n"
            "(1, 'Alice'),\n"
            "(3, 'Bob');\n"
            "\n"   
            "SELECT b.title, a.name AS author\n"
            "FROM books b\n"
            "JOIN authors a ON b.author_id = a.id;",
        "instantiation_notice": "Students can Access the server via "
                                "'psql -h <ip-address> -U <username> -d <db_name>'",
        "fixed_ram_gb": "1",
        "fixed_disk_gb": "10",
        "fixed_cores": "1",
        "volume_size_gb": "0",
        "public": False,
        "instantiation_attributes": [],
        "account_attributes": [{"name": "username"}, {"name": "db_name"}, {"name": "password"}],
        "script":   "# Create a temporary config file\n"
                    "  - path: /tmp/pg_hba.conf\n"
                    "    permissions: '0644'\n"
                    "    content: |\n"
                    "      # TYPE  DATABASE        USER            ADDRESS                 METHOD\n"
                    "      local   all             all                                     peer\n"
                    "      host    all             all             0.0.0.0/0               md5\n"
                    "      host    all             all             ::/0                    md5\n"
                    "\n"
                    "# Install PostgreSQL and useful extensions\n"
                    "packages:\n"
                    "  - postgresql\n"
                    "  - postgresql-contrib\n"
                    "\n"
                    "# Write PostgreSQL configuration files to temporary paths.\n"
                    "# These will be copied into place *after* cluster is initialized.\n"
                    "\n"
                    "runcmd:\n"
                    "  # Explicitly initialize PostgreSQL cluster (not always done automatically)\n"
                    "  #- pg_createcluster 14 main --start\n"
                    "\n"
                    "  # Stop PostgreSQL to apply changes\n"
                    "  - systemctl stop postgresql\n"
                    "\n"
                    "  # Overwrite default configuration files with custom versions\n"
                    "  - cp /tmp/pg_hba.conf /etc/postgresql/14/main/pg_hba.conf\n"
                    "  - sed -i \"/^#listen_addresses =/c\listen_addresses = '*'\" "
                        "/etc/postgresql/14/main/postgresql.conf\n"
                    "  - sed -i \"/^#max_connections =/c\max_connections = 100\" "
                        "/etc/postgresql/14/main/postgresql.conf\n"
                    "  - chown postgres:postgres /etc/postgresql/14/main/*.conf\n"
                    "\n"
                    "  # Restart PostgreSQL to apply new configuration\n"
                    "  - systemctl restart postgresql\n"
                    "\n"
                    "  # Set password for default 'postgres' user\n"
                    "  - sudo -u postgres psql -c \"ALTER USER postgres PASSWORD 'adminpass';\"\n"
                    "\n"
                    "    # Loop through user:db_name entries to create roles and databases\n"
                    "  - |\n"
                    "    while IFS=':' read -r username db_name password; do\n"
                    "      sudo -u postgres psql -c "
                        "\"CREATE ROLE $username WITH LOGIN PASSWORD '$password';\"\n"
                    "      sudo -u postgres psql -c "
                        "\"CREATE DATABASE $db_name OWNER $username;\"\n"
                    "    done < /etc/users.txt\n"
                    "\n"
                    "  # Restart again --> ensure all changes are active (optional)\n"
                    "  - systemctl restart postgresql\n"
                    "\n"
                    "# Final confirmation message in cloud-init log\n"
                    "final_message: \"PostgreSQL teaching server is ready.\"\n"
    },
    "openstack_devstack": {
        "name": "OpenStack DevStack",
        "short_description": "Self-hosted OpenStack environment",
        "description": "This template installs DevStack on an Ubuntu instance for individual "
                       "OpenStack experiments.",
        "instantiation_notice": "The initialization takes several minutes, "
                                "the pre-configured users are 'admin' and 'demo' with the password 'secret'.",
        "fixed_ram_gb": "2",
        "fixed_disk_gb": "10",
        "fixed_cores": "2",
        "public": False,
        "instantiation_attributes": [],
        "account_attributes": [],
        "script": "packages:\r\n  - git\r\n  - sudo\r\n  - python3-pip\r\n\r\n"
                  "runcmd:\r\n  - cd /home/ubuntu\r\n  "
                  "- git clone https://opendev.org/openstack/devstack.git\r\n"
                  "  - chown -R ubuntu:ubuntu devstack\r\n  - echo '[[local|localrc]]' >"
                  " /home/ubuntu/devstack/local.conf\r\n"
                  "  - echo 'ADMIN_PASSWORD=secret' >> /home/ubuntu/devstack/local.conf\r\n"
                  "  - echo 'DATABASE_PASSWORD=$ADMIN_PASSWORD' >> /home/ubuntu/devstack/local.conf\r\n"
                  "  - echo 'RABBIT_PASSWORD=$ADMIN_PASSWORD' >> /home/ubuntu/devstack/local.conf\r\n"
                  "  - echo 'SERVICE_PASSWORD=$ADMIN_PASSWORD' >> /home/ubuntu/devstack/local.conf\r\n"
                  "  - echo \"HOST_IP=$(hostname -I | awk '{print \\$1}')\" >> "
                  "/home/ubuntu/devstack/local.conf\r\n"
                  "  - su - ubuntu -c \"/home/ubuntu/devstack/stack.sh\"\r\n\r\n"
                  "final_message: \"DevStack-Installation completed.\""
    }
}