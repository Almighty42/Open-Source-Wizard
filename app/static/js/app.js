const mode_switch = document.getElementById("mode_switch")
const root = document.documentElement

let dark_mode = false

function update_theme() {
	const theme = root.getAttribute("data-theme") || "light";
	const is_dark = theme === "dark";

	mode_switch.textContent = is_dark ? "[ ☾ ]" : "[ ☼ ]";

	document.querySelectorAll("[data-theme-image]").forEach((img) => {
		img.src = is_dark ? img.dataset.darkSrc : img.dataset.lightSrc;
	});
}

mode_switch?.addEventListener("click", () => {
	const currentTheme = root.getAttribute("data-theme") || "light";
	const newTheme = currentTheme === "dark" ? "light" : "dark";

	root.setAttribute("data-theme", newTheme);
	localStorage.setItem("theme", newTheme);
	update_theme();
})

const saved_theme = localStorage.getItem("theme");
if (saved_theme) {
	root.setAttribute("data-theme", saved_theme);
}

const CHECK_ICON = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" 
  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="20 6 9 17 4 12"/>
</svg>`;

document.querySelectorAll(".code-copy-btn").forEach(btn => {
	const icon_span = btn.querySelector(".code-copy-icon");
	const copy_text = btn.querySelector(".code-copy-text");
	const original_icon = icon_span.innerHTML;

	btn.addEventListener("click", () => {
		const code = btn.closest(".code-block").querySelector("code");
		navigator.clipboard.writeText(code.innerText).then(() => {
			icon_span.innerHTML = CHECK_ICON;
			if (copy_text) copy_text.textContent = "COPIED";
			btn.classList.add("copied");

			setTimeout(() => {
				icon_span.innerHTML = original_icon;
				if (copy_text) copy_text.textContent = "COPY";
				btn.classList.remove("copied");
			}, 1500);
		});
	});
});

update_theme();
