const ALL_INSTANCES_INDEX = 0
const TAB_PREFIX = 'instanceTab_'
const CONTENT_PREFIX = 'instanceContent_'

let allInstanceChangedFieldInfo = {
    element: null,
    fieldType: ''
};

//Volumes
const attachableVolumes = [
    {% for volume in attachable_volumes %}
{ id: "{{ volume.id }}", name: "{{ volume.name }}", size: {{ volume.size }} },
{% endfor %}
];

function generateVolumeDropdown(instanceIndex) {
    let html = `<option value="" disabled selected>Select Volume</option>`;
    let requiredVolumeSize = {{ volume_size }};
    attachableVolumes.forEach(volume => {
        if (volume.size >= requiredVolumeSize) {
            html += `<option value="${volume.id}" data-volume-id="${volume.id}">
                    ${volume.name} (${volume.size} GB)
                 </option>`;
        }

    });
    return html;
}


document.getElementById("num_instances").addEventListener("input", function () {
    const MAX_NUM_INSTANCES = 100;
    if (this.value > MAX_NUM_INSTANCES) {
        this.value = MAX_NUM_INSTANCES;
    } else if (this.value < 1) {
        this.value = 1;
    }
});

let accountAttributes = {{ expected_account_fields|safe }};
let instantiationAttribute = {{ expected_instantiation_fields|safe }};

function generateFlavorSection(instanceIndex) {
    const labelPrefix = (instanceIndex === ALL_INSTANCES_INDEX ) ? "{{ _('Select Flavor for all Instances') }}" : "{{ _('Select Flavor') }}";
    return `
                 <!-- Flavor Selection -->
                <div class="form-group">
                    <label for="flavor_id_${instanceIndex}">${labelPrefix}</label>
                     <select class="form-control flavor-dropdown"
                            id="flavor_id_${instanceIndex}"
                            name="flavor_id_${instanceIndex}" required>
                     {% if flavors.suitable_flavors %}
                        {% for flavor_id, flavor_data in flavors.suitable_flavors.items %}
                            <option value="{{ flavor_id }}"
                                    data-flavor-details='{"id": "{{ flavor_id }}", "name": "{{ flavor_data.name }}", "ram": {{ flavor_data.ram }}, "disk": {{ flavor_data.disk }}, "vcpus": {{ flavor_data.cores }} }'
                                    {% if flavor_id == flavors.selected_flavor %} selected {% endif %}>
                                {{ flavor_data.name }}
                            </option>
                        {% endfor %}
                        {% else %}
                            <option value="" disabled>{{ _("No suitable flavors found.") }}</option>
                        {% endif %}
                    </select>
                </div>
            `;
}

function generateNetworkSection(instanceIndex) {
    const labelPrefix = (instanceIndex === ALL_INSTANCES_INDEX ) ? "{{ _('Select Network for all Instances') }}" : "{{ _('Select Network') }}";
    return `
                <div class="form-group">
                    <label for="network_id_${instanceIndex}">${labelPrefix}</label>
                    <select class="form-control"
                            id="network_id_${instanceIndex}"
                            name="network_id_${instanceIndex}" required>
                        {% if networks %}
                            {% for network_id, network_name in networks.items %}
                                <option value="{{ network_id }}" {% if loop.first %}selected{% endif %}>{{ network_name }}</option>
                            {% endfor %}
                        {% else %}
                            <option value="" disabled selected>{{ _("No networks available") }}</option>
                        {% endif %}
                    </select>
                </div>
            `;
}

function generateVolumeSection(instanceIndex) {
    return `
                <!-- Volumes -->
                <div class="form-group">
                    <label for="use_existing_volume_${instanceIndex}">{{ _("Additional Volumes") }}</label>
                    <select class="form-control use-existing-volume"
                            id="use_existing_volume_${instanceIndex}"
                            name="use_existing_volume_${instanceIndex}"
                            data-instance="${instanceIndex}">
                        <option value="new" selected>Create new volume</option>
                        {% if hasAttachableVolumes %}
                            <option value="existing">Attach existing volume</option>
                        {% endif %}
                        {% if volume_size == 0 %}
                            <option value="none">No additional volumes</option>
                        {% endif %}
                    </select>
                    {% if not hasAttachableVolumes %}
                        <small class="form-text">There are currently no available volumes that can be attached.</small>
                    {% endif %}
                </div>
                
                <div class="form-group create-volume-size-group" id="create_volume_size_group_${instanceIndex}" style="display: none;">
                    <label for="volume_size_instance_${instanceIndex}">Volume Size (GB)</label>
                    <input type="number" class="form-control" id="volume_size_instance_${instanceIndex}" name="volume_size_instance_${instanceIndex}"  value="{{ volume_size }}" min="{{ volume_size }}">
                </div>
            `;
}

function generateInstantiationAttributesSection(instanceIndex) {
    const sectionTitle = (instanceIndex === ALL_INSTANCES_INDEX ) ? "{{ _('Instantiation Attributes for all Instances') }}" : "{{ _('Instantiation Attributes') }}";

    return `
                <div class="section-container">
                    <h5>${sectionTitle}</h5>
                    <div id="instantiation_section_${instanceIndex}">
                        <div id="dynamic_instantiation_container_${instanceIndex}">
                            ${generateInstantiationFields(instanceIndex)}
                        </div>
                    </div>
                </div>
            `;
}

function generateFixedRessourceSection(instanceIndex){
    return `
                <h5>{{ _("Resource Configuration") }}</h5>

                <!-- Display Fixed Resource Requirements and Available Resources -->
                <div class="alert alert-info mt-3">
                    <p><strong>{{ _("Resource Requirements") }}:</strong></p>
                    <ul>
                        <li>{{ _("RAM") }}: <span id="total_ram_${instanceIndex}"></span> GB </li>
                        <li>{{ _("Disk") }}: <span id="total_disk_${instanceIndex}"></span> GB </li>
                        <li>{{ _("CPU Cores") }}: <span id="total_cores_${instanceIndex}"></span></li>
                    </ul>
                </div>
            `;
}

function generateAccountAttributesSection(instanceIndex){
    return`
                <div class="section-container">
                    <h5>{{ _("User Configuration") }}</h5>
                    <div class="form-group form-check">
                        <input type="checkbox" class="form-check-input no_additional_users" id="no_additional_users_${instanceIndex}" name="no_additional_users_${instanceIndex}" checked>
                        <label class="form-check-label" for="no_additional_users_${instanceIndex}">{{ _("No additional users") }}</label>
                    </div>

                    <div class="form-group mt-3" id="user_count_section_${instanceIndex}" style="display: none;">
                        <label for="user_count_${instanceIndex}">{{ _("Number of Additional Users") }}</label>
                        <input type="number" class="form-control user-count-input" id="user_count_${instanceIndex}" name="user_count_${instanceIndex}" min="1" value="1">
                    </div>

                    <div id="accounts_section_${instanceIndex}" style="display: none;">
                        <!-- CSV Upload -->
                        <div class="form-group" style="display: flex; align-items: center; gap: 10px;">
                            <div style="flex-grow: 1;">
                                <label for="csvUpload_${instanceIndex}">{{ _("Upload CSV") }}</label>
                                <div style="display: flex; align-items: center;">
                                    <input type="file" class="form-control-file csv-upload" id="csvUpload_${instanceIndex}"
                                           data-instance="${instanceIndex}" accept=".csv" style="width: auto;">
                                    <!-- Undo button will be inserted here by JavaScript -->
                                </div>
                            </div>
                        </div>
                        <h6>{{ _("Accounts") }}</h6>
                        <div id="dynamic_accounts_container_${instanceIndex}" class="account-grid"></div>
                        <button type="button" class="btn btn-secondary add_account_btn" data-instance="${instanceIndex}" style="display: none;">{{ _("Add Account") }}</button>
                    </div>
                </div>
            `;
}

function generateNavigationSection(instanceIndex, countInstances){
    return `
                <div class="d-flex justify-content-between mt-3">
                    ${(countInstances != 1 &&  instanceIndex > ALL_INSTANCES_INDEX ) ? `<button type="button" class="btn btn-secondary prev-instance" data-instance="${instanceIndex}">← {{ _("Previous Instance") }}</button>` : ""}
                    ${(instanceIndex < countInstances || instanceIndex === ALL_INSTANCES_INDEX) ? `<button type="button" class="btn btn-primary next-instance" data-instance="${instanceIndex}">→ {{ _("Next Instance") }}</button>` : ""}
                </div>
            `;
}

function generateCSVAllInstanceSection(){
    return`
                <div class="section-container">
                    <h5>{{ _("User Configuration for All Instances") }}</h5>

                    <!-- CSV Upload with Instance Mapping -->
                    <div class="form-group" style="display: flex; align-items: center; gap: 10px;">
                        <div style="flex-grow: 1;">
                            <label for="csvUpload_${ALL_INSTANCES_INDEX}">{{ _("Upload CSV with Instance Mapping") }}</label>
                            <div style="display: flex; align-items: center;">
                                <input type="file" class="form-control-file"
                                       id="csvUpload_${ALL_INSTANCES_INDEX}" accept=".csv" style="width: auto;">
                                <!-- Undo button will be inserted here by JavaScript -->
                            </div>
                            <small class="form-text text-muted">
                                Upload a CSV file with headers: ${accountAttributes.join(", ")}, instance
                            </small>
                        </div>
                    </div>

                    <div id="all_instances_csv_preview" class="mt-3">
                        <!-- CSV preview will be shown here -->
                    </div>
                </div>
            `
}

function singleInstanceTab(instanceName, instanceIndex){
    return `
                <li class="nav-item">
                    <a class="nav-link" id="${TAB_PREFIX}${instanceIndex}" data-toggle="tab" href="#${CONTENT_PREFIX}${instanceIndex}" role="tab">
                        ${instanceName}
                    </a>
                </li>
            `;
}

function singleInstanceContainer(instanceName, instanceIndex, countInstances){
    return`
                <div class="tab-pane" id="${CONTENT_PREFIX}${instanceIndex}" role="tabpanel">
                    <h4 id="instanceTitle_${instanceIndex}">${instanceName}</h4>
                    <input type="hidden" name="generated_instance_name_${instanceIndex}" value="${instanceName}">

                    <div class="section-container">
                        ${generateFixedRessourceSection(instanceIndex)}
                        ${generateFlavorSection(instanceIndex)}
                        ${generateNetworkSection(instanceIndex)}
                        ${generateVolumeSection(instanceIndex)}
                    </div>

                    ${generateInstantiationAttributesSection(instanceIndex)}
                     <!-- All Instances Tab has different Account Section: CSV Upload for all Instances -->
                     ${instanceIndex === ALL_INSTANCES_INDEX ? generateCSVAllInstanceSection() : generateAccountAttributesSection(instanceIndex)}
                    ${generateNavigationSection(instanceIndex, countInstances)}
                </div>
            `
}

function generateInstanceFields() {
    let instanceTabs = document.getElementById("instanceTabs");
    let instancesContainer = document.getElementById("instancesContainer");

    let countInstancesInput = document.getElementById("num_instances");
    //ensure countInstances is a natural number base 10, if not 1
    let countInstances = parseInt(countInstancesInput.value, 10) || 1;
    countInstancesInput.value = countInstances;

    const baseNameInput = document.getElementById("instances_name");
    let baseName = baseNameInput ? baseNameInput.value.trim() : "";

    instanceTabs.innerHTML = "";
    instancesContainer.innerHTML = "";


    // Add all Instance Tab
    if (countInstances > 1) {
        allInstancesName = "All Instances"
        instanceTabs.innerHTML += singleInstanceTab(allInstancesName, ALL_INSTANCES_INDEX)
        instancesContainer.innerHTML += singleInstanceContainer(allInstancesName, ALL_INSTANCES_INDEX, countInstances)
    }
    // Generate individual instance tabs
    for (let i = 1; i <= countInstances; i++) {
        let instanceName = "";
        if (baseName) {
            instanceName = (countInstances === 1) ? baseName : `${baseName}-${i}`;
        }
        instanceTabs.innerHTML += singleInstanceTab(instanceName, i);
        instancesContainer.innerHTML += singleInstanceContainer(instanceName, i, countInstances);
    }

    document.querySelectorAll(".use-existing-volume").forEach(select => {
        select.addEventListener("change", function () {
            const instance = this.dataset.instance;
            const group = document.getElementById(`existing_volume_group_${instance}`);
            const volumeSelect = document.getElementById(`existing_volume_id_${instance}`);
            if (this.value === "existing") {
                group.style.display = "block";
                volumeSelect.required = true;
                volumeSelect.setCustomValidity("");
            } else {
                if (group) group.style.display = "none";
                if (volumeSelect) volumeSelect.required = false;
            }
        });
        select.dispatchEvent(new Event("change"));
    });

    // Select Automatic Flavor for all instances including AllInstanceTab
    for (let i = ALL_INSTANCES_INDEX; i <= countInstances; i++) {
        selectAutomaticFlavor(i);
    }
    startInstanceIndex = (countInstances > 1) ? ALL_INSTANCES_INDEX : 1;
    switchToInstance(startInstanceIndex)
    if (countInstances > 1) {
        attachAllInstancesEventListeners();
    }
    attachInstanceEventListeners();
    attachAccountButtonListeners();
    attachFlavorCalculationListeners();
    attachVolumeOptionListeners();
    attachVolumeChangeHandlers();
}

function attachAllInstancesEventListeners() {
    // Handle "Apply to All Instances" button from the modal
    document.querySelector('.confirm-apply-modal').addEventListener('click', function() {
        applyAllInstancesSettings();
        hideWarningModal();
    });

    // All instance tab value change - ADD THIS TIMEOUT
    setTimeout(() => {
        document.querySelectorAll(`#flavor_id_${ALL_INSTANCES_INDEX}, #network_id_${ALL_INSTANCES_INDEX}, #use_existing_volume_${ALL_INSTANCES_INDEX}, #existing_volume_id_${ALL_INSTANCES_INDEX}`).forEach(element => {
            // Remove existing event listeners to prevent duplicates
            element.removeEventListener('change', showWarningModal);
            element.addEventListener('change', showWarningModal);
        });

        // Add handlers for instantiation attributes if they exist
        if (instantiationAttribute.length > 0) {
            instantiationAttribute.forEach(attr => {
                const element = document.getElementById(`${attr}_${ALL_INSTANCES_INDEX}_instantiation`);
                if (element) {
                    // Remove existing event listeners to prevent duplicates
                    element.removeEventListener('change', showWarningModal);
                    element.addEventListener('change', showWarningModal);
                }
            });
        }
    }, 100);  // Short delay to prevent immediate triggering
    hideWarningModal();
}

function showWarningModal() {
    allInstanceChangedFieldInfo.element = event.target;
    const fieldId = event.target.id;

    // Determine field type based on ID
    switch (true) {
        case fieldId.includes('flavor_id'):
            allInstanceChangedFieldInfo.fieldType = 'flavor';
            break;
        case fieldId.includes('network_id'):
            allInstanceChangedFieldInfo.fieldType = 'network';
            break;
        case fieldId.includes('use_existing_volume'):
            allInstanceChangedFieldInfo.fieldType = 'volume_type';
            break;
        case fieldId.includes('existing_volume_id'):
            allInstanceChangedFieldInfo.fieldType = 'volume_selection';
            break;
        case fieldId.includes('_instantiation'):
            allInstanceChangedFieldInfo.fieldType = 'instantiation';
            allInstanceChangedFieldInfo.attrName = event.target.getAttribute('data-attr-name');
            break;
        default:
            allInstanceChangedFieldInfo.fieldType = 'unknown';
    }

    const warningText = document.querySelector('#allInstancesWarningModal .modal-body p');
    if (warningText) {
        warningText.innerHTML = `<strong>{{ _("Warning:") }}</strong> {{ _("This will apply the selected ") }}
                    <strong>${getFieldTypeDisplayName(allInstanceChangedFieldInfo.fieldType)}</strong>
                    {{ _(" to all individual instances.") }}`;
    }

    $('#allInstancesWarningModal').modal('show');
}

// Helper function to get a display name for the field type
function getFieldTypeDisplayName(fieldType) {
    switch (fieldType) {
        case 'flavor': return 'flavor';
        case 'network': return 'network';
        case 'volume_type': return 'volume type';
        case 'volume_selection': return 'volume selection';
        case 'instantiation':
            return `instantiation attribute "${allInstanceChangedFieldInfo.attrName}"`;
        default: return 'setting';
    }
}

function hideWarningModal(){
    $('#allInstancesWarningModal').modal('hide');
}

function applyAllInstancesSettings() {
    const countInstances = parseInt(document.getElementById('num_instances').value, 10) || 1;

    // Only apply the specific changed setting
    switch (allInstanceChangedFieldInfo.fieldType) {
        case 'flavor':
            const allFlavorSelect = document.getElementById(`flavor_id_${ALL_INSTANCES_INDEX}`);
            if (allFlavorSelect && allFlavorSelect.value) {
                for (let i = 1; i <= countInstances; i++) {
                    const instanceFlavorSelect = document.getElementById(`flavor_id_${i}`);
                    if (instanceFlavorSelect) {
                        instanceFlavorSelect.value = allFlavorSelect.value;
                    }
                }
            }
            break;

        case 'network':
            const allNetworkSelect = document.getElementById(`network_id_${ALL_INSTANCES_INDEX}`);
            if (allNetworkSelect && allNetworkSelect.value) {
                for (let i = 1; i <= countInstances; i++) {
                    const instanceNetworkSelect = document.getElementById(`network_id_${i}`);
                    if (instanceNetworkSelect) {
                        instanceNetworkSelect.value = allNetworkSelect.value;
                    }
                }
            }
            break;

        case 'volume_type':
            const allVolumeOption = document.getElementById(`use_existing_volume_${ALL_INSTANCES_INDEX}`);
            if (allVolumeOption) {
                const volumeChoice = allVolumeOption.value;
                for (let i = 1; i <= countInstances; i++) {
                    const instanceVolumeOption = document.getElementById(`use_existing_volume_${i}`);
                    if (instanceVolumeOption) {
                        instanceVolumeOption.value = volumeChoice;
                        instanceVolumeOption.dispatchEvent(new Event('change'));
                    }
                }
            }
            break;

        case 'volume_selection':
            const allVolumeSelect = document.getElementById(`existing_volume_id_${ALL_INSTANCES_INDEX}`);
            if (allVolumeSelect && allVolumeSelect.value) {
                for (let i = 1; i <= countInstances; i++) {
                    const instanceVolumeSelect = document.getElementById(`existing_volume_id_${i}`);
                    if (instanceVolumeSelect) {
                        instanceVolumeSelect.value = allVolumeSelect.value;
                    }
                }
            }
            break;

        case 'instantiation':
            if (allInstanceChangedFieldInfo.attrName) {
                const allAttrInput = document.getElementById(`${allInstanceChangedFieldInfo.attrName}_${ALL_INSTANCES_INDEX}_instantiation`);
                if (allAttrInput && allAttrInput.value !== undefined) {
                    for (let i = 1; i <= countInstances; i++) {
                        const instanceAttrInput = document.getElementById(`${allInstanceChangedFieldInfo.attrName}_${i}_instantiation`);
                        if (instanceAttrInput) {
                            instanceAttrInput.value = allAttrInput.value;
                        }
                    }
                }
            }
            break;
    }

    allInstanceChangedFieldInfo = { element: null, fieldType: '', attrName: null };
}

function attachVolumeOptionListeners() {
    document.querySelectorAll(".use-existing-volume").forEach(select => {
        select.addEventListener("change", function () {
            const instance = this.dataset.instance;
            const volumeGroup = document.getElementById(`existing_volume_group_${instance}`);
            const selectedVolume = document.getElementById(`existing_volume_id_${instance}`);
            // Check if the volumeGroup and selectedVolumeId exist for attaching existing volumes
            // If they do, toggle their visibility to block or none
            if (volumeGroup && selectedVolume) {
                if (this.value === "existing") {
                    volumeGroup.style.display = "block";
                    selectedVolume.required = true;
                } else {
                    volumeGroup.style.display = "none";
                    selectedVolume.required = false;
                }
            }
            attachVolumeCreateListeners(instance);
        });

        select.dispatchEvent(new Event("change"));

    });
}

function attachVolumeCreateListeners(instance) {
    const volumeSizeInputField = document.getElementById(`create_volume_size_group_${instance}`);
    const volumeModeSelect = document.getElementById(`use_existing_volume_${instance}`);

    try {
        if (volumeModeSelect.value === "new") {
            volumeSizeInputField.style.display = "block";
        } else {
            volumeSizeInputField.style.display = "none";
        }
    } catch (error) {
        console.error("Error handling volume mode selection:", error);
    }
}

function attachInstanceEventListeners() {
    document.querySelectorAll(".next-instance").forEach(button => {
        button.addEventListener("click", function () {
            let instanceIndex = parseInt(this.getAttribute("data-instance"));
            switchToInstance(instanceIndex + 1);
        });
    });

    document.querySelectorAll(".prev-instance").forEach(button => {
        button.addEventListener("click", function () {
            let instanceIndex = parseInt(this.getAttribute("data-instance"));
            switchToInstance(instanceIndex - 1);
        });
    });

    document.querySelectorAll(".nav-link").forEach(tab => {
        tab.addEventListener("click", function (event) {
            event.preventDefault();
            let instanceIndex = parseInt(this.id.replace(TAB_PREFIX, ""));
            switchToInstance(instanceIndex);
        });
    });
}

function switchToInstance(instanceIndex) {
    if (instanceIndex < 0 ){ console.error("Can't have a negative InstanceIndex: {{ instanceIndex }}")}
    document.querySelectorAll(".tab-pane").forEach(el => {
        el.classList.remove("show", "active");
        el.style.display = "none";
    });

    let newContent = document.getElementById(`${CONTENT_PREFIX}${instanceIndex}`);
    if (newContent) {
        newContent.classList.add("show", "active");
        newContent.style.display = "block";
    }

    document.querySelectorAll(".nav-link").forEach(tab => {
        tab.classList.remove("active");
    });

    let newTab = document.getElementById(`${TAB_PREFIX}${instanceIndex}`);
    if (newTab) {
        newTab.classList.add("active");
        newTab.click();
    }
}


function attachAccountButtonListeners() {
    document.querySelectorAll(".no_additional_users").forEach(checkbox => {
        checkbox.addEventListener("change", function () {
            let instanceIndex = this.id.split("_").pop();
            let accountsSection = document.getElementById(`accounts_section_${instanceIndex}`);
            let addAccountButton = document.querySelector(`.add_account_btn[data-instance='${instanceIndex}']`);
            let userCountSection = document.getElementById(`user_count_section_${instanceIndex}`);
            let userCountInput = document.getElementById(`user_count_${instanceIndex}`);

            if (this.checked) {
                accountsSection.style.display = "none";
                addAccountButton.style.display = "none";
                userCountSection.style.display = "none";
                document.getElementById(`dynamic_accounts_container_${instanceIndex}`).innerHTML = "";
            } else {
                accountsSection.style.display = "block";
                addAccountButton.style.display = "none";
                userCountSection.style.display = "block";
                let userCount = parseInt(userCountInput.value) || 1;
                generateMultipleAccountFields(instanceIndex, userCount);
            }
        });
    });

    document.querySelectorAll(".user-count-input").forEach(input => {
        input.addEventListener("input", function () {
            let instanceIndex = this.id.split("_").pop();
            let userCount = parseInt(this.value) || 1;
            generateMultipleAccountFields(instanceIndex, userCount);
        });
    });
}

function generateMultipleAccountFields(instanceIndex, userCount) {
    let accountsContainer = document.getElementById(`dynamic_accounts_container_${instanceIndex}`);
    if (!accountsContainer) return;

    accountsContainer.innerHTML = "";
    userCount = Math.max(userCount, 1);

    for (let i = 1; i <= userCount; i++) {
        let accountSection = document.createElement("div");
        accountSection.classList.add("card", "p-3", "mb-3", "position-relative");
        accountSection.id = `account_${instanceIndex}_${i}`;
        accountSection.dataset.accountNumber = i;
        accountSection.style.border = "1px solid #ccc";
        accountSection.style.borderRadius = "5px";
        accountSection.style.padding = "15px";

        // Add remove button
        const removeBtn = document.createElement("button");
        removeBtn.className = "btn btn-danger btn-sm position-absolute";
        removeBtn.style.top = "5px";
        removeBtn.style.right = "5px";
        removeBtn.innerHTML = "Remove";
        removeBtn.onclick = function() {
            accountSection.remove();
            renumberAccounts(instanceIndex);
            updateUserCount(instanceIndex);
            selectAutomaticFlavor(instanceIndex);
        };

        let fieldsHtml = `<h5 class="account-title">Account ${i}</h5>`;
        accountAttributes.forEach(attr => {
            fieldsHtml += `
                <div class="form-group md-5">
                    <label for="${attr}_${instanceIndex}_${i}">${attr}</label>
                    <input type="text" class="form-control" id="${attr}_${instanceIndex}_${i}" name="${attr}_${instanceIndex}[]" required>
                </div>
            `;
        });

        accountSection.innerHTML = fieldsHtml;
        accountSection.appendChild(removeBtn);
        accountsContainer.appendChild(accountSection);
    }
}

function renumberAccounts(instanceIndex) {
    const accountsContainer = document.getElementById(`dynamic_accounts_container_${instanceIndex}`);
    if (!accountsContainer) return;

    const accountSections = Array.from(accountsContainer.querySelectorAll('.card'));
    accountSections.forEach((section, index) => {
        const newNumber = index + 1;

        section.dataset.accountNumber = newNumber;

        section.id = `account_${instanceIndex}_${newNumber}`;

        const title = section.querySelector('.account-title');
        if (title) title.textContent = `Account ${newNumber}`;

        accountAttributes.forEach(attr => {
            const input = section.querySelector(`input[id$="${attr}_${instanceIndex}_${index+1}"]`);
            if (input) {
                input.id = `${attr}_${instanceIndex}_${newNumber}`;
                input.name = `${attr}_${instanceIndex}[]`;
            }
        });
    });
}

function generateInstantiationFields(instanceIndex) {
    let fieldsHtmlInstance = ``;
    instantiationAttribute.forEach(attr => {
        fieldsHtmlInstance += `
                    <div class="form-group md-5">
                        <label for="${attr}_${instanceIndex}_instantiation">${attr}</label>
                        <input type="text"
                               class="form-control"
                               id="${attr}_${instanceIndex}_instantiation"
                               name="${attr}_${instanceIndex}_instantiation[]"
                               data-attr-name="${attr}"
                               required>
                    </div>
                `;
    });
    return fieldsHtmlInstance;
}

function selectAutomaticFlavor(instanceIndex) {
    const flavorDropdown = document.getElementById(`flavor_id_${instanceIndex}`);
    if (!flavorDropdown) return;

    const noAdditionalUsersCheckbox = document.getElementById(`no_additional_users_${instanceIndex}`);
    const userCountInput = document.getElementById(`user_count_${instanceIndex}`);

    const requiredRAM = parseFloat("{{ app_template.fixed_ram_gb }}");
    const requiredDisk = parseFloat("{{ app_template.fixed_disk_gb }}");
    const requiredCores = parseInt("{{ app_template.fixed_cores }}");

    let totalRAM = requiredRAM;
    let totalDisk = requiredDisk;
    let totalCores = requiredCores;

    // AllInstanceTab only shows fixed resources
    if (instanceIndex != ALL_INSTANCES_INDEX && !noAdditionalUsersCheckbox.checked) {
        const perUserRAM = parseFloat("{{ app_template.per_user_ram_gb }}");
        const perUserDisk = parseFloat("{{ app_template.per_user_disk_gb }}");
        const perUserCores = parseFloat("{{ app_template.per_user_cores }}");
        const userCount = parseInt(userCountInput.value) || 0;

        totalRAM += userCount * perUserRAM;
        totalDisk += userCount * perUserDisk;
        totalCores += userCount * perUserCores;
    }

    document.getElementById(`total_ram_${instanceIndex}`).textContent = totalRAM.toFixed(2);
    document.getElementById(`total_disk_${instanceIndex}`).textContent = totalDisk.toFixed(2);
    document.getElementById(`total_cores_${instanceIndex}`).textContent = totalCores;

    let selectedFlavor = null;

    Array.from(flavorDropdown.options).forEach(option => {
        if (option.value) {
            const flavorDetails = JSON.parse(option.getAttribute('data-flavor-details'));
            const flavorRAM = flavorDetails.ram / 1024;
            const flavorDisk = flavorDetails.disk;
            const flavorCores = flavorDetails.vcpus;


            option.textContent = flavorDetails.name;

            if (flavorRAM >= totalRAM && flavorDisk >= totalDisk && flavorCores >= totalCores) {
                if (!selectedFlavor ||
                    (flavorRAM <= JSON.parse(selectedFlavor.getAttribute('data-flavor-details')).ram / 1024 &&
                        flavorDisk <= JSON.parse(selectedFlavor.getAttribute('data-flavor-details')).disk &&
                        flavorCores <= JSON.parse(selectedFlavor.getAttribute('data-flavor-details')).vcpus))
                {
                    selectedFlavor = option;
                }
                option.disabled = false;
                option.style.color = "black";
            } else {
                option.disabled = true;
                option.style.color = "gray";
                option.textContent += " (Too small for required resources)";
            }
        }
    });


    if (selectedFlavor) {
        flavorDropdown.value = selectedFlavor.value;
    } else {
        alert("No suitable flavor found. Please select one manually.");
    }
}



function attachFlavorCalculationListeners() {
    document.querySelectorAll(".no_additional_users").forEach(checkbox => {
        checkbox.addEventListener("change", function () {
            let instanceIndex = this.id.split("_").pop();
            selectAutomaticFlavor(instanceIndex);
        });
    });

    document.querySelectorAll(".user-count-input").forEach(input => {
        input.addEventListener("input", function () {
            let instanceIndex = this.id.split("_").pop();
            selectAutomaticFlavor(instanceIndex);
        });
    });
}

window.onload = function () {
    let countInstancesInput = document.getElementById("num_instances");
    let instancesNameInput = document.getElementById("instances_name");
    let instanceTabs = document.getElementById("instanceTabs");
    let instancesContainer = document.getElementById("instancesContainer");

    if (!countInstancesInput || !instancesNameInput || !instanceTabs || !instancesContainer) {
        console.error("Missing HTML elements. Check IDs.");
        return;
    }

    countInstancesInput.value = "1";
    generateInstanceFields();

    countInstancesInput.addEventListener("input", generateInstanceFields);
    instancesNameInput.addEventListener("input", generateInstanceFields);

    attachFlavorCalculationListeners();
};


let instantiationAttributes = {{ app_template.instantiation_attributes|safe }};
let formattedInstantiation = instantiationAttributes.map(acc => acc.name).join(":");
document.getElementById("structured-instantiation").textContent = formattedInstantiation;

let accountAttribute = {{ app_template.account_attributes|safe }}
let formattedAccounts = accountAttributes.map(acc => acc.name).join(":");
document.getElementById("structured-accounts").textContent = formattedAccounts;

{% if modal_message %}
$(document).ready(function () {
    $('#responseModal').modal('show');
});
{% endif %}



document.addEventListener("change", function(event) {
    if (!event.target.classList.contains("csv-upload")) return;

    const file = event.target.files[0];
    if (!file) return;

    const instanceIndex = event.target.getAttribute("data-instance");
    if (!instanceIndex) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const text = e.target.result;
        const lines = text.trim().split("\n");

        if (lines.length === 0) {
            alert("CSV file is empty");
            return;
        }


        function parseCSVLine(line) {
            const result = [];
            let inQuotes = false;
            let currentField = "";

            for (let i = 0; i < line.length; i++) {
                const char = line[i];

                if (char === '"') {
                    if (inQuotes && line[i+1] === '"') {

                        currentField += '"';
                        i++;
                    } else {
                        inQuotes = !inQuotes;
                    }
                } else if (char === ',' && !inQuotes) {
                    result.push(currentField.trim());
                    currentField = "";
                } else {
                    currentField += char;
                }
            }

            result.push(currentField.trim());
            return result;
        }


        const headers = parseCSVLine(lines[0]).map(h => h.toLowerCase());

        const lowerAccountAttrs = accountAttributes.map(a => a.toLowerCase());
        const isValidCSV = lowerAccountAttrs.every(attr =>
            headers.includes(attr)
        );

        if (!isValidCSV) {
            alert(`CSV headers don't match expected fields. Expected: ${accountAttributes.join(", ")}`);
            return;
        }

        const fieldMapping = accountAttributes.map(attr =>
            headers.indexOf(attr.toLowerCase())
        );

        const accountsData = [];
        for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim() === "") continue;

            const values = parseCSVLine(lines[i]);
            if (values.length !== headers.length) {
                console.warn(`Skipping row ${i+1}: column count mismatch`);
                continue;
            }

            const accountData = {};
            accountAttributes.forEach((attr, idx) => {
                accountData[attr] = values[fieldMapping[idx]] || "";
            });
            accountsData.push(accountData);
        }

        if (accountsData.length === 0) {
            alert("No valid account data found in CSV");
            return;
        }

        const accountsContainer = document.getElementById(`dynamic_accounts_container_${instanceIndex}`);
        const userCountInput = document.getElementById(`user_count_${instanceIndex}`);
        const noAdditionalUsersCheckbox = document.getElementById(`no_additional_users_${instanceIndex}`);

        if (noAdditionalUsersCheckbox.checked) {
            noAdditionalUsersCheckbox.checked = false;
            document.getElementById(`accounts_section_${instanceIndex}`).style.display = "block";
            document.getElementById(`user_count_section_${instanceIndex}`).style.display = "block";
        }

        accountsContainer.innerHTML = "";

        accountsData.forEach((account, index) => {
            const accountSection = document.createElement("div");
            accountSection.className = "card p-3 mb-3 position-relative";
            accountSection.id = `account_${instanceIndex}_${index+1}`;
            accountSection.dataset.accountNumber = index+1;
            accountSection.style.border = "1px solid #ccc";
            accountSection.style.borderRadius = "5px";
            accountSection.style.padding = "15px";

            const removeBtn = document.createElement("button");
            removeBtn.className = "btn btn-danger btn-sm position-absolute";
            removeBtn.style.top = "5px";
            removeBtn.style.right = "5px";
            removeBtn.innerHTML = "Remove";
            removeBtn.onclick = function() {
                accountSection.remove();
                renumberAccounts(instanceIndex);
                updateUserCount(instanceIndex);
                selectAutomaticFlavor(instanceIndex);
            };


            let fieldsHtml = `<h5 class="account-title">Account ${index+1}</h5>`;
            accountAttributes.forEach(attr => {
                fieldsHtml += `
                    <div class="form-group md-5">
                        <label for="${attr}_${instanceIndex}_${index+1}">${attr}</label>
                        <input type="text" class="form-control"
                               id="${attr}_${instanceIndex}_${index+1}"
                               name="${attr}_${instanceIndex}[]"
                               value="${account[attr] || ''}"
                               required>
                    </div>
                `;
            });

            accountSection.innerHTML = fieldsHtml;
            accountSection.appendChild(removeBtn);
            accountsContainer.appendChild(accountSection);
        });

        updateUserCount(instanceIndex);
        selectAutomaticFlavor(instanceIndex);
    };

    reader.readAsText(file);
});

function updateUserCount(instanceIndex) {
    const accountsContainer = document.getElementById(`dynamic_accounts_container_${instanceIndex}`);
    const userCountInput = document.getElementById(`user_count_${instanceIndex}`);

    if (accountsContainer && userCountInput) {
        userCountInput.value = accountsContainer.querySelectorAll('.card').length;
    }
}


document.addEventListener("change", function(event) {
    if (!event.target.classList.contains("csv-upload")) return;

    const fileInput = event.target;
    const file = fileInput.files[0];
    if (!file) return;

    const instanceIndex = fileInput.getAttribute("data-instance");
    if (!instanceIndex) return;

    const formGroup = fileInput.closest('.form-group');

    const existingUndoBtn = formGroup.querySelector('.undo-csv');
    if (existingUndoBtn) {
        existingUndoBtn.remove();
    }

    const undoBtn = document.createElement("button");
    undoBtn.type = "button";
    undoBtn.className = "btn btn-danger btn-sm undo-csv ml-2";
    undoBtn.dataset.instance = instanceIndex;
    undoBtn.innerHTML = `{{ _("Undo CSV Upload") }}`;

    undoBtn.style.display = "inline-block";
    undoBtn.style.verticalAlign = "middle";

    fileInput.insertAdjacentElement('afterend', undoBtn);

    undoBtn.addEventListener("click", function() {
        resetCSVUpload(instanceIndex);
    });

    const reader = new FileReader();
    reader.onload = function(e) {
        const text = e.target.result;
        const lines = text.trim().split("\n");

        if (lines.length === 0) {
            alert("CSV file is empty");
            return;
        }

    };

    reader.readAsText(file);
});

function resetCSVUpload(instanceIndex) {
    const accountsContainer = document.getElementById(`dynamic_accounts_container_${instanceIndex}`);
    const userCountInput = document.getElementById(`user_count_${instanceIndex}`);
    const csvInput = document.getElementById(`csvUpload_${instanceIndex}`);
    const undoBtn = document.querySelector(`.undo-csv[data-instance="${instanceIndex}"]`);

    csvInput.value = "";

    if (undoBtn) {
        undoBtn.remove();
    }

    userCountInput.value = 1;

    accountsContainer.innerHTML = "";
    generateMultipleAccountFields(instanceIndex, 1);

    selectAutomaticFlavor(instanceIndex);
}

function attachVolumeChangeHandlers() {
    document.querySelectorAll(".existing-volume-select").forEach(select => {
        select.addEventListener("change", () => {
            const selectedVolumes = Array.from(document.querySelectorAll(".existing-volume-select"))
                .map(sel => sel.value)
                .filter(val => val);
            document.querySelectorAll(".existing-volume-select").forEach(select => {
                const currentValue = select.value;
                Array.from(select.options).forEach(option => {
                    if (
                        selectedVolumes.includes(option.value) &&
                        option.value !== currentValue
                    ) {
                        option.disabled = true;
                    } else {
                        option.disabled = false;
                    }
                });
            });
        });
    });
}
