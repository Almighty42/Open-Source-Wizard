const DESKTOP_QUERY = '(min-width: 650px)'; // keep in sync with the `header` breakpoint in Sass

export function initHeaderMenu() {
	const button = document.querySelector('.header__menu-button');
	const menu = document.getElementById('header-menu');
	if (!button || !menu) return;

	const setOpen = (open) => {
		menu.classList.toggle('is-open', open);
		button.setAttribute('aria-expanded', String(open));
	};
	const isOpen = () => menu.classList.contains('is-open');

	button.addEventListener('click', () => setOpen(!isOpen()));

	// Click outside closes the menu
	document.addEventListener('click', (e) => {
		if (isOpen() && !menu.contains(e.target) && !button.contains(e.target)) {
			setOpen(false);
		}
	});

	// Escape closes it and returns focus to the button
	document.addEventListener('keydown', (e) => {
		if (e.key === 'Escape' && isOpen()) {
			setOpen(false);
			button.focus();
		}
	});

	// Reset state when the window grows past the breakpoint
	window.matchMedia(DESKTOP_QUERY).addEventListener('change', (e) => {
		if (e.matches) setOpen(false);
	});
}
