<template>
    <div class="user-management">
        <div class="management-header">
            <h2>User Management</h2>
            <div class="search-box">
                <input v-model="searchQuery" placeholder="Search users by name or email..." class="search-input">
            </div>
        </div>

        <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>Loading users...</p>
        </div>

        <div v-else-if="users.length === 0" class="empty-state">
            <p>No users found.</p>
        </div>

        <div v-else class="table-container">
            <table class="user-table">
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="user in filteredUsers" :key="user.id">
                        <td>
                            <div class="user-info">
                                <span class="user-fullname">{{ user.fullname || user.user_name }}</span>
                                <span class="user-username">@{{ user.user_name }}</span>
                            </div>
                        </td>
                        <td>{{ user.email }}</td>
                        <td>
                            <span class="role-badge" :class="{ admin: user.isadmin }">
                                {{ user.isadmin ? 'Admin' : 'User' }}
                            </span>
                        </td>
                        <td>
                            <span class="status-badge" :class="{ blocked: user.is_blocked }">
                                {{ user.is_blocked ? 'Blocked' : 'Active' }}
                            </span>
                        </td>
                        <td>
                            <div class="action-buttons">
                                <button class="btn-icon view-btn" @click="viewScores(user)"
                                    title="View Scores">📊</button>
                                <button v-if="!user.isadmin" class="btn-icon block-btn"
                                    :class="{ active: user.is_blocked }"
                                    @click="confirmAction(user, user.is_blocked ? 'unblock' : 'block')"
                                    :title="user.is_blocked ? 'Unblock User' : 'Block User'">
                                    {{ user.is_blocked ? '🔓' : '🚫' }}
                                </button>
                                <button v-if="!user.isadmin" class="btn-icon delete-btn"
                                    @click="confirmAction(user, 'delete')" title="Delete User">🗑️</button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- User Scores Modal -->
        <div v-if="selectedUserScores" class="modal-backdrop" @click.self="selectedUserScores = null">
            <div class="modal-card scores-modal">
                <div class="modal-header">
                    <h3>Activity for {{ selectedUser?.fullname || selectedUser?.user_name }}</h3>
                    <button class="close-btn" @click="selectedUserScores = null">×</button>
                </div>
                <div class="modal-body">
                    <div v-if="loadingScores" class="loading-scores">Loading activity...</div>
                    <div v-else-if="selectedUserScores.length === 0" class="empty-scores">No activity recorded for this
                        user.</div>
                    <div v-else class="scores-list">
                        <div v-for="(score, idx) in selectedUserScores" :key="idx" class="score-card">
                            <div class="score-main">
                                <span class="quiz-title">{{ score.quiz }}</span>
                                <span class="score-value">{{ score.score }} pts</span>
                            </div>
                            <div class="score-meta">
                                <span class="type-badge" :class="score.type.toLowerCase()">{{ score.type }}</span>
                                <span class="date">{{ formatDate(score.date) }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Security Action Modal -->
        <div v-if="confirmationStep > 0" class="modal-backdrop security-backdrop">
            <div class="modal-card security-modal">
                <div class="modal-header">
                    <h3>Confirm {{ actionType.toUpperCase() }}</h3>
                    <button class="close-btn" @click="resetConfirmation">×</button>
                </div>

                <div class="modal-body">
                    <!-- Step 1 & 2: Double Confirmation -->
                    <div v-if="confirmationStep === 1 || confirmationStep === 2" class="confirmation-content">
                        <div class="warning-icon">⚠️</div>
                        <p v-if="confirmationStep === 1">
                            Are you sure you want to <strong>{{ actionType }}</strong>
                            the user <strong>{{ targetUser?.user_name }}</strong>?
                        </p>
                        <p v-if="confirmationStep === 2" class="critical-warning">
                            THIS ACTION IS IRREVERSIBLE. Are you ABSOLUTELY certain?
                        </p>
                        <div class="confirm-actions">
                            <button class="btn-text" @click="resetConfirmation">Cancel</button>
                            <button class="btn-danger" @click="confirmationStep++">Yes, Continue</button>
                        </div>
                    </div>

                    <!-- Step 3: Password Verification -->
                    <div v-if="confirmationStep === 3" class="password-verification">
                        <p>Please enter your administrator password to proceed:</p>
                        <input v-model="adminPassword" type="password" placeholder="Your Admin Password"
                            class="modern-input" @keyup.enter="executeAction">
                        <p v-if="passwordError" class="error-msg">{{ passwordError }}</p>
                        <div class="confirm-actions">
                            <button class="btn-text" @click="resetConfirmation">Cancel</button>
                            <button class="btn-danger" :disabled="!adminPassword || executing" @click="executeAction">
                                {{ executing ? 'Verifying...' : 'Final Confirm' }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '@/services/api';

const users = ref([]);
const loading = ref(true);
const searchQuery = ref('');

// Score Viewing
const selectedUser = ref(null);
const selectedUserScores = ref(null);
const loadingScores = ref(false);

// Security Actions
const confirmationStep = ref(0);
const actionType = ref(''); // 'block' or 'delete'
const targetUser = ref(null);
const adminPassword = ref('');
const passwordError = ref('');
const executing = ref(false);

const fetchUsers = async () => {
    try {
        const res = await api.get('/users/getusers');
        users.value = res.data.users;
    } catch (e) {
        console.error("Failed to fetch users", e);
    } finally {
        loading.value = false;
    }
};

const filteredUsers = computed(() => {
    if (!searchQuery.value) return users.value;
    const q = searchQuery.value.toLowerCase();
    return users.value.filter(u =>
        u.user_name.toLowerCase().includes(q) ||
        (u.fullname && u.fullname.toLowerCase().includes(q)) ||
        u.email.toLowerCase().includes(q)
    );
});

const viewScores = async (user) => {
    selectedUser.value = user;
    selectedUserScores.value = [];
    loadingScores.value = true;
    try {
        const res = await api.get(`/admin/user/${user.id}/scores`);
        selectedUserScores.value = res.data.scores;
    } catch (e) {
        console.error("Failed to fetch scores", e);
    } finally {
        loadingScores.value = false;
    }
};

const confirmAction = (user, type) => {
    targetUser.value = user;
    actionType.value = type;
    confirmationStep.value = 1;
};

const resetConfirmation = () => {
    confirmationStep.value = 0;
    actionType.value = '';
    targetUser.value = null;
    adminPassword.value = '';
    passwordError.value = '';
};

const executeAction = async () => {
    executing.value = true;
    passwordError.value = '';
    try {
        // 1. Verify Password
        const verifyRes = await api.post('/auth/verify_password', { password: adminPassword.value });

        if (verifyRes.data.verified) {
            // 2. Perform Action
            if (actionType.value === 'block' || actionType.value === 'unblock') {
                await api.post(`/users/blockuser/${targetUser.value.id}`);
            } else if (actionType.value === 'delete') {
                await api.delete(`/users/deleteuser/${targetUser.value.id}`);
            }

            // Refresh list
            await fetchUsers();
            resetConfirmation();
            alert(`User ${actionType.value}ed successfully.`);
        }
    } catch (e) {
        if (e.response?.status === 401) {
            passwordError.value = "Incorrect password.";
        } else {
            passwordError.value = e.response?.data?.message || "An error occurred.";
        }
    } finally {
        executing.value = false;
    }
};

const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

onMounted(fetchUsers);
</script>

<style scoped>
.user-management {
    background: var(--bg-secondary);
    border-radius: 20px;
    border: 1px solid var(--border-color);
    padding: 1.5rem;
    margin-top: 2rem;
}

.management-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    gap: 1rem;
    flex-wrap: wrap;
}

.management-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
}

.search-box {
    flex: 1;
    max-width: 400px;
}

.search-input {
    width: 100%;
    padding: 0.75rem 1rem;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    background: var(--bg-primary);
    color: var(--text-primary);
}

.table-container {
    overflow-x: auto;
}

.user-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
}

.user-table th {
    padding: 1rem;
    border-bottom: 2px solid var(--border-color);
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 0.85rem;
}

.user-table td {
    padding: 1rem;
    border-bottom: 1px solid var(--border-color);
}

.user-info {
    display: flex;
    flex-direction: column;
}

.user-fullname {
    font-weight: 600;
    color: var(--text-primary);
}

.user-username {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.role-badge,
.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

.role-badge {
    background: rgba(34, 197, 94, 0.1);
    color: #22c55e;
}

.role-badge.admin {
    background: rgba(99, 102, 241, 0.1);
    color: #6366f1;
}

.status-badge {
    background: rgba(34, 197, 94, 0.1);
    color: #22c55e;
}

.status-badge.blocked {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
}

.action-buttons {
    display: flex;
    gap: 0.5rem;
}

.btn-icon {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-icon:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.delete-btn:hover {
    color: #ef4444;
    border-color: #ef4444;
}

.block-btn.active {
    background: #ef4444;
    color: white;
    border-color: #ef4444;
}

/* Modals */
.modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-card {
    background: var(--bg-secondary);
    border-radius: 20px;
    padding: 2rem;
    width: 90%;
    max-width: 600px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.scores-modal {
    max-height: 80vh;
    display: flex;
    flex-direction: column;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.modal-header h3 {
    margin: 0;
}

.modal-body {
    overflow-y: auto;
    flex: 1;
}

.close-btn {
    background: transparent;
    border: none;
    font-size: 1.5rem;
    color: var(--text-secondary);
    cursor: pointer;
}

.score-card {
    background: var(--bg-primary);
    padding: 1rem;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    margin-bottom: 1rem;
}

.score-main {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.quiz-title {
    font-weight: 700;
}

.score-value {
    color: var(--primary-color);
    font-weight: 700;
}

.score-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: var(--text-secondary);
}

/* Security Modal */
.security-modal {
    max-width: 400px;
    text-align: center;
}

.warning-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.critical-warning {
    color: #ef4444;
    font-weight: 700;
}

.confirm-actions {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 2rem;
}

.btn-danger {
    background: #ef4444;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
}

.btn-text {
    background: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    cursor: pointer;
}

.modern-input {
    width: 100%;
    padding: 0.75rem;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    margin-top: 1rem;
    background: var(--bg-primary);
    color: var(--text-primary);
}

.error-msg {
    color: #ef4444;
    font-size: 0.85rem;
    margin-top: 0.5rem;
}

.loading-state,
.loading-scores,
.empty-state,
.empty-scores {
    text-align: center;
    padding: 3rem;
    color: var(--text-secondary);
}

.type-badge {
    padding: 0.1rem 0.5rem;
    border-radius: 4px;
    font-size: 0.7rem;
    text-transform: uppercase;
}

.type-badge.mock {
    background: rgba(79, 70, 229, 0.1);
    color: #4f46e5;
}

.type-badge.standard {
    background: rgba(34, 197, 94, 0.1);
    color: #22c55e;
}
</style>
