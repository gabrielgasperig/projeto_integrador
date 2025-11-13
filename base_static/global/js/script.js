// Smooth scroll para âncoras considerando header fixo (compatível e robusto)
document.addEventListener('DOMContentLoaded', function() {
    function getHeaderHeight() {
        const header = document.querySelector('header');
        if (!header) return 0;
        return header.offsetHeight || 0;
    }
    // Aplica o scroll customizado para links do menu principal, mobile e footer
    const desktopNav = document.querySelectorAll('ul.md\\:flex.items-center.gap-8 a[href^="#"]');
    const mobileNav = document.querySelectorAll('ul.flex.flex-col.gap-4.px-4 a[href^="#"]');
    const footerLinks = document.querySelectorAll('footer ul.space-y-2 a[href^="#"]');

    [...desktopNav, ...mobileNav, ...footerLinks].forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href.length > 1 && href.startsWith('#')) {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    const headerHeight = getHeaderHeight();
                    target.style.setProperty('scroll-margin-top', (headerHeight + 12) + 'px', 'important');
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    setTimeout(function() {
                        const y = target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 12;
                        window.scrollTo({ top: y, behavior: 'smooth' });
                    }, 200);
                }
            }
        });
    });
});
