console.log("Script loaded!");

// --- Age Validation ---
function validateAge() {
    const dobString = document.getElementById('dob').value;
    const dobError = document.getElementById('dobError');
    if (!dobString) {
        dobError.textContent = ''; // Clear error if field is empty
        return;
    }

    const dob = new Date(dobString);
    const today = new Date();

    let age = today.getFullYear() - dob.getFullYear();
    const monthDiff = today.getMonth() - dob.getMonth();
    const dayDiff = today.getDate() - dob.getDate();

    if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) {
        age--;
    }

    if (age < 18) {
        dobError.textContent = 'Applicant must be 18 years or older.';
        return false;
    } else {
        dobError.textContent = '';
        return true;
    }
}

// --- Education Section Logic ---
const educationEntriesContainer = document.getElementById('education_entries_container');
const addEducationButton = document.getElementById('add_education_button');
let educationEntryIndex = 0; // To keep track of the next index

function createEducationEntryHTML(index) {
    return `
        <div class="education_entry" data-index="${index}">
            <label for="education[${index}][school_name]">School Name:</label><br>
            <input type="text" name="education[${index}][school_name]" required><br><br>

            <label for="education[${index}][subject_studied]">Subject Studied:</label><br>
            <input type="text" name="education[${index}][subject_studied]"><br><br>

            <label for="education[${index}][school_year_from]">School Year (From):</label><br>
            <input type="date" name="education[${index}][school_year_from]" required><br><br>

            <label for="education[${index}][school_year_to]">School Year (To):</label><br>
            <input type="date" name="education[${index}][school_year_to]" required><br><br>

            <label for="education[${index}][education_level]">Education Level:</label><br>
            <select name="education[${index}][education_level]" required>
                <option value="" disabled selected>Select Level</option>
                <option value="High School">High School</option>
                <option value="Senior High School">Senior High School</option>
                <option value="College">College (Non-degree)</option>
                <option value="Bachelor's">Bachelor’s Degree</option>
                <option value="Master's">Master’s Degree</option>
                <option value="PhD">PhD</option>
            </select><br><br>

            <button type="button" class="remove_education_entry">Remove</button>
            <hr>
        </div>
    `;
}

function reindexEducationEntries() {
    const entries = educationEntriesContainer.querySelectorAll('.education_entry');
    entries.forEach((entry, newIndex) => {
        entry.dataset.index = newIndex; // Update data-index attribute

        const inputs = entry.querySelectorAll('input, select');
        inputs.forEach(input => {
            const nameAttr = input.getAttribute('name');
            if (nameAttr) {
                // Replace the old index (e.g., education[OLD_INDEX][field]) with the newIndex
                const newName = nameAttr.replace(/\[\d+\]/, `[${newIndex}]`);
                input.setAttribute('name', newName);
                // Update 'for' attributes of labels if they exist and follow a similar pattern
                const label = entry.querySelector(`label[for^="${nameAttr.substring(0, nameAttr.lastIndexOf('['))}"]`);
                if (label) {
                    const oldFor = label.getAttribute('for');
                    const newFor = oldFor.replace(/\[\d+\]/, `[${newIndex}]`);
                    label.setAttribute('for', newFor);
                }
            }
        });
    });
    // Update the global index counter to the next available index
    educationEntryIndex = entries.length;
}


function addEducationEntry() {
    // Determine the next index by counting current entries
    // This is more robust than a simple incrementer if entries were re-ordered or manipulated externally
    // but for add/remove, a counter that's updated on reindex is also fine.
    // Using the reindex function to set the global educationEntryIndex
    
    const newEntryHTML = createEducationEntryHTML(educationEntryIndex);
    educationEntriesContainer.insertAdjacentHTML('beforeend', newEntryHTML);
    educationEntryIndex++; // Increment for the next potential add
    // No need to add remove listener here if using event delegation
}

function removeEducationEntry(event) {
    if (event.target.classList.contains('remove_education_entry')) {
        const entryToRemove = event.target.closest('.education_entry');
        if (entryToRemove) {
            entryToRemove.remove();
            reindexEducationEntries(); // Re-index after removal
        }
    }
}

// Event Listener for adding entries
if (addEducationButton) {
    addEducationButton.addEventListener('click', addEducationEntry);
}

// Event Delegation for removing entries
if (educationEntriesContainer) {
    educationEntriesContainer.addEventListener('click', removeEducationEntry);
    // Initialize educationEntryIndex based on existing entries (e.g. the first one)
    // This is important if the page is reloaded with form data that includes education entries
    // However, for this subtask, we assume we start with one entry defined in HTML.
    const initialEntries = educationEntriesContainer.querySelectorAll('.education_entry');
    educationEntryIndex = initialEntries.length;
}

// --- Work Experience Section Logic ---
const experienceEntriesContainer = document.getElementById('experience_entries_container');
const addExperienceButton = document.getElementById('add_experience_button');
let experienceEntryIndex = 0; // To keep track of the next index

function createExperienceEntryHTML(index) {
    return `
        <div class="experience_entry" data-index="${index}">
            <label for="experience[${index}][company_name]">Company Name:</label><br>
            <input type="text" name="experience[${index}][company_name]"><br><br>

            <label for="experience[${index}][job_title]">Job Title:</label><br>
            <input type="text" name="experience[${index}][job_title]"><br><br>

            <label for="experience[${index}][from_date]">From Date:</label><br>
            <input type="date" name="experience[${index}][from_date]"><br><br>

            <label for="experience[${index}][to_date]">To Date:</label><br>
            <input type="date" name="experience[${index}][to_date]"><br><br>

            <button type="button" class="remove_experience_entry">Remove</button>
            <hr>
        </div>
    `;
}

function reindexExperienceEntries() {
    const entries = experienceEntriesContainer.querySelectorAll('.experience_entry');
    entries.forEach((entry, newIndex) => {
        entry.dataset.index = newIndex; // Update data-index attribute

        const inputs = entry.querySelectorAll('input'); // Only inputs for experience
        inputs.forEach(input => {
            const nameAttr = input.getAttribute('name');
            if (nameAttr) {
                const newName = nameAttr.replace(/\[\d+\]/, `[${newIndex}]`);
                input.setAttribute('name', newName);
                const label = entry.querySelector(`label[for^="${nameAttr.substring(0, nameAttr.lastIndexOf('['))}"]`);
                if (label) {
                    const oldFor = label.getAttribute('for');
                    const newFor = oldFor.replace(/\[\d+\]/, `[${newIndex}]`);
                    label.setAttribute('for', newFor);
                }
            }
        });
    });
    experienceEntryIndex = entries.length;
}

function addExperienceEntry() {
    const newEntryHTML = createExperienceEntryHTML(experienceEntryIndex);
    experienceEntriesContainer.insertAdjacentHTML('beforeend', newEntryHTML);
    experienceEntryIndex++;
}

function removeExperienceEntry(event) {
    if (event.target.classList.contains('remove_experience_entry')) {
        const entryToRemove = event.target.closest('.experience_entry');
        if (entryToRemove) {
            entryToRemove.remove();
            reindexExperienceEntries();
        }
    }
}

if (addExperienceButton) {
    addExperienceButton.addEventListener('click', addExperienceEntry);
}

if (experienceEntriesContainer) {
    experienceEntriesContainer.addEventListener('click', removeExperienceEntry);
    const initialExpEntries = experienceEntriesContainer.querySelectorAll('.experience_entry');
    experienceEntryIndex = initialExpEntries.length;
}

// --- Language Section Logic ---
const languageEntriesContainer = document.getElementById('language_entries_container');
const addLanguageButton = document.getElementById('add_language_button');
let languageEntryIndex = 0; // To keep track of the next index

function createLanguageEntryHTML(index) {
    return `
        <div class="language_entry" data-index="${index}">
            <label for="language[${index}][name]">Language:</label><br>
            <select name="language[${index}][name]" required>
                <option value="" disabled selected>Select Language</option>
                <option value="English">English</option>
                <option value="Spanish">Spanish</option>
                <option value="Turkish">Turkish</option>
                <option value="Italian">Italian</option>
                <option value="German">German</option>
                <option value="Arabic">Arabic</option>
                <option value="Tagalog">Tagalog</option>
                <option value="Urdu">Urdu</option>
                <option value="Hindi">Hindi</option>
                <option value="Bisaya">Bisaya</option>
                <option value="Ilonggo">Ilonggo</option>
                <option value="Other">Other</option>
            </select><br><br>

            <label for="language[${index}][fluency]">Fluency:</label><br>
            <select name="language[${index}][fluency]" required>
                <option value="" disabled selected>Select Fluency</option>
                <option value="Native">Native</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Beginner">Beginner</option>
                <option value="A1">A1</option>
                <option value="A2">A2</option>
                <option value="B1">B1</option>
                <option value="B2">B2</option>
                <option value="C1">C1</option>
                <option value="C2">C2</option>
            </select><br><br>

            <button type="button" class="remove_language_entry">Remove</button>
            <hr>
        </div>
    `;
}

function reindexLanguageEntries() {
    const entries = languageEntriesContainer.querySelectorAll('.language_entry');
    entries.forEach((entry, newIndex) => {
        entry.dataset.index = newIndex; // Update data-index attribute

        const selects = entry.querySelectorAll('select');
        selects.forEach(select => {
            const nameAttr = select.getAttribute('name');
            if (nameAttr) {
                const newName = nameAttr.replace(/\[\d+\]/, `[${newIndex}]`);
                select.setAttribute('name', newName);
                const label = entry.querySelector(`label[for^="${nameAttr.substring(0, nameAttr.lastIndexOf('['))}"]`);
                if (label) {
                    const oldFor = label.getAttribute('for');
                    const newFor = oldFor.replace(/\[\d+\]/, `[${newIndex}]`);
                    label.setAttribute('for', newFor);
                }
            }
        });
    });
    languageEntryIndex = entries.length;
}

function addLanguageEntry() {
    const newEntryHTML = createLanguageEntryHTML(languageEntryIndex);
    languageEntriesContainer.insertAdjacentHTML('beforeend', newEntryHTML);
    languageEntryIndex++;
}

function removeLanguageEntry(event) {
    if (event.target.classList.contains('remove_language_entry')) {
        // As per instruction, allow removal, rely on server-side for "at least one"
        const entryToRemove = event.target.closest('.language_entry');
        if (entryToRemove) {
            entryToRemove.remove();
            reindexLanguageEntries();
        }
    }
}

if (addLanguageButton) {
    addLanguageButton.addEventListener('click', addLanguageEntry);
}

if (languageEntriesContainer) {
    languageEntriesContainer.addEventListener('click', removeLanguageEntry);
    const initialLangEntries = languageEntriesContainer.querySelectorAll('.language_entry');
    languageEntryIndex = initialLangEntries.length;
}

// --- Social Media Section Logic ---
const socialMediaEntriesContainer = document.getElementById('social_media_entries_container');
const addSocialMediaButton = document.getElementById('add_social_media_button');
let socialMediaEntryIndex = 0; // Initialized to 0 as no entries are in HTML initially

function createSocialMediaEntryHTML(index) {
    return `
        <div class="social_media_entry" data-index="${index}">
            <label for="social_media[${index}][platform]">Platform:</label><br>
            <select name="social_media[${index}][platform]" required>
                <option value="" disabled selected>Select Platform</option>
                <option value="Facebook">Facebook</option>
                <option value="LinkedIn">LinkedIn</option>
                <option value="Twitter (X)">Twitter (X)</option>
                <option value="Instagram">Instagram</option>
                <option value="Reddit">Reddit</option>
                <option value="TikTok">TikTok</option>
            </select><br><br>

            <label for="social_media[${index}][profile_link]">Profile Link:</label><br>
            <input type="url" name="social_media[${index}][profile_link]" placeholder="https://example.com/profile"><br><br>

            <button type="button" class="remove_social_media_entry">Remove</button>
            <hr>
        </div>
    `;
}

function reindexSocialMediaEntries() {
    const entries = socialMediaEntriesContainer.querySelectorAll('.social_media_entry');
    entries.forEach((entry, newIndex) => {
        entry.dataset.index = newIndex;

        const selects = entry.querySelectorAll('select');
        selects.forEach(select => {
            const nameAttr = select.getAttribute('name');
            if (nameAttr) {
                const newName = nameAttr.replace(/\[\d+\]/, `[${newIndex}]`);
                select.setAttribute('name', newName);
                const label = entry.querySelector(`label[for^="${nameAttr.substring(0, nameAttr.lastIndexOf('['))}"]`);
                if (label) {
                    const oldFor = label.getAttribute('for'); // Example: social_media[0][platform]
                    const newFor = oldFor.replace(/\[\d+\]/, `[${newIndex}]`);
                    label.setAttribute('for', newFor);
                }
            }
        });

        const inputs = entry.querySelectorAll('input[type="url"]');
        inputs.forEach(input => {
            const nameAttr = input.getAttribute('name');
            if (nameAttr) {
                const newName = nameAttr.replace(/\[\d+\]/, `[${newIndex}]`);
                input.setAttribute('name', newName);
                 const label = entry.querySelector(`label[for^="${nameAttr.substring(0, nameAttr.lastIndexOf('['))}"]`);
                if (label) {
                    const oldFor = label.getAttribute('for');
                    const newFor = oldFor.replace(/\[\d+\]/, `[${newIndex}]`);
                    label.setAttribute('for', newFor);
                }
            }
        });
    });
    socialMediaEntryIndex = entries.length;
}

function addSocialMediaEntry() {
    const newEntryHTML = createSocialMediaEntryHTML(socialMediaEntryIndex);
    socialMediaEntriesContainer.insertAdjacentHTML('beforeend', newEntryHTML);
    socialMediaEntryIndex++;
}

function removeSocialMediaEntry(event) {
    if (event.target.classList.contains('remove_social_media_entry')) {
        const entryToRemove = event.target.closest('.social_media_entry');
        if (entryToRemove) {
            entryToRemove.remove();
            reindexSocialMediaEntries();
        }
    }
}

if (addSocialMediaButton) {
    addSocialMediaButton.addEventListener('click', addSocialMediaEntry);
}

if (socialMediaEntriesContainer) {
    socialMediaEntriesContainer.addEventListener('click', removeSocialMediaEntry);
    // socialMediaEntryIndex is already initialized to 0, no need to count initial entries
}


const dobInput = document.getElementById('dob');
if (dobInput) {
    dobInput.addEventListener('change', validateAge);
    dobInput.addEventListener('blur', validateAge);
}

// --- Address Dropdown Logic ---
const countrySelect = document.getElementById('country');
const provinceSelect = document.getElementById('province');
const citySelect = document.getElementById('city');
let countriesData = [];

async function loadCountries() {
    try {
        const response = await fetch('/data/countries.json'); // Path relative to the public folder
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        countriesData = await response.json();

        // For now, we assume "Philippines" is the only country and it's pre-selected in HTML.
        // If we were populating the country dropdown:
        // countriesData.forEach(country => {
        //     const option = document.createElement('option');
        //     option.value = country.name;
        //     option.textContent = country.name;
        //     countrySelect.appendChild(option);
        // });

        // countrySelect.value = "Philippines"; // Ensure Philippines is selected if populated dynamically

        if (countrySelect.value === "Philippines") {
            loadProvinces(countrySelect.value);
        }

    } catch (error) {
        console.error("Failed to load countries.json:", error);
    }
}

function loadProvinces(countryName) {
    // Clear previous options
    provinceSelect.innerHTML = '<option value="" disabled selected>Select Province</option>';
    citySelect.innerHTML = '<option value="" disabled selected>Select City/Municipality</option>';

    const selectedCountry = countriesData.find(country => country.name === countryName);

    if (selectedCountry && selectedCountry.provinces) {
        selectedCountry.provinces.forEach(province => {
            const option = document.createElement('option');
            option.value = province.name;
            option.textContent = province.name;
            provinceSelect.appendChild(option);
        });
    }
}

function loadCities(countryName, provinceName) {
    // Clear previous options
    citySelect.innerHTML = '<option value="" disabled selected>Select City/Municipality</option>';

    const selectedCountry = countriesData.find(country => country.name === countryName);
    if (!selectedCountry) return;

    const selectedProvince = selectedCountry.provinces.find(province => province.name === provinceName);

    if (selectedProvince && selectedProvince.cities) {
        selectedProvince.cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        });
    }
}

// Event Listeners
if (countrySelect) {
    countrySelect.addEventListener('change', function() {
        loadProvinces(this.value);
    });
}

if (provinceSelect) {
    provinceSelect.addEventListener('change', function() {
        const selectedCountry = countrySelect.value;
        loadCities(selectedCountry, this.value);
    });
}

// Initial load & repopulation logic
document.addEventListener('DOMContentLoaded', async () => {
    // formDataFromServer is now globally available from the inline script in index.html
    await loadCountries(); // Wait for countries and initial provinces to load

    if (formDataFromServer && formDataFromServer.country) {
        countrySelect.value = formDataFromServer.country;
        // Trigger change to load provinces if not already loaded for the default country
        // This assumes loadCountries might not have already loaded them if country wasn't default
        if (countrySelect.value) { // Check if a valid country is selected
            await loadProvinces(countrySelect.value); // Ensure provinces are loaded
            if (formDataFromServer.province) {
                provinceSelect.value = formDataFromServer.province;
                if (provinceSelect.value) { // Check if a valid province is selected
                    await loadCities(countrySelect.value, provinceSelect.value); // Ensure cities are loaded
                    if (formDataFromServer.city) {
                        citySelect.value = formDataFromServer.city;
                    }
                }
            }
        }
    }
});

// Ensure loadProvinces and loadCities return a promise if they become async due to fetch/await,
// or adjust the calling logic if they remain synchronous.
// For now, assuming they populate synchronously after countriesData is available.
// Making them async to be safe for future changes.

async function loadProvinces(countryName) {
    // Clear previous options
    provinceSelect.innerHTML = '<option value="" disabled selected>Select Province</option>';
    citySelect.innerHTML = '<option value="" disabled selected>Select City/Municipality</option>';

    const selectedCountry = countriesData.find(country => country.name === countryName);

    if (selectedCountry && selectedCountry.provinces) {
        selectedCountry.provinces.forEach(province => {
            const option = document.createElement('option');
            option.value = province.name;
            option.textContent = province.name;
            provinceSelect.appendChild(option);
        });
    }
}

async function loadCities(countryName, provinceName) {
    // Clear previous options
    citySelect.innerHTML = '<option value="" disabled selected>Select City/Municipality</option>';

    const selectedCountry = countriesData.find(country => country.name === countryName);
    if (!selectedCountry) return;

    const selectedProvince = selectedCountry.provinces.find(province => province.name === provinceName);

    if (selectedProvince && selectedProvince.cities) {
        selectedProvince.cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        });
    }
}
