/**
 * EDUAI Cameroun — JavaScript Principal
 * Projet Tuteuré 2025
 */

document.addEventListener('DOMContentLoaded', function () {

  // ── Auto-dismiss toasts Bootstrap ──
  document.querySelectorAll('.toast').forEach(el => {
    const toast = new bootstrap.Toast(el, { delay: 4500 });
    toast.show();
  });

  // ── Animation fade-in au scroll ──
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('fade-in');
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.epreuve-card, .quiz-card, .stat-card, .feature-card').forEach(el => {
    observer.observe(el);
  });

  // ── Validation formulaires Bootstrap ──
  document.querySelectorAll('form[novalidate]').forEach(form => {
    form.addEventListener('submit', e => {
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
      }
      form.classList.add('was-validated');
    });
  });

  // ── Prévisualisation avatar/image ──
  const avatarInput = document.querySelector('input[name="avatar"]');
  if (avatarInput) {
    avatarInput.addEventListener('change', function () {
      const file = this.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = e => {
          const preview = document.querySelector('.avatar-preview');
          if (preview) preview.src = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // ── Barre de recherche live ──
  const searchInput = document.querySelector('#searchInput');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      const q = this.value.toLowerCase();
      document.querySelectorAll('.epreuve-card, .quiz-card').forEach(card => {
        const text = card.textContent.toLowerCase();
        card.closest('.col-md-6, .col-md-4, .col-lg-4').style.display = text.includes(q) ? '' : 'none';
      });
    });
  }

  // ── Compteur de caractères pour les textarea IA ──
  document.querySelectorAll('textarea[maxlength]').forEach(ta => {
    const counter = document.createElement('small');
    counter.className = 'text-muted d-block text-end mt-1';
    ta.parentNode.appendChild(counter);
    const update = () => counter.textContent = `${ta.value.length}/${ta.getAttribute('maxlength')} caractères`;
    ta.addEventListener('input', update);
    update();
  });

  // ── Confirmation avant soumission de quiz ──
  const quizForm = document.getElementById('quizForm');
  if (quizForm) {
    quizForm.addEventListener('submit', function (e) {
      const total = document.querySelectorAll('[name^="question_"]').length;
      const answered = document.querySelectorAll('input[type="radio"]:checked').length;
      if (answered < total) {
        const ok = confirm(`Vous avez répondu à ${answered}/${total} questions. Soumettre quand même ?`);
        if (!ok) e.preventDefault();
      }
    });
  }

  // ── Copier IP en un clic ──
  document.querySelectorAll('code').forEach(el => {
    el.style.cursor = 'pointer';
    el.title = 'Cliquer pour copier';
    el.addEventListener('click', () => {
      navigator.clipboard.writeText(el.textContent);
      const original = el.textContent;
      el.textContent = '✓ Copié !';
      setTimeout(() => el.textContent = original, 1500);
    });
  });

});
