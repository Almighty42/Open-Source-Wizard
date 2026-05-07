const root = document.documentElement;

export function update_theme() {
	const change_theme = document.getElementById("change-theme");
	const theme = root.getAttribute("data-theme") || "light";
	const is_dark = theme === "dark";

	if (change_theme) {
		change_theme.textContent = is_dark ? "[ ☾ ]" : "[ ☼ ]";
	}

	document.querySelectorAll("[data-theme-image]").forEach((img) => {
		img.src = is_dark ? img.dataset.darkSrc : img.dataset.lightSrc;
	});
}
