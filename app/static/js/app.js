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

document.querySelectorAll(".custom-select").forEach(select => {
	const trigger = select.querySelector(".custom-select__trigger");
	const options = select.querySelectorAll(".custom-select__option");
	const valueDisplay = select.querySelector(".custom-select__value");
	const isMulti = select.classList.contains("custom-multiselect");
	const form = select.closest("form");
	const name = select.dataset.name;

	const MAX_VISIBLE = 2;

	function updateLabel() {
		if (isMulti) {
			const checked = [...options].filter(o => o.classList.contains("checked"));
			if (checked.length === 0) {
				valueDisplay.textContent = "All";
			} else if (checked.length <= MAX_VISIBLE) {
				valueDisplay.textContent = checked.map(o => o.textContent.trim()).join(", ");
			} else {
				const visible = checked.slice(0, MAX_VISIBLE).map(o => o.textContent.trim()).join(", ");
				valueDisplay.textContent = `${visible} +${checked.length - MAX_VISIBLE}`;
			}
		} else {
			const selected = select.querySelector(".custom-select__option.selected");
			if (selected) valueDisplay.textContent = selected.textContent.trim();
		}
	}

	function syncHiddenInputs() {
		select.querySelectorAll("input[type='hidden']").forEach(i => i.remove());
		const checked = [...options].filter(o => o.classList.contains("checked"));
		checked.forEach(o => {
			const input = document.createElement("input");
			input.type = "hidden";
			input.name = name;
			input.value = o.dataset.value;
			select.appendChild(input);
		});
	}

	updateLabel();

	trigger.addEventListener("click", e => {
		e.stopPropagation();
		select.classList.toggle("open");
	});

	options.forEach(option => {
		option.addEventListener("click", () => {
			if (isMulti) {
				option.classList.toggle("checked");
				syncHiddenInputs();
				updateLabel();
				fetchArticles();
			} else {
				options.forEach(o => o.classList.remove("selected"));
				option.classList.add("selected");
				updateLabel();

				const hidden = select.querySelector("input[type='hidden']");
				if (hidden) hidden.value = option.dataset.value;

				select.classList.remove("open");
				fetchArticles();
			}
		});
	});

	document.addEventListener("click", () => select.classList.remove("open"));
});

const searchInput = document.querySelector("#nav-search input");
const articlesList = document.getElementById("articles-list");

function getFilterParams() {
	const form = document.getElementById("article-filter");
	return new URLSearchParams(new FormData(form)).toString();
}

async function fetchArticles() {
	const params = getFilterParams();
	window.history.replaceState({}, "", `/articles/?${params}`);
	const res = await fetch(`/articles/?${params}`, {
		headers: { "X-Requested-With": "XMLHttpRequest" }
	});
	if (res.ok) {
		articlesList.innerHTML = await res.text();
	}
}

let debounceTimer;
searchInput?.addEventListener("input", () => {
	clearTimeout(debounceTimer);
	debounceTimer = setTimeout(fetchArticles, 300);
});

const topLink = document.getElementById("top-link");

window.addEventListener("scroll", () => {
	if (window.scrollY > 50) {
		topLink.classList.add("visible");
	} else {
		topLink.classList.remove("visible");
	}
});
