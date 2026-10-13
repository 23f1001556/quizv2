<template>
    <nav class="nav-bar" aria-label="Main navigation">
        <router-link to="/" class="logo" aria-label="Quizzy home">
            <span class="logo-icon">⚡</span>
            <span class="logo-text">Quizzy</span>
        </router-link>
        <div class="nav-actions">
            <router-link to="/login" class="nav-link">Login</router-link>
            <router-link to="/register" class="btn-primary-sm">Get Started</router-link>
        </div>
    </nav>
</template>

<style scoped>
.nav-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 5%;
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(12px);
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: white;
    font-size: 1.5rem;
    font-weight: 800;
    text-decoration: none;
}

.logo-icon {
    background: linear-gradient(135deg, #6366f1, #a855f7);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.nav-actions {
    display: flex;
    align-items: center;
    gap: 2rem;
}

.nav-link {
    color: #94a3b8;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
}

.nav-link:hover {
    color: white;
}

.btn-primary-sm {
    padding: 0.6rem 1.2rem;
    background: #6366f1;
    color: white;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.2s;
}
</style>
