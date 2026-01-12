<script setup>
import { ref, computed } from 'vue'
import { FILE_UPLOAD } from '../constants'

const props = defineProps({
  modelValue: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'extract', 'file-selected'])

const inputMode = ref('paste') // 'paste' or 'upload'
const selectedFile = ref(null)
const dragOver = ref(false)

const hasContent = computed(() => {
  return inputMode.value === 'paste'
    ? props.modelValue.trim().length > 0
    : selectedFile.value !== null
})

function handleFileSelect(event) {
  const file = event.target.files?.[0]
  if (file) {
    validateAndSetFile(file)
  }
}

function handleDrop(event) {
  dragOver.value = false
  const file = event.dataTransfer.files?.[0]
  if (file) {
    validateAndSetFile(file)
  }
}

function validateAndSetFile(file) {
  const isValidType = FILE_UPLOAD.ACCEPTED_MIME_TYPES.includes(file.type) ||
    FILE_UPLOAD.ACCEPTED_EXTENSIONS.some(ext => file.name.toLowerCase().endsWith(ext))

  if (!isValidType) {
    alert('Please select a valid file type (PDF, DOCX, MD, or TXT)')
    return
  }

  const maxSizeBytes = FILE_UPLOAD.MAX_SIZE_MB * 1024 * 1024
  if (file.size > maxSizeBytes) {
    alert(`File size must be less than ${FILE_UPLOAD.MAX_SIZE_MB}MB`)
    return
  }

  selectedFile.value = file
  emit('file-selected', file)
}

function clearFile() {
  selectedFile.value = null
}

function handleExtract() {
  if (inputMode.value === 'paste') {
    emit('extract', { type: 'text', content: props.modelValue })
  } else if (selectedFile.value) {
    emit('extract', { type: 'file', file: selectedFile.value })
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<template>
  <div class="space-y-4">
    <!-- Input Mode Toggle -->
    <div class="flex gap-2 p-1 bg-gray-100 rounded-lg w-fit">
      <button
        type="button"
        class="px-4 py-2 text-sm font-medium rounded-md transition-all duration-150"
        :class="inputMode === 'paste'
          ? 'bg-white text-gray-900 shadow-sm'
          : 'text-gray-500 hover:text-gray-700'"
        @click="inputMode = 'paste'"
      >
        <span class="flex items-center gap-2">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
            <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
          </svg>
          Paste Text
        </span>
      </button>
      <button
        type="button"
        class="px-4 py-2 text-sm font-medium rounded-md transition-all duration-150"
        :class="inputMode === 'upload'
          ? 'bg-white text-gray-900 shadow-sm'
          : 'text-gray-500 hover:text-gray-700'"
        @click="inputMode = 'upload'"
      >
        <span class="flex items-center gap-2">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          Upload File
        </span>
      </button>
    </div>

    <!-- Paste Text Mode -->
    <div v-if="inputMode === 'paste'" class="space-y-3">
      <textarea
        :value="modelValue"
        @input="emit('update:modelValue', $event.target.value)"
        :disabled="disabled"
        class="w-full h-48 px-4 py-3 text-sm bg-white border border-gray-200 rounded-lg resize-none transition-all duration-150 focus:outline-none focus:border-accent focus:ring-[3px] focus:ring-accent/10 placeholder:text-gray-400 disabled:bg-gray-50 disabled:cursor-not-allowed"
        placeholder="Paste your meeting notes here...

Example:
- John to review API docs by Friday
- Sarah will update the deployment scripts
- Schedule follow-up meeting next week"
      />
      <p class="text-xs text-gray-400">
        Paste meeting notes, transcripts, or any text containing action items
      </p>
    </div>

    <!-- Upload File Mode -->
    <div v-else class="space-y-3">
      <div
        class="relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-150"
        :class="dragOver
          ? 'border-accent bg-accent/5'
          : selectedFile
            ? 'border-accent bg-accent/5'
            : 'border-gray-200 hover:border-gray-300'"
        @dragover.prevent="dragOver = true"
        @dragleave.prevent="dragOver = false"
        @drop.prevent="handleDrop"
      >
        <template v-if="!selectedFile">
          <div class="flex flex-col items-center gap-3">
            <div class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-gray-400">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-600">
                <label class="text-accent font-medium cursor-pointer hover:text-accent-dim">
                  Click to upload
                  <input
                    type="file"
                    class="hidden"
                    :accept="FILE_UPLOAD.ACCEPTED_EXTENSIONS.join(',')"
                    @change="handleFileSelect"
                  />
                </label>
                or drag and drop
              </p>
              <p class="text-xs text-gray-400 mt-1">PDF, DOCX, MD, or TXT files</p>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="flex items-center justify-center gap-4">
            <div class="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-accent">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
            </div>
            <div class="text-left">
              <p class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</p>
              <p class="text-xs text-gray-400">{{ formatFileSize(selectedFile.size) }}</p>
            </div>
            <button
              type="button"
              class="ml-4 p-2 text-gray-400 hover:text-error hover:bg-error/10 rounded transition-all duration-150"
              @click="clearFile"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        </template>
      </div>
    </div>

    <!-- Extract Button -->
    <div class="flex justify-end">
      <button
        type="button"
        class="btn btn-primary"
        :disabled="!hasContent || disabled"
        @click="handleExtract"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
        </svg>
        Extract Action Items
      </button>
    </div>
  </div>
</template>
