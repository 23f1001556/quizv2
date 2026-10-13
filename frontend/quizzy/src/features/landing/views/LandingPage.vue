<template>
    <div class="landing-page">
        <PublicNavbar />

        <!-- Hero Section -->
        <section class="hero">
            <div class="hero-content">
                <div class="pill-badge">AI-Powered Learning</div>
                <h1>Master Your Studies with <span class="gradient-text">Intelligence</span></h1>
                <p class="subtitle">
                    Transform your study materials into interactive quizzes, analyze your performance,
                    and conquer mock exams with anti-cheat protection. All in one place.
                </p>
                <div class="hero-actions">
                    <router-link to="/register" class="btn-hero-primary">Start Learning for Free</router-link>
                    <router-link to="/demo" class="btn-hero-secondary">View Demo</router-link>
                </div>
            </div>
            <div class="hero-visual">
                <div class="glass-card main-card">
                    <div class="card-header">
                        <div class="dots"><span></span><span></span><span></span></div>
                    </div>
                    <div class="card-body">
                        <div class="mock-quiz">
                            <div class="mock-line title"></div>
                            <div class="mock-line opt"></div>
                            <div class="mock-line opt active"></div>
                            <div class="mock-line opt"></div>
                        </div>
                    </div>
                </div>
                <div class="floating-badge badge-1">🤖 AI Generated</div>
                <div class="floating-badge badge-2">🏆 Top Scorer</div>
            </div>
        </section>

        <!-- Features Section -->
        <section class="features">
            <div class="section-header">
                <h2>Everything you need to <span class="gradient-text">Excel</span></h2>
                <p>Powerful tools designed to help you study smarter, not harder.</p>
            </div>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">📝</div>
                    <h3>AI Quiz Generation</h3>
                    <p>Upload PDFs or type a topic to generate custom quizzes in seconds using Gemini AI.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🛡️</div>
                    <h3>Secure Mock Exams</h3>
                    <p>Standardized testing with full-screen enforcement, anti-tab switching, and keyboard locking.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3>Smart Analytics</h3>
                    <p>Visualize your progress over time and identify weak concepts with personalized AI feedback.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📚</div>
                    <h3>Study Materials</h3>
                    <p>Generate comprehensive study guides and explanations tailored to your performance.</p>
                </div>
            </div>
        </section>

        <!-- Footer -->
        <footer class="footer">
            <p>&copy; 2026 Quizzy. Built for serious students.</p>
        </footer>
    </div>
</template>

<script setup>
import PublicNavbar from '@/components/PublicNavbar.vue'

// Landing page logic (mostly static for now)
</script>

<style scoped>
.landing-page {
    min-height: 100vh;
    background: #0f172a;
    color: white;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    overflow-x: hidden;
}

/* Hero Section */
.hero {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 4rem;
    padding: 6rem 5% 4rem;
    max-width: 1400px;
    margin: 0 auto;
    align-items: center;
}

.pill-badge {
    display: inline-block;
    padding: 0.4rem 1rem;
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 100px;
    color: #818cf8;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
}

.hero h1 {
    font-size: clamp(2.5rem, 5vw, 4rem);
    line-height: 1.1;
    font-weight: 800;
    margin-bottom: 1.5rem;
    letter-spacing: -0.02em;
}

.gradient-text {
    background: linear-gradient(135deg, #6366f1, #a855f7);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    font-size: 1.25rem;
    color: #94a3b8;
    line-height: 1.6;
    margin-bottom: 2.5rem;
    max-width: 600px;
}

.hero-actions {
    display: flex;
    gap: 1rem;
}

.btn-hero-primary {
    padding: 1rem 2rem;
    background: #6366f1;
    color: white;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 700;
    box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.4);
    transition: all 0.2s;
}

.btn-hero-secondary {
    padding: 1rem 2rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: white;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.2s;
}

.btn-hero-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 30px -5px rgba(99, 102, 241, 0.5);
}

/* Hero Visual */
.hero-visual {
    position: relative;
    display: flex;
    justify-content: center;
}

.glass-card {
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    width: 100%;
    max-width: 450px;
    aspect-ratio: 4/3;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    animation: float 6s ease-in-out infinite;
}

.card-header {
    padding: 0.75rem 1.25rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.dots {
    display: flex;
    gap: 6px;
}

.dots span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
}

.card-body {
    padding: 2rem;
}

.mock-quiz {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.mock-line {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
}

.mock-line.title {
    width: 80%;
    height: 20px;
    margin-bottom: 1rem;
    background: rgba(255, 255, 255, 0.1);
}

.mock-line.opt {
    width: 100%;
    height: 40px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.mock-line.opt.active {
    border-color: #6366f1;
    background: rgba(99, 102, 241, 0.1);
}

.floating-badge {
    position: absolute;
    padding: 0.75rem 1.25rem;
    background: #1e293b;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.9rem;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
}

.badge-1 {
    top: -20px;
    right: -20px;
    animation: float 5s ease-in-out infinite reverse;
}

.badge-2 {
    bottom: 20px;
    left: -20px;
    animation: float 7s ease-in-out infinite;
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-20px);
    }
}

/* Features Section */
.features {
    padding: 8rem 5%;
    max-width: 1400px;
    margin: 0 auto;
}

.section-header {
    text-align: center;
    margin-bottom: 4rem;
}

.section-header h2 {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
}

.section-header p {
    color: #94a3b8;
    font-size: 1.1rem;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
}

.feature-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 2.5rem;
    border-radius: 24px;
    transition: all 0.3s;
}

.feature-card:hover {
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(99, 102, 241, 0.3);
    transform: translateY(-5px);
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 1.5rem;
}

.feature-card h3 {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.feature-card p {
    color: #94a3b8;
    line-height: 1.6;
}

.footer {
    text-align: center;
    padding: 4rem 5%;
    color: #475569;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}

@media (max-width: 968px) {
    .hero {
        grid-template-columns: 1fr;
        text-align: center;
        padding-top: 3rem;
    }

    .subtitle {
        margin-left: auto;
        margin-right: auto;
    }

    .hero-actions {
        justify-content: center;
    }

    .hero-visual {
        margin-top: 4rem;
    }
}
</style>
