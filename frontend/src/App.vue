<!-- frontend/src/App.vue -->
<template>
  <div id="app">
    <div class="container">
      <h1>AI Automated Test Evaluator</h1>
      
      <div v-if="!selectedClassId" class="card" style="text-align: center;">
        <h2>Select a Class</h2>
        <select v-model="selectedClassId" @change="fetchTests" class="form-input" style="max-width: 300px; margin: auto;">
          <option :value="null">-- Select Class --</option>
          <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      
      <div v-if="selectedClassId && !selectedTestId" class="card">
        <h2>Tests for {{ selectedClassName }}</h2>
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
         <button @click="selectedClassId = null" style="background: none; border: none; cursor: pointer; color: #6b7280; margin-top: 1.5rem;">&lt; Back to Class Selection</button>
      </div>

      <TestWorkflow v-if="selectedTestId" :test-id="selectedTestId" @back-to-tests="selectedTestId = null" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import TestWorkflow from './components/TestWorkflow.vue';

const API_BASE_URL = 'http://127.0.0.1:8000/api/';

const classes = ref([]);
const tests = ref([]);
const selectedClassId = ref(null);
const selectedTestId = ref(null);
const newTestName = ref('');

const selectedClassName = computed(() => {
    const cls = classes.value.find(c => c.id === selectedClassId.value);
    return cls ? cls.name : '';
});

const fetchClasses = async () => {
    const response = await axios.get(`${API_BASE_URL}classes/`);
    classes.value = response.data;
};

const fetchTests = async () => {
    if (!selectedClassId.value) return;
    const response = await axios.get(`${API_BASE_URL}classes/${selectedClassId.value}/tests/`);
    tests.value = response.data;
    selectedTestId.value = null;
};

const createTest = async () => {
    if (newTestName.value.trim() && selectedClassId.value) {
        await axios.post(`${API_BASE_URL}tests/`, {
            name: newTestName.value,
            class_group: selectedClassId.value
        });
        newTestName.value = '';
        fetchTests();
    }
};

const selectTest = (test) => {
    selectedTestId.value = test.id;
};

onMounted(fetchClasses);
</script>