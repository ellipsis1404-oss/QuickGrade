<!-- frontend/src/components/CameraCapture.vue -->
<template>
  <div class="modal-overlay">
    <div class="modal-content" style="width: 90%; max-width: 600px;">
      <h3>Capture Student Answer</h3>
      
      <!-- Live Camera Feed -->
      <div v-show="!capturedImage" class="camera-container">
        <!-- We add a @click handler for tap-to-focus -->
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

const startCamera = async () => {
  try {
    // --- FOCUS IMPROVEMENT #1: REQUEST CONTINUOUS AUTOFOCUS ---
    const constraints = {
      video: {
        facingMode: 'environment', // Prefer back camera
        focusMode: 'continuous'    // Request continuous autofocus
      }
    };
    stream = await navigator.mediaDevices.getUserMedia(constraints);
    if (video.value) {
      video.value.srcObject = stream;
    }
  } catch (err) {
    console.error("Error accessing camera:", err);
    alert("Could not access camera. Please ensure you've given permission and that your device supports the requested features.");
    emit('close');
  }
};

const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
  }
};

// --- FOCUS IMPROVEMENT #2: TAP-TO-FOCUS LOGIC ---
const handleFocus = async (event) => {
  if (!stream) return;
  
  const [track] = stream.getVideoTracks();
  const capabilities = track.getCapabilities();

  // Check if the browser supports manual focus control
  if (!capabilities.focusMode || !capabilities.focusMode.includes('single-shot')) {
    console.log("Tap-to-focus is not supported by this browser/camera.");
    return;
  }

  // Show a visual indicator for the focus point
  const indicator = focusIndicator.value;
  indicator.style.left = `${event.offsetX - 25}px`;
  indicator.style.top = `${event.offsetY - 25}px`;
  indicator.classList.add('active');
  setTimeout(() => indicator.classList.remove('active'), 1000);

  // Calculate the focus point (coordinates must be normalized between 0 and 1)
  const focusPoint = {
    x: event.offsetX / video.value.offsetWidth,
    y: event.offsetY / video.value.offsetHeight
  };

  try {
    // Apply the focus point
    await track.applyConstraints({
      advanced: [{
        pointsOfInterest: [focusPoint],
        focusMode: 'single-shot'
      }]
    });
    console.log("Focus point applied.");
  } catch (err) {
    console.error("Failed to apply focus point:", err);
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