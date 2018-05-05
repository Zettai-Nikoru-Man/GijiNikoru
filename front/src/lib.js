import settings from "./content.settings.js";
import log from "loglevel";
import pify from "pify";
import waitFor from "wait-for-element/lib/wait-by-observer.js";
import parse from "date-fns/esm/parse/index.js";
import isAfter from "date-fns/esm/isAfter/index.js";
import isValid from "date-fns/esm/isValid/index.js";
import format from "date-fns/esm/format/index.js";
import addYears from "date-fns/esm/addYears/index.js";
import ms from "ms";

/**
 * @param {string} selector
 * @param {Node} [root=document]
 * @returns {?Node}
 */
export const $ = (selector, root = document) => root.querySelector(selector);

/**
 * @param {string} selector
 * @param {Node} [root=document]
 * @returns {NodeList}
 */
export const $$ = (selector, root = document) => root.querySelectorAll(selector);

/**
 * 要素が存在するか判定する
 * @param {string} selector - 要素のCSSセレクターの文字列
 * @param {Element} [root] - ルートとなる要素
 * @returns {boolean} - 存在すればtrueそうでなければfalse
 */
export function exists(selector, root) {
	return $(selector, root) !== null;
}

// コメントのスタイルを返却する
function getCommentStyle(nikorare) {

	if (nikorare >= 1 && nikorare < 3) {
		// 黒太文字
		return {
			fontWeight: "bold",
		};
	}

	if (nikorare >= 3 && nikorare < 10) {
		// オレンジ太文字
		return {
			fontWeight: "bold",
			color: "orange",
		};
	}

	if (nikorare >= 10) {
		// 赤太文字
		return {
			fontWeight: "bold",
			color: "red",
		};
	}

	throw Error("スタイルの設定に失敗しました。ニコる情報が不正です。");
}

// ログレベルを設定したloglevelをexportする
log.setLevel(settings.logLevel);
export { log };

// イベントを無効化する
export function killEvent(event) {
	event.preventDefault();
	event.stopPropagation();
}

// 合計ニコられ数表示を更新する
export async function setVideoTotalNikoru(inHTML5PlayerPage, myNimj) {
	let videoTotalNikoru = 0;
	for (let commentNikoru in myNimj) {
		videoTotalNikoru += myNimj[commentNikoru];
	}
	const videoTotalNikoru_commaSeparated = videoTotalNikoru.toLocaleString("ja-JP");

	// 合計ニコられ数表示枠がまだ存在しない場合は追加する
	if (!exists("#nikoruKun_total")) {
		const target = inHTML5PlayerPage
			? ".CommentCountMeta-counter"
			: ".videoStatsComment";
		const targetElement = await waitFor(target, ms("1min"));
		targetElement.insertAdjacentHTML(
			"beforeend",
			`<span style="margin-left: 5px;">/<img id="nikoruKun_total" src="${settings.nikoruImage_tate}"><span id="videoTotalNikorare"></span></span>`
		);
	}

	// 表示中の合計ニコられ数を更新する
	$("#videoTotalNikorare").textContent = videoTotalNikoru_commaSeparated;
}

// get nicoru data of current video from GijiNikoru server
export async function getNimj(mid) {
	const response = await fetch(`http://${settings.API_HOST}/nicoru/${mid}`);
	return response.json();
}

export function isHereHTML5PlayerPage() {
	const inHTML5PlayerPage = exists("#js-app");
	log.info(inHTML5PlayerPage ? "HTML5版プレイヤーページです" : "Flash版プレイヤーページです");
	return inHTML5PlayerPage;
}

/**
 * HTML要素のstyle属性を上書きする
 * @param {Element} element - 対象の要素
 * @param {Object} css - プロパティがキャメライズされたCSSライクなオブジェクト
 */
function addStyle(element, css = {}) {
	Object.entries(css).forEach(([prop, value]) => {
		element.style[prop] = value
	});
}

// 行を受け取り、スタイルを設定する
export function setRowStyle(row, inHTML5PlayerPage, originalNimj, nikorizumiCIDList) {
	const cid = getCommentId(row, inHTML5PlayerPage);
	const nikorare = getRealNikorare(cid, originalNimj, nikorizumiCIDList);

	// ニコられが無ければ終了
	if (nikorare === undefined || nikorare === 0) {
		return true; // as continue.
	}

	const style = getCommentStyle(nikorare);

	const targetElement = inHTML5PlayerPage
		? $("[data-name=content] .CommentPanelDataGrid-cell", row)
		: $(".r0", row);

	addStyle(targetElement, style);
}

/**
 * @param {Element} row - 行要素のDOM
 * @returns {Object} - Proxyのhandlerとなるオブジェクト
 */
const tooltipStyleSetterCreater = row => ({
	set: (obj, prop, value) => {
		// プロパティごとに行要素の属性を更新する
		if (prop === "disabled") {
			// booleanはstringに暗黙に変換されるので、明示的に書いてわかりやすくしておく。
			row.dataset.gijinikoruDisabled = value ? "true" : "false";
		} else if (prop === "content") {
			row.dataset.gijinikoruCount = value;
		}
		// 既定の動作
		return Reflect.set(obj, prop, value);
	},
});

/**
 * 行要素のツールチップに関する情報を返す。
 * Proxyなので、値が変更されると行要素の属性も更新される。
 * @param {Element} row - 行要素のDOM
 * @returns {Proxy} - 行要素の状態を表すプロキシ
 */
export function getTooltipStyle(row) {
	return new Proxy({
		disabled: row.dataset.gijinikoruDisabled === "true",
		content: row.dataset.gijinikoruCount,
	}, tooltipStyleSetterCreater(row));
}

// コメント行DOMからコメ番を取得する
export function getCommentId(row, inHTML5PlayerPage) {
	return inHTML5PlayerPage ? $("[data-name=no] .CommentPanelDataGrid-cell", row).textContent : $(".r3", row).textContent;
}

/**
 * コメント行DOMが処理可能であるかを判定する
 * @param row コメント行DOM
 * @param inHTML5PlayerPage HTML5ページか
 * @returns {boolean} 処理可能である場合、 true。そうでなければ、false。
 */
export function rowIsProcessable(row, inHTML5PlayerPage) {
	const commentIdCell = inHTML5PlayerPage ? "[data-name=no] .CommentPanelDataGrid-cell" : ".r3";
	return exists(commentIdCell, row);
}

/**
 * コメント行DOMから書込時刻を取得する
 *
 * 2017/12/16 現在、niconico では、一年以内のコメントの書込時刻については、年の情報が記載されず、"mm/dd hh:mm" の形式で表示される。
 * 一年より前のコメントの書込時刻については、"yyyy/mm/dd" の形式で表示される。
 * これを利用し、"yyyy/mm/dd" 形式に統一して返却する。
 * 解釈に失敗した場合、表示値をそのまま返却する。
 */
export function getCommentedAt(row, inHTML5PlayerPage) {
	const value = inHTML5PlayerPage ? $("[data-name=date] .CommentPanelDataGrid-cell", row).textContent : $(".r2", row).textContent;
	const now = new Date();
	let date = parse(
		value,
		"MM/DD hh:mm",
		now
	);
	if (isAfter(date, now)) {
		date = addYears(date, -1);
	}
	if (isValid(date)) {
		return format(date, "YYYY/MM/DD", now);
	}
	return value;
}

// コメント行DOMから再生時間を取得する
export function getCommentedPoint(row, inHTML5PlayerPage) {
	return inHTML5PlayerPage ? $("[data-name=vpos] .CommentPanelDataGrid-cell", row).textContent : $(".r1", row).textContent;
}

// コメントの現在ニコられを取得する。サーバーを参照するのではなく、このページでニコられていれば、取得時点の数に1を足すだけ。
export function getRealNikorare(cid, originalNimj, nikorizumiCIDList) {
	const originalNikorare = originalNimj[cid] || 0;
	const realNikorare = nikorizumiCIDList.includes(cid) ? originalNikorare + 1 : originalNikorare;

	// 3桁までに制限する
	return Math.min(realNikorare, settings.maxDisplayNikorare);
}

const storage = chrome.storage.sync || chrome.storage.local; // ストレージ参照
const promisifiedStorage = pify(storage, { errorFirst: false });
export { promisifiedStorage as storage };


/**
 * 数をピクセル表示にする
 * @param {number} num - 数値
 * @returns {string} - px表示の文字列
 */
export const px = num => `${num}px`;

/**
 * 複数のオブジェクトを融合する
 * 引数のオブジェクトは変更されない
 * @param {...Object} obj - 融合されるオブジェクト
 * @returns {Object} - 融合されたオブジェクト
 */
export const merge = (...obj) => Object.assign({}, ...obj);

