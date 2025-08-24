<!-- frontend/src/components/TestWorkflow.vue -->
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
              <input id="file-upload" ref="fileUploadInput" type="file" @change="handleFileUpload" accept="image/*" style="display: none;" />
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
                    <button @click="openEditModal(answer)" class="btn btn-blue" style="margin-top: 0.5rem; padding: 0.25rem 0.5rem; font-size: 0.875rem;">Edit & Re-evaluate</button>
                    <details><summary>View Evaluation Details</summary>
                      <p style="margin-top: 0.5rem;"><strong>Recognized Text:</strong> {{ answer.ocr_text }}</p>
                      <p><strong>Strengths:</strong> {{ answer.ai_strength_points }}</p>
                      <p><strong>Improvements:</strong> {{ answer.ai_improvement_points }}</p>
                    </details>
                  </div>
                  <div v-else>
                    <p style="color: #ca8a04;">Status: Not yet evaluated.</p>
                    <div v-if="isReevaluatingId === answer.id" class="spinner" style="margin-top: 0.5rem;"></div>
                    <button v-else @click="reEvaluateAnswer(answer.id)" class="btn btn-purple" style="margin-top: 0.5rem;">Run AI Evaluation Now</button>
                  </div>
              </div>
          </div>
          <hr style="margin: 1.5rem 0;">
          <div style="display: flex; gap: 0.5rem;">
              <button @click="exportReportToCSV" class="btn btn-blue" :disabled="!answers.length">Export as CSV</button>
              <button @click="exportReportToPDF" class="btn btn-green" :disabled="!answers.length">Export as PDF</button>
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

    <!-- Edit & Re-evaluate Modal -->
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
          <button @click="submitReEvaluation" :disabled="isEvaluating" class="btn btn-purple">{{ isEvaluating ? 'Re-evaluating...' : 'Save & Re-evaluate' }}</button>
          <button @click="showEditModal = false" class="btn btn-gray">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Camera Modal -->
    <CameraCapture v-if="showCamera" @close="showCamera = false" @photo-captured="handlePhotoCaptured" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import apiClient from '../api/config.js'; // Use the central API client
import CameraCapture from './CameraCapture.vue';
import jsPDF from "jspdf";
import autoTable from 'jspdf-autotable';

const props = defineProps({ testId: { type: Number, required: true } });
const emit = defineEmits(['backToTests']);

// --- STATE MANAGEMENT ---
const activeTab = ref('questions');
const test = ref({});
const students = ref([]);
const questions = ref([]);
const answers = ref([]);
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
const fileUploadInput = ref(null); // Ref for the file input element
const showEditModal = ref(false);
const answerToEdit = ref(null);
const isReevaluatingId = ref(null);

// frontend/src/components/TestWorkflow.vue

// --- DATA FETCHING FUNCTIONS ---
const fetchTestDetails = async () => {
    try {
        const testResp = await apiClient.get(`tests/${props.testId}/`);
        test.value = testResp.data;
        
        const studentResp = await apiClient.get(`classes/${test.value.class_group}/students/`);
        students.value = studentResp.data;
        
        // --- THIS IS A CRITICAL FIX ---
        // Ensure a default is set only after students have loaded.
        if (students.value.length > 0) {
            selectedStudentId.value = students.value[0].id;
        }
    } catch (error) { 
        console.error("Failed to fetch test details:", error); 
    }
};

const fetchQuestions = async () => {
    try {
        const resp = await apiClient.get(`questions/?test=${props.testId}`);
        questions.value = resp.data;
        
        // --- THIS IS A CRITICAL FIX ---
        // Ensure a default is set only after questions have loaded.
        if (questions.value.length > 0) {
            selectedQuestionId.value = questions.value[0].id;
        }
    } catch (error) { 
        console.error("Failed to fetch questions:", error); 
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
const loadReport = async () => {
    activeTab.value = 'report';
    try {
        const allAnswersResp = await apiClient.get(`answers/?question__test=${props.testId}`);
        answers.value = allAnswersResp.data;
    } catch (error) { console.error("Failed to load report answers:", error); }
};

// --- QUESTION MANAGEMENT FUNCTIONS ---
const addQuestion = () => {
    modalQuestion.value = { q_number: questions.value.length + 1, max_mark: 10, description: '', model_answer: '', marking_scheme: '' };
    questionImageFile.value = null;
    showQuestionModal.value = true;
};
const editQuestion = (q) => {
    modalQuestion.value = { ...q };
    questionImageFile.value = null;
    showQuestionModal.value = true;
};
const handleQuestionImageUpload = (event) => { questionImageFile.value = event.target.files[0]; };
const saveQuestion = async () => {
    const formData = new FormData();
    formData.append('test', props.testId);
    formData.append('q_number', modalQuestion.value.q_number);
    formData.append('description', modalQuestion.value.description);
    formData.append('max_mark', modalQuestion.value.max_mark);
    formData.append('model_answer', modalQuestion.value.model_answer);
    formData.append('marking_scheme', modalQuestion.value.marking_scheme);
    if (questionImageFile.value) {
        formData.append('question_image', questionImageFile.value);
    }
    try {
        if (modalQuestion.value.id) {
            await apiClient.patch(`questions/${modalQuestion.value.id}/`, formData);
        } else {
            await apiClient.post('questions/', formData);
        }
        alert('Question saved successfully!');
        showQuestionModal.value = false;
        fetchQuestions();
        fetchTestDetails();
    } catch (error) {
        console.error("Failed to save question:", error.response?.data || error);
        alert('Failed to save question.');
    }
};
const generateModelAnswer = async () => {
    if (!modalQuestion.value.description || !modalQuestion.value.marking_scheme) {
        return alert('Please provide a Question Description and Marking Scheme first.');
    }
    isGenerating.value = true;
    const formData = new FormData();
    formData.append('description', modalQuestion.value.description);
    formData.append('marking_scheme', modalQuestion.value.marking_scheme);
    if (questionImageFile.value) {
        formData.append('question_image', questionImageFile.value);
    }
    try {
        const response = await apiClient.post('generate-model-answer/', formData);
        modalQuestion.value.model_answer = response.data.model_answer;
    } catch (error) {
        console.error("AI Generation failed:", error);
        alert("Failed to generate model answer.");
    } finally {
        isGenerating.value = false;
    }
};

// --- MARKING PRINCIPLE MANAGEMENT ---
const onPrincipleChange = async () => {
    try {
        await apiClient.patch(`tests/${props.testId}/`, {
            marking_principle: test.value.marking_principle
        });
        alert('Marking principle updated successfully!');
    } catch (error) { console.error("Failed to update marking principle:", error); }
};

// --- STUDENT ANSWER EVALUATION WORKFLOW ---
const resetEvaluationState = () => {
    imageForOcr.value = null;
    ocrText.value = '';
    evaluationMessage.value = '';
    if (fileUploadInput.value) fileUploadInput.value.value = ''; // Visually clear file input
};
const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
        imageForOcr.value = file;
        runOcr();
    }
};
const handlePhotoCaptured = (photoBlob) => {
    const file = new File([photoBlob], "capture.png", { type: "image/png" });
    imageForOcr.value = file;
    runOcr();
};
const runOcr = async () => {
    if (!selectedStudentId.value || !selectedQuestionId.value) {
        alert("Please select a student and question.");
        resetEvaluationState();
        return;
    }
    isOcrRunning.value = true;
    evaluationMessage.value = '';
    const formData = new FormData();
    formData.append('student', selectedStudentId.value);
    formData.append('question', selectedQuestionId.value);
    formData.append('uploaded_image', imageForOcr.value);
    try {
        const response = await apiClient.post('answers/', formData);
        const answerId = response.data.id;
        const ocrResponse = await apiClient.post(`answers/${answerId}/run-ocr/`);
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
    evaluationMessage.value = 'Evaluating answer...';
    try {
        const answerId = imageForOcr.value.tempAnswerId;
        const evalResponse = await apiClient.post(`answers/${answerId}/run-marking/`, {
            corrected_text: ocrText.value
        });
        evaluationMessage.value = `Evaluation Complete! Mark: ${evalResponse.data.mark_gained} / ${evalResponse.data.question.max_mark}`;
        resetEvaluationState();
    } catch (error) {
        console.error("Marking step failed:", error.response?.data || error);
        evaluationMessage.value = `Error during marking: ${error.response?.data?.detail || error.message}`;
    } finally {
        isEvaluating.value = false;
    }
};
const reEvaluateAnswer = async (answerId) => {
    isReevaluatingId.value = answerId;
    try {
        const ocrResponse = await apiClient.post(`answers/${answerId}/run-ocr/`);
        const evalResponse = await apiClient.post(`answers/${answerId}/run-marking/`, {
            corrected_text: ocrResponse.data.ocr_text
        });
        alert(`Evaluation complete! Mark: ${evalResponse.data.mark_gained}`);
        loadReport();
    } catch (error) {
        console.error("Re-evaluation failed:", error.response?.data || error);
        alert("Re-evaluation failed.");
    } finally {
        isReevaluatingId.value = null;
    }
};
const openEditModal = (answer) => {
    answerToEdit.value = { ...answer };
    showEditModal.value = true;
};
const submitReEvaluation = async () => {
    if (!answerToEdit.value) return;
    isEvaluating.value = true;
    try {
        const answerId = answerToEdit.value.id;
        await apiClient.post(`answers/${answerId}/run-marking/`, {
            corrected_text: answerToEdit.value.ocr_text
        });
        alert(`Re-evaluation complete!`);
        showEditModal.value = false;
        loadReport();
    } catch (error) {
        console.error("Re-evaluation submission failed:", error.response?.data || error);
        alert("Failed to submit re-evaluation.");
    } finally {
        isEvaluating.value = false;
    }
};

// --- EXPORT FUNCTIONS ---
const exportReportToCSV = async () => {
    await loadReport();
    if (!answers.value.length) return alert("No answers to export.");
    const headers = ['Student Name', 'Question Number', 'Mark Gained', 'Max Mark', 'Recognized Text', 'Strengths', 'Improvements', 'Model Answer'];
    const csvRows = [headers.join(',')];
    const clean = (text) => `"${(text || '').replace(/"/g, '""')}"`;
    for (const answer of answers.value) {
        csvRows.push([
            clean(answer.student.name), answer.question.q_number, answer.mark_gained, answer.question.max_mark,
            clean(answer.ocr_text), clean(answer.ai_strength_points), clean(answer.ai_improvement_points),
            clean(answer.question.model_answer)
        ].join(','));
    }
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `Report_${test.value.name.replace(/ /g, '_')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};
const exportReportToPDF = async () => {
    await loadReport();
    if (!answers.value.length) return alert("No answers to export.");
    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.setFont(undefined, 'bold');
    doc.text(`Evaluation Report: ${test.value.name}`, 14, 22);
    doc.setFontSize(11);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(100);
    const className = answers.value[0]?.student?.class_group_name || 'N/A';
    doc.text(`Class: ${className}`, 14, 30);
    const tableRows = [];
    answers.value.forEach(answer => {
        tableRows.push([
            answer.student.name, answer.question.q_number, `${answer.mark_gained} / ${answer.question.max_mark}`, answer.ai_evaluation_summary || ''
        ]);
    });
    autoTable(doc, {
        head: [["Student", "Q#", "Score", "Summary"]],
        body: tableRows,
        startY: 40,
        headStyles: { fillColor: [41, 128, 185] },
        columnStyles: { 3: { cellWidth: 'auto' } }
    });
    answers.value.forEach((answer) => {
        doc.addPage();
        let currentY = 22;
        const leftMargin = 15;
        const usableWidth = 180;
        doc.setFontSize(16);
        doc.setFont(undefined, 'bold');
        doc.setTextColor(0);
        doc.text(`Detailed Evaluation for: ${answer.student.name} - Q${answer.question.q_number}`, leftMargin, currentY);
        currentY += 15;
        doc.setFontSize(11);
        const drawTextBlock = (title, text) => {
            if (currentY > 260) {
                doc.addPage();
                currentY = 22;
            }
            doc.setFont(undefined, 'bold');
            doc.text(title, leftMargin, currentY);
            currentY += 7;
            doc.setFont(undefined, 'normal');
            const cleanedText = (text || 'N/A').replace(/\r\n/g, '\n').replace(/ +/g, ' ').trim();
            const lines = doc.splitTextToSize(cleanedText, usableWidth);
            doc.text(lines, leftMargin, currentY);
            currentY += lines.length * 5 + 10;
        };
        drawTextBlock("Recognized Text:", answer.ocr_text);
        drawTextBlock("Strengths:", answer.ai_strength_points);
        drawTextBlock("Improvements:", answer.ai_improvement_points);
        drawTextBlock("Model Answer:", answer.question.model_answer);
    });
    doc.save(`PDF_Report_${test.value.name.replace(/ /g, '_')}.pdf`);
};

// --- LIFECYCLE HOOKS ---
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>