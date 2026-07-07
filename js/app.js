let dnsDatabase = [];

async function loadDatabase(){

	const response = await fetch("dns.json");

	dnsDatabase = await response.json();

	refresh();
}

loadDatabase();

const state = {
	filter: "NSFW",
	region: "MY",
	provider: null,
	network: null,
	feature: null,
	kind: "DoH"
};

function randomServer(list){
	return list[Math.floor(Math.random() * list.length)];
}

function uniqueValues(data, field){

	return [...new Set(
		data.flatMap(item => {

			if(Array.isArray(item[field])){
				return item[field];
			}

			return [item[field]];
		})
	)];
}

function filterData(){

	return dnsDatabase.filter(item => {

		if(state.filter && item.filter !== state.filter)
			return false;

		if(state.region && item.region !== state.region)
			return false;

		return true;
	});
}

function renderStatic(group){

	const buttons = document.querySelectorAll(`[data-group="${group}"]`);

	buttons.forEach(btn => {

		const value = btn.dataset.value;

		const valid = dnsDatabase.some(item => {

			if(group === "filter"){
				return item.filter === value &&
					item.region === state.region;
			}

			if(group === "region"){
				return item.region === value &&
					item.filter === state.filter;
			}

			return true;
		});

		btn.disabled = !valid;

		btn.classList.toggle("disabled-option", !valid);

		btn.classList.toggle(
			"active",
			state[group] === value
		);
	});
}

function renderDynamic(field, containerId, dataset){

	const container = document.getElementById(containerId);

	const allValues = uniqueValues(dnsDatabase, field);

	const validValues = uniqueValues(dataset, field);

	if(!validValues.includes(state[field])){
		state[field] = validValues[0] || null;
	}

	container.innerHTML = "";

	allValues.forEach(value => {

		const btn = document.createElement("button");

		btn.className = "option-btn";
		btn.innerText = value;

		const valid = validValues.includes(value);

		btn.disabled = !valid;

		if(!valid){
			btn.classList.add("disabled-option");
		}

		if(state[field] === value){
			btn.classList.add("active");
		}

		btn.onclick = () => {

			if(!valid) return;

			state[field] = value;

			refresh();
		};

		container.appendChild(btn);
	});
}

function refresh(){

	renderStatic("filter");
	renderStatic("region");

	// Provider
	let data = filterData();

	renderDynamic(
		"provider",
		"provider-options",
		data
	);

	data = data.filter(item =>
		item.provider === state.provider
	);

	// Network
	renderDynamic(
		"network",
		"network-options",
		data
	);

	data = data.filter(item =>
		item.network === state.network
	);

	// Feature
	renderDynamic(
		"feature",
		"feature-options",
		data
	);

	data = data.filter(item =>
		item.feature === state.feature
	);

	// Kind
	renderDynamic(
		"kind",
		"kind-options",
		data
	);

	data = data.filter(item =>
		item.kind.includes(state.kind)
	);

	const result = data[0];

	if(result){

		const domain = randomServer(result.servers);

		let endpoint = "";

		if(state.kind === "DoH"){
			endpoint =
				`https://${domain}/dns-query`;
		}
		else{
			endpoint =
				`tls://${domain}`;
		}

		document.getElementById("endpoint")
			.innerText = endpoint;

		document.getElementById("server-list")
			.innerHTML = result.servers.map(server => `
				<span class="server-badge">
					${server}
				</span>
			`).join("");

		document.getElementById("summary")
			.innerHTML = `
				Type: <b>${state.filter}</b> |
				Region: <b>${state.region}</b> |
				Provider: <b>${state.provider}</b> |
				Network: <b>${state.network}</b> |
				Feature: <b>${state.feature}</b> |
				Kind: <b>${state.kind}</b>
			`;
	}

	const rscButton =
		document.getElementById("download-rsc-btn");

	const hostButton =
		document.getElementById("copy-host-btn");

	if(state.kind === "DoH"){
		rscButton.style.display = "inline-block";
		hostButton.style.display = "none";
	}
	else{
		rscButton.style.display = "none";
		hostButton.style.display = "inline-block";
	}
}

document.querySelectorAll("[data-group]").forEach(btn => {

	btn.onclick = () => {

		if(btn.disabled) return;

		const group = btn.dataset.group;

		state[group] = btn.dataset.value;

		// structural reset
		if(group === "filter" || group === "region"){

			state.provider = null;
			state.network = null;
			state.feature = null;
			state.kind = "DoH";
		}

		refresh();
	};
});

refresh();

document.getElementById("copy-btn")
	.onclick = async () => {

	const text =
		document.getElementById("endpoint")
			.innerText;

	try{

		await navigator.clipboard.writeText(text);

		const btn =
			document.getElementById("copy-btn");

		btn.innerText = "Copied";

		setTimeout(() => {
			btn.innerText = "Copy";
		}, 1200);

	} catch(err){

		alert("Clipboard copy failed");
	}
};

document.getElementById("copy-host-btn")
    .onclick = async () => {

    const endpoint =
        document.getElementById("endpoint")
            .innerText;

    let hostname = endpoint;

    try{

        if(endpoint.startsWith("tls://")){

            hostname =
                endpoint.replace("tls://", "");

        } else {

            hostname =
                new URL(endpoint).hostname;
        }

        await navigator.clipboard
            .writeText(hostname);

        const btn =
            document.getElementById("copy-host-btn");

        btn.innerHTML =
            '<i class="bi bi-check"></i> Copied';

        setTimeout(() => {

            btn.innerHTML =
                '<i class="bi bi-phone"></i> Copy Hostname';

        }, 1200);

    } catch(err){

        alert("Clipboard copy failed");
    }
};