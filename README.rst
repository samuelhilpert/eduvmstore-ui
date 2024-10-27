EduVMStore
==========

This repo contains the UI for the EduVMStore, which can be found under the following link:
https://github.com/samuelhilpert/eduvmstore.git

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
