<!-- frontend/src/components/CameraCapture.vue -->
<template>
  <div class="modal-overlay">
    <div class="modal-content" style="width: 90%; max-width: 600px;">
      <h3>Capture Student Answer</h3>
      
      <div v-show="!capturedImage" class="camera-container">
        <video ref="video" autoplay playsinline></video>
        <button @click="takePhoto" class="btn btn-blue capture-btn">Take Photo</button>
      </div>
      
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

// This is a simpler, more compatible startCamera function
const startCamera = async () => {
  try {
    // This simple constraint asks for the back camera and lets the browser decide the rest.
    const constraints = {
      video: { facingMode: 'environment' }
    };
    stream = await navigator.mediaDevices.getUserMedia(constraints);
    if (video.value) {
      video.value.srcObject = stream;
    }
  } catch (err) {
    console.error("Error accessing camera:", err);
    alert("Could not access the camera. Please ensure you've given permission.");
    emit('close');
  }
};

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
    stopCamera();
  }
};

const retakePhoto = () => {
  capturedImage.value = null;
  startCamera();
};

const usePhoto = () => {
  if (canvas.value) {
    canvas.value.toBlob((blob) => {
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
  position: relative; margin-top: 1rem; border: 1px solid #ccc; background: #000;
}
video, canvas { display: block; width: 100%; height: auto; }
.capture-btn { position: absolute; bottom: 1rem; left: 50%; transform: translateX(-50%); z-index: 10; }
.modal-actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem; }
</style>