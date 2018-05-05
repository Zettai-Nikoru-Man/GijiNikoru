"use strict";

// オプション定義
const OPTIONS = [
	{
		id: "seekByDoubleClick",
		defaultValue: false,
		type: "checkbox"
	}
//	{
//		id: "stopScrollByMouseOver",
//		defaultValue: true,
//		type: "checkbox"
//	}
];

// WebExtensionsとの互換性確保
const storage = chrome.storage.sync || chrome.storage.local;

const $ = document.querySelector.bind(document)

// 入力された設定値をストレージに保存する
const saveOptions = () => {

	// 入力値を取得する
	const inputOptionValues = {};
	for (let opt of OPTIONS) {
		inputOptionValues[opt.id] = getChecked(opt.id);
	}

	saveOnStorage(inputOptionValues);
};

// デフォルト値を復元する
const restoreDefault = () => {
	for (let opt of OPTIONS) {
		setChecked(opt.id, opt.defaultValue);
	}
};

// ストレージへの値の保存を実行する
const saveOnStorage = (values) => {

	// ストレージ保存処理
	storage.set(values, function() {

		// 更新メッセージを表示
		$("#status").removeAttribute("hidden");

		// 更新メッセージを消す
		setTimeout(function() {
			$("#status").setAttribute("hidden", "");
		}, 1000);
	});
}

// ストレージから設定をロードする
const loadOptions = () => {

	// デフォルト値
	const defaultOptionValues = {};
	for (let opt of OPTIONS) {
		defaultOptionValues[opt.id] = opt.defaultValue;
	}

	// ストレージ値ロード処理
	storage.get(defaultOptionValues, function(items) {

		// ロード
		for (let opt of OPTIONS) {
			setChecked(opt.id, items[opt.id]);
		}
	});
};

// チェック状態を取得する
const getChecked = (id) => {
	return $(`#${id}`).checked;
};

// チェック状態を設定する
const setChecked = (id, value) => {
	$(`#${id}`).checked = value;
};

// 読み込み完了時
window.addEventListener("load", () => {
	// 設定ロード
	loadOptions();

	// イベントハンドラ登録
	$("#save").addEventListener("click", saveOptions);
	$("#default").addEventListener("click", restoreDefault);
});

