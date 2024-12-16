document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.querySelector('.btn[href="/login"]');
    const registerButton = document.querySelector('.btn[href="/register"]');

    loginButton.addEventListener('click', (e) => {
        e.preventDefault();

        window.location.href = '/login';
    });

    registerButton.addEventListener('click', (e) => {
        e.preventDefault();

        window.location.href = '/register';
    });
});
