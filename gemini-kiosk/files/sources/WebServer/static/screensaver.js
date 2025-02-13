document.addEventListener('DOMContentLoaded', () => {
    const logo = document.getElementById('logo');
    const container = document.getElementById('container');

    let x = Math.random() * (container.clientWidth - logo.clientWidth);
    let y = Math.random() * (container.clientHeight - logo.clientHeight);
    let dx = 2;
    let dy = 2;

    function moveLogo() {
        x += dx;
        y += dy;

        // Rebondir sur les bords
        if (x + logo.clientWidth > container.clientWidth || x < 0) {
            dx = -dx;
        }
        if (y + logo.clientHeight > container.clientHeight || y < 0) {
            dy = -dy;
        }

        logo.style.left = x + 'px';
        logo.style.top = y + 'px';

        requestAnimationFrame(moveLogo);
    }

    moveLogo();
});
