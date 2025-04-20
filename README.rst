EduVMStore
==========

This repo contains the UI for the EduVMStore, which can be found under the following link:
https://github.com/samuelhilpert/eduvmstore.git

Environment Setup
-----------------

To configure sensitive information and environment-specific settings (for development and testing),
create a `.env` file in the `myplugin` directory. Find the required variables below
(replace `<...>` with your values):

.. code-block:: dotenv

   # env
   BASE_URL=<your-base-url>

In **Production Environment** set these variables in the system environment instead of using a `.env` file.
You can use the `export` command (e.g. `export OPENSTACK_AUTH_URL=<your-openstack-auth-url>`) in your terminal
to set these variables on OS level.

Alternatively, use a process manager like systemd or Docker to manage these variables.

Installation Guide
------------------

1. Install DevStack.

2. Go to the ``Devstack`` folder.

3. Open the file ``local.conf``.

4. Add the following line as the first line:
   
   ``ENABLE_PLUGIN eduvmstore-ui https://github.com/samuelhilpert/eduvmstore-ui main``
   
5. Run the command in the ``Devstack`` folder:

   ``./stack.sh``

6. After successful execution, the EduVMStore is visible in DevStack as a new dashboard after registration.

7. To also run the backend, please follow the steps from the readme of https://github.com/samuelhilpert/eduvmstore.git

Quick Installation using Cloud-Init-Script
==========================================

1. Go to `https://stack.dhbw.cloud/ <https://stack.dhbw.cloud/>` and create a new instance.

2. Under **Source**:
   - Choose **Image as Boot Source**.
   - Select **Ubuntu 22.04** as the image.
   - Do not create a new volume.

3. Select the **Flavor** of your choice.

4. Under **Network**, select **provider_912**.

5. In the **Security Group**, ensure that incoming TCP connections are allowed on the following ports:
   - Port **8000**.
   - Port **22**.

6. Select the **SSH Keypair** of your choice to access the VM via SSH.

7. Under **Configuration**, upload the Cloud-Init script `frontendscript.yaml`.

8. Launch the instance.

9. Once the instance is running, access it via SSH:

   .. code-block:: bash

      ssh ubuntu@<instance-ip> -i <path-to-keyfile>

10. Run the initialization script:

    .. code-block:: bash

       /initilization_script

11. To select the plugin branch used for the installation, the ``devstack/local.conf`` file can be edited.

12. Start the installation with:

    .. code-block:: bash

       ./stack.sh
