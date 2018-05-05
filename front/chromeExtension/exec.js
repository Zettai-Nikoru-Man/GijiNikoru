// ページのDOMを受け取り、処理を実行する
const c = () => {
};

const execute = (tab) => {

	// URL判定
	const matched = tab.url.match("http://www.nicovideo.jp/watch/([a-z0-9]+)");

	if (matched === null) {
		// もはやニコニコの動画ページではない
		return;
	}

	// 該当するタブにメッセージを送る
	chrome.tabs.sendMessage(tab.id, {movieId: matched[1]}, c);
};

// タブ更新時
chrome.tabs.onUpdated.addListener(function(tabId, changedInfo, tab) {
	execute(tab);
});

// タブ作成時
chrome.tabs.onCreated.addListener(function(tab) {
	execute(tab);
});
