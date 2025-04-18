// cloudinit_snippets.js
const scriptSnippets = {
    "ssh_script":"runcmd:\r\n  - |\r\n    # Create directory for private keys\r\n    " +
        "mkdir -p /home/ubuntu/user_keys\r\n    chmod 700 /home/ubuntu/user_keys\r\n    " +
        "chown ubuntu:ubuntu /home/ubuntu/user_keys\r\n\r\n    # Set first user account as admin\r\n    " +
        "FIRST_USER=$(head -n 1 /etc/users.txt | cut -d':' -f1)\r\n\r\n    # Create users\r\n    " +
        "while IFS=: read -r username password; do\r\n      if ! id \"$username\" &>/dev/null; then\r\n " +
        "       useradd -m -s /bin/bash \"$username\"\r\n        echo \"$username:$password\" | " +
        "chpasswd\r\n      fi\r\n\r\n      # Create SSH directory and key\r\n      " +
        "sudo -u \"$username\" mkdir -p /home/\"$username\"/.ssh\r\n      " +
        "chmod 700 /home/\"$username\"/.ssh\r\n\r\n      # Generate SSH key\r\n      " +
        "sudo -u \"$username\" ssh-keygen -t rsa -b 2048 -f " +
        "/home/\"$username\"/.ssh/id_rsa -N \"\"\r\n\r\n      # Set Public Key as authorized_key\r\n    " +
        "  cat /home/\"$username\"/.ssh/id_rsa.pub >> /home/\"$username\"/.ssh/authorized_keys\r\n    " +
        "  chmod 600 /home/\"$username\"/.ssh/authorized_keys\r\n      " +
        "chown -R \"$username:$username\" /home/\"$username\"/.ssh\r\n\r\n     " +
        " # Secure private keys for the admin & Ubuntu user\r\n      " +
        "cp /home/\"$username\"/.ssh/id_rsa /home/ubuntu/user_keys/\"$username\"_id_rsa\r\n     " +
        " chmod 600 /home/ubuntu/user_keys/\"$username\"_id_rsa\r\n      " +
        "chown ubuntu:ubuntu /home/ubuntu/user_keys/\"$username\"_id_rsa\r\n    " +
        "done < /etc/users.txt\r\n\r\n    # Set first user as admin\r\n    " +
        "if [ -n \"$FIRST_USER\" ]; then\r\n      echo \"$FIRST_USER ALL=(ALL) NOPASSWD:ALL\" > " +
        "/etc/sudoers.d/$FIRST_USER\r\n      chmod 440 /etc/sudoers.d/$FIRST_USER\r\n    fi\r\n\r\n  " +
        "  # SSH configuration: Disable password login\r\n    " +
        "sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config\r\n    " +
        "sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config\r\n   " +
        " systemctl restart ssh",

    "base_configuration":'package_update: true\\r\\npackage_upgrade: ' +
        'true\\r\\n\\r\\npackages:\\r\\n  - \\r\\n\\r\\nruncmd:\\r\\n  ' +
        '-\\r\\n\\r\\nfinal_message: \\"\\"',

    "user_add":'runcmd:\\r\\n  - |\\r\\n    while IFS=\':\' read -r username password; do\\r\\n    ' +
        '  if ! id \\"$username\\" &>/dev/null; then\\r\\n      ' +
        '  useradd -m -s \\"/bin/bash\\" \\"$username\\"\\r\\n      ' +
        '  echo \\"$username:$password\\" | chpasswd\\r\\n      fi\\r\\n    done < /etc/users.txt',

    "sshscript_base_configuration":"package_update: true\\\\r\\\\npackage_upgrade:\n" +
        "    true\\\\r\\\\n\\\\r\\\\npackages:\\\\r\\\\n  - \\\\r\\\\n\\\\r\\\\nruncmd:\r\n  - |\r\n  " +
        "  # Create directory for private keys\r\n    " +
        "mkdir -p /home/ubuntu/user_keys\r\n    chmod 700 /home/ubuntu/user_keys\r\n    " +
        "chown ubuntu:ubuntu /home/ubuntu/user_keys\r\n\r\n    # Set first user account as admin\r\n    " +
        "FIRST_USER=$(head -n 1 /etc/users.txt | cut -d':' -f1)\r\n\r\n    # Create users\r\n    " +
        "while IFS=: read -r username password; do\r\n      if ! id \"$username\" &>/dev/null; then\r\n " +
        "       useradd -m -s /bin/bash \"$username\"\r\n        echo \"$username:$password\" | " +
        "chpasswd\r\n      fi\r\n\r\n      # Create SSH directory and key\r\n      " +
        "sudo -u \"$username\" mkdir -p /home/\"$username\"/.ssh\r\n      " +
        "chmod 700 /home/\"$username\"/.ssh\r\n\r\n      # Generate SSH key\r\n      " +
        "sudo -u \"$username\" ssh-keygen -t rsa -b 2048 -f " +
        "/home/\"$username\"/.ssh/id_rsa -N \"\"\r\n\r\n      # Set Public Key as authorized_key\r\n    " +
        "  cat /home/\"$username\"/.ssh/id_rsa.pub >> /home/\"$username\"/.ssh/authorized_keys\r\n    " +
        "  chmod 600 /home/\"$username\"/.ssh/authorized_keys\r\n      " +
        "chown -R \"$username:$username\" /home/\"$username\"/.ssh\r\n\r\n     " +
        " # Secure private keys for the admin & Ubuntu user\r\n      " +
        "cp /home/\"$username\"/.ssh/id_rsa /home/ubuntu/user_keys/\"$username\"_id_rsa\r\n     " +
        " chmod 600 /home/ubuntu/user_keys/\"$username\"_id_rsa\r\n      " +
        "chown ubuntu:ubuntu /home/ubuntu/user_keys/\"$username\"_id_rsa\r\n    " +
        "done < /etc/users.txt\r\n\r\n    # Set first user as admin\r\n    " +
        "if [ -n \"$FIRST_USER\" ]; then\r\n      echo \"$FIRST_USER ALL=(ALL) NOPASSWD:ALL\" > " +
        "/etc/sudoers.d/$FIRST_USER\r\n      chmod 440 /etc/sudoers.d/$FIRST_USER\r\n    fi\r\n\r\n  " +
        "  # SSH configuration: Disable password login\r\n    " +
        "sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config\r\n    " +
        "sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config\r\n   " +
        " systemctl restart ssh ",

    "base_user":'package_update: true\\r\\npackage_upgrade: ' +
        'true\\r\\n\\r\\npackages:\\r\\n  - \\r\\n\\r\\nruncmd:\\r\\n  - |\\r\\n    ' +
        'while IFS=\':\' read -r username password; do\\r\\n    ' +
        '  if ! id \\"$username\\" &>/dev/null; then\\r\\n      ' +
        '  useradd -m -s \\"/bin/bash\\" \\"$username\\"\\r\\n      ' +
        '  echo \\"$username:$password\\" | chpasswd\\r\\n      fi\\r\\n    done < /etc/users.txt\\r\\n  ' +
        '-\\r\\n\\r\\nfinal_message: \\"\\"',

};
