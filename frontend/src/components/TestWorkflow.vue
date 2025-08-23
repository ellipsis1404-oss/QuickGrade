<!-- frontend/src/components/TestWorkflow.vue -->

<!-- =================================================================
     TEMPLATE: The HTML structure of the component
     ================================================================= -->
<template>
  <div>
    <div class="card">
      <button @click="$emit('backToTests')" style="background: none; border: none; cursor: pointer; color: #3b82f6; margin-bottom: 1rem;">&lt; Back to Tests</button>
      <h2>{{ test.name }} Workflow</h2>

      <!-- Marking Principle Selection -->
      <div class="card" style="margin-top: 0; margin-bottom: 1rem;">
          <div class="form-group">
              <label class="form-label"><strong>Select Overall Marking Principle:</strong></label>
              <select v-model="test.marking_principle" @change="onPrincipleChange" class="form-input">
                  <option :value="null">-- None --</option>
                  <option v-for="p in markingPrinciples" :key="p.id" :value="p.id">
                      {{ p.name }}
                  </option>
              </select>
          </div>
      </div>
      
      <!-- Tab Navigation -->
      <div class="tabs">
        <button @click="activeTab = 'questions'" :class="{ active: activeTab === 'questions' }" class="tab-button">1. Setup Questions</button>
        <button @click="activeTab = 'upload'" :class="{ active: activeTab === 'upload' }" class="tab-button">2. Upload Answers</button>
        <button @click="loadReport" :class="{ active: activeTab === 'report' }" class="tab-button">3. View Report</button>
      </div>

      <!-- Tab Content: Questions -->
      <div v-if="activeTab === 'questions'">
        <h3>Define Marking Scheme</h3>
        <div v-for="q in questions" :key="q.id" class="list-item" style="cursor: default; flex-direction: column; align-items: start; gap: 0.5rem;">
          <p><strong>Q{{ q.q_number }} (Max: {{ q.max_mark }}) - {{ q.description }}</strong></p>
          <p><strong>Model Answer:</strong> {{ q.model_answer.substring(0, 50) }}...</p>
          <p><strong>Scheme:</strong> {{ q.marking_scheme.substring(0, 50) }}...</p>
          <button @click="editQuestion(q)" style="background: none; border: none; color: #3b82f6; cursor: pointer; padding: 0;">Edit Details</button>
        </div>
        <button @click="addQuestion" class="btn btn-green" style="margin-top: 1rem;">Add New Question</button>
      </div>

      <!-- Tab Content: Upload Answers -->
      <div v-if="activeTab === 'upload'">
        <h3>Submit Student Answer</h3>
        <div class="form-group">
          <label class="form-label">Select Student:</label>
          <select v-model="selectedStudentId" class="form-input"><option v-for="s in students" :key="s.id" :value="s.id">{{ s.name }}</option></select>
        </div>
        <div class="form-group">
          <label class="form-label">Select Question:</label>
          <select v-model="selectedQuestionId" class="form-input"><option v-for="q in questions" :key="q.id" :value="q.id">Q{{ q.q_number }}</option></select>
        </div>
        <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
          <button @click="showCamera = true" class="btn btn-blue">Capture from Camera</button>
          <div>
              <label for="file-upload" class="btn btn-gray">Upload Image File</label>
              <input id="file-upload" type="file" @change="handleFileUpload" accept="image/*" style="display: none;" />
          </div>
        </div>
        <div v-if="imageForOcr" class="card">
          <h4>Step 2: Correct OCR Text & Evaluate</h4>
          <p v-if="isOcrRunning" style="color: #6b7280;">Extracting text from image...</p>
          <div v-else>
              <div class="form-group">
                  <label class="form-label"><strong>Extracted Text (Editable):</strong></label>
                  <textarea v-model="ocrText" class="form-input" rows="8"></textarea>
              </div>
              <button @click="runFinalEvaluation" :disabled="isEvaluating" class="btn btn-purple">
                  {{ isEvaluating ? 'Evaluating...' : 'Confirm and Evaluate' }}
              </button>
          </div>
        </div>
        <p v-if="evaluationMessage" style="margin-top: 0.75rem; font-weight: 600; color: #16a34a;">{{ evaluationMessage }}</p>
      </div>

      <!-- Tab Content: Report -->
      <div v-if="activeTab === 'report'">
    <h3>Test Report & Individual Answers</h3>
    <div v-if="!answers.length">
        <p>No student answers have been submitted for this test yet.</p>
    </div>
    <div v-else>
        <div v-for="answer in answers" :key="answer.id" class="list-item" style="cursor: default; flex-direction: column; align-items: start; gap: 0.5rem;">
            <p><strong>{{ answer.student.name }} - Q{{ answer.question.q_number }}</strong></p>
            
            <div v-if="answer.is_evaluated">
                <p style="color: #16a34a; font-weight: bold;">Mark: {{ answer.mark_gained }} / {{ answer.question.max_mark }}</p>
                <button @click="openEditModal(answer)" class="btn btn-blue" style="margin-top: 0.5rem; padding: 0.25rem 0.5rem; font-size: 0.875rem;">
        Edit & Re-evaluate
    </button>
                <details>
                    <summary>View Evaluation Details</summary>
                    <p style="margin-top: 0.5rem;"><strong>Recognized Text:</strong> {{ answer.ocr_text }}</p>
                    <p><strong>Strengths:</strong> {{ answer.ai_strength_points }}</p>
                    <p><strong>Improvements:</strong> {{ answer.ai_improvement_points }}</p>
                </details>
            </div>
            
           <div v-else>
                <p style="color: #ca8a04;">Status: Not yet evaluated.</p>
                
                <!-- IF this answer is the one being re-evaluated, show the spinner -->
                <div v-if="isReevaluatingId === answer.id" class="spinner" style="margin-top: 0.5rem;"></div>

                <!-- OTHERWISE, show the button -->
                <button v-else @click="reEvaluateAnswer(answer.id)" class="btn btn-purple" style="margin-top: 0.5rem;">
                    Run AI Evaluation Now
                </button>
            </div>
      </div>
    </div>
</div>

    </div>

    <!-- Question Modal -->
    <div v-if="showQuestionModal" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ modalQuestion.id ? 'Edit' : 'Add' }} Question</h3>
        <div class="form-group"><label class="form-label">Q Number:</label><input v-model.number="modalQuestion.q_number" type="number" class="form-input"/></div>
        <div class="form-group"><label class="form-label">Max Mark:</label><input v-model.number="modalQuestion.max_mark" type="number" class="form-input"/></div>
        <div class="form-group"><label class="form-label">Question Description:</label><textarea v-model="modalQuestion.description" class="form-input"></textarea></div>
        <div class="form-group"><label class="form-label">Upload Diagram (Optional):</label><input type="file" @change="handleQuestionImageUpload" class="form-input" /></div>
        <div class="form-group"><label class="form-label">Marking Scheme:</label><textarea v-model="modalQuestion.marking_scheme" class="form-input"></textarea></div>
        <div class="form-group">
            <label class="form-label">Model Answer:</label>
            <button @click="generateModelAnswer" :disabled="isGenerating" class="btn btn-blue" style="margin-bottom: 0.5rem;">
                {{ isGenerating ? 'Generating...' : 'Generate with AI' }}
            </button>
            <textarea v-model="modalQuestion.model_answer" class="form-input" rows="5"></textarea>
        </div>
        <div class="modal-actions">
          <button @click="saveQuestion" class="btn btn-green">Save</button>
          <button @click="showQuestionModal = false" class="btn btn-gray">Cancel</button>
        </div>
      </div>
    </div>

    <div v-if="showEditModal && answerToEdit" class="modal-overlay">
      <div class="modal-content">
        <h3>Edit OCR Text & Re-evaluate</h3>
        <p><strong>Student:</strong> {{ answerToEdit.student.name }}</p>
        <p><strong>Question:</strong> Q{{ answerToEdit.question.q_number }}</p>
        <div class="form-group">
            <label class="form-label"><strong>Recognized Text (Editable):</strong></label>
            <textarea v-model="answerToEdit.ocr_text" class="form-input" rows="10"></textarea>
        </div>
        <div class="modal-actions">
          <button @click="submitReEvaluation" :disabled="isEvaluating" class="btn btn-purple">
            {{ isEvaluating ? 'Re-evaluating...' : 'Save & Re-evaluate' }}
          </button>
          <button @click="showEditModal = false" class="btn btn-gray">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Camera Modal -->
    <CameraCapture v-if="showCamera" @close="showCamera = false" @photo-captured="handlePhotoCaptured" />
  </div>
</template>


<!-- =================================================================
     SCRIPT: The JavaScript logic for the component
     ================================================================= -->
<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import CameraCapture from './CameraCapture.vue';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/';

const props = defineProps({ testId: { type: Number, required: true } });
const emit = defineEmits(['backToTests']);

// --- STATE MANAGEMENT ---
const activeTab = ref('questions');
const test = ref({});
const students = ref([]);
const questions = ref([]);
const answers = ref([]); // For the report tab
const reportResults = ref([]); // For the old summary report
const markingPrinciples = ref([]);
const selectedStudentId = ref(null);
const selectedQuestionId = ref(null);
const imageForOcr = ref(null);
const ocrText = ref('');
const isOcrRunning = ref(false);
const isEvaluating = ref(false);
const evaluationMessage = ref('');
const showCamera = ref(false);
const showQuestionModal = ref(false);
const modalQuestion = ref({});
const isGenerating = ref(false);
const questionImageFile = ref(null);
const isReevaluatingId = ref(null);
const showEditModal = ref(false);
const answerToEdit = ref(null);

// --- DATA FETCHING FUNCTIONS ---
const fetchTestDetails = async () => { /* ... unchanged ... */ };
const fetchQuestions = async () => { /* ... unchanged ... */ };
const fetchMarkingPrinciples = async () => { /* ... unchanged ... */ };
const loadReport = async () => {
    activeTab.value = 'report';
    const allAnswersResp = await axios.get(`${API_BASE_URL}answers/?question__test=${props.testId}`);
    answers.value = allAnswersResp.data;
};

// --- QUESTION MANAGEMENT FUNCTIONS ---
const addQuestion = () => { /* ... unchanged ... */ };
const editQuestion = (q) => { /* ... unchanged ... */ };
const handleQuestionImageUpload = (event) => { /* ... unchanged ... */ };
const saveQuestion = async () => { /* ... unchanged ... */ };
const generateModelAnswer = async () => { /* ... unchanged ... */ };

// --- MARKING PRINCIPLE MANAGEMENT ---
const onPrincipleChange = async () => { /* ... unchanged ... */ };

// --- STUDENT ANSWER EVALUATION WORKFLOW ---
const resetEvaluationState = () => { /* ... unchanged ... */ };
const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
        imageForOcr.value = file;
        runOcr();
    }
};
const handlePhotoCaptured = (photoBlob) => { /* ... unchanged ... */ };
const runOcr = async () => {
    if (!selectedStudentId.value || !selectedQuestionId.value) {
        alert("Please select a student and question.");
        return;
    }
    isOcrRunning.value = true;
    const formData = new FormData();
    formData.append('student', selectedStudentId.value);
    formData.append('question', selectedQuestionId.value);
    formData.append('uploaded_image', imageForOcr.value);
    try {
        const response = await axios.post(`${API_BASE_URL}answers/`, formData);
        const answerId = response.data.id;
        const ocrResponse = await axios.post(`${API_BASE_URL}answers/${answerId}/run-ocr/`); // Must have hyphen
        ocrText.value = ocrResponse.data.ocr_text;
        imageForOcr.value.tempAnswerId = answerId;
    } catch (error) {
        console.error("OCR step failed:", error.response?.data || error);
        evaluationMessage.value = `Error during OCR: ${error.response?.data?.detail || error.message}`;
        resetEvaluationState();
    } finally {
        isOcrRunning.value = false;
    }
};
const runFinalEvaluation = async () => {
    if (!imageForOcr.value?.tempAnswerId) return;
    isEvaluating.value = true;
    try {
        const answerId = imageForOcr.value.tempAnswerId;
        await axios.post(`${API_BASE_URL}answers/${answerId}/run-marking/`, { // Must have hyphen
            corrected_text: ocrText.value
        });
        evaluationMessage.value = `Evaluation Complete!`;
        resetEvaluationState();
    } catch (error) {
        console.error("Marking step failed:", error.response?.data || error);
        evaluationMessage.value = `Error during marking: ${error.response?.data?.detail || error.message}`;
    } finally {
        isEvaluating.value = false;
    }
};

// --- NEW RE-EVALUATION FUNCTION ---
const reEvaluateAnswer = async (answerId) => {
    isReevaluatingId.value = answerId;
    try {
        alert("Starting evaluation for this answer. This may take a moment.");
        const ocrResponse = await axios.post(`${API_BASE_URL}answers/${answerId}/run-ocr/`); // Must have hyphen
        const evalResponse = await axios.post(`${API_BASE_URL}answers/${answerId}/run-marking/`, { // Must have hyphen
            corrected_text: ocrResponse.data.ocr_text
        });
        alert(`Evaluation complete! Mark: ${evalResponse.data.mark_gained}`);
        loadReport();
    } catch (error) {
        console.error("Re-evaluation failed:", error.response?.data || error);
        alert("Re-evaluation failed. See console for details.");
    }
    finally {
        isReevaluatingId.value = null; // <-- Clear loading state
    }
};

// Function to open the modal and populate it with the answer's data
const openEditModal = (answer) => {
    // Create a copy of the answer object to avoid modifying the original list directly
    answerToEdit.value = { ...answer }; 
    showEditModal.value = true;
};

// Function to submit the corrected text for re-marking
const submitReEvaluation = async () => {
    if (!answerToEdit.value) return;

    isEvaluating.value = true; // Use the existing loading state
    try {
        const answerId = answerToEdit.value.id;
        
        // Call the same run_marking endpoint as before
        const evalResponse = await axios.post(`${API_BASE_URL}answers/${answerId}/run-marking/`, {
            corrected_text: answerToEdit.value.ocr_text // Send the edited text
        });

        alert(`Re-evaluation complete! New Mark: ${evalResponse.data.mark_gained}`);
        showEditModal.value = false;
        loadReport(); // Refresh the report with the new data
    } catch (error) {
        console.error("Re-evaluation submission failed:", error.response?.data || error);
        alert("Failed to submit re-evaluation. See console for details.");
    } finally {
        isEvaluating.value = false;
    }
};

// --- VUE LIFECYCLE HOOKS ---
onMounted(() => {
    fetchTestDetails();
    fetchQuestions();
    fetchMarkingPrinciples();
});
watch(activeTab, (newTab) => {
    if (newTab === 'upload') resetEvaluationState();
    if (newTab === 'report') loadReport();
});


</script>

<style scoped>
.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border-left-color: #09f;
  animation: spin 1s ease infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>