// cloudinit_snippets.js
const scriptSnippets = {
    ssh_script: {
        runcmd: [
            `# Create directory for private keys
mkdir -p /home/ubuntu/user_keys
chmod 700 /home/ubuntu/user_keys
chown ubuntu:ubuntu /home/ubuntu/user_keys

while IFS=: read -r username password; do
  if ! id "$username" &>/dev/null; then
    useradd -m -s /bin/bash "$username"
    echo "$username:$password" | chpasswd
  fi
  sudo -u "$username" mkdir -p /home/"$username"/.ssh
  chmod 700 /home/"$username"/.ssh
  sudo -u "$username" ssh-keygen -t rsa -b 2048 -f /home/"$username"/.ssh/id_rsa -N ""
  cat /home/"$username"/.ssh/id_rsa.pub >> /home/"$username"/.ssh/authorized_keys
  chmod 600 /home/"$username"/.ssh/authorized_keys
  chown -R "$username:$username" /home/"$username"/.ssh
  cp /home/"$username"/.ssh/id_rsa /home/ubuntu/user_keys/"$username"_id_rsa
  chmod 600 /home/ubuntu/user_keys/"$username"_id_rsa
  chown ubuntu:ubuntu /home/ubuntu/user_keys/"$username"_id_rsa
done < /etc/users.txt

# SSH configuration: Disable password login
sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
systemctl restart ssh`
        ]
    },

    basic_upgrade: {
        package_update: true,
        package_upgrade: true,
        packages: [],
        runcmd: []
    },

    user_creation: {
        runcmd: [
            `while IFS=':' read -r username password; do
if ! id "$username" &>/dev/null; then
useradd -m -s "/bin/bash" "$username"
echo "$username:$password" | chpasswd
fi
done < /etc/users.txt`
        ]
    }
};
