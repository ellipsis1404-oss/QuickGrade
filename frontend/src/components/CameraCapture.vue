<!-- frontend/src/components/CameraCapture.vue -->
<template>
  <div class="modal-overlay">
    <div class="modal-content" style="width: 90%; max-width: 600px;">
      <h3>Capture Student Answer</h3>
      
      <!-- Live Camera Feed -->
      <div v-show="!capturedImage" class="camera-container">
        <video ref="video" autoplay playsinline></video>
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
const capturedImage = ref(null);
let stream = null;

// Function to start the camera
const startCamera = async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'environment' } // Prefer the back camera on phones
    });
    if (video.value) {
      video.value.srcObject = stream;
    }
  } catch (err) {
    console.error("Error accessing camera:", err);
    alert("Could not access the camera. Please ensure you've given permission.");
    emit('close');
  }
};

// Function to stop the camera
const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
  }
};

const takePhoto = () => {
  if (video.value && canvas.value) {
    const context = canvas.value.getContext('2d');
    canvas.value.width = video.value.videoWidth;
    canvas.value.height = video.value.videoHeight;
    context.drawImage(video.value, 0, 0, canvas.value.width, canvas.value.height);
    capturedImage.value = canvas.value.toDataURL('image/png');
    stopCamera(); // Stop the live feed after taking photo
  }
};

const retakePhoto = () => {
  capturedImage.value = null;
  startCamera(); // Restart the camera feed
};

const usePhoto = () => {
  if (canvas.value) {
    // Convert the canvas image to a Blob, which is like a file
    canvas.value.toBlob((blob) => {
      // Emit the blob (the image file) to the parent component
      emit('photo-captured', blob);
      emit('close');
    }, 'image/png');
  }
};

onMounted(() => {
  startCamera();
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
}
</style>