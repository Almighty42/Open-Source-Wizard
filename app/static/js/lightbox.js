export function closeLightbox() {
	const lightbox = document.getElementById("lightbox");
	if (!lightbox) return;

	lightbox.classList.remove("active");
	document.body.style.overflow = "";
}
