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
            <input v-model="newTestName" placeholder="New Test Name" class="form-input" style="border-radius: 0.375rem 0 0 0.375rem;"/>
            <button @click="createTest" class="btn btn-blue" style="border-radius: 0 0.375rem 0.375rem 0;">Create Test</button>
          </div>
          <ul class="list">
            <li v-for="t in tests" :key="t.id" @click="selectTest(t)" class="list-item">
              <span>{{ t.name }}</span>
              <span style="font-size: 0.875rem; color: #4b5563;">Max Mark: {{ t.total_max_mark }}</span>
            </li>
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
      <div v-if="showPrinciplesModal" class="modal-overlay">
  <div class="modal-content">
    <h3>Manage Marking Principles</h3>
    
    <!-- List of existing principles -->
    <h4>Existing Principles:</h4>
    <ul class="list">
      <li v-for="p in markingPrinciples" :key="p.id" class="list-item" style="cursor: default;">
        <span>{{ p.name }}</span>
      </li>
      <li v-if="!markingPrinciples.length" style="padding: 0.75rem;">No principles have been uploaded yet.</li>
    </ul>

    <hr style="margin: 1.5rem 0;">

    <!-- Form to upload a new principle -->
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
import axios from 'axios';
import TestWorkflow from './components/TestWorkflow.vue';

const API_BASE_URL = 'http://127.0.0.1:8000/api/';

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

const selectedClassName = computed(() => {
    const cls = classes.value.find(c => c.id === selectedClassId.value);
    return cls ? cls.name : '';
});

const fetchMarkingPrinciples = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}marking-principles/`);
        markingPrinciples.value = response.data;
    } catch (error) {
        console.error("Failed to fetch marking principles:", error);
    }
};

const handlePrincipleFileUpload = (event) => {
    newPrincipleFile.value = event.target.files[0];
};

const uploadPrinciple = async () => {
    if (!newPrincipleName.value.trim() || !newPrincipleFile.value) {
        alert("Please provide a name and select a PDF file.");
        return;
    }

    const formData = new FormData();
    formData.append('name', newPrincipleName.value);
    formData.append('pdf_file', newPrincipleFile.value);

    try {
        await axios.post(`${API_BASE_URL}marking-principles/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });

        alert('Marking principle uploaded successfully! Text extraction will happen in the background.');
        newPrincipleName.value = '';
        newPrincipleFile.value = null; // This won't clear the file input visually, a common HTML limitation
        await fetchMarkingPrinciples(); // Refresh the list
    } catch (error) {
        console.error("Failed to upload principle:", error.response?.data || error);
        alert("Failed to upload principle. See console for details.");
    }
};

const fetchClasses = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}classes/`);
        classes.value = response.data;
    } catch (error) {
        console.error("Failed to fetch classes:", error);
    }
};

const fetchTests = async () => {
    if (!selectedClassId.value) return;
    try {
        const response = await axios.get(`${API_BASE_URL}classes/${selectedClassId.value}/tests/`);
        tests.value = response.data;
    } catch (error) {
        console.error("Failed to fetch tests:", error);
    }
};

const fetchStudents = async () => {
    if (!selectedClassId.value) return;
    try {
        const response = await axios.get(`${API_BASE_URL}classes/${selectedClassId.value}/students/`);
        students.value = response.data;
    } catch (error) {
        console.error("Failed to fetch students:", error);
    }
};

const onClassSelect = async () => {
    if (!selectedClassId.value) return;
    managementTab.value = 'tests'; // Reset to tests tab on new selection
    selectedTestId.value = null;
    await fetchTests();
    await fetchStudents();
};

const createClass = async () => {
    if (!newClassName.value.trim()) {
        alert('Please enter a class name.');
        return;
    }
    try {
        await axios.post(`${API_BASE_URL}classes/`, { name: newClassName.value });
        newClassName.value = '';
        alert('Class created successfully!');
        await fetchClasses();
    } catch (error) {
        console.error("Failed to create class:", error.response?.data || error);
        alert("Failed to create class. See console for details.");
    }
};

const createTest = async () => {
    if (!newTestName.value.trim() || !selectedClassId.value) return;
    try {
        await axios.post(`${API_BASE_URL}tests/`, {
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
    if (!newStudentName.value.trim() || !selectedClassId.value) {
        alert('Please enter a student name.');
        return;
    }
    try {
        await axios.post(`${API_BASE_URL}students/`, {
            name: newStudentName.value,
            class_group: selectedClassId.value
        });
        newStudentName.value = '';
        alert('Student added successfully!');
        await fetchStudents(); // Refresh the list
    } catch (error) {
        console.error("Failed to create student:", error.response?.data || error);
        alert("Failed to create student. See console for details.");
    }
};

const selectTest = (test) => {
    selectedTestId.value = test.id;
};

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