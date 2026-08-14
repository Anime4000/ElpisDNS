/*
	ΕΛΠΙΣ DNS - selector engine

	Everything on the page is built from dns.json.
	Nothing here needs to change when a resolver is added,
	so contributors only ever touch the JSON.
*/

const DEFAULTS = {
	dohPath: "/dns-query",
	dotPort: 853
};

// Order matters: each selector narrows the ones after it.
const GROUPS = [
	{ key: "filter",   field: "filter",   container: "filter-options",   label: "Filter"    },
	{ key: "region",   field: "region",   container: "region-options",   label: "Region"    },
	{ key: "provider", field: "provider", container: "provider-options", label: "Provider"  },
	{ key: "network",  field: "network",  container: "network-options",  label: "Network"   },
	{ key: "feature",  field: "feature",  container: "feature-options",  label: "Feature"   },
	{ key: "kind",     field: "kind",     container: "kind-options",     label: "Transport" }
];

const db = {
	regions: [],
	filters: [],
	defaults: { ...DEFAULTS },
	resolvers: []
};

const state = {
	filter: null,
	region: null,
	provider: null,
	network: null,
	feature: null,
	kind: null
};

let current = null;

/* ---------- loading ---------- */

async function loadDatabase(){

	try{

		const response = await fetch("dns.json", { cache: "no-cache" });

		if(!response.ok){
			throw new Error(`dns.json responded ${response.status}`);
		}

		adopt(await response.json());

	} catch(err){

		console.error("Unable to load dns.json", err);

		const endpoint = document.getElementById("endpoint");

		if(endpoint){
			endpoint.innerText =
				"dns.json could not be loaded. Serve this folder over HTTP, not file://";
		}

		return;
	}

	readHash();

	refresh();
}

// Accepts the v2 object or the old bare array, so a stale
// fork or a cached copy never breaks the page.
function adopt(raw){

	const resolvers = Array.isArray(raw) ? raw : (raw.resolvers || []);

	db.resolvers = resolvers.filter(isUsable);

	db.defaults = {
		...DEFAULTS,
		...(Array.isArray(raw) ? {} : raw.defaults)
	};

	db.regions = (Array.isArray(raw) ? [] : raw.regions) ||
		[...new Set(db.resolvers.map(r => r.region))].map(code => ({
			code,
			label: code
		}));

	db.filters = (Array.isArray(raw) ? [] : raw.filters) ||
		[...new Set(db.resolvers.map(r => r.filter))].map(code => ({
			code,
			label: code
		}));

	// The first filter and region declared in dns.json are what a
	// first-time visitor lands on.
	state.filter = db.filters[0] ? db.filters[0].code : null;
	state.region = db.regions[0] ? db.regions[0].code : null;
	state.kind = "DoH";
}

function isUsable(entry){

	const ok = entry &&
		entry.region &&
		entry.provider &&
		entry.filter &&
		entry.network &&
		entry.feature &&
		Array.isArray(entry.kind) && entry.kind.length &&
		Array.isArray(entry.servers) && entry.servers.length;

	if(!ok){
		console.warn("Skipping malformed resolver entry", entry);
	}

	return ok;
}

/* ---------- labels ---------- */

function labelFor(group, value){

	if(group === "region"){

		const hit = db.regions.find(r => r.code === value);

		return hit ? hit.label : value;
	}

	if(group === "filter"){

		const hit = db.filters.find(f => f.code === value);

		return hit ? hit.label : value;
	}

	return value;
}

function describeFilter(code){

	const hit = db.filters.find(f => f.code === code);

	return hit && hit.description ? hit.description : "";
}

/* ---------- matching ---------- */

function valuesOf(list, field){

	return [...new Set(
		list.flatMap(item =>
			Array.isArray(item[field]) ? item[field] : [item[field]]
		)
	)];
}

function matches(entry, group){

	const wanted = state[group.key];

	if(wanted === null || wanted === undefined) return true;

	const value = entry[group.field];

	return Array.isArray(value)
		? value.includes(wanted)
		: value === wanted;
}

// Walk the groups in order, repairing any selection that the
// previous choices just invalidated.
function reconcile(){

	let data = db.resolvers;

	GROUPS.forEach(group => {

		const options = valuesOf(data, group.field);

		if(!options.includes(state[group.key])){
			state[group.key] = options[0] ?? null;
		}

		data = data.filter(entry => matches(entry, group));
	});

	return data;
}

// Which selections a group is judged against.
//
// Only the groups *above* it, never the ones below. Check a group
// against everything and the table locks: picking Perfect Internet
// strikes out every region Perfect Internet does not serve, and the
// visitor can never change country again. Choices below simply repair
// themselves in reconcile().
//
// Filter and Region are the two structural axes and are peers, so
// they check each other.
function scopeFor(group){

	const index = GROUPS.indexOf(group);

	if(group.key === "filter"){
		return GROUPS.filter(other => other.key === "region");
	}

	return GROUPS.slice(0, index);
}

// A value is offered when at least one resolver satisfies it
// together with the selections above it.
function enabledValues(group){

	const scope = scopeFor(group);

	const others = db.resolvers.filter(entry =>
		scope.every(other => matches(entry, other))
	);

	return valuesOf(others, group.field);
}

/* ---------- rendering ---------- */

// Buttons follow the order declared in dns.json where there is one,
// so contributors control how the row reads.
function orderedValues(group){

	const values = valuesOf(db.resolvers, group.field);

	const declared =
		group.key === "region" ? db.regions.map(r => r.code) :
		group.key === "filter" ? db.filters.map(f => f.code) :
		null;

	if(!declared) return values;

	return [
		...declared.filter(code => values.includes(code)),
		...values.filter(code => !declared.includes(code))
	];
}

function renderGroup(group){

	const container = document.getElementById(group.container);

	if(!container) return;

	const all = orderedValues(group);

	const enabled = enabledValues(group);

	container.innerHTML = "";

	all.forEach(value => {

		const btn = document.createElement("button");

		btn.type = "button";
		btn.className = "option-btn";
		btn.innerText = labelFor(group.key, value);
		btn.dataset.group = group.key;
		btn.dataset.value = value;

		const usable = enabled.includes(value);

		btn.disabled = !usable;

		btn.classList.toggle("disabled-option", !usable);
		btn.classList.toggle("active", state[group.key] === value);

		btn.setAttribute("aria-pressed", String(state[group.key] === value));

		if(usable){

			btn.onclick = () => {

				state[group.key] = value;

				refresh();
			};
		}
		else{
			btn.title = "Not available with the rest of your selection";
		}

		container.appendChild(btn);
	});
}

function buildEndpoint(entry, kind){

	const host = entry.servers[
		Math.floor(Math.random() * entry.servers.length)
	];

	if(kind === "DoT"){

		const port = entry.dotPort || db.defaults.dotPort;

		return port === 853
			? `tls://${host}`
			: `tls://${host}:${port}`;
	}

	const path = entry.dohPath || db.defaults.dohPath;

	return kind === "DoQ"
		? `quic://${host}`
		: `https://${host}${path}`;
}

function setText(id, value){

	const node = document.getElementById(id);

	if(node) node.innerText = value;
}

function setHTML(id, value){

	const node = document.getElementById(id);

	if(node) node.innerHTML = value;
}

function escapeHTML(value){

	return String(value).replace(/[&<>"']/g, ch => ({
		"&": "&amp;",
		"<": "&lt;",
		">": "&gt;",
		'"': "&quot;",
		"'": "&#39;"
	}[ch]));
}

// The setup page reads this back, so the guide can show the
// endpoint the visitor actually picked instead of an example.
function remember(endpoint){

	try{
		localStorage.setItem("elpis-endpoint", endpoint);
		localStorage.setItem("elpis-host", hostnameOf(endpoint));
	}
	catch(err){
		/* private browsing, nothing to remember */
	}
}

function renderResult(entry){

	current = entry;

	if(!entry){

		setText("endpoint", "No resolver matches that combination.");
		setHTML("server-list", "");
		setHTML("summary", "");

		return;
	}

	const endpoint = buildEndpoint(entry, state.kind);

	setText("endpoint", endpoint);

	remember(endpoint);

	setHTML("server-list", entry.servers.map(server => `
		<span class="server-badge">${escapeHTML(server)}</span>
	`).join(""));

	const chips = GROUPS.map(group => `
		<span class="summary-chip">
			<span class="summary-key">${group.label}</span>
			<b>${escapeHTML(labelFor(group.key, state[group.key]))}</b>
		</span>
	`).join("");

	const notes = entry.notes
		? `<div class="summary-note">${escapeHTML(entry.notes)}</div>`
		: "";

	const filterNote = describeFilter(state.filter)
		? `<div class="summary-note">${escapeHTML(describeFilter(state.filter))}</div>`
		: "";

	const credit = entry.maintainer
		? `<div class="summary-meta">Kept running by ${
			entry.homepage
				? `<a href="${escapeHTML(entry.homepage)}" target="_blank" rel="noopener">${escapeHTML(entry.maintainer)}</a>`
				: escapeHTML(entry.maintainer)
		} &bull; ${entry.servers.length} host${entry.servers.length === 1 ? "" : "s"} in rotation</div>`
		: "";

	setHTML("summary", `<div class="summary-chips">${chips}</div>${notes}${filterNote}${credit}`);
}

function renderActions(){

	const rsc = document.getElementById("download-rsc-btn");
	const host = document.getElementById("copy-host-btn");

	if(rsc) rsc.style.display = state.kind === "DoH" ? "inline-flex" : "none";
	if(host) host.style.display = state.kind === "DoT" ? "inline-flex" : "none";
}

function refresh(){

	const data = reconcile();

	GROUPS.forEach(renderGroup);

	renderResult(data[0] || null);

	renderActions();

	writeHash();
}

/* ---------- shareable links ---------- */

function writeHash(){

	if(!current) return;

	const parts = [
		current.id || `${state.region}-${state.provider}`.toLowerCase().replace(/\s+/g, "-"),
		state.kind
	];

	const hash = `#${parts.map(encodeURIComponent).join("/")}`;

	if(location.hash !== hash){
		history.replaceState(null, "", hash);
	}
}

function readHash(){

	const raw = location.hash.replace(/^#/, "");

	if(!raw) return;

	const [id, kind] = raw.split("/").map(decodeURIComponent);

	const entry = db.resolvers.find(r => r.id === id);

	if(!entry) return;

	state.filter = entry.filter;
	state.region = entry.region;
	state.provider = entry.provider;
	state.network = entry.network;
	state.feature = entry.feature;

	state.kind = kind && entry.kind.includes(kind)
		? kind
		: entry.kind[0];
}

/* ---------- clipboard ---------- */

async function copy(text, button, done){

	const original = button.innerHTML;

	try{

		await navigator.clipboard.writeText(text);

		button.innerHTML = `<i class="bi bi-check2"></i> ${done}`;

	} catch(err){

		console.error(err);

		button.innerHTML = `<i class="bi bi-x-lg"></i> Blocked`;
	}

	setTimeout(() => {
		button.innerHTML = original;
	}, 1400);
}

function hostnameOf(endpoint){

	if(endpoint.includes("://")){

		try{
			return new URL(endpoint).hostname;
		}
		catch(err){
			return endpoint.replace(/^[a-z]+:\/\//, "").split("/")[0];
		}
	}

	return endpoint;
}

function wire(id, handler){

	const node = document.getElementById(id);

	if(node) node.onclick = handler;
}

wire("copy-btn", event => {

	copy(
		document.getElementById("endpoint").innerText,
		event.currentTarget,
		"Copied"
	);
});

wire("copy-host-btn", event => {

	copy(
		hostnameOf(document.getElementById("endpoint").innerText),
		event.currentTarget,
		"Copied"
	);
});

wire("shuffle-btn", () => {

	if(!current) return;

	const endpoint = buildEndpoint(current, state.kind);

	setText("endpoint", endpoint);

	remember(endpoint);
});

window.addEventListener("hashchange", () => {

	readHash();

	refresh();
});

// Exposed so app-mikrotik.js can ask what is on the table.
window.ElpisDNS = {
	get entry(){ return current; },
	get state(){ return { ...state }; },
	get database(){ return db; }
};

loadDatabase();
