<!-- frontend/src/App.vue -->
<template>
  <div id="app">
    <div class="container">
      <h1>AI Automated Test Evaluator</h1>

      <!-- Class Selection / Creation -->
      <div v-if="!selectedClassId" class="card">
        <h2 style="text-align: center;">Select or Create a Class</h2>
        <div class="form-group">
            <label class="form-label">Existing Classes:</label>
            <select v-model="selectedClassId" @change="onClassSelect" class="form-input">
              <option :value="null">-- Select Class --</option>
              <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
        </div>
        <hr style="margin: 1.5rem 0;">
        <h3>Add a New Class</h3>
        <div style="display: flex; gap: 0.5rem;">
            <input v-model="newClassName" @keyup.enter="createClass" placeholder="e.g., Grade 9 - History" class="form-input" />
            <button @click="createClass" class="btn btn-green">Add Class</button>
        </div>
        <hr style="margin: 1.5rem 0;">
        <div style="text-align: center;">
            <button @click="showPrinciplesModal = true" class="btn btn-gray">Manage Marking Principles</button>
        </div>
      </div>

      <!-- Test and Student Management -->
      <div v-if="selectedClassId && !selectedTestId" class="card">
        <button @click="selectedClassId = null" style="background: none; border: none; cursor: pointer; color: #6b7280; margin-bottom: 1rem;">&lt; Back to Class Selection</button>
        <h2>Manage: {{ selectedClassName }}</h2>
        <div class="tabs">
          <button @click="managementTab = 'tests'" :class="{ active: managementTab === 'tests' }" class="tab-button">Tests</button>
          <button @click="managementTab = 'students'" :class="{ active: managementTab === 'students' }" class="tab-button">Students</button>
        </div>
        <div v-if="managementTab === 'tests'">
          <h3>Create or Select a Test</h3>
          <div style="display: flex; margin-bottom: 1rem;">
            <input v-model="newTestName" @keyup.enter="createTest" placeholder="New Test Name" class="form-input" style="border-radius: 0.375rem 0 0 0.375rem;"/>
            <button @click="createTest" class="btn btn-blue" style="border-radius: 0 0.375rem 0.375rem 0;">Create Test</button>
          </div>
          <ul class="list">
            <li v-for="t in tests" :key="t.id" @click="selectTest(t)" class="list-item">
              <span>{{ t.name }}</span>
              <span style="font-size: 0.875rem; color: #4b5563;">Max Mark: {{ t.total_max_mark || 0 }}</span>
            </li>
            <li v-if="!tests.length" style="padding: 0.75rem;">No tests have been created for this class yet.</li>
          </ul>
        </div>
        <div v-if="managementTab === 'students'">
          <h3>Add or View Students</h3>
          <div style="display: flex; margin-bottom: 1rem;">
              <input v-model="newStudentName" @keyup.enter="createStudent" placeholder="New Student Name" class="form-input" style="border-radius: 0.375rem 0 0 0.375rem;" />
              <button @click="createStudent" class="btn btn-green" style="border-radius: 0 0.375rem 0.375rem 0;">Add Student</button>
          </div>
          <h4>Current Roster:</h4>
          <ul class="list">
              <li v-for="student in students" :key="student.id" class="list-item" style="cursor: default;">
                  <span>{{ student.name }}</span>
              </li>
              <li v-if="!students.length" style="padding: 0.75rem;">No students have been added to this class yet.</li>
          </ul>
        </div>
      </div>

      <!-- Marking Principles Management Modal -->
      <div v-if="showPrinciplesModal" class="modal-overlay">
        <div class="modal-content">
          <h3>Manage Marking Principles</h3>
          <h4>Existing Principles:</h4>
          <ul class="list">
            <li v-for="p in markingPrinciples" :key="p.id" class="list-item" style="cursor: default;">
              <span>{{ p.name }}</span>
            </li>
            <li v-if="!markingPrinciples.length" style="padding: 0.75rem;">No principles have been uploaded yet.</li>
          </ul>
          <hr style="margin: 1.5rem 0;">
          <h4>Add New Principle:</h4>
          <div class="form-group">
              <label class="form-label">Principle Name:</label>
              <input v-model="newPrincipleName" placeholder="e.g., A-Level Chemistry Standard" class="form-input"/>
          </div>
          <div class="form-group">
              <label class="form-label">PDF File:</label>
              <input type="file" @change="handlePrincipleFileUpload" accept=".pdf" class="form-input"/>
          </div>
          <div class="modal-actions">
              <button @click="uploadPrinciple" class="btn btn-green">Upload</button>
              <button @click="showPrinciplesModal = false" class="btn btn-gray">Close</button>
          </div>
        </div>
      </div>

      <!-- Main Test Workflow Component -->
      <TestWorkflow v-if="selectedTestId" :test-id="selectedTestId" @back-to-tests="selectedTestId = null" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import apiClient from './api/config.js'; // Use the central API client
import TestWorkflow from './components/TestWorkflow.vue';

// --- STATE MANAGEMENT ---
const classes = ref([]);
const tests = ref([]);
const students = ref([]);
const selectedClassId = ref(null);
const selectedTestId = ref(null);
const newClassName = ref('');
const newTestName = ref('');
const newStudentName = ref('');
const managementTab = ref('tests');
const showPrinciplesModal = ref(false);
const markingPrinciples = ref([]);
const newPrincipleName = ref('');
const newPrincipleFile = ref(null);

// --- COMPUTED PROPERTIES ---
const selectedClassName = computed(() => {
    const cls = classes.value.find(c => c.id === selectedClassId.value);
    return cls ? cls.name : '';
});

// --- DATA FETCHING FUNCTIONS ---
const fetchClasses = async () => {
    try {
        const response = await apiClient.get('classes/');
        classes.value = response.data;
    } catch (error) {
        console.error("Failed to fetch classes:", error);
    }
};
const fetchTests = async () => {
    if (!selectedClassId.value) return;
    try {
        const response = await apiClient.get(`classes/${selectedClassId.value}/tests/`);
        tests.value = response.data;
    } catch (error) {
        console.error("Failed to fetch tests:", error);
    }
};
const fetchStudents = async () => {
    if (!selectedClassId.value) return;
    try {
        const response = await apiClient.get(`classes/${selectedClassId.value}/students/`);
        students.value = response.data;
    } catch (error) {
        console.error("Failed to fetch students:", error);
    }
};
const fetchMarkingPrinciples = async () => {
    try {
        const response = await apiClient.get('marking-principles/');
        markingPrinciples.value = response.data;
    } catch (error) {
        console.error("Failed to fetch marking principles:", error);
    }
};

// --- USER ACTIONS ---
const onClassSelect = async () => {
    if (!selectedClassId.value) return;
    managementTab.value = 'tests';
    selectedTestId.value = null;
    await fetchTests();
    await fetchStudents();
};
const createClass = async () => {
    if (!newClassName.value.trim()) return alert('Please enter a class name.');
    try {
        await apiClient.post('classes/', { name: newClassName.value });
        newClassName.value = '';
        alert('Class created successfully!');
        await fetchClasses();
    } catch (error) {
        console.error("Failed to create class:", error.response?.data || error);
        alert("Failed to create class.");
    }
};
const createTest = async () => {
    if (!newTestName.value.trim()) return alert('Please enter a test name.');
    try {
        await apiClient.post('tests/', {
            name: newTestName.value,
            class_group: selectedClassId.value
        });
        newTestName.value = '';
        await fetchTests();
    } catch (error) {
        console.error("Failed to create test:", error.response?.data || error);
    }
};
const createStudent = async () => {
    if (!newStudentName.value.trim()) return alert('Please enter a student name.');
    try {
        await apiClient.post('students/', {
            name: newStudentName.value,
            class_group: selectedClassId.value
        });
        newStudentName.value = '';
        alert('Student added successfully!');
        await fetchStudents();
    } catch (error) {
        console.error("Failed to create student:", error.response?.data || error);
        alert("Failed to create student.");
    }
};
const selectTest = (test) => {
    selectedTestId.value = test.id;
};
const handlePrincipleFileUpload = (event) => {
    newPrincipleFile.value = event.target.files[0];
};
const uploadPrinciple = async () => {
    if (!newPrincipleName.value.trim() || !newPrincipleFile.value) {
        return alert("Please provide a name and select a PDF file.");
    }
    const formData = new FormData();
    formData.append('name', newPrincipleName.value);
    formData.append('pdf_file', newPrincipleFile.value);
    try {
        await apiClient.post('marking-principles/', formData);
        alert('Marking principle uploaded successfully!');
        newPrincipleName.value = '';
        newPrincipleFile.value = null;
        document.querySelector('input[type="file"]').value = ''; // Visually clear the file input
        await fetchMarkingPrinciples();
    } catch (error) {
        console.error("Failed to upload principle:", error.response?.data || error);
        alert("Failed to upload principle.");
    }
};

// --- LIFECYCLE HOOKS ---
onMounted(() => {
    fetchClasses();
    fetchMarkingPrinciples();
});
watch(showPrinciplesModal, (isShowing) => {
    if (isShowing) {
        fetchMarkingPrinciples();
    }
});
</script>