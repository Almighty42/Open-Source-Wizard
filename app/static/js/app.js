import { initRemoteSelect, updateLabel, syncHiddenInputs } from './tomselect.js'
import { closeLightbox } from './lightbox.js'
import { update_theme } from './theme.js'
import { fetchArticles, syncProjectDateState, syncPublishedDateState } from './form.js'

const root = document.documentElement;


const saved_theme = localStorage.getItem("theme");
if (saved_theme) {
	root.setAttribute("data-theme", saved_theme);
}

const CHECK_ICON = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" 
  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="20 6 9 17 4 12"/>
</svg>`;

document.addEventListener("DOMContentLoaded", () => {
	const change_theme = document.getElementById("change-theme");
	const searchInput = document.querySelector("#nav-search input");
	const filterForm = document.querySelector("form[id$='-filter']");
	const itemsList = document.getElementById("articles-list") || document.getElementById("projects-list");
	const topLink = document.getElementById("top-link");

	const lightbox = document.getElementById("lightbox");
	const lightboxImg = document.getElementById("lightbox-img");
	const lightboxCaption = document.getElementById("lightbox-caption");
	const lightboxClose = document.getElementById("lightbox-close");

	const statusField = document.getElementById("status");
	const publishedAtField = document.getElementById("published_at");

	const projectStateField = document.getElementById("project_state");
	const startedAtField = document.getElementById("started_at");
	const completedAtField = document.getElementById("completed_at");

	initRemoteSelect("#tags-select", { maxItems: null });
	initRemoteSelect("#attachments-select", { maxItems: null });
	initRemoteSelect("#cover-asset-select", { maxItems: 1 });
	initRemoteSelect("#inline-assets-select", { maxItems: null });

	change_theme?.addEventListener("click", () => {
		const currentTheme = root.getAttribute("data-theme") || "light";
		const newTheme = currentTheme === "dark" ? "light" : "dark";

		root.setAttribute("data-theme", newTheme);
		localStorage.setItem("theme", newTheme);
		update_theme();
	});

	document.querySelectorAll(".code-copy-btn").forEach((btn) => {
		const icon_span = btn.querySelector(".code-copy-icon");
		const copy_text = btn.querySelector(".code-copy-text");
		const original_icon = icon_span?.innerHTML || "";

		btn.addEventListener("click", () => {
			const text_to_copy = btn.dataset.copy || "";

			navigator.clipboard.writeText(text_to_copy).then(() => {
				if (icon_span) icon_span.innerHTML = CHECK_ICON;
				if (copy_text) copy_text.textContent = "COPIED";
				btn.classList.add("copied");

				setTimeout(() => {
					if (icon_span) icon_span.innerHTML = original_icon;
					if (copy_text) copy_text.textContent = "COPY";
					btn.classList.remove("copied");
				}, 1500);
			});
		});
	});

	update_theme();

	document.querySelectorAll(".custom-select").forEach((select) => {
		const trigger = select.querySelector(".custom-select__trigger");
		const options = select.querySelectorAll(".custom-select__option");
		const valueDisplay = select.querySelector(".custom-select__value");
		const isMulti = select.classList.contains("custom-multiselect");
		const name = select.dataset.name;

		const MAX_VISIBLE = 2;

		function updateLabel() {
			if (!valueDisplay) return;

			if (isMulti) {
				const checked = [...options].filter((o) => o.classList.contains("checked"));

				if (checked.length === 0) {
					valueDisplay.textContent = "All";
				} else if (checked.length <= MAX_VISIBLE) {
					valueDisplay.textContent = checked
						.map((o) => o.textContent.trim())
						.join(", ");
				} else {
					const visible = checked
						.slice(0, MAX_VISIBLE)
						.map((o) => o.textContent.trim())
						.join(", ");

					valueDisplay.textContent = `${visible} +${checked.length - MAX_VISIBLE}`;
				}
			} else {
				const selected = select.querySelector(".custom-select__option.selected");
				if (selected) {
					valueDisplay.textContent = selected.textContent.trim();
				}
			}
		}

		function syncHiddenInputs() {
			select.querySelectorAll("input[type='hidden']").forEach((i) => i.remove());

			const checked = [...options].filter((o) => o.classList.contains("checked"));

			checked.forEach((o) => {
				const input = document.createElement("input");
				input.type = "hidden";
				input.name = name;
				input.value = o.dataset.value;
				select.appendChild(input);
			});
		}

		updateLabel();

		trigger?.addEventListener("click", (e) => {
			e.stopPropagation();
			select.classList.toggle("open");
		});

		options.forEach((option) => {
			option.addEventListener("click", () => {
				if (isMulti) {
					option.classList.toggle("checked");
					syncHiddenInputs();
					updateLabel();
					fetchArticles();
				} else {
					options.forEach((o) => o.classList.remove("selected"));
					option.classList.add("selected");
					updateLabel();

					let hidden = select.querySelector("input[type='hidden']");
					if (!hidden) {
						hidden = document.createElement("input");
						hidden.type = "hidden";
						hidden.name = name;
						select.appendChild(hidden);
					}
					hidden.value = option.dataset.value || "";

					select.classList.remove("open");
					fetchArticles();
				}
			});
		});

		document.addEventListener("click", () => {
			select.classList.remove("open");
		});
	});



	let debounceTimer;
	searchInput?.addEventListener("input", () => {
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(fetchArticles, 300);
	});

	window.addEventListener("scroll", () => {
		if (!topLink) return;

		if (window.scrollY > 50) {
			topLink.classList.add("visible");
		} else {
			topLink.classList.remove("visible");
		}
	});

	document.querySelectorAll(".article-body figure.inline-image img, .article-body figure.diagram img")
		.forEach((img) => {
			img.addEventListener("click", () => {
				if (!lightbox || !lightboxImg || !lightboxCaption) return;

				lightboxImg.src = img.src;
				lightboxImg.alt = img.alt;
				const caption = img.closest("figure")?.querySelector("figcaption")?.textContent || "";
				lightboxCaption.textContent = caption;
				lightbox.classList.add("active");
				document.body.style.overflow = "hidden";
			});
		});


	lightboxClose?.addEventListener("click", closeLightbox);
	lightbox?.addEventListener("click", (e) => {
		if (e.target === lightbox) closeLightbox();
	});
	document.addEventListener("keydown", (e) => {
		if (e.key === "Escape") closeLightbox();
	});



	statusField?.addEventListener("change", syncPublishedDateState);
	projectStateField?.addEventListener("change", syncProjectDateState);

	syncPublishedDateState();
	syncProjectDateState();
});

