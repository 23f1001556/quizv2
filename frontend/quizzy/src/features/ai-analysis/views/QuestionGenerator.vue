<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const props = defineProps(['initialTopic'])
const router = useRouter()
const file = ref(null)
const topic = ref('')
const activeMode = ref('topic') // 'topic' or 'upload'

const loading = ref(false)
const parsedQuestions = ref(null)
const selectedIndices = ref([])
const isDragging = ref(false)

// Save Logic
const showModal = ref(false)
const saving = ref(false)
const subjects = ref([])
const chapters = ref([])
const saveForm = ref({
    name: '',
    subject_id: '',
    chapter_id: '',
    new_chapter_name: '',
    new_subject_name: ''
})

const difficulty = ref('Medium')
const questionCount = ref(5)

// Watch for prop changes
watch(() => props.initialTopic, (newVal) => {
    if (newVal) {
        topic.value = newVal
        activeMode.value = 'topic'
    }
}, { immediate: true })

const handleFile = (event) => {
    const selectedFile = event.target.files[0]
    if (selectedFile) processFile(selectedFile)
}

const handleDrop = (event) => {
    isDragging.value = false
    const droppedFile = event.dataTransfer.files[0]
    const validTypes = ['application/pdf', 'image/jpeg', 'image/png']
    if (droppedFile && validTypes.includes(droppedFile.type)) {
        processFile(droppedFile)
    } else {
        alert("Please upload a PDF or Image file.")
    }
}

const processFile = (inputFile) => {
    file.value = inputFile
    activeMode.value = 'upload'
    // Auto-trigger analysis? Maybe wait for button click.
    // user likely wants to click 'Generate' explicitly.
}

const generate = async () => {
    if (loading.value) return

    loading.value = true
    parsedQuestions.value = null

    try {
        let res;
        if (activeMode.value === 'upload') {
            if (!file.value) {
                alert("Please select a file first.")
                loading.value = false
                return
            }
            const formData = new FormData()
            formData.append('file', file.value)
            formData.append('action', 'generate_quiz')
            formData.append('difficulty', difficulty.value)
            formData.append('count', questionCount.value)

            res = await api.post('/ai/upload_pdf', formData, {
                timeout: 65000,
                headers: { 'Content-Type': 'multipart/form-data' }
            })
            handleResponse(res.data.result, file.value.name.split('.')[0])

        } else {
            if (!topic.value) {
                alert("Please enter a topic.")
                loading.value = false
                return
            }
            res = await api.post('/ai/generate_questions', {
                topic: topic.value,
                count: questionCount.value,
                difficulty: difficulty.value
            }, {
                timeout: 65000
            })
            // The /generate_questions endpoint returns { questions: [...] } directly
            // unlike upload_pdf which returns { result: "string_json" }
            parsedQuestions.value = res.data.questions
            selectedIndices.value = res.data.questions.map((_, i) => i)
            saveForm.value.name = topic.value + ' Quiz'
        }

    } catch (error) {
        alert(
            error.response?.data?.message
            || (error.code === 'ECONNABORTED'
                ? 'Generation took too long. Please try again with fewer questions or a shorter prompt.'
                : 'Generation failed')
        )
    } finally {
        loading.value = false
    }
}

const handleResponse = (rawJsonString, defaultName) => {
    let raw = rawJsonString
    if (typeof raw === 'string') {
        raw = raw.replace(/```json/g, '').replace(/```/g, '').trim()
    }

    try {
        const json = typeof raw === 'object' ? raw : JSON.parse(raw)
        // Check structure
        const qs = json.questions || json
        if (Array.isArray(qs)) {
            parsedQuestions.value = qs
            selectedIndices.value = qs.map((_, i) => i)
            saveForm.value.name = defaultName + ' Quiz'
        } else {
            throw new Error("Invalid format")
        }
    } catch (e) {
        console.error(e)
        alert("Failed to parse AI response.")
    }
}

const toggleSelection = (idx) => {
    if (selectedIndices.value.includes(idx)) {
        selectedIndices.value = selectedIndices.value.filter(i => i !== idx)
    } else {
        selectedIndices.value.push(idx)
    }
}

const reset = () => {
    parsedQuestions.value = null
    file.value = null
    selectedIndices.value = []
}

const openSaveModal = async () => {
    try {
        const res = await api.get('/subjects/getsubjects')
        subjects.value = res.data.subjects
        showModal.value = true
    } catch (e) {
        alert("Failed to load subjects")
    }
}

const handleSubjectChange = () => {
    saveForm.value.chapter_id = ''
    if (saveForm.value.subject_id === 'new') {
        chapters.value = []
    } else {
        fetchChapters()
    }
}

const fetchChapters = async () => {
    if (!saveForm.value.subject_id || saveForm.value.subject_id === 'new') return
    try {
        const res = await api.get(`/chapters/getchapters/${saveForm.value.subject_id}`)
        chapters.value = res.data.chapters
    } catch (e) {
        console.error(e)
    }
}

const saveQuiz = async () => {
    saving.value = true
    try {
        let finalChapterId = saveForm.value.chapter_id
        let finalSubjectId = saveForm.value.subject_id

        if (saveForm.value.subject_id === 'new') {
            // Create Subject First
            const subRes = await api.post('/subjects/createsubject', {
                subject_name: saveForm.value.new_subject_name,
                description: 'Created via AI Quiz'
            })
            // Refetch subjects to find the new one's ID
            const resSub = await api.get('/subjects/getsubjects')
            const newSub = resSub.data.subjects.find(s => s.name === saveForm.value.new_subject_name)
            if (newSub) {
                finalSubjectId = newSub.id
            } else {
                throw new Error("Failed to create subject")
            }
        }

        if (saveForm.value.chapter_id === 'new' || saveForm.value.subject_id === 'new') {
            if (!saveForm.value.new_chapter_name) {
                alert("Please enter a name for the new chapter")
                saving.value = false
                return
            }
            const chapRes = await api.post('/chapters/createchapter', {
                chapter_name: saveForm.value.new_chapter_name,
                subject_id: finalSubjectId,
                description: 'Created via AI Quiz'
            })

            // Refetch chapters for the subject to find the new one's ID
            const resChap = await api.get(`/chapters/getchapters/${finalSubjectId}`)
            const newChap = resChap.data.chapters.find(c => c.name === saveForm.value.new_chapter_name)
            if (newChap) {
                finalChapterId = newChap.id
            } else {
                throw new Error("Could not verify created chapter.")
            }
        }

        const questionsToSave = parsedQuestions.value.filter((_, i) => selectedIndices.value.includes(i))

        const payload = {
            name: saveForm.value.name,
            chapter_id: finalChapterId,
            questions: questionsToSave
        }

        const res = await api.post('/quiz/save_generated', payload)
        router.push(`/dashboard/quiz/${res.data.quiz_id}/attempt`)
    } catch (error) {
        alert(error.response?.data?.message || 'Save failed')
    } finally {
        saving.value = false
        showModal.value = false
    }
}
</script>

<template>
    <div class="generator-panel">
        <div class="intro-section" v-if="!parsedQuestions && !loading">

            <div class="mode-toggles">
                <button :class="{ active: activeMode === 'topic' }" @click="activeMode = 'topic'">Type Topic</button>
                <button :class="{ active: activeMode === 'upload' }" @click="activeMode = 'upload'">Upload File</button>
            </div>

            <div class="input-area">
                <transition name="fade" mode="out-in">
                    <div v-if="activeMode === 'topic'" key="topic" class="topic-box">
                        <input v-model="topic" placeholder="e.g. Photosynthesis, Victorian Era, Calculus..."
                            class="topic-input" @keyup.enter="generate">
                    </div>

                    <div v-else key="upload" class="upload-zone" @dragover.prevent="isDragging = true"
                        @dragleave.prevent="isDragging = false" @drop.prevent="handleDrop"
                        :class="{ 'dragging': isDragging }" @click="$refs.fileInput.click()">
                        <div class="upload-content">
                            <div class="upload-icon">📷</div>
                            <div class="text-group">
                                <h3>{{ file ? file.name : 'Upload Material' }}</h3>
                                <p v-if="!file">PDF, Images or Capture Photo</p>
                            </div>
                            <button class="btn-browse">{{ file ? 'Change' : 'Browse' }}</button>
                            <input type="file" ref="fileInput" accept="application/pdf,image/*" @change="handleFile"
                                hidden>
                        </div>
                    </div>
                </transition>
            </div>

            <div class="settings-bar">
                <div class="setting-item">
                    <label>Difficulty</label>
                    <select v-model="difficulty" class="compact-select">
                        <option>Easy</option>
                        <option>Medium</option>
                        <option>Hard</option>
                    </select>
                </div>
                <div class="setting-item">
                    <label>Questions: {{ questionCount }}</label>
                    <input type="range" min="1" max="15" v-model="questionCount" class="compact-range">
                </div>
                <button class="btn-generate" @click="generate" :disabled="loading || (!topic && !file)">
                    Generate Quiz 🚀
                </button>
            </div>

            <div class="info-badges">
                <div class="badge">
                    <span class="icon">🤖</span>
                    <span>AI Analysis</span>
                </div>
                <div class="badge">
                    <span class="icon">📝</span>
                    <span>Smart Questions</span>
                </div>
            </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="processing-state">
            <div class="spinner-ring"></div>
            <h3>Generating Quiz...</h3>
            <p>Crafting questions based on {{ activeMode === 'topic' ? 'your topic' : 'your file' }}.</p>
        </div>

        <!-- Result Area (Existing Code continues...) -->

        <div v-if="parsedQuestions" class="preview-area">
            <div class="preview-header">
                <div class="header-left">
                    <h4>Generated Questions</h4>
                    <span class="count-badge">{{ parsedQuestions.length }} items</span>
                </div>
                <div class="actions">
                    <button class="btn-text" @click="reset">Start Over</button>
                    <button class="btn-primary" @click="openSaveModal" :disabled="selectedIndices.length === 0">
                        Save Selected ({{ selectedIndices.length }})
                    </button>
                </div>
            </div>

            <div class="questions-list">
                <div v-for="(q, idx) in parsedQuestions" :key="idx" class="q-card"
                    :class="{ 'selected': selectedIndices.includes(idx) }" @click="toggleSelection(idx)">

                    <div class="selection-indicator">
                        <div class="checkbox" :class="{ checked: selectedIndices.includes(idx) }">
                            <span v-if="selectedIndices.includes(idx)">✓</span>
                        </div>
                    </div>

                    <div class="q-content">
                        <p class="q-text"><strong>Q{{ idx + 1 }}</strong> {{ q.question }}</p>
                        <div class="options-grid">
                            <div v-for="(opt, key) in q.options" :key="key" class="opt"
                                :class="{ correct: key === q.answer }">
                                <span class="opt-tag">{{ key }}</span>
                                <span class="opt-text">{{ opt }}</span>
                                <span v-if="key === q.answer" class="correct-icon">✨ Correct</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Save Modal -->
        <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
            <div class="modal-card">
                <div class="modal-header">
                    <h3>Save Your Quiz</h3>
                    <button class="close-btn" @click="showModal = false">×</button>
                </div>

                <form @submit.prevent="saveQuiz">
                    <div class="form-group">
                        <label>Quiz Title</label>
                        <input v-model="saveForm.name" required placeholder="e.g. History Chapter 1 Quiz"
                            class="modern-input">
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>Subject</label>
                            <select v-model="saveForm.subject_id" @change="handleSubjectChange" required
                                class="modern-select">
                                <option value="" disabled>Select Subject</option>
                                <option value="new">+ Create New Subject</option>
                                <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Chapter</label>
                            <select v-model="saveForm.chapter_id" :disabled="!saveForm.subject_id" required
                                class="modern-select">
                                <option value="" disabled>Select Chapter</option>
                                <option value="new">+ Create New Chapter</option>
                                <option v-for="c in chapters" :key="c.id" :value="c.id">{{ c.name }}</option>
                            </select>
                        </div>
                    </div>

                    <transition name="slide-fade">
                        <div>
                            <div class="form-group" v-if="saveForm.subject_id === 'new'">
                                <label>New Subject Name</label>
                                <input v-model="saveForm.new_subject_name" placeholder="e.g. Physics" required
                                    class="modern-input">
                            </div>

                            <div class="form-group" v-if="saveForm.chapter_id === 'new'">
                                <label>New Chapter Name</label>
                                <input v-model="saveForm.new_chapter_name" placeholder="Enter chapter name" required
                                    class="modern-input">
                            </div>
                        </div>
                    </transition>

                    <div class="modal-footer">
                        <button type="button" class="btn-text" @click="showModal = false">Cancel</button>
                        <button type="submit" class="btn-primary" :disabled="saving">
                            {{ saving ? 'Saving...' : 'Save & View Quiz' }}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<style scoped>
.generator-panel {
    min-height: 400px;
}

.mode-toggles {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 2rem;
}

.mode-toggles button {
    background: transparent;
    border: 2px solid var(--border-color);
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
}

.mode-toggles button.active {
    border-color: var(--primary-color);
    background: rgba(79, 70, 229, 0.05);
    color: var(--primary-color);
}

.input-area {
    margin-bottom: 2rem;
    min-height: 120px;
}

.topic-box {
    text-align: center;
    padding: 2rem;
    background: var(--bg-secondary);
    border-radius: 16px;
    border: 1px solid var(--border-color);
}

.topic-input {
    width: 100%;
    max-width: 500px;
    padding: 1rem 1.5rem;
    font-size: 1.1rem;
    border: 2px solid var(--border-color);
    border-radius: 12px;
    background: var(--bg-primary);
    color: var(--text-primary);
    outline: none;
    transition: border-color 0.2s;
    text-align: center;
}

.topic-input:focus {
    border-color: var(--primary-color);
}

.btn-generate {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    margin-left: auto;
}

.btn-generate:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}


.settings-bar {
    display: flex;
    gap: 2rem;
    margin-bottom: 1rem;
    background: var(--bg-secondary);
    padding: 1rem 1.5rem;
    border-radius: 12px;
    border: 1px solid var(--border-color);
}

.setting-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.setting-item label {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-secondary);
    white-space: nowrap;
}

.compact-select {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    color: var(--text-primary);
    padding: 0.25rem 0.5rem;
    font-size: 0.9rem;
}

.compact-range {
    width: 100px;
    accent-color: var(--primary-color);
}

/* Upload Zone - Compact Horizontal */
.upload-zone {
    border: 2px dashed var(--border-color);
    border-radius: 16px;
    padding: 1.5rem;
    cursor: pointer;
    background: rgba(255, 255, 255, 0.02);
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    text-align: left;
}

.upload-content {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    width: 100%;
}

.upload-icon {
    font-size: 2rem;
    width: 60px;
    height: 60px;
    background: var(--bg-primary);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0;
    flex-shrink: 0;
}

.upload-content .text-group {
    flex: 1;
}

.upload-content h3 {
    font-size: 1.1rem;
    margin: 0 0 0.25rem 0;
    color: var(--text-primary);
}

.upload-content p {
    font-size: 0.9rem;
    margin: 0;
    color: var(--text-secondary);
}

.btn-browse {
    padding: 0.6rem 1.25rem;
    font-size: 0.9rem;
}

.info-badges {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    margin-top: 1.5rem;
}

.badge {
    font-size: 0.8rem;
    padding: 0.35rem 0.75rem;
    background: var(--bg-primary);
    border-radius: 20px;
}

/* Processing State */
.processing-state {
    text-align: center;
    padding: 4rem;
}

.spinner-ring {
    width: 60px;
    height: 60px;
    border: 4px solid rgba(79, 70, 229, 0.1);
    border-left-color: var(--primary-color);
    border-radius: 50%;
    margin: 0 auto 2rem;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

/* Preview Area */
.preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.header-left h4 {
    font-size: 1.25rem;
    margin: 0;
    color: var(--text-primary);
}

.count-badge {
    font-size: 0.85rem;
    color: var(--text-secondary);
    background: var(--bg-primary);
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    margin-left: 0.5rem;
}

.actions {
    display: flex;
    gap: 1rem;
}

.questions-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.q-card {
    background: var(--bg-primary);
    padding: 1.5rem;
    border-radius: 16px;
    border: 2px solid transparent;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}

.q-card:hover {
    border-color: rgba(79, 70, 229, 0.3);
}

.q-card.selected {
    border-color: var(--primary-color);
    background: rgba(79, 70, 229, 0.02);
}

.selection-indicator {
    padding-top: 0.25rem;
}

.checkbox {
    width: 24px;
    height: 24px;
    border: 2px solid var(--border-color);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 0.8rem;
    transition: all 0.2s;
}

.checkbox.checked {
    background: var(--primary-color);
    border-color: var(--primary-color);
}

.q-content {
    flex: 1;
}

.q-text {
    font-size: 1.05rem;
    margin-bottom: 1.25rem;
    color: var(--text-primary);
    line-height: 1.5;
}

.options-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
}

.opt {
    padding: 0.75rem 1rem;
    background: var(--bg-secondary);
    border-radius: 10px;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    border: 1px solid transparent;
}

.opt.correct {
    background: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.3);
    color: #065f46;
}

.opt-tag {
    font-weight: 700;
    color: var(--text-secondary);
    width: 20px;
}

.correct .opt-tag {
    color: #065f46;
}

.correct-icon {
    margin-left: auto;
    font-size: 0.75rem;
    font-weight: 600;
    background: #065f46;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
}

/* Modal */
.modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
}

.modal-card {
    background: var(--bg-secondary);
    width: 100%;
    max-width: 500px;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.close-btn {
    background: transparent;
    border: none;
    font-size: 1.5rem;
    color: var(--text-secondary);
    cursor: pointer;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.form-group label {
    display: block;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.modern-input,
.modern-select {
    width: 100%;
    padding: 0.85rem 1rem;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    color: var(--text-primary);
    font-size: 1rem;
    transition: border-color 0.2s;
}

.modern-input:focus,
.modern-select:focus {
    border-color: var(--primary-color);
    outline: none;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2rem;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 0.85rem 1.75rem;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.btn-text {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    padding: 0.85rem 1.5rem;
    font-weight: 500;
    cursor: pointer;
}

.slide-fade-enter-active {
    transition: all 0.3s ease-out;
}

.slide-fade-enter-from {
    opacity: 0;
    transform: translateY(-10px);
}
</style>
