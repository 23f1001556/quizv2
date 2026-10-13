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
                <h1>Welcome Back</h1>
                <p>Sign in to continue to Quizzy</p>
            </div>

            <form @submit.prevent="handleLogin" class="auth-form">
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" v-model="email" placeholder="name@example.com" required />
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" v-model="password" placeholder="••••••••" required />
                </div>

                <div class="form-actions">
                    <router-link to="/forgot-password" class="forgot-password">Forgot password?</router-link>
                </div>

                <button type="submit" class="btn-primary" :disabled="isLoading">
                    <span v-if="isLoading">Signing in...</span>
                    <span v-else>Sign In</span>
                </button>

                <div v-if="error" class="error-message">
                    {{ error }}
                </div>
            </form>

            <div class="auth-footer">
                <p>Don't have an account? <router-link to="/register">Sign up</router-link></p>
            </div>
            </div>

        </main>
        <AdminLoginCard @login="handleLogin" />
    </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import AdminLoginCard from '@/components/AdminLoginCard.vue'
import PublicNavbar from '@/components/PublicNavbar.vue'
import { demoAdminCredentials, regularUserCredentials } from '@/features/auth/demoAdminCredentials'

const router = useRouter()
const route = useRoute()
const email = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')

const handleLogin = async (credentials = null) => {
    isLoading.value = true
    error.value = ''

    try {
        const response = await api.post('/auth/login', {
            email: credentials?.email || email.value,
            password: credentials?.password || password.value
        })

        const { token, user } = response.data

        // Store token
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))

        // Redirect based on user role/id
        if (user.isadmin) {
            router.push('/dashboard/admin')
        } else {
            router.push('/dashboard')
        }

    } catch (err) {
        console.error(err)
        error.value = err.response?.data?.message || 'Login failed. Please try again.'
    } finally {
        isLoading.value = false
    }
}

onMounted(() => {
    if (route.query.adminLogin === 'true') {
        handleLogin(demoAdminCredentials)
    } else if (route.query.userLogin === 'true') {
        handleLogin(regularUserCredentials)
    }
})
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
    max-width: 420px;
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

.form-actions {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 1.5rem;
}

.forgot-password {
    color: #6366f1;
    font-size: 0.875rem;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
}

.forgot-password:hover {
    color: #818cf8;
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
