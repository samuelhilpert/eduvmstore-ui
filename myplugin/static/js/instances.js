$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();

});
//For the all instances tab index 0 is used for easier calculation
const ALL_INSTANCES_INDEX = 0;
const TAB_PREFIX = 'instanceTab_';
const CONTENT_PREFIX = 'instanceContent_';
const VOLUME_SELECTION = 'use_existing_volume_';
const VOLUME_SELECTION_CLASS = VOLUME_SELECTION.replace(/_/g, '-').slice(0, -1);
const FLAVOR_ID = 'flavor_id_';
const NETWORK_ID = 'network_id_';
const VOLUME_SIZE = 'volume_size_';
const INSTANTIATION_POSTFIX = '_instantiation'
const data = window.templateContext || {};

let volumeSelections = {};

let allInstanceChangedFieldInfo = {
    element: null,
    fieldType: ''
};

//Volumes
const attachableVolumes = data.attachableVolumes || [];


document.getElementById("instance_count").addEventListener("input", function () {
    const MAX_NUM_INSTANCES = 100;
    if (this.value > MAX_NUM_INSTANCES) {
        this.value = MAX_NUM_INSTANCES;
    } else if (this.value < 1) {
        this.value = 1;
    }
});

let accountAttributes = data.expectedAccountAttributes;
let instantiationAttribute = data.expectedInstantiationAttributes;

function generateFlavorSection(instanceIndex) {
    const flavors = window.templateContext.flavors.suitable_flavors;
    const selected = window.templateContext.flavors.selected_flavor;

    const labelPrefix = (instanceIndex === ALL_INSTANCES_INDEX)
        ? "Select Flavor for all Instances"
        : "Select Flavor";

    let options = "";

    const flavorKeys = Object.keys(flavors);
    if (flavorKeys.length > 0) {
        for (const flavor_id of flavorKeys) {
            const flavor_data = flavors[flavor_id];
            const selectedAttr = (flavor_id === selected) ? "selected" : "";
            const flavorDetails = {
                id: flavor_id,
                name: flavor_data.name,
                ram: flavor_data.ram,
                disk: flavor_data.disk,
                vcpus: flavor_data.vcpus
            };
            options += `
                <option value="${flavor_id}"
                        data-flavor-details='${JSON.stringify(flavorDetails)}'
                        ${selectedAttr}>
                    ${flavor_data.name} — ${flavor_data.ram} MB RAM, ${flavor_data.vcpus} vCPU, ${flavor_data.disk} GB Disk
                </option>
            `;
        }
    } else {
        options = `<option value="" disabled>No suitable flavors found.</option>`;
    }

    return `
        <div class="form-group">
            <label for="${FLAVOR_ID}${instanceIndex}">${labelPrefix}
                <span data-toggle="tooltip"
                      title="A flavor is a performance package for your virtual machine. It defines how much memory (RAM), computing power (CPU), and storage (disk space) it gets.">
                    <i class="fa fa-question-circle"></i>
                </span>
            </label>
            <select class="form-control flavor-dropdown"
                    id="${FLAVOR_ID}${instanceIndex}"
                    name="${FLAVOR_ID}${instanceIndex}" required>
                ${options}
            </select>
        </div>
    `;
}


function generateNetworkSection(instanceIndex) {
    const labelPrefix = (instanceIndex === ALL_INSTANCES_INDEX)
        ? "Select Network for all Instances"
        : "Select Network";

    const networks = window.templateContext.networks || {};

    let options = "";

    const networkEntries = Object.entries(networks);
    if (networkEntries.length > 0) {
        networkEntries.forEach(([network_id, network_name], index) => {
            const selected = index === 0 ? "selected" : "";
            options += `<option value="${network_id}" ${selected}>${network_name}</option>`;
        });
    } else {
        options = `<option value="" disabled selected>No networks available</option>`;
    }

    return `
        <div class="form-group">
            <label for="${NETWORK_ID}${instanceIndex}">${labelPrefix} <span data-toggle="tooltip"
            title="Select a network that the instance should be connected to. This determines its connectivity.">
                    <i class="fa fa-question-circle"></i>
              </span></label>
            <select class="form-control"
                    id="${NETWORK_ID}${instanceIndex}"
                    name="${NETWORK_ID}${instanceIndex}" required>
                ${options}
            </select>
        </div>
    `;
}


function generateVolumeSection(instanceIndex) {
    const labelVolumeSizePrefix = (instanceIndex === ALL_INSTANCES_INDEX ) ? "Choose Volume Size (GB) for all Instances" : "Choose Volume Size GB";
    let volumeOptions = '';
    let requiredVolumeSize = data.volumeSize;

    // Option of attaching no volume
    if (requiredVolumeSize === 0){
        volumeOptions += `<option value="none">No additional volumes</option>`
    }

    volumeOptions += `<option value="new">Create new volume</option>`;
    //add existing volumes to selection options
    attachableVolumes.forEach(volume => {
        const isTooSmall = volume.size < requiredVolumeSize;
        // AllInstance Tab can't select volumes as they are only at one instance and too small Values are not selectable
        volumeOptions += `<option value="${volume.id}" data-volume-id="${volume.id}"
                                  ${(isTooSmall || instanceIndex === ALL_INSTANCES_INDEX) ? 'disabled style="color: gray;"' : ''}>
                    ${volume.name} (${volume.size} GB) ${isTooSmall ? ' (Too small)' : ''}
                    ${(instanceIndex === ALL_INSTANCES_INDEX) ? '(Select Volume for each instance)' : ''}
                </option>`;
    });


    return `
                <!-- Volumes -->
                <div class="form-group">
                    <label for="${VOLUME_SELECTION}${instanceIndex}">Select Volume
                     <span data-toggle="tooltip"
                    title="Choose to attach an existing volume or create a new one. Must meet the minimum volume size requirement.">
                            <i class="fa fa-question-circle"></i>
                      </span></label>
                    <select class="form-control ${VOLUME_SELECTION_CLASS}"
                            id="${VOLUME_SELECTION}${instanceIndex}"
                            name="${VOLUME_SELECTION}${instanceIndex}"
                            data-instance="${instanceIndex}">
                        ${volumeOptions}
                    </select>
                </div>

                <div class="form-group create-volume-size-group" id="volume_size_input_${instanceIndex}" style="display: none;">
                    <label for="${VOLUME_SIZE}${instanceIndex}">${labelVolumeSizePrefix} <span data-toggle="tooltip"
                    title="Specify the size in GB if a new volume is to be created. Must be equal to or greater than the minimum volume size.">
                            <i class="fa fa-question-circle"></i>
                      </span></label>
                    <input type="number" class="form-control" id="${VOLUME_SIZE}${instanceIndex}" name="${VOLUME_SIZE}${instanceIndex}"  value="data.volumeSize" min="data.volumeSize">
                </div>
            `;
}

function generateInstantiationAttributesSection(instanceIndex) {
    const sectionTitle = (instanceIndex === ALL_INSTANCES_INDEX ) ? "Instantiation Attributes for all Instances" : "Instantiation Attributes";

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

function generateRessourceSection(instanceIndex){
    return `
                <h5>Resource Configuration</h5>

                <!-- Display Resource Requirements and Available Resources -->
                <div class="alert alert-info mt-3">
                    <p style="margin-bottom: 4px;"><strong>Resource Requirements:</strong></p>
                    <div>
                        <p style="margin-bottom: 4px;">RAM: <span id="total_ram_${instanceIndex}"></span> GB</p>
                        <p style="margin-bottom: 4px;">Disk: <span id="total_disk_${instanceIndex}"></span> GB</p>
                        <p style="margin-bottom: 4px;">CPU Cores: <span id="total_cores_${instanceIndex}"></span></p>
                    </div>
                </div>
            `;
}

function generateAccountAttributesSection(instanceIndex) {

    if (!Array.isArray(accountAttributes) || accountAttributes.length === 0) {
        return '';
    }
    const sectionTitle = (instanceIndex === ALL_INSTANCES_INDEX ) ? "User Configuration for all Instances" : "User Configuration";
    const uploadCSVText = (instanceIndex === ALL_INSTANCES_INDEX ) ? "Upload CSV for Accounts in all instances" : "Upload CSV";
    const uploadCSVHeaders = (instanceIndex === ALL_INSTANCES_INDEX ) ? `${accountAttributes.join(", ")}, instance index` : `${accountAttributes.join(", ")}`;
    const uploadCSVTextTooltip = `Upload Account Attributes for all instances in the following structure: ${uploadCSVHeaders}`;

    let noAdditionalUsersHtml = '';
    let accountsHTML = '';
    if (instanceIndex !== ALL_INSTANCES_INDEX){
        noAdditionalUsersHtml += `
                <p style="margin-bottom: 20px;">Enter the number of users to be added to the instance. Upload a CSV file with the user data or enter the user data directly by filling the form fields.</p>
        <div class="form-group mt-3" id="user_count_section_${instanceIndex}">
            <label for="user_count_${instanceIndex}">Number of Additional Users<span data-toggle="tooltip"
                title="Specify how many additional users should be created. 0 disables account creation.">
                <i class="fa fa-question-circle"></i>
            </span> </label>
            <input type="number" class="form-control user-count-input" id="user_count_${instanceIndex}" name="user_count_${instanceIndex}" min="0" value="0">
        </div>
    `;

        accountsHTML += `

                    <h6>Accounts</h6>
                    <div id="dynamic_accounts_container_${instanceIndex}" class="account-grid"></div>
                    <button type="button" class="btn btn-secondary add_account_btn" data-instance="${instanceIndex}" style="display: none;">Add Account</button>

                         <div class="d-flex justify-content-end mb-2 mt" style="margin-top: 15px;">
                <button type="button" class="btn btn-outline-success btn-sm export_csv_btn" data-instance="${instanceIndex}">
                    <i class="fa fa-download"></i> Export CSV
                </button>
            </div>
                `
    }

    return `
                <div class="section-container">
                    <h5>${sectionTitle}</h5>

                    ${noAdditionalUsersHtml}
                    <!-- CSV Upload -->
                    <div class="form-group" style="display: flex; align-items: center; gap: 10px;">
                            <div style="flex-grow: 1; margin-top: 15px;">
                                <label for="csvUpload_${instanceIndex}">${uploadCSVText}
                                    <span data-toggle="tooltip" title="${uploadCSVTextTooltip}">
                                        <i class="fa fa-question-circle"></i>
                                    </span>
                                </label>
                                <div style="display: flex; align-items: center; margin-bottom: 15px; margin-top: 8px;">
                                    <input type="file" class="form-control-file csv-upload" id="csvUpload_${instanceIndex}"
                                           data-instance="${instanceIndex}" accept=".csv" style="width: auto;">
                                     <div class="undo-placeholder" style="margin-left: 10px;"></div>
                                </div>
                                <small class="form-text text-muted" style="margin-bottom: 20px">
                                    Upload a CSV file with headers: ${accountAttributes.join(", ")}${instanceIndex === ALL_INSTANCES_INDEX ? ", instance index" : ""}
                                </small>
                            </div>
                        </div>

                    <div id="accounts_section_${instanceIndex}" style="display: ${instanceIndex == ALL_INSTANCES_INDEX ? 'block' : 'none'};">


                        ${accountsHTML}
                    </div>
                </div>
            `;
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

function singleInstanceContainer(instanceName, instanceIndex){
    return`
                <div class="tab-pane" id="${CONTENT_PREFIX}${instanceIndex}" role="tabpanel">
                    <h4 id="instanceTitle_${instanceIndex}">${instanceName}</h4>
                    <input type="hidden" name="generated_instance_name_${instanceIndex}" value="${instanceName}">

                    <div class="section-container">
                        ${generateRessourceSection(instanceIndex)}
                        ${generateFlavorSection(instanceIndex)}
                        ${generateNetworkSection(instanceIndex)}
                        ${generateVolumeSection(instanceIndex)}
                    </div>

                    ${generateInstantiationAttributesSection(instanceIndex)}

                     ${generateAccountAttributesSection(instanceIndex)}
                </div>
            `
}

function generateInstanceFields() {
    let instanceTabs = document.getElementById("instanceTabs");
    let instancesContainer = document.getElementById("instancesContainer");

    let countInstancesInput = document.getElementById("instance_count");
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
        instancesContainer.innerHTML += singleInstanceContainer(allInstancesName, ALL_INSTANCES_INDEX)
    }
    // Generate individual instance tabs
    for (let i = 1; i <= countInstances; i++) {
        let instanceName = "";
        if (baseName) {
            instanceName = (countInstances === 1) ? baseName : `${baseName}-${i}`;
        }
        instanceTabs.innerHTML += singleInstanceTab(instanceName, i);
        instancesContainer.innerHTML += singleInstanceContainer(instanceName, i);
    }

    document.querySelectorAll(`.${VOLUME_SELECTION_CLASS}`).forEach(select => {
        select.addEventListener("change", function () {
            const instance = this.dataset.instance;
            const group = document.getElementById(`existing_volume_group_${instance}`);
            if (this.value === "existing") {
                group.style.display = "block";
            } else {
                if (group) group.style.display = "none";
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
        document.querySelectorAll(`#${FLAVOR_ID}${ALL_INSTANCES_INDEX}, #${NETWORK_ID}${ALL_INSTANCES_INDEX}, #${VOLUME_SELECTION}${ALL_INSTANCES_INDEX}, #${VOLUME_SIZE}${ALL_INSTANCES_INDEX}`).forEach(element => {
            // Remove existing event listeners to prevent duplicates
            element.removeEventListener('change', showWarningModal);
            element.addEventListener('change', showWarningModal);
        });

        // Add handlers for instantiation attributes if they exist
        if (instantiationAttribute.length > 0) {
            instantiationAttribute.forEach(attr => {
                const element = document.getElementById(`${attr}_${ALL_INSTANCES_INDEX}${INSTANTIATION_POSTFIX}`);
                if (element) {

                    element.removeEventListener('change', showWarningModal);
                    element.addEventListener('change', showWarningModal);
                }
            });
        }
    }, 100);
    hideWarningModal();
}

function showWarningModal() {
    allInstanceChangedFieldInfo.element = event.target;
    const fieldId = event.target.id;

    // Determine field type based on ID
    switch (true) {
        case fieldId.includes(FLAVOR_ID):
            allInstanceChangedFieldInfo.fieldType = 'flavor';
            break;
        case fieldId.includes(NETWORK_ID):
            allInstanceChangedFieldInfo.fieldType = 'network';
            break;
        case fieldId.includes(VOLUME_SELECTION):
            allInstanceChangedFieldInfo.fieldType = 'volume_selection';
            break;
        case fieldId.includes(VOLUME_SIZE):
            allInstanceChangedFieldInfo.fieldType = 'new_volume_size';
            break;
        case fieldId.includes(INSTANTIATION_POSTFIX):
            allInstanceChangedFieldInfo.fieldType = 'instantiation';
            allInstanceChangedFieldInfo.attrName = event.target.getAttribute('data-attr-name');
            break;
        default:
            allInstanceChangedFieldInfo.fieldType = 'unknown';
    }

    const warningText = document.querySelector('#allInstancesWarningModal .modal-body p');
    if (warningText) {
        warningText.innerHTML = `This will apply the selected
                    <strong>${getFieldTypeDisplayName(allInstanceChangedFieldInfo.fieldType)}</strong>
                    to all individual instances.`;
    }

    $('#allInstancesWarningModal').modal('show');
}

// Helper function to get a display name for the field type
function getFieldTypeDisplayName(fieldType) {
    switch (fieldType) {
        case 'flavor': return 'flavor';
        case 'network': return 'network';
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
    const countInstances = parseInt(document.getElementById('instance_count').value, 10) || 1;

    // Only apply the specific changed setting
    switch (allInstanceChangedFieldInfo.fieldType) {
        case 'flavor':
            const allFlavorSelect = document.getElementById(`${FLAVOR_ID}${ALL_INSTANCES_INDEX}`);
            if (allFlavorSelect && allFlavorSelect.value) {
                for (let i = 1; i <= countInstances; i++) {
                    const instanceFlavorSelect = document.getElementById(`${FLAVOR_ID}${i}`);
                    if (instanceFlavorSelect) {
                        instanceFlavorSelect.value = allFlavorSelect.value;
                    }
                }
            }
            break;

        case 'network':
            const allNetworkSelect = document.getElementById(`${NETWORK_ID}${ALL_INSTANCES_INDEX}`);
            if (allNetworkSelect && allNetworkSelect.value) {
                for (let i = 1; i <= countInstances; i++) {
                    const instanceNetworkSelect = document.getElementById(`${NETWORK_ID}${i}`);
                    if (instanceNetworkSelect) {
                        instanceNetworkSelect.value = allNetworkSelect.value;
                    }
                }
            }
            break;

        case 'volume_selection':
            const allVolumeOption = document.getElementById(`${VOLUME_SELECTION}${ALL_INSTANCES_INDEX}`);
            if (allVolumeOption) {
                const volumeChoice = allVolumeOption.value;
                for (let i = 1; i <= countInstances; i++) {
                    const instanceVolumeOption = document.getElementById(`${VOLUME_SELECTION}${i}`);
                    if (instanceVolumeOption) {
                        instanceVolumeOption.value = volumeChoice;
                        instanceVolumeOption.dispatchEvent(new Event('change'));
                    }
                }
            }
            break;
        case 'new_volume_size':
            const allVolumeSizeInput = document.getElementById(`${VOLUME_SIZE}${ALL_INSTANCES_INDEX}`);
            if (allVolumeSizeInput && allVolumeSizeInput.value) {
                const volumeSize = allVolumeSizeInput.value;
                for (let i = 1; i <= countInstances; i++) {
                    const instanceVolumeSizeInput = document.getElementById(`${VOLUME_SIZE}${i}`);
                    if (instanceVolumeSizeInput) {
                        instanceVolumeSizeInput.value = volumeSize;
                    }
                }
            }
            break;

        case 'instantiation':
            if (allInstanceChangedFieldInfo.attrName) {
                const allAttrInput = document.getElementById(`${allInstanceChangedFieldInfo.attrName}_${ALL_INSTANCES_INDEX}${INSTANTIATION_POSTFIX}`);
                if (allAttrInput && allAttrInput.value !== undefined) {
                    for (let i = 1; i <= countInstances; i++) {
                        const instanceAttrInput = document.getElementById(`${allInstanceChangedFieldInfo.attrName}_${i}${INSTANTIATION_POSTFIX}`);
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
    document.querySelectorAll(`.${VOLUME_SELECTION_CLASS}`).forEach(select => {
        select.addEventListener("change", function () {
            const instance = this.dataset.instance;
            const volumeGroup = document.getElementById(`existing_volume_group_${instance}`);

            if (volumeGroup && selectedVolume) {
                if (this.value === "existing") {
                    volumeGroup.style.display = "block";
                } else {
                    volumeGroup.style.display = "none";
                }
            }
            attachVolumeCreateListeners(instance);
            updateVolumeSelection(instance, this.value)
        });

        select.dispatchEvent(new Event("change"));

    });
}

function updateVolumeSelection(instance, value) {

    if (value !== "new" && value !== "none") {
        volumeSelections[instance] = value;
    } else {

        delete volumeSelections[instance];
    }

    updateVolumeSelectionOptions();
}

function updateVolumeSelectionOptions() {
    const countInstances = parseInt(document.getElementById('instance_count').value, 10) || 1;


    for (let i = 1; i <= countInstances; i++) {
        const volumeSelect = document.getElementById(`${VOLUME_SELECTION}${i}`);
        if (!volumeSelect) continue;


        Array.from(volumeSelect.options).forEach(option => {
            const volumeId = option.value;


            let selectedInInstance = null;
            for (const [instanceIdx, selectedVolumeId] of Object.entries(volumeSelections)) {
                if (selectedVolumeId === volumeId && instanceIdx != i) {
                    selectedInInstance = instanceIdx;
                    break;
                }
            }

            if (selectedInInstance && volumeId) {

                option.disabled = true;
                option.textContent = `${option.textContent.split('(')[0]} (already selected in instance ${selectedInInstance})`;
            } else if (volumeId !== "new" && volumeId !== "none") {

                const originalVolume = attachableVolumes.find(v => v.id === volumeId);
                if (originalVolume) {
                    const isTooSmall = originalVolume.size < parseFloat(data.volumeSize);

                    option.disabled = isTooSmall;
                    option.textContent = `${originalVolume.name} (${originalVolume.size} GB)${isTooSmall ? ' (Too small)' : ''}`;
                }
            }
        });
    }
}

function attachVolumeCreateListeners(instance) {
    const volumeSizeInputField = document.getElementById(`volume_size_input_${instance}`);
    const volumeSelection = document.getElementById(`${VOLUME_SELECTION}${instance}`);

    try {
        if (volumeSelection.value === "new") {
            volumeSizeInputField.style.display = "block";
        } else {
            volumeSizeInputField.style.display = "none";
        }
    } catch (error) {
        console.error("Error handling volume mode selection:", error);
    }
}

function attachInstanceEventListeners() {
    document.querySelectorAll(".nav-link").forEach(tab => {
        tab.addEventListener("click", function (event) {
            event.preventDefault();
            let instanceIndex = parseInt(this.id.replace(TAB_PREFIX, ""));
            switchToInstance(instanceIndex);
        });
    });
}

function switchToInstance(instanceIndex) {
    if (instanceIndex < 0 ){ console.error(`Can't have a negative InstanceIndex: ${instanceIndex}`)}
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
    document.querySelectorAll(".user-count-input").forEach(input => {
        input.addEventListener("input", function () {
            let instanceIndex = this.id.split("_").pop();
            let userCount = parseInt(this.value) || 0;
            generateMultipleAccountFields(instanceIndex, userCount);
        });
    });
}


document.querySelectorAll(".user-count-input").forEach(input => {
    input.addEventListener("input", function () {
        let instanceIndex = this.id.split("_").pop();
        let userCount = parseInt(this.value) || 1;
        generateMultipleAccountFields(instanceIndex, userCount);
    });
});


function generateMultipleAccountFields(instanceIndex, userCount) {
    let accountsContainer = document.getElementById(`dynamic_accounts_container_${instanceIndex}`);
    if (!accountsContainer) return;

    document.getElementById(`accounts_section_${instanceIndex}`).style.display = userCount > 0 ? "block" : "none";


    const existingValues = {};
    const inputs = accountsContainer.querySelectorAll("input");
    inputs.forEach(input => {
        existingValues[input.id] = input.value;
    });


    accountsContainer.innerHTML = "";
    userCount = Math.max(userCount, 0);
    if (userCount === 0) return;

    for (let i = 1; i <= userCount; i++) {
        let accountSection = document.createElement("div");
        accountSection.classList.add("card", "p-3", "mb-3", "position-relative");
        accountSection.id = `account_${instanceIndex}_${i}`;
        accountSection.dataset.accountNumber = i;
        accountSection.style.border = "1px solid #ccc";
        accountSection.style.borderRadius = "5px";
        accountSection.style.padding = "15px";

        const removeBtn = document.createElement("button");
        removeBtn.className = "btn btn-danger btn-sm position-absolute";
        removeBtn.style.top = "5px";
        removeBtn.style.right = "5px";
        removeBtn.innerHTML = "Remove";
        removeBtn.onclick = function () {
            accountSection.remove();
            renumberAccounts(instanceIndex);
            updateUserCount(instanceIndex);
            selectAutomaticFlavor(instanceIndex);
        };

        let fieldsHtml = `<h5 class="account-title">Account ${i}</h5>`;
        accountAttributes.forEach(attr => {
            const fieldId = `${attr}_${instanceIndex}_${i}`;
            const savedValue = existingValues[fieldId] || "";

            fieldsHtml += `
                <div class="form-group md-5">
                    <label for="${fieldId}">${attr}</label>
                    <input type="text" class="form-control"
                        id="${fieldId}"
                        name="${attr}_${instanceIndex}"
                        value="${savedValue}"
                        required>
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
                input.name = `${attr}_${instanceIndex}`;
            }
        });
    });
}

function generateInstantiationFields(instanceIndex) {
    let fieldsHtmlInstance = ``;
    instantiationAttribute.forEach(attr => {
        fieldsHtmlInstance += `
                    <div class="form-group md-5">
                        <label for="${attr}_${instanceIndex}${INSTANTIATION_POSTFIX}">${attr} </label>
                        <input type="text"
                               class="form-control"
                               id="${attr}_${instanceIndex}${INSTANTIATION_POSTFIX}"
                               name="${attr}_${instanceIndex}${INSTANTIATION_POSTFIX}"
                               data-attr-name="${attr}"
                               required>
                    </div>
                `;
    });
    return fieldsHtmlInstance;
}

function selectAutomaticFlavor(instanceIndex) {
    const flavorDropdown = document.getElementById(`${FLAVOR_ID}${instanceIndex}`);
    if (!flavorDropdown) return;

    const requiredRAM = data.requiredRAM;
    const requiredDisk = data.requiredDisk;
    const requiredCores = data.requiredCores;

    document.getElementById(`total_ram_${instanceIndex}`).textContent = requiredRAM.toFixed(2);
    document.getElementById(`total_disk_${instanceIndex}`).textContent = requiredDisk.toFixed(2);
    document.getElementById(`total_cores_${instanceIndex}`).textContent = requiredCores;

    let selectedFlavor = null;

    Array.from(flavorDropdown.options).forEach(option => {
        if (option.value) {
            const flavorDetails = JSON.parse(option.getAttribute('data-flavor-details'));
            const flavorRAM = flavorDetails.ram / 1024;
            const flavorDisk = flavorDetails.disk;
            const flavorCores = flavorDetails.vcpus;


            option.textContent = `${flavorDetails.name} — ${flavorRAM} GB RAM, ${flavorDetails.vcpus} vCPU, ${flavorDetails.disk} GB Disk`;

            if (flavorRAM >= requiredRAM && flavorDisk >= requiredDisk && flavorCores >= requiredCores) {
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
        alert("No suitable flavor found. Please add a flavor manually or change the settings of the appTemplate.");
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
    let countInstancesInput = document.getElementById("instance_count");
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


let instantiationAttributes = data.instanceAttribute;
let formattedInstantiation = instantiationAttributes.map(acc => acc.name).join(":");
document.getElementById("structured-instantiation").textContent = formattedInstantiation;

let accountAttribute = data.accountAttribute;
let formattedAccounts = accountAttributes.map(acc => acc.name).join(":");
document.getElementById("structured-accounts").textContent = formattedAccounts;





document.addEventListener("change", function(event) {
    if (!event.target.classList.contains("csv-upload")) return;

    const file = event.target.files[0];

    // Add Undo button
    const placeholder = event.target.parentElement.querySelector('.undo-placeholder');
    if (placeholder && !placeholder.querySelector('.undo-csv')) {
        const instanceIndex = event.target.getAttribute("data-instance");
        const undoBtn = document.createElement("button");
        undoBtn.type = "button";
        undoBtn.className = "btn btn-sm btn-warning undo-csv";
        undoBtn.dataset.instance = instanceIndex;
        undoBtn.style.marginLeft = "10px";
        undoBtn.innerHTML = '<i class="fa fa-undo"></i> Undo';

        undoBtn.addEventListener("click", () => resetCSVUpload(instanceIndex));
        placeholder.appendChild(undoBtn);
    }

    if (!file) return;

    const instanceIndex = parseInt(event.target.getAttribute("data-instance"), 10);
    if (isNaN(instanceIndex) || instanceIndex < 0) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const text = e.target.result;
        //const lines = text.trim().split("\n");
        const lines = text.split(/\r\n|\r|\n/).filter(line => line.trim() !== "");

        if (lines.length === 0) {
            alert("CSV file is empty");
            return;
        }


        function parseCSVLine(line) {
            if (!line || line.trim() === "") return [];

            const delimiter = (line.split(';').length > line.split(',').length) ? ';' : ',';

            const result = [];
            let inQuotes = false;
            let currentField = "";

            for (let i = 0; i < line.length; i++) {
                const char = line[i];

                if (char === '"') {
                    if (inQuotes && line[i + 1] === '"') {
                        currentField += '"';
                        i++;
                    } else {
                        inQuotes = !inQuotes;
                    }
                } else if (char === delimiter && !inQuotes) {
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

        const instanceIndexCol = headers.findIndex(h =>
            h === 'instance index' || h === 'instance_index' || h === 'instanceindex' || h === 'index' || h === 'instance');
        if (instanceIndexCol === -1 && instanceIndex === ALL_INSTANCES_INDEX) {
            alert("CSV must include 'instance index' column");
            return;
        }

        const lowerAccountAttrs = accountAttributes.map(a => a.toLowerCase());
        const isValidCSV = lowerAccountAttrs.every(attr =>
            headers.includes(attr)
        );

        if (!isValidCSV) {
            const instanceIndexHeader = instanceIndex === ALL_INSTANCES_INDEX ? ", instance index" : "";
            alert(`CSV headers don't match expected fields. Expected: ${accountAttributes.join(", ")}${instanceIndexHeader}`);
            return;
        }

        const accountsByInstance = {};
        const fieldMapping = accountAttributes.map(attr =>
            headers.indexOf(attr.toLowerCase())
        );
        for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim() === "") continue;

            const values = parseCSVLine(lines[i]);
            if (values.length !== headers.length) {
                console.warn(`Skipping row ${i + 1}: column count mismatch`);
                continue;
            }


            let csvInstanceIndex;
            if (instanceIndex === ALL_INSTANCES_INDEX) {

                csvInstanceIndex = parseInt(values[instanceIndexCol].trim(), 10);
                if (!/^\d+$/.test(csvInstanceIndex.toString()) || csvInstanceIndex === 0) {
                    console.warn(`Skipping row ${i + 1}: invalid instance index "${csvInstanceIndex}"`);
                    continue;
                }
            } else {

                csvInstanceIndex = instanceIndex;
            }

            const accountData = {};
            accountAttributes.forEach((attr, idx) => {
                accountData[attr] = values[fieldMapping[idx]] || "";
            });

            if (!accountsByInstance[csvInstanceIndex]) {
                accountsByInstance[csvInstanceIndex] = [];
            }
            accountsByInstance[csvInstanceIndex].push(accountData);
        }

        if (Object.keys(accountsByInstance).length === 0) {
            alert("No valid account data found in CSV");
            return;
        }

        Object.entries(accountsByInstance).forEach(([instanceIdx, accounts]) => {
            const csvInstanceIndex = parseInt(instanceIdx, 10);
            const instanceCount = parseInt(document.getElementById("instance_count").value, 10) || 1;

            if (csvInstanceIndex > instanceCount) {
                alert(`Warning: CSV contains data for instance ${csvInstanceIndex}, but only ${instanceCount} instances are configured. Increase instance count to use all data.`);
                return;
            }
            if (csvInstanceIndex === ALL_INSTANCES_INDEX) {
                alert(`Warning: CSV contains data for index ${ALL_INSTANCES_INDEX}. This index represents all instances and can't currently be used.`);
                return;
            }

            const accountsContainer = document.getElementById(`dynamic_accounts_container_${csvInstanceIndex}`);
            if (!accountsContainer) {
                console.error(`Container for instance ${csvInstanceIndex} not found`);
                return;
            }

            document.getElementById(`accounts_section_${csvInstanceIndex}`).style.display = "block";
            document.getElementById(`user_count_section_${csvInstanceIndex}`).style.display = "block";

            accountsContainer.innerHTML = "";

            accounts.forEach((account, index) => {
                const accountSection = document.createElement("div");
                accountSection.className = "card p-3 mb-3 position-relative";
                accountSection.id = `account_${csvInstanceIndex}_${index + 1}`;
                accountSection.dataset.accountNumber = index + 1;
                accountSection.style.border = "1px solid #ccc";
                accountSection.style.borderRadius = "5px";
                accountSection.style.padding = "15px";

                const removeBtn = document.createElement("button");
                removeBtn.className = "btn btn-danger btn-sm position-absolute";
                removeBtn.style.top = "5px";
                removeBtn.style.right = "5px";
                removeBtn.innerHTML = "Remove";
                removeBtn.onclick = function () {
                    accountSection.remove();
                    renumberAccounts(csvInstanceIndex);
                    updateUserCount(csvInstanceIndex);
                    selectAutomaticFlavor(csvInstanceIndex);
                };


                let fieldsHtml = `<h5 class="account-title">Account ${index + 1}</h5>`;
                accountAttributes.forEach(attr => {
                    fieldsHtml += `
                        <div class="form-group md-5">
                            <label for="${attr}_${csvInstanceIndex}_${index + 1}">${attr}</label>
                            <input type="text" class="form-control"
                                   id="${attr}_${csvInstanceIndex}_${index + 1}"
                                   name="${attr}_${csvInstanceIndex}"
                                   value="${account[attr] || ''}"
                                   required>
                        </div>
                    `;
                });

                accountSection.innerHTML = fieldsHtml;
                accountSection.appendChild(removeBtn);
                accountsContainer.appendChild(accountSection);
            });

            updateUserCount(csvInstanceIndex);
            selectAutomaticFlavor(instanceIndex);
        });
    }

    reader.readAsText(file);
});

function updateUserCount(instanceIndex) {
    const accountsContainer = document.getElementById(`dynamic_accounts_container_${instanceIndex}`);
    const userCountInput = document.getElementById(`user_count_${instanceIndex}`);

    if (accountsContainer && userCountInput) {
        userCountInput.value = accountsContainer.querySelectorAll('.card').length;
    }
}

function resetCSVUpload(instanceIndex) {
    const csvInput = document.getElementById(`csvUpload_${instanceIndex}`);
    const undoBtn = document.querySelector(`.undo-csv[data-instance="${instanceIndex}"]`);

    if (csvInput) csvInput.value = "";
    if (undoBtn) undoBtn.remove();

    // Wenn wir All Instances (Index 0) zurücksetzen wollen:
    if (parseInt(instanceIndex) === 0) {
        const totalInstances = parseInt(document.getElementById("instance_count").value, 10) || 1;

        for (let i = 1; i <= totalInstances; i++) {
            const accountsContainer = document.getElementById(`dynamic_accounts_container_${i}`);
            const userCountInput = document.getElementById(`user_count_${i}`);

            if (accountsContainer && userCountInput) {
                accountsContainer.innerHTML = "";
                userCountInput.value = "0";
                const section = document.getElementById(`accounts_section_${i}`);
                if (section) section.style.display = "none";
            }
        }
    } else {

        const accountsContainer = document.getElementById(`dynamic_accounts_container_${instanceIndex}`);
        const userCountInput = document.getElementById(`user_count_${instanceIndex}`);

        if (accountsContainer && userCountInput) {
            accountsContainer.innerHTML = "";
            userCountInput.value = "0";

            const section = document.getElementById(`accounts_section_${instanceIndex}`);
            if (section) section.style.display = "none";
        }
    }
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

document.querySelector("form").addEventListener("submit", function(event) {

    document.getElementById('loadingModal').style.display = 'flex';
});

function updateLoadingModal(message) {
    document.getElementById('loadingModal').querySelector('.loading-modal-content p').textContent = message;
}

document.addEventListener("click", function (e) {
    if (e.target.closest(".export_csv_btn")) {
        const btn = e.target.closest(".export_csv_btn");
        const instanceIndex = btn.dataset.instance;
        exportAccountsToCSV(instanceIndex);
    }
});

function exportAccountsToCSV(instanceIndex) {
    const accountsContainer = document.getElementById(`dynamic_accounts_container_${instanceIndex}`);
    if (!accountsContainer) return;

    const rows = [];
    rows.push(accountAttributes.join(","));

    const accountCards = accountsContainer.querySelectorAll(".card");
    accountCards.forEach(card => {
        const values = accountAttributes.map(attr => {
            const input = card.querySelector(`input[name="${attr}_${instanceIndex}"]`);
            return input ? `"${(input.value || "").replace(/"/g, '""')}"` : "";
        });
        rows.push(values.join(","));
    });

    const csvContent = rows.join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `accounts_instance_${instanceIndex}.csv`;
    a.style.display = "none";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

