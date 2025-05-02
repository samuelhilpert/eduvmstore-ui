from django.views import generic
from django.shortcuts import render, redirect
import logging
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from openstack_dashboard.api import neutron, nova, cinder
from myplugin.content.eduvmstore.utils import get_app_template, generate_cloud_config
import re
import time

class InstancesView(generic.TemplateView):
    """
        View for displaying instances, including form input for instance creation.
    """
    template_name = 'eduvmstore_dashboard/eduvmstore/instances.html'
    page_title = _("Launch")

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to create multiple instances.

        This method processes the form data submitted via POST request to create multiple instances
        based on the provided AppTemplate. It handles the creation of key pairs, user data,
        and metadata for each instance, and initiates the instance creation process using the Nova API.

        :param request: The incoming HTTP request.
        :type request: HttpRequest
        :param args: Additional positional arguments.
        :type args: tuple
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return:HTTP response redirecting to the success page or rendering the form with error message.
        :rtype: HttpResponse
        """
        try:
            num_instances = int(request.POST.get('instance_count', 1))
            base_name = request.POST.get('instances_name')
            app_template = get_app_template(self.request, self.kwargs['image_id'])
            image_id = app_template.get('image_id')
            script = app_template.get('script')
            app_template_name = app_template.get('name')
            app_template_description = app_template.get('description')
            created = app_template.get('created_at', '').split('T')[0]
            volume_size = int(app_template.get('volume_size_gb') or 0)
            ssh_user_requested = app_template.get('ssh_user_requested', False)

            for key in list(request.session.keys()):
                if key.startswith("ip_addresses_") or key.startswith("keypair_name_") or \
                        key.startswith("private_key_"):
                    request.session.pop(key, None)

            request.session.pop("keypair_name", None)
            request.session.pop("private_key", None)
            request.session.pop("image_id", None)
            request.session.pop("ssh_user_requested", None)


            request.session["app_template"] = app_template_name
            request.session["created"] = created
            request.session["num_instances"] = num_instances
            request.session["base_name"] = base_name
            request.session["image_id"] = image_id
            request.session["ssh_user_requested"] = ssh_user_requested

            separate_keys = request.POST.get("separate_keys", "false").lower() == "true"
            request.session["separate_keys"] = separate_keys

            security_groups = [sg["name"] for sg in app_template.get("security_groups", [])]

            instances = []
            shared_keypair_name = f"{base_name}_shared_key"
            shared_private_key = None

            if not separate_keys:
                existing_keypairs = {kp.name for kp in nova.keypair_list(request)}
                if shared_keypair_name in existing_keypairs:
                    request.session["keypair_name"] = shared_keypair_name
                    request.session["private_key"] = None
                else:
                    keypair = nova.keypair_create(request, name=shared_keypair_name)
                    shared_private_key = keypair.private_key
                    request.session["keypair_name"] = shared_keypair_name
                    request.session["private_key"] = shared_private_key

            for i in range(1, num_instances + 1):
                instance_name = f"{base_name}-{i}"
                flavor_id = request.POST.get(f'flavor_id_{i}')
                network_id = request.POST.get(f'network_id_{i}')
                network_name = self.get_network_name_by_id(request, network_id)
                use_existing = request.POST.get(f"use_existing_volume_{i}")
                create_volume_size = request.POST.get(f"volume_size_{i}")
                user_count = request.POST.get(f"user_count_{i}", 0)
                accounts = []
                instantiations = []
                try:
                    volume_size = int(create_volume_size)
                except ValueError:
                    volume_size = 1



                if int(user_count) > 0:
                    try:
                        accounts = self.extract_accounts_from_form_new(request, i)
                    except Exception:
                        accounts = []

                request.session[f"accounts_{i}"] = accounts
                request.session[f"names_{i}"] = instance_name


                try:
                    instantiations = self.extract_accounts_from_form_instantiation(request, i)
                except Exception:
                    instantiations = []

                request.session[f"instantiations_{i}"] = instantiations

                description = self.format_description(app_template_description)


                if not script and not accounts:
                    user_data = None
                elif not script and accounts:
                    user_data = generate_cloud_config(accounts, None, instantiations)
                elif script and int(user_count) == 0:
                    user_data = f"#cloud-config\n{script}"
                else:
                    user_data = generate_cloud_config(accounts, script, instantiations)

                nics = [{"net-id": network_id}]
                if separate_keys:
                    keypair_name = f"{instance_name}_keypair"
                    existing_keypairs = {kp.name for kp in nova.keypair_list(request)}

                    if keypair_name in existing_keypairs:
                        request.session[f"keypair_name_{i}"] = keypair_name
                        request.session[f"private_key_{i}"] = None
                    else:
                        keypair = nova.keypair_create(request, name=keypair_name)
                        private_key = keypair.private_key
                        request.session[f"keypair_name_{i}"] = keypair_name
                        request.session[f"private_key_{i}"] = private_key
                else:
                    keypair_name = shared_keypair_name

                metadata = {"App_Template": app_template_name}
                for index, account in enumerate(accounts):
                    user_data_account = ", ".join([f"{key}: {value}" for key, value in account.items()])
                    metadata[f"User_{index + 1}"] = user_data_account
                for index, instantiation in enumerate(instantiations):

                    parts = []
                    current_part = ""
                    for kv_pair in [f"{key}: {value}" for key, value in instantiation.items()]:

                        if len(current_part) + len(kv_pair) + 2 > 255:
                            parts.append(current_part.rstrip(", "))
                            current_part = ""
                        current_part += kv_pair + ", "
                    if current_part:
                        parts.append(current_part.rstrip(", "))

                    for part_index, part_content in enumerate(parts):
                        key = f"Instantiation_{index+1}_Part{part_index+1}"
                        metadata[key] = part_content

                block_device_mapping_v2 = []

                # OpenStack only allows Volumes larger than 1 GB
                if use_existing == "new" and volume_size >= 1:

                    volume_name = f"{instance_name}-volume"
                    # Create Volume via Cinder
                    volume_type = self.get_available_volume_types(request)
                    volume = cinder.volume_create(
                        request,
                        size=volume_size,
                        name=volume_name,
                        description=f"Extra volume for {instance_name}",
                        volume_type=volume_type
                    )
                    volume = self.wait_for_volume_available(request, volume.id)

                    # Attach an additional block device (a virtual disk) to the instance.
                    block_device_mapping_v2.append({
                        "boot_index": -1,
                        "uuid": volume.id,
                        "source_type": "volume",
                        "destination_type": "volume",
                        "delete_on_termination": True,
                        "device_name": "/dev/vdb",
                    })
                elif use_existing == "none":
                    logging.info(f"Skipping {instance_name}")
                elif use_existing == "new" and volume_size < 1:
                    logging.error(f"Volume size must be at least 1 GB. Skipping {instance_name}.")
                else:
                    block_device_mapping_v2.append({
                        "boot_index": -1,
                        "uuid": use_existing,
                        "source_type": "volume",
                        "destination_type": "volume",
                        "delete_on_termination": True,
                        "device_name": "/dev/vdb",
                    })

                created_server = nova.server_create(
                    request,
                    name=instance_name,
                    image=image_id,
                    flavor=flavor_id,
                    key_name=keypair_name,
                    user_data=user_data,
                    security_groups=security_groups,
                    nics=nics,
                    meta=metadata,
                    description=description,
                    block_device_mapping_v2=block_device_mapping_v2,
                )

                server = self.wait_for_server(request, created_server.id)
                ip_list = self.wait_for_ip_in_network(request, server.id, network_name)
                request.session[f"ip_addresses_{i}"] = ip_list
                instances.append(instance_name)

            return redirect(reverse('horizon:eduvmstore_dashboard:eduvmstore:success'))

        except Exception as e:
            logging.error(f"Failed to create instances: {e}")
            modal_message = _(f"Failed to create instances. Error: {e}")

        context = self.get_context_data(modal_message=modal_message)
        return render(request, self.template_name, context)

    def get_available_volume_types(self, request):
        try:

            volume_types = cinder.volume_type_list(request)
            if not volume_types:
                logging.error("No volume types available.")
                return None
            # choose the first volume type
            return volume_types[0].name
        except Exception as e:
            logging.error(f"Error during get volume types: {e}")
            return None

    def wait_for_volume_available(self, request, volume_id, timeout=60):
        """
        Wait for a volume to become available within a specified timeout period.

        This function repeatedly checks the status of a volume until it becomes available
        or an error occurs. If the volume does not become available within the timeout period,
        a TimeoutError is raised.

        :param request: The incoming HTTP request.
        :type request: HttpRequest
        :param volume_id: The ID of the volume to check.
        :type volume_id: str
        :param timeout: The maximum time to wait for the volume to become available, in seconds.
        :type timeout: int
        :return: The volume object if it becomes available.
        :rtype: Volume
        :raises TimeoutError: If the volume does not become available within the timeout period.
        :raises Exception: If the volume status is 'error'.
        """
        for i in range(timeout):
            volume = cinder.volume_get(request, volume_id)
            if volume.status == "available":
                return volume
            elif volume.status == "error":
                raise Exception(f"Volume {volume_id} failed to build.")
            time.sleep(1)
        raise TimeoutError(f"Timeout while waiting for volume {volume_id} to become available.")

    def get_network_name_by_id(self, request, network_id):
        try:
            networks = neutron.network_list(request)
            for network in networks:
                if network.id == network_id:
                    return network.name
        except Exception as e:
            logging.error(f"Failed to resolve network name: {e}")
        return None


    def wait_for_ip_in_network(self, request, server_id, network_name, timeout=30):
        """
        Wait for an IP address from a specific network.

        This method repeatedly checks if an IP address is available for a server in a given network.
        If an IP address is found, it is returned. Otherwise, after the timeout, a list with an error
        message is returned.

        :param request: The incoming HTTP request.
        :type request: HttpRequest
        :param server_id: The ID of the server for which the IP address is being searched.
        :type server_id: str
        :param network_name: The name of the network in which the IP address is being searched.
        :type network_name: str
        :param timeout: The maximum wait time in seconds before the search is aborted.
        :type timeout: int
        :return: The found IP address or a list with an error message.
        :rtype: str or list
        """
        for i in range(timeout):
            try:
                server = nova.server_get(request, server_id)
                addresses = server.addresses.get(network_name)
                if addresses:
                    ip_list = [addr.get("addr") for addr in addresses if addr.get("addr")]
                    if ip_list:
                        return ip_list[0] if ip_list else f"No IP found in network '{network_name}'"
            except Exception as e:
                logging.debug(f"IP attempt {i+1}/{timeout} for network '{network_name}': {e}")
            time.sleep(1)

        return [f"No IP found in the network '{network_name}'"]


    def wait_for_server(self, request, instance_id, timeout=30):
        """
        Wait until an instance appears in the Nova API.

        This method repeatedly checks if an instance with the given ID is available in the Nova API.
        If the instance is found, it is returned. If the instance does not appear within the timeout
        period, an exception is raised.

        :param request: The incoming HTTP request.
        :type request: HttpRequest
        :param instance_id: The ID of the instance to wait for.
        :type instance_id: str
        :param timeout: The maximum time to wait for the instance, in seconds.
        :type timeout: int
        :return: The instance object if found.
        :rtype: Server
        :raises Exception: If the instance is not found within the timeout period.
        """
        for i in range(timeout):
            try:
                server = nova.server_get(request, instance_id)
                if server:
                    return server
            except Exception as e:
                logging.debug(f"Waiting for instance {instance_id}: Attempt {i + 1}, Error: {e}")
            time.sleep(1)
        raise Exception(f"Instance {instance_id} could not be found after {timeout} seconds.")






    def get_context_data(self, **kwargs):
        """
            Add form and optional image ID to the context for rendering the template.

            :param kwargs: Additional context parameters.
            :return: Context dictionary containing the form and image ID if specified.
            :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        app_template_id = self.kwargs['image_id']
        app_template = get_app_template(self.request, self.kwargs['image_id'])


        # Fetch available flavors from Nova
        context['flavors'] = self.get_flavors(app_template)

        # Context for the selected AppTemplate --> Display system infos
        context['app_template'] = app_template

        # Fetch available networks
        context['networks'] = self.get_networks()

        # Include the app_template_id in the context
        context['app_template_id'] = app_template_id

        context['expected_account_fields'] = self.get_expected_fields()

        context['expected_instantiation_fields'] = self.get_expected_fields_instantiation()

        context['volume_size'] =  int(app_template.get('volume_size_gb') or 0)

        volumes = cinder.volume_list(self.request)
        attachable_volumes = [volume for volume in volumes if volume.status == "available"]
        context['attachable_volumes'] = attachable_volumes

        has_attachable_volumes = len(attachable_volumes) > 0
        context['hasAttachableVolumes'] = has_attachable_volumes

        context['page_title'] = self.page_title

        return context


    def get_flavors(self, app_template):
        """
        Fetch all available flavors from Nova and filter them based on the system requirements
        specified in the AppTemplate.

        :param app_template: The AppTemplate containing system requirements.
        :type app_template: dict
        :return: A dictionary containing all flavors, suitable flavors, and the selected flavor.
        :rtype: dict
        """
        try:
            flavors = nova.flavor_list(self.request)
            if not flavors:
                logging.error("No flavors returned from Nova API.")
                return {}

            flavor_dict = {str(flavor.id): flavor for flavor in flavors}
            logging.info(f"Found {len(flavors)} flavors.")

            suitable_flavors = {}

            for flavor_id, flavor in flavor_dict.items():
                suitable_flavors[flavor_id] = {
                    'name': flavor.name,
                    'ram': flavor.ram,
                    'disk': flavor.disk,
                    'cores': flavor.vcpus
                }

            if not suitable_flavors:
                logging.warning("No suitable flavors found for the given requirements.")


            result = {
                'flavors': {flavor_id: flavor.name for flavor_id, flavor in flavor_dict.items()},
                'suitable_flavors': suitable_flavors
            }

            logging.info(f"Returning flavor data: {result}")
            return result

        except Exception as e:
            logging.error(f"An error occurred while fetching flavors: {e}")
            return {}



    def get_expected_fields(self):
        """
        Retrieve the expected fields for account creation from the AppTemplate.

        This function fetches the AppTemplate and extracts the account attributes,
        which are the expected fields for account creation.

        :return: A list of expected field names for account creation.
        :rtype: list
        """
        app_template = get_app_template(self.request, self.kwargs['image_id'])


        account_attributes = app_template.get('account_attributes')

        account_attribute = [attr['name'] for attr in account_attributes]
        return account_attribute

    def extract_accounts_from_form_new(self, request, instance_id):
        """
        Extract account information from the form data for a specific instance.

        This function retrieves the expected fields for account creation, extracts the corresponding
        data from the POST request for the specified instance, and compiles it into a list of account
        dictionaries.

        :param request: The incoming HTTP request containing form data.
        :type request: HttpRequest
        :param instance_id: The ID of the instance for which to extract account data.
        :type instance_id: int
        :return: A list of dictionaries, each containing account information for the specified instance.
        :rtype: list
        """
        accounts = []
        expected_fields = self.get_expected_fields()

        extracted_data = {
            field: request.POST.getlist(f"{field}_{instance_id}")
            for field in expected_fields
        }

        num_entries = len(next(iter(extracted_data.values()), []))

        for i in range(num_entries):
            account = {field: extracted_data[field][i] for field in expected_fields}
            accounts.append(account)

        return accounts

    def get_expected_fields_instantiation(self):
        """
        Retrieve the expected fields for account creation from the AppTemplate.

        This function fetches the AppTemplate and extracts the instantiation attributes,
        which are the expected fields for account creation.

        :return: A list of expected field names for account creation.
        :rtype: list
        """
        app_template = get_app_template(self.request, self.kwargs['image_id'])

        instantiation_attributes = app_template.get('instantiation_attributes')

        instantiation_attribute = [attr['name'] for attr in instantiation_attributes]
        return instantiation_attribute

    def extract_accounts_from_form_instantiation(self, request, instance_id):
        """
        Extract account information from the form data for a specific instance.

        This function retrieves the expected fields for account creation, extracts the corresponding
        data from the POST request for the specified instance, and compiles it into a list of account
        dictionaries.

        :param request: The incoming HTTP request containing form data.
        :type request: HttpRequest
        :param instance_id: The ID of the instance for which to extract account data.
        :type instance_id: int
        :return: A list of dictionaries, each containing account information for the specified instance.
        :rtype: list
        """
        instantiations = []
        expected_fields_instantiation = self.get_expected_fields_instantiation()

        extracted_data_instantiations = {
            field: request.POST.getlist(f"{field}_{instance_id}_instantiation")
            for field in expected_fields_instantiation
        }

        num_entries = len(next(iter(extracted_data_instantiations.values()), []))

        for i in range(num_entries):
            instantiation = {field: extracted_data_instantiations[field][i]
                             for field in expected_fields_instantiation}
            instantiations.append(instantiation)

        return instantiations

    def get_networks(self):
        """
        Fetch networks from Neutron for the current tenant.

        This function retrieves the list of networks available to the current tenant
        by making a call to the Neutron API. It returns a dictionary mapping network
        IDs to network names.

        :return: A dictionary where the keys are network IDs and the values are network names.
        :rtype: dict
        """
        try:
            tenant_id = self.request.user.tenant_id
            networks = neutron.network_list_for_tenant(self.request, tenant_id)
            return {network.id: network.name for network in networks}
        except Exception as e:
            logging.error(f"Unable to fetch networks: {e}")
            return {}



    def format_description(self, description):
        """
    Format the given description by removing extra whitespace and truncating it to a maximum length.

    This function removes any extra whitespace from the description and ensures that the resulting
    string does not exceed 255 characters in length.

    :param description: The description string to be formatted.
    :type description: str
    :return: The formatted description string.
    :rtype: str
    """
        description = re.sub(r'\s+', ' ', description)
        description = description[:255]
        return description