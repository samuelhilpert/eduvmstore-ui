# EduVMStore installation instructions 

This document describes how to install the product “EduVMStore”. It is divided into two parts: Backend installation and front-end installation.
It might be necessary to start the frontend first as this also starts openstack. Only then can the backend be started inside the frontend.

## Backend installation
You can find the backend installation instructions in the [Backend Repository](https://github.com/samuelhilpert/eduvmstore/blob/dev/backend_setup.md).
For production, it is recommended to follow the cloud-init script approach.

## Frontend installation

### 1: With DevStack (recommended for development)
[Devstack](https://docs.openstack.org/devstack/latest/) is "a series of extensible scripts used to quickly bring up a complete OpenStack environment". We advice using it for the development testing of the EduVMstore UI Plugin.

To set up the EduVMStore on a DevStack environment, a DevStack environment is required first. This installation uses a simple Ubuntu server environment (in our case Ubuntu 22.04).
- On `https://stack.dhbw.cloud/` create a new instance (Virtual Machine)
  - At Source choose Image Ubuntu 22.04 
  - Select no new Volume
  - Choose a large Flavor of choice (Recommendation: m1_extra_large)
  - Choose Network: provider_912
  - Choose a Security Group that inhabits the following: Allows inbound (ingress) on ports 22 and 8000 from the IP address of the Backend VM.
  - Choose your SSH Keypair of your choice: Used to access the VM through ssh 
  - At Configuration choose the Cloud-Init-Script [devstack_frontendscript.yaml](/devstack_frontendscript.yaml). This automatically sets up the DevStack environment (see [OpenStack Devstack installation](https://docs.openstack.org/devstack/latest/)) with the local.conf file and adds the EduVMStore UI Plugin in there.
  - Launch the Instance

- After the instance is launched, use SSH to connect to the instance.

- Execute the following command to start the script:
```bash
/tmp/init.sh
```

- After the script is finished, the DevStack environment is set up. The script automatically creates a local.conf file in the devstack folder. This file contains the configuration for the DevStack environment and the EduVMStore UI Plugin.

- To switch the branch navigate to `devstack/local.conf`. Change this line (if not existing add it in the beginning):
```ini
enable_plugin eduvmstore-ui https://github.com/samuelhilpert/eduvmstore-ui main
```
to the branch you want to use
```ini
enable_plugin eduvmstore-ui https://github.com/samuelhilpert/eduvmstore-ui <your-branch>
```


- Start the DevStack environment by executing the following command (also known as stacking, this takes a while) This loads the github repository if there is no folder named `eduvmstore-ui` in the `devstack` folder. If there is a folder named `eduvmstore-ui`, delete it before preceding.
```bash
devstack/stack.sh
```

After successful execution, the EduVMStore is visible in DevStack as a dashboard after login.

Before stacking again be sure to run the following commands:
```bash
devstack/unstack.sh
```
and remove the eduvmstore-ui folder:
```bash
rm -rf eduvmstore-ui
```
If anythin looks weird also run:
```bash
devstack/clean.sh
```
If you want to test a new branch, don't forget to change it in the local.conf

## Installation Guide for Kolla-Ansible (recommended for production)
[Kolla-Ansible](https://docs.openstack.org/kolla-ansible/latest/) is a production-ready OpenStack deployment tool
that uses Docker containers and Ansible playbooks to deploy OpenStack services.
Our current approach uses a manual step of adding the plugin during the kolla ansible installation.
This means it needs to be manually done for every deployment.

Beware that this installation was specifically designed for a specific infrastructure and might not work on other kolla ansible configurations.

Please also refer to the excel sheet which lists the installation steps.

Preconditions:
- Keystone is used for authentication in the backend. Therefore, Keystone's IP and Port must be accessible for the backend IP in the security group of keystones docker. In a standard OpenStack installation, Keystone runs on port 5000.
- In the globals.yml file, `enable_cinder` must be set to `yes` to enable Cinder. This is necessary for the backend to work properly.

After the Setup of Openstack, EduVMStore can be added.
- Open the Horizon container:
```bash
sudo docker exec -it horizon bash
``` 
- For launching the EduVMStore UI Plugin, you can use a script or do it manually. 
- The script is located in [kolla_frontendscript.yaml](/kolla_frontendscript.yaml):
  - Open the horizon container `sudo docker exec -it horizon`
  - Copy the script to the horizon container
  - Execute the script with the following command 
  - Leave the container with `exit`
  - Restarts the horizon container with `sudo docker restart horizon`
  ```bash
  - Open the Horizon dashboard via the IP-Address of the docker in your browser and log in.

- Alternatively, you can do it manually:
    - Clone the EduVMStore-UI repository in the site-packages folder:
  ```bash
  cd /var/lib/kolla/venv/lib/python3.12/site-packages/
  git clone https://github.com/samuelhilpert/eduvmstore-ui.git
  ```
  - Move the folder with the plugin `myplugin` to the correct location in the horizon container:
  ```bash
  mv eduvmstore-ui/myplugin .
  rm -rf eduvmstore-ui
  ```
  - Now horizon needs to know about the new plugin. Therefore the enable files must be on the correct folder. First, navigate to the enabled folder:
  ```bash
  cd /var/lib/kolla/venv/lib/python3.12/site-packages/openstack_dashboard/enabled/
  ```
  - Now create symlinks to the enable files from the plugin:
  ```bash
  ln -s /var/lib/kolla/venv/lib/python3.12/site-packages/myplugin/enabled/_31000_my_plugin.py .
  ln -s /var/lib/kolla/venv/lib/python3.12/site-packages/myplugin/enabled/_31100_my_second_plugin.py .
  ln -s /var/lib/kolla/venv/lib/python3.12/site-packages/myplugin/enabled/_31150_tutorial_group.py .
  ln -s /var/lib/kolla/venv/lib/python3.12/site-packages/myplugin/enabled/_31200_tutorial_panel.py .
  ln -s /var/lib/kolla/venv/lib/python3.12/site-packages/myplugin/enabled/_31210_instructions_panel.py .
  ln -s /var/lib/kolla/venv/lib/python3.12/site-packages/myplugin/enabled/_31220_script_panel.py .
  ln -s /var/lib/kolla/venv/lib/python3.12/site-packages/myplugin/enabled/_31230_example_panel.py .
  ln -s /var/lib/kolla/venv/lib/python3.12/site-packages/myplugin/enabled/_31240_admin_instructions_panel.py .
  ln -s /var/lib/kolla/venv/lib/python3.12/site-packages/myplugin/enabled/_32000_my_new_dashboard.py .
  ```
  - For the plugin to work, the library `reportlab` must be installed and the static files must be loaded. This can be done with the following command:
  ```bash
  pip install reportlab
  /var/lib/kolla/venv/bin/python3 /var/lib/kolla/venv/bin/manage.py collectstatic --noinput
  /var/lib/kolla/venv/bin/python3 /var/lib/kolla/venv/bin/manage.py compress --force
  ```
  - Now the horizon container and the plugin is ready to be used. Restart the horizon container to load the new plugin:
  ```bash
  exit
  sudo docker restart horizon
  ```
  
  - Open the Horizon dashboard via the IP-Address of the docker in your browser and log in.

