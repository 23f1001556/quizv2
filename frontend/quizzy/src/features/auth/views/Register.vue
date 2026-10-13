<template>
    <div class="auth-page">
        <PublicNavbar />
        <main class="auth-container">
            <!-- Background Decorations -->
            <div class="glow-blob blob-1"></div>
            <div class="glow-blob blob-2"></div>
            <div class="ribbon ribbon-1"></div>
            <div class="ribbon ribbon-2"></div>

            <div class="auth-card">
            <div class="auth-header">
                <h1>Create Account</h1>
                <p>Join Quizzy and start your journey</p>
            </div>

            <form @submit.prevent="handleRegister" class="auth-form">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" v-model="username" placeholder="johndoe" required minlength="5"
                        maxlength="20" />
                </div>

                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" v-model="email" placeholder="name@example.com" required />
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" v-model="password" placeholder="••••••••" required
                        minlength="8" />
                    <span class="hint">Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special</span>
                </div>

                <div class="form-group">
                    <label for="confirmPassword">Confirm Password</label>
                    <input type="password" id="confirmPassword" v-model="confirmPassword" placeholder="••••••••"
                        required />
                </div>

                <button type="submit" class="btn-primary" :disabled="isLoading">
                    <span v-if="isLoading">Creating account...</span>
                    <span v-else>Sign Up</span>
                </button>

                <div v-if="error" class="error-message">
                    {{ error }}
                </div>
                <div v-if="success" class="success-message">
                    {{ success }}
                </div>
            </form>

            <div class="auth-footer">
                <p>Already have an account? <router-link to="/login">Sign in</router-link></p>
            </div>
            </div>

        </main>
        <AdminLoginCard mode="register" />
    </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api'
import AdminLoginCard from '@/components/AdminLoginCard.vue'
import PublicNavbar from '@/components/PublicNavbar.vue'

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const error = ref('')
const success = ref('')

const handleRegister = async () => {
    if (password.value !== confirmPassword.value) {
        error.value = "Passwords do not match"
        return
    }

    isLoading.value = true
    error.value = ''
    success.value = ''

    try {
        const response = await api.post('/auth/register', {
            username: username.value,
            email: email.value,
            password: password.value
        })

        success.value = response.data.message || 'Account created! Please check your email to verify.'

        // Clear form
        username.value = ''
        email.value = ''
        password.value = ''
        confirmPassword.value = ''

    } catch (err) {
        console.error(err)
        error.value = err.response?.data?.message || 'Registration failed. Please try again.'
    } finally {
        isLoading.value = false
    }
}
</script>

<style scoped>
.auth-page {
    min-height: 100vh;
    background: #020617;
}

.auth-container {
    min-height: calc(100vh - 72px);
    display: flex;
    align-items: center;
    justify-content: center;
    background: #020617;
    padding: 2rem;
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
    position: relative;
    overflow: hidden;
}

/* Background Decorations */
.glow-blob {
    position: absolute;
    width: 500px;
    height: 500px;
    filter: blur(80px);
    opacity: 0.15;
    border-radius: 50%;
    z-index: 0;
    pointer-events: none;
    animation: float 10s ease-in-out infinite;
}

.blob-1 {
    background: #6366f1;
    top: -100px;
    right: -100px;
}

.blob-2 {
    background: #a855f7;
    bottom: -150px;
    left: -150px;
    animation-delay: -5s;
}

.ribbon {
    position: absolute;
    background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.1), transparent);
    transform: rotate(-45deg);
    pointer-events: none;
    z-index: 0;
}

.ribbon-1 {
    width: 200%;
    height: 1px;
    top: 20%;
    right: -50%;
}

.ribbon-2 {
    width: 200%;
    height: 2px;
    bottom: 30%;
    left: -50%;
}

@keyframes float {

    0%,
    100% {
        transform: translate(0, 0) scale(1);
    }

    33% {
        transform: translate(30px, -50px) scale(1.1);
    }

    66% {
        transform: translate(-20px, 20px) scale(0.9);
    }
}

.auth-card {
    width: 100%;
    max-width: 480px;
    /* Slightly wider for register */
    background: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    padding: 3rem 2.5rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    position: relative;
    z-index: 10;
}

.auth-header {
    text-align: center;
    margin-bottom: 2.5rem;
}

.auth-header h1 {
    color: #fff;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
    letter-spacing: -0.025em;
}

.auth-header p {
    color: #94a3b8;
    font-size: 1rem;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    color: #e2e8f0;
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
}

.form-group input {
    width: 100%;
    padding: 0.875rem 1rem;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    color: #fff;
    font-size: 1rem;
    transition: all 0.2s ease;
}

.form-group input:focus {
    outline: none;
    border-color: #6366f1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.form-group input::placeholder {
    color: #64748b;
}

.hint {
    display: block;
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.5rem;
}

.btn-primary {
    width: 100%;
    padding: 0.875rem;
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    border: none;
    border-radius: 12px;
    color: #fff;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
}

.btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
}

.btn-primary:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
}

.error-message {
    margin-top: 1rem;
    padding: 0.75rem;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.2);
    border-radius: 8px;
    color: #f87171;
    font-size: 0.875rem;
    text-align: center;
}

.success-message {
    margin-top: 1rem;
    padding: 0.75rem;
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.2);
    border-radius: 8px;
    color: #4ade80;
    font-size: 0.875rem;
    text-align: center;
}

.auth-footer {
    margin-top: 2rem;
    text-align: center;
    color: #94a3b8;
    font-size: 0.875rem;
}

.auth-footer a {
    color: #6366f1;
    text-decoration: none;
    font-weight: 600;
    transition: color 0.2s;
}

.auth-footer a:hover {
    color: #818cf8;
}
</style>
