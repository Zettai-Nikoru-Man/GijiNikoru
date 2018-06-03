import log from "loglevel";

const settings = {
	// APIホスト名
	API_HOST: "localhost",

	// ログレベル指定
	logLevel: log.levels.INFO,

	// 最大表示ニコられ数
	maxDisplayNikorare: 999,

	// 縦ニコるくんURL
	nikoruImage_tate: chrome.runtime.getURL("images/nikoru_tate.png"),

	// 背景画像
	nikoruBackground: chrome.runtime.getURL("images/background.svg"),

	// デバッグフラグ
	debug: false
};

// ニコる情報送信先
settings.POST_URL = `http://${settings.API_HOST}/nicoru/`;

// ニコられたページ
settings.NICORARETA_PAGE_URL = `http://${settings.API_HOST}/page/nicorareta/`;

export default settings;
