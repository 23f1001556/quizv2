<template>
    <Teleport to="body">
        <section v-if="isOpen" class="admin-login-card" aria-label="Shared login credentials">
            <button class="dismiss-button" type="button" aria-label="Dismiss login credentials"
                @click="isOpen = false">
                ×
            </button>

            <section class="user-access" aria-labelledby="user-login-title">
                <header class="card-header">
                    <div>
                        <h2 id="user-login-title">User access</h2>
                        <p>Regular user account credentials.</p>
                    </div>
                </header>

                <dl class="credentials">
                    <div>
                        <dt>Email</dt>
                        <dd>{{ regularUserCredentials.email }}</dd>
                    </div>
                    <div>
                        <dt>Password</dt>
                        <dd>{{ regularUserCredentials.password }}</dd>
                    </div>
                    <div>
                        <dt>Role</dt>
                        <dd>User</dd>
                    </div>
                </dl>

                <button class="login-button user-login-button" type="button" @click="loginAsUser">
                    Login as User
                </button>
            </section>

            <div class="section-divider"></div>

            <header class="card-header">
                <div>
                    <h2 id="admin-login-title">Admin access</h2>
                    <p>These credentials provide full admin access.</p>
                </div>
            </header>

            <dl class="credentials">
                <div>
                    <dt>Email</dt>
                    <dd>{{ demoAdminCredentials.email }}</dd>
                </div>
                <div>
                    <dt>Password</dt>
                    <dd>{{ demoAdminCredentials.password }}</dd>
                </div>
                <div>
                    <dt>Role</dt>
                    <dd>Admin</dd>
                </div>
            </dl>

            <button class="login-button" type="button" @click="loginAsAdmin">
                Login as Admin
            </button>
        </section>

        <button v-else class="reopen-button" type="button" @click="isOpen = true">
            Admin login
        </button>
    </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { demoAdminCredentials, regularUserCredentials } from '@/features/auth/demoAdminCredentials'

const props = defineProps({
    mode: {
        type: String,
        default: 'login'
    }
})

const emit = defineEmits(['login'])
const router = useRouter()
const isOpen = ref(true)

const loginAsAdmin = () => {
    if (props.mode === 'register') {
        router.push({ name: 'Login', query: { adminLogin: 'true' } })
        return
    }

    emit('login', demoAdminCredentials)
}

const loginAsUser = () => {
    if (props.mode === 'register') {
        router.push({ name: 'Login', query: { userLogin: 'true' } })
        return
    }

    emit('login', regularUserCredentials)
}
</script>

<style scoped>
.admin-login-card {
    position: fixed;
    right: 1.25rem;
    bottom: 1.25rem;
    z-index: 1000;
    width: min(360px, calc(100vw - 2rem));
    padding: 1.25rem;
    border: 1px solid rgba(129, 140, 248, 0.4);
    border-radius: 16px;
    background: rgba(15, 23, 42, 0.96);
    color: #e2e8f0;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
    backdrop-filter: blur(16px);
}

.card-header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
}

.card-header h2 {
    margin: 0;
    color: #fff;
    font-size: 1.1rem;
}

.card-header p {
    margin: 0.4rem 0 0;
    color: #fbbf24;
    font-size: 0.8rem;
    line-height: 1.4;
}

.user-access .card-header p {
    color: #94a3b8;
}

.section-divider {
    height: 1px;
    margin: 1.25rem 0;
    background: rgba(255, 255, 255, 0.12);
}

.dismiss-button {
    position: absolute;
    top: 0.55rem;
    right: 0.75rem;
    display: grid;
    width: 2rem;
    height: 2rem;
    place-items: center;
    border: 0;
    border-radius: 6px;
    background: transparent;
    color: #cbd5e1;
    font-size: 1.5rem;
    line-height: 1;
    cursor: pointer;
}

.dismiss-button:hover {
    background: rgba(255, 255, 255, 0.1);
}

.credentials {
    display: grid;
    gap: 0.75rem;
    margin: 1rem 0;
}

.credentials div {
    display: grid;
    grid-template-columns: 5rem minmax(0, 1fr);
    gap: 0.5rem;
}

.credentials dt {
    color: #94a3b8;
    font-size: 0.85rem;
}

.credentials dd {
    margin: 0;
    color: #fff;
    font-family: monospace;
    font-size: 0.85rem;
    overflow-wrap: anywhere;
}

.login-button,
.reopen-button {
    border: 0;
    border-radius: 9px;
    background: #6366f1;
    color: #fff;
    font-weight: 700;
    cursor: pointer;
}

.login-button {
    width: 100%;
    padding: 0.75rem 1rem;
}

.user-login-button {
    background: #0f766e;
}

.reopen-button {
    position: fixed;
    right: 1.25rem;
    bottom: 1.25rem;
    z-index: 1000;
    padding: 0.75rem 1rem;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

@media (max-width: 640px) {
    .admin-login-card,
    .reopen-button {
        right: 0.75rem;
        bottom: 0.75rem;
    }
}
</style>
