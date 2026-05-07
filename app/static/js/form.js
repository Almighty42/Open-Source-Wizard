function getFilterParams(filterForm) {
	if (!filterForm) return "";
	return new URLSearchParams(new FormData(filterForm)).toString();
}

export async function fetchArticles() {
	const filterForm = document.querySelector("form[id$='-filter']");
	const itemsList =
		document.getElementById("articles-list") ||
		document.getElementById("projects-list");

	if (!filterForm || !itemsList) return;

	const params = getFilterParams(filterForm);
	const baseUrl = filterForm.action;
	const url = params ? `${baseUrl}?${params}` : baseUrl;

	window.history.replaceState({}, "", url);

	const res = await fetch(url, {
		headers: { "X-Requested-With": "XMLHttpRequest" }
	});

	if (res.ok) {
		itemsList.innerHTML = await res.text();
	}
}

export function syncProjectDateState() {
	const projectStateField = document.getElementById("project_state");
	const startedAtField = document.getElementById("started_at");
	const completedAtField = document.getElementById("completed_at");

	if (!projectStateField) return;

	if (startedAtField) {
		const disableStarted = projectStateField.value === "planned";
		startedAtField.disabled = disableStarted;

		if (disableStarted) {
			startedAtField.value = "";
		}
	}

	if (completedAtField) {
		const disableCompleted = projectStateField.value !== "finished";
		completedAtField.disabled = disableCompleted;

		if (disableCompleted) {
			completedAtField.value = "";
		}
	}
}

export function syncPublishedDateState() {
	const statusField = document.getElementById("status");
	const publishedAtField = document.getElementById("published_at");

	if (!statusField || !publishedAtField) return;

	const shouldDisable =
		statusField.value === "draft" || statusField.value === "archived";

	publishedAtField.disabled = shouldDisable;

	if (shouldDisable) {
		publishedAtField.value = "";
	}
}
