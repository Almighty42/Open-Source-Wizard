export function initRemoteSelect(
	selector,
	{
		valueField = "value",
		labelField = "text",
		searchField = "text",
		maxItems = null
	} = {}
) {
	const el = document.querySelector(selector);
	if (!el) return;

	new TomSelect(el, {
		valueField,
		labelField,
		searchField,
		maxItems,
		preload: false,
		create: false,
		loadThrottle: 250,
		plugins: ["remove_button", "virtual_scroll"],
		firstUrl(query) {
			const url = new URL(el.dataset.remoteUrl, window.location.origin);
			url.searchParams.set("q", query || "");
			url.searchParams.set("page", "1");
			return url.toString();
		},
		load(query, callback) {
			const url = this.getUrl(query);
			fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
				.then((res) => res.json())
				.then((data) => {
					if (data.has_more) {
						const nextUrl = new URL(url);
						const nextPage =
							Number(nextUrl.searchParams.get("page") || "1") + 1;
						nextUrl.searchParams.set("page", String(nextPage));
						this.setNextUrl(query, nextUrl.toString());
					}
					callback(data.results);
				})
				.catch(() => callback());
		},
		render: {
			option(item, escape) {
				return `<div>${escape(item.text)}</div>`;
			},
			item(item, escape) {
				return `<div>${escape(item.text)}</div>`;
			}
		}
	});
}

export function updateLabel() {
	if (!valueDisplay) return;

	if (isMulti) {
		const checked = [...options].filter((o) => o.classList.contains("checked"));
		if (checked.length === 0) {
			valueDisplay.textContent = "All";
		} else if (checked.length <= MAX_VISIBLE) {
			valueDisplay.textContent = checked.map((o) => o.textContent.trim()).join(", ");
		} else {
			const visible = checked.slice(0, MAX_VISIBLE).map((o) => o.textContent.trim()).join(", ");
			valueDisplay.textContent = `${visible} +${checked.length - MAX_VISIBLE}`;
		}
	} else {
		const selected = select.querySelector(".custom-select__option.selected");
		if (selected) valueDisplay.textContent = selected.textContent.trim();
	}
}

export function syncHiddenInputs() {
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
