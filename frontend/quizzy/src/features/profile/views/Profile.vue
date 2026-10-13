<template>
    <div class="profile-container">
        <!-- Header Section -->
        <div class="profile-header-card">
            <div class="header-background"></div>
            <div class="header-content">
                <div class="avatar-wrapper">
                    <div class="avatar">{{ initials }}</div>
                    <div class="status-indicator"></div>
                </div>
                <div class="user-info">
                    <div class="name-row">
                        <h1>{{ user.fullname || user.username }}</h1>
                        <span v-if="user.isadmin" class="badge admin-badge">Admin</span>
                    </div>
                    <p class="email">{{ user.email }}</p>
                    <p class="qualification" v-if="user.qualification">{{ user.qualification }}</p>
                </div>
            </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid" v-if="!user.isadmin">
            <div class="stat-card">
                <div class="stat-icon quizzes">📚</div>
                <div class="stat-info">
                    <h3>Total Quizzes</h3>
                    <p>{{ stats.total_quizzes }}</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon score">🏆</div>
                <div class="stat-info">
                    <h3>Avg. Score</h3>
                    <p>{{ stats.average_score }}%</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon active">🔥</div>
                <div class="stat-info">
                    <h3>Days Active</h3>
                    <p>{{ stats.days_active }}</p>
                </div>
            </div>
        </div>

        <div class="main-content-grid" :class="{ 'admin-grid': user.isadmin }">
            <!-- Edit Profile Section -->
            <div class="content-card edit-profile">
                <h2>Edit Profile</h2>
                <form @submit.prevent="saveProfile" class="modern-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Full Name</label>
                            <input v-model="form.fullname" placeholder="John Doe" />
                        </div>
                        <div class="form-group">
                            <label>Qualification</label>
                            <input v-model="form.qualification" placeholder="e.g. BSc Computer Science" />
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Date of Birth</label>
                        <input type="date" v-model="form.dob" />
                    </div>

                    <div class="form-actions">
                        <button type="submit" class="btn-save" :disabled="saving">
                            <span v-if="saving">Saving...</span>
                            <span v-else>Save Changes</span>
                        </button>
                    </div>
                </form>
            </div>

            <!-- Recent Activity Section -->
            <div class="content-card recent-activity">
                <h2>Recent Activity</h2>
                <div v-if="stats.recent_activity && stats.recent_activity.length > 0" class="activity-list">
                    <div v-for="(activity, index) in stats.recent_activity" :key="index" class="activity-item">
                        <div class="activity-icon" :class="activity.type.toLowerCase()">
                            <template v-if="activity.type === 'Standard'">📝</template>
                            <template v-else-if="activity.type === 'Mock'">🤖</template>
                            <template v-else-if="activity.type === 'Action'">⚡</template>
                        </div>
                        <div class="activity-details">
                            <span class="activity-title">{{ activity.title }}</span>
                            <span class="activity-meta" v-if="activity.details">{{ activity.details }}</span>
                            <span class="activity-meta" v-else>{{ activity.type }} Quiz • {{ activity.date }}</span>
                        </div>
                        <div class="activity-score" v-if="activity.score !== undefined"
                            :class="getScoreClass(activity.score)">
                            {{ activity.score }} pts
                        </div>
                        <div class="activity-date" v-else>
                            {{ activity.date }}
                        </div>
                    </div>
                </div>
                <div v-else class="empty-state">
                    <p>No recent activity found.</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const user = ref({})
const stats = ref({
    total_quizzes: 0,
    average_score: 0,
    days_active: 0,
    recent_activity: []
})

const form = ref({
    fullname: '',
    qualification: '',
    dob: ''
})
const saving = ref(false)

const initials = computed(() => {
    const name = user.value.fullname || user.value.username || 'User'
    return name.substring(0, 2).toUpperCase()
})

const fetchProfile = async () => {
    try {
        const res = await api.get('/users/profile')
        user.value = res.data.user
        stats.value = res.data.stats

        // Populate form
        form.value.fullname = user.value.fullname || ''
        form.value.qualification = user.value.qualification || ''
        form.value.dob = user.value.dob || ''
    } catch (error) {
        console.error("Failed to load profile", error)
    }
}

const saveProfile = async () => {
    saving.value = true
    try {
        await api.put('/users/profile', form.value)
        // Refresh to get updated data/stats if needed, usually just user data updates
        await fetchProfile()
        alert("Profile updated successfully")
    } catch (error) {
        console.error(error)
        alert("Failed to update profile")
    } finally {
        saving.value = false
    }
}

const getScoreClass = (score) => {
    if (score >= 80) return 'score-high'
    if (score >= 50) return 'score-medium'
    return 'score-low'
}

onMounted(() => {
    fetchProfile()
})
</script>

<style scoped>
.profile-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

/* Header Card */
.profile-header-card {
    position: relative;
    background: var(--bg-secondary);
    border-radius: 24px;
    overflow: hidden;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color);
}

.header-background {
    height: 120px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    opacity: 0.9;
}

.header-content {
    padding: 0 2rem 2rem 2rem;
    display: flex;
    align-items: flex-end;
    gap: 2rem;
    margin-top: -40px;
}

.avatar-wrapper {
    position: relative;
}

.avatar {
    width: 120px;
    height: 120px;
    background: #1e293b;
    color: #fff;
    border: 4px solid var(--bg-secondary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    font-weight: 700;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.status-indicator {
    position: absolute;
    bottom: 10px;
    right: 10px;
    width: 20px;
    height: 20px;
    background: #22c55e;
    border: 3px solid var(--bg-secondary);
    border-radius: 50%;
}

.user-info {
    padding-bottom: 0.5rem;
    flex: 1;
}

.name-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.25rem;
}

.name-row h1 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    color: var(--text-primary);
}

.email {
    color: var(--text-secondary);
    font-size: 1rem;
    margin: 0;
}

.qualification {
    color: var(--primary-color);
    font-weight: 500;
    margin: 0.25rem 0 0 0;
    font-size: 0.9rem;
}

.badge {
    padding: 0.25rem 0.75rem;
    border-radius: 50px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.admin-badge {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
}

/* Stats Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: var(--bg-secondary);
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 1.5rem;
    transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.75rem;
}

.stat-icon.quizzes {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
}

.stat-icon.score {
    background: rgba(234, 179, 8, 0.1);
    color: #eab308;
}

.stat-icon.active {
    background: rgba(236, 72, 153, 0.1);
    color: #ec4899;
}

.stat-info h3 {
    margin: 0;
    font-size: 0.875rem;
    color: var(--text-secondary);
    font-weight: 500;
}

.stat-info p {
    margin: 0.25rem 0 0 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
}

/* Main Content Grid */
.main-content-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.main-content-grid.admin-grid {
    grid-template-columns: 1fr;
}

@media (max-width: 900px) {

    .main-content-grid,
    .main-content-grid.admin-grid {
        grid-template-columns: 1fr;
    }

    .header-content {
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding-bottom: 1.5rem;
    }

    .name-row {
        justify-content: center;
    }
}

.content-card {
    background: var(--bg-secondary);
    border-radius: 20px;
    padding: 2rem;
    border: 1px solid var(--border-color);
}

.content-card h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-primary);
}

/* Form Styles */
.modern-form {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-group label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-secondary);
}

.form-group input {
    padding: 0.875rem 1rem;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    background: var(--bg-primary);
    color: var(--text-primary);
    font-size: 0.95rem;
    transition: all 0.2s;
}

.form-group input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.btn-save {
    width: 100%;
    padding: 1rem;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.btn-save:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
}

.btn-save:disabled {
    opacity: 0.7;
    cursor: default;
}

/* Activity List */
.activity-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.activity-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: var(--bg-primary);
    border-radius: 12px;
    border: 1px solid var(--border-color);
    transition: transform 0.2s;
}

.activity-item:hover {
    transform: translateX(4px);
    border-color: var(--primary-color);
}

.activity-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    flex-shrink: 0;
}

.activity-icon.standard {
    background: rgba(59, 130, 246, 0.1);
}

.activity-icon.mock {
    background: rgba(168, 85, 247, 0.1);
}

.activity-icon.action {
    background: rgba(245, 158, 11, 0.1);
    color: #f59e0b;
}

.activity-details {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.activity-title {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 0.95rem;
}

.activity-meta {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.activity-score {
    font-weight: 700;
    font-size: 0.9rem;
    padding: 0.25rem 0.75rem;
    border-radius: 8px;
    background: var(--bg-secondary);
}

.activity-date {
    font-size: 0.8rem;
    color: var(--text-secondary);
    padding: 0.25rem 0.75rem;
    background: var(--bg-secondary);
    border-radius: 8px;
}

.score-high {
    color: #10b981;
    background: rgba(16, 185, 129, 0.1);
}

.score-medium {
    color: #f59e0b;
    background: rgba(245, 158, 11, 0.1);
}

.score-low {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
}

.empty-state {
    text-align: center;
    color: var(--text-secondary);
    padding: 2rem;
    font-style: italic;
}
</style>
