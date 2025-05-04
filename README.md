# EduVMStore

This repo contains the UI for the EduVMStore, which can be found under the following link:  
https://github.com/samuelhilpert/eduvmstore.git

---

## Installation Guide for DevStack

1. **Install DevStack**  
   https://docs.openstack.org/devstack/latest/

2. Go to the `Devstack` folder.

3. Open the file `local.conf`.

4. Add the following line as the first line:

   ```ini
   ENABLE_PLUGIN eduvmstore-ui https://github.com/samuelhilpert/eduvmstore-ui main
   ```

5. Install ReportLab:

   ```bash
   pip install reportlab
   ```

6. Run the following command in the `Devstack` folder:

   ```bash
   ./stack.sh
   ```

7. After successful execution, the EduVMStore is visible in DevStack as a new dashboard after registration.

8. To also run the backend, follow the README at:  
   https://github.com/samuelhilpert/eduvmstore.git

---

## Quick Installation using Cloud-Init Script for DevStack

1. Go to [https://stack.dhbw.cloud/](https://stack.dhbw.cloud/) and create a new instance.

2. Under **Source**:
   - Choose **Image as Boot Source**
   - Select **Ubuntu 22.04**
   - Do **not** create a new volume

3. Select the **Flavor** of your choice.

4. Under **Network**, select **provider_912**.

5. Under **Security Group**, ensure the following ports are open:
   - TCP port **8000**
   - TCP port **22**

6. Choose the **SSH keypair** you want to use.

7. Under **Configuration**, upload the Cloud-Init script `frontendscript.yaml`.

8. Launch the instance.

9. Once the instance is running, SSH into it:

   ```bash
   ssh ubuntu@<instance-ip> -i <path-to-keyfile>
   ```

10. Run the initialization script:

    ```bash
    /initilization_script
    ```

11. If needed, adjust the plugin branch in `devstack/local.conf`.

12. Start the installation:

    ```bash
    ./stack.sh
    ```

---

## Installation Guide for Kolla-Ansible

1. Install OpenStack with Kolla-Ansible.

2. Enter the Horizon container:

   ```bash
   sudo docker exec -it horizon bash
   ```

3. Go to:

   ```bash
   cd /var/lib/kolla/venv/lib/python3.12/site-packages/
   ```

4. Clone the EduVMStore-UI repository:

   ```bash
   git clone https://github.com/samuelhilpert/eduvmstore-ui.git
   ```

5. Move the folder `myplugin` to the correct location:

   ```bash
   mv eduvmstore-ui/myplugin .
   rm -rf eduvmstore-ui
   ```

6. Go to:

   ```bash
   cd /var/lib/kolla/venv/lib/python3.12/site-packages/openstack_dashboard/enabled/
   ```

7. Create symlinks:

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

8. Install ReportLab:

   ```bash
   pip install reportlab
   ```

9. Load all static files:

   ```bash
   /var/lib/kolla/venv/bin/python3 /var/lib/kolla/venv/bin/manage.py collectstatic --noinput
   /var/lib/kolla/venv/bin/python3 /var/lib/kolla/venv/bin/manage.py compress --force
   ```

10. Restart the Horizon container:

   ```bash
   exit
   sudo docker restart horizon
   ```