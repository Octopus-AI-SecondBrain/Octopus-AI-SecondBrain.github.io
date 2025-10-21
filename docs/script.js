// Demo Modal functionality
const demoModal = document.getElementById('demoModal');
const tryDemoBtn = document.getElementById('tryDemoBtn');
const tryDemoBtn2 = document.getElementById('tryDemoBtn2');
const modalCloseBtn = document.querySelector('.modal-close');
const modalCloseBtnFooter = document.querySelector('.modal-close-btn');

// Open modal
function openDemoModal(e) {
    e.preventDefault();
    demoModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// Close modal
function closeDemoModal() {
    demoModal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

if (tryDemoBtn) {
    tryDemoBtn.addEventListener('click', openDemoModal);
}

if (tryDemoBtn2) {
    tryDemoBtn2.addEventListener('click', openDemoModal);
}

if (modalCloseBtn) {
    modalCloseBtn.addEventListener('click', closeDemoModal);
}

if (modalCloseBtnFooter) {
    modalCloseBtnFooter.addEventListener('click', closeDemoModal);
}

// Close modal on background click
demoModal.addEventListener('click', (e) => {
    if (e.target === demoModal) {
        closeDemoModal();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && demoModal.classList.contains('active')) {
        closeDemoModal();
    }
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        
        // Don't prevent default for modal triggers
        if (href === '#' || href === '#demo-modal') {
            return;
        }
        
        e.preventDefault();
        const target = document.querySelector(href);
        
        if (target) {
            const navHeight = document.querySelector('.navbar').offsetHeight;
            const targetPosition = target.offsetTop - navHeight;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Navbar background on scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
    } else {
        navbar.style.boxShadow = 'none';
    }
});

// Animate elements on scroll (intersection observer)
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards
document.querySelectorAll('.feature-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'all 0.6s ease-out';
    observer.observe(card);
});

// Video placeholder click handler
const videoPlaceholder = document.querySelector('.video-placeholder');
if (videoPlaceholder) {
    videoPlaceholder.addEventListener('click', () => {
        // Replace with actual video embed when ready
        alert('Demo video coming soon! Meanwhile, try the live demo.');
    });
}

