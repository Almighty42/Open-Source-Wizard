const root = document.documentElement;

export function update_theme() {
	const mode_switch = document.getElementById("mode_switch");
	const theme = root.getAttribute("data-theme") || "light";
	const is_dark = theme === "dark";

	if (mode_switch) {
		mode_switch.textContent = is_dark ? "[ ☾ ]" : "[ ☼ ]";
	}

	document.querySelectorAll("[data-theme-image]").forEach((img) => {
		img.src = is_dark ? img.dataset.darkSrc : img.dataset.lightSrc;
	});
}
