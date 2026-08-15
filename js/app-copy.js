/*
	ΕΛΠΙΣ DNS - clipboard

	Shared by every page. Anything carrying data-copy hands its value to
	the clipboard and says so on the button for a moment.

	Lives on its own so the mission page can have working copy buttons
	without dragging in the whole selector engine.
*/

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

document.addEventListener("DOMContentLoaded", () => {

	document.querySelectorAll("[data-copy]").forEach(button => {

		button.onclick = event =>
			copy(button.dataset.copy, event.currentTarget, "Copied");
	});
});
