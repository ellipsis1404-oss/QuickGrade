<!-- frontend/src/components/CameraCapture.vue -->
<template>
  <div class="modal-overlay">
    <div class="modal-content" style="width: 90%; max-width: 600px;">
      <h3>Capture Student Answer</h3>
      
      <!-- NEW: Camera Selection Dropdown -->
      <div v-if="cameras.length > 1" class="form-group">
        <label class="form-label" style="color: white;">Select Camera:</label>
        <select v-model="selectedCameraId" @change="startCamera" class="form-input">
          <option v-for="(camera, index) in cameras" :key="camera.deviceId" :value="camera.deviceId">
            Camera {{ index + 1 }} {{ camera.label.includes('back') ? '(Back)' : '' }}
          </option>
        </select>
      </div>
      
      <!-- Live Camera Feed -->
      <div v-show="!capturedImage" class="camera-container">
        <video ref="video" autoplay playsinline @click="handleFocus"></video>
        <div class="focus-indicator" ref="focusIndicator"></div>
        <button @click="takePhoto" class="btn btn-blue capture-btn">Take Photo</button>
      </div>
      
      <!-- Captured Image Preview -->
      <div v-show="capturedImage" class="preview-container">
        <canvas ref="canvas"></canvas>
        <div class="modal-actions">
          <button @click="retakePhoto" class="btn btn-gray">Retake</button>
          <button @click="usePhoto" class="btn btn-green">Use this Photo</button>
        </div>
      </div>
      
      <button @click="$emit('close')" class="btn btn-gray" style="margin-top: 1rem;">Cancel</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const emit = defineEmits(['close', 'photo-captured']);

const video = ref(null);
const canvas = ref(null);
const focusIndicator = ref(null);
const capturedImage = ref(null);
let stream = null;

// --- NEW STATE for camera selection ---
const cameras = ref([]);
const selectedCameraId = ref(null);


// --- NEW FUNCTION to detect all cameras ---
const getCameras = async () => {
  try {
    // We need to request permission first to get the device labels
    await navigator.mediaDevices.getUserMedia({ video: true });
    
    const devices = await navigator.mediaDevices.enumerateDevices();
    cameras.value = devices.filter(device => device.kind === 'videoinput');
    
    if (cameras.value.length > 0) {
      // Try to intelligently select the back camera first
      const backCamera = cameras.value.find(c => c.label.toLowerCase().includes('back'));
      selectedCameraId.value = backCamera ? backCamera.deviceId : cameras.value[0].deviceId;
    }
  } catch (error) {
    console.error("Could not enumerate cameras:", error);
  }
};


// --- MODIFIED FUNCTION to use the selected camera ---
const startCamera = async () => {
  // Stop any existing stream before starting a new one
  if (stream) {
    stopCamera();
  }
  
  if (!selectedCameraId.value) {
    console.warn("No camera selected.");
    return;
  }
  
  // Build constraints with the EXACT device ID
  const constraints = {
    video: {
      deviceId: { exact: selectedCameraId.value },
      // Optional: Request a higher resolution for better quality
      width: { ideal: 1920 },
      height: { ideal: 1080 }
    }
  };

  try {
    stream = await navigator.mediaDevices.getUserMedia(constraints);
    if (video.value) {
      video.value.srcObject = stream;
    }
  } catch (err) {
    console.error("Error starting selected camera:", err);
    alert("Could not start the selected camera.");
    emit('close');
  }
};

const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
};

const handleFocus = (event) => { /* ... (This function is unchanged) ... */ };
const takePhoto = () => { /* ... (This function is unchanged) ... */ };
const retakePhoto = () => { capturedImage.value = null; startCamera(); };
const usePhoto = () => { /* ... (This function is unchanged) ... */ };


// --- MODIFIED onMounted to handle the new detection flow ---
onMounted(async () => {
  await getCameras(); // First, find all available cameras
  await startCamera();  // Then, start the default or selected camera
});

onUnmounted(() => {
  stopCamera();
});
</script>

<style scoped>
.camera-container, .preview-container {
  position: relative;
  margin-top: 1rem;
  border: 1px solid #ccc;
  background: #000;
  cursor: pointer; /* Indicate that the video is clickable */
}
video, canvas {
  display: block;
  width: 100%;
  height: auto;
}
.capture-btn {
  position: absolute;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}
/* Style for the tap-to-focus indicator */
.focus-indicator {
  position: absolute;
  width: 50px;
  height: 50px;
  border: 2px solid yellow;
  border-radius: 50%;
  opacity: 0;
  transform: scale(1.5);
  transition: opacity 0.3s ease-out, transform 0.3s ease-out;
  pointer-events: none; /* Make it unclickable */
}
.focus-indicator.active {
  opacity: 1;
  transform: scale(1);
}
</style>