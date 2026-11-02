// post_toc.js
// Closes the "On this page" dropdown after a link click, an outside click or Escape.

export function initPostToc() {
	const toc = document.getElementById("post-toc");
	if (!toc) return;

	const close = () => toc.removeAttribute("open");

	toc.addEventListener("click", (e) => {
		if (e.target.closest("a")) close();
	});

	document.addEventListener("click", (e) => {
		if (!toc.contains(e.target)) close();
	});

	document.addEventListener("keydown", (e) => {
		if (e.key === "Escape") close();
	});
}
