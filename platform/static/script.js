document.addEventListener('DOMContentLoaded', () => {
    // Add subtle parallax or interactive elements here if needed
    console.log('Platform Loaded');

    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            if (card.classList.contains('coming-soon')) return;

            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            card.style.setProperty('--x', `${x}px`);
            card.style.setProperty('--y', `${y}px`);
        });
    });
});
