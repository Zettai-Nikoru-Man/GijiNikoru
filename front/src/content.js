import GN from "./gn.js";

// Listen for messages
chrome.runtime.onMessage.addListener(function (msg) {
	GN.init(msg.movieId);
});
