import settings from "./content.settings.js";
import waitFor from "wait-for-element/lib/wait-by-observer.js";
import ms from "ms";
import Tooltip from "./single-tooltip.js";
import {
	$,
	$$,
	exists,
	log,
	killEvent,
	setVideoTotalNikoru,
	getNimj,
	getRealNikorare,
	isHereHTML5PlayerPage,
	setRowStyle,
	getTooltipStyle,
	getCommentId,
	rowIsProcessable,
	storage
} from "./lib.js";

const GN = {};
let nikorizumiCIDList = []; // ニコり済みコメ番リスト
let nikorichuCIDList = []; // （範囲ニコる用）ニコり中コメ番リスト
let nikorichuAllCIDList = []; // （範囲ニコる用）ニコり中に収集した全てのコメ番のリスト
let nikorichuRowList = []; // （範囲ニコる用）ニコり中行DOMリスト
let nikorichu = false; // （範囲ニコる用）ニコり中か
let mid = null; // 動画番号
let myNimj = null; // NIJ
let originalNimj = null; // 初期NIJ
let gridCanvasDOM = null; // グリッドカンバスDOM
let optionValues = null; // オプション
let canvasTicket = null; // グリッドカンバスDOM監視処理チケット
let inHTML5PlayerPage = false; // HTML5版プレイヤーページか
let debugTooltipIsSet = false; // デバッグ用ツールチップセットフラグ
let tooltip = null;
let observer = null;

// 初期化処理
GN.init = async function (movieId) {
	log.info("初期化中…");
	inHTML5PlayerPage = isHereHTML5PlayerPage(); // HTML5版プレイヤーであるかを判定・記録する

	// 初期化済みであれば何もしない
	if (hasInitiated(movieId)) {
		log.info("このページでは既に初期化済です。初期化を行いませんでした。");
		return;
	}
	log.debug("初期化を開始します。");
	await prepare(movieId); // 各種情報の初期化
	getNimj(mid) // NIMJを取得する
		.then(onGotNimj);
};

// インスタンス初期化処理
async function prepare(movieId) {
	mid = movieId; // 動画IDのセット
	myNimj = null; // 古いニコられ情報を消去
	originalNimj = null;

	// ユーザID をストレージに保存する
	const userId = $("#siteHeaderNotification").getAttribute("data-nico-userid");
	log.info(`userId -> ${userId}`);
	if (userId != null) {
		storage.set({"userId": userId});
	}

	// カンバス監視を停止
	if (canvasTicket != null) {
		clearInterval(canvasTicket);
	}
	gridCanvasDOM = null; // カンバスDOMキャッシュを消去
	nikorizumiCIDList = []; // ニコり済みコメ番リストを初期化
	optionValues = await loadOptions(); // オプションをロード

	// コメント再読み込みボタンの押下時にNIMJを再取得する
	const target = inHTML5PlayerPage ? ".ReloadButton" : ".refresh.on";
	waitFor(target, ms("1min"))
		.then(targetElement => {
			targetElement.removeEventListener("click", onRefreshButtonClick);
			targetElement.addEventListener("click", onRefreshButtonClick);
		});

	// すでにあるツールチップを削除
	if (tooltip !== null) {
		tooltip.remove();
	}
	// ツールチップを初期化
	tooltip = new Tooltip({
		content: row => getTooltipStyle(row).content,
		open: (row, tooltip) => {
			// 行DOMの属性をツールチップに反映する
			tooltip.dataset.disabled = getTooltipStyle(row).disabled ? "true" : "false";
		},
		margin: 52,
		classes: ["gijinikoru_nikoruTooltip"],
	});

	// CSS変数を設定
	document.body.style.setProperty(
		"--gijinikoru-nikorukun-tate",
		`url(${settings.nikoruImage_tate})`
	);
	document.body.style.setProperty(
		"--gijinikoru-background",
		`url(${settings.nikoruBackground})`
	);
}

// 更新ボタン押下イベントハンドラ
const onRefreshButtonClick = () => {
	getNimj(mid)
		.then(refreshNimj);
};

// NIMJを更新する
function refreshNimj(nimj) {
	myNimj = nimj; // 取得したNIMJを保存する
	setVideoTotalNikoru(inHTML5PlayerPage, myNimj); // 合計ニコられ数表示を更新する
}

// NIMJ取得イベントハンドラ
async function onGotNimj(nimj) {
	log.debug("ニコる情報を取得しました。", nimj);
	myNimj = nimj; // 取得したNIMJを保存する

	// 初期NIMJを複製して保存する
	if (originalNimj == null) {
		originalNimj = Object.assign({}, nimj);
	}
	setVideoTotalNikoru(inHTML5PlayerPage, myNimj); // 合計ニコられ数表示を更新する

	log.debug("コメントリスト表示待ち中…");
	const target = inHTML5PlayerPage ? ".___table___3Fnci" : ".player-tab-content-item.comment .grid-canvas";
	const element = await waitFor(target, ms("1min"));
	log.debug("コメントリストが表示されました。");
	const gridCanvas = gridCanvasDOM = element;

	if (observer != null) {
		// 画面更新なしで別動画に遷移した場合の監視の多重実行を防ぐための制御
		observer.disconnect();
	}

	// コメント枠内部の監視方法を定義する
	observer = new MutationObserver(function (mutations) {
		mutations.forEach(function (mutation) {
			const target = inHTML5PlayerPage
				? $$("[role=row]:not(.nikoru)", mutation.target)
				: mutation.addedNodes;
			canvasObserver(target);
		});
	});
	let config = {childList: true};
	observer.observe(gridCanvasDOM, config); // コメント枠内部の監視を開始する

	addRangeNicoru(gridCanvasDOM);

	// 監視前に追加された行を処理する
	const rowDOM = inHTML5PlayerPage
		? $$("[role=row]", gridCanvas)
		: $$(":scope > .slick-row", gridCanvas);
	canvasObserver(rowDOM);
}

// DOM変更時処理
function canvasObserver(rows) {
	log.info("コメントリスト処理を開始します。");

	if (rows.length === 0) {
		log.info("処理対象コメントが見つかりませんでした。");
		return;
	}

	// ツールチップとニコる処理を付与する
	rows.forEach(row => {
		// 行が対象外であれば、処理をしない
		if (!rowIsProcessable(row, inHTML5PlayerPage)) {
			return;
		}

		setRowStyle(row, inHTML5PlayerPage, originalNimj, nikorizumiCIDList);
		const commentId = getCommentId(row, inHTML5PlayerPage);
		const isNikorared = nikorizumiCIDList.includes(commentId);
		const rowTooltipStyle = getTooltipStyle(row);
		rowTooltipStyle.content = getRealNikorare(commentId, originalNimj, nikorizumiCIDList);

		// ニコられていたらニコるくんを灰色にする
		if (isNikorared) {
			rowTooltipStyle.disabled = true;
		}
		tooltip.registerElement(row);

		// デバッグモード時、デバッグ用にツールチップを消えないようにする
		if (settings.debug && !debugTooltipIsSet) {
			$(".gijinikoru_nikoruTooltip")
				.style.setProperty("display", "block", "important");
			debugTooltipIsSet = true;
		}

		// ニコられていなければニコるイベントハンドラを付加する
		if (isNikorared === false) {
			row.addEventListener("dblclick", execNikoru); // ニコるイベントハンドラを付加する

			row.addEventListener("dragstart", function(e) {
				log.info("start", e);
				// evt.dataTransfer.setData('Text', evt.target.id);
			});
		}
	});
}

function addRangeNicoru(gridCanvasDOM) {
	gridCanvasDOM.addEventListener("mousedown", (e) => {
		nikorichuCIDList = [];
		nikorichuAllCIDList = [];
		nikorichuRowList = [];
		if (addRowForRangeNicoru(e) === true) {
			nikorichu = true;
		}
	});
	gridCanvasDOM.addEventListener("mousemove", (e) => {
		if (!nikorichu) return;
		addRowForRangeNicoru(e);
	});
	gridCanvasDOM.addEventListener("mouseup", (e) => {
		if (!nikorichu) return;
		addRowForRangeNicoru(e);
		if (nikorichuAllCIDList.length < 2) return; // if user did not select multi rows
		for (let i = 0, len = nikorichuCIDList.length; i < len; i++) {
			execNikoruImpl(nikorichuRowList[i], nikorichuCIDList[i]);
		}
		nikorichu = false;
		nikorichuCIDList = [];
		nikorichuAllCIDList = [];
		nikorichuRowList = [];
	});
}

function addRowForRangeNicoru(e) {
	const row = getRowFromTarget(e);
	if (!row) return;
	const commentId = getCommentId(row, inHTML5PlayerPage);
	if (nikorichuCIDList.includes(commentId)) return;
	nikorichuAllCIDList.push(row); // record also nikorizumi CID to recognize if user selected multi rows
	if (nikorizumiCIDList.includes(commentId)) return;
	nikorichuCIDList.push(commentId);
	nikorichuRowList.push(row);
	return true;
}

function getRowFromTarget(e) {
	const clickedElement = e.target;
	const shouldProcess = inHTML5PlayerPage
		? exists(".CommentPanelDataGrid-cell", clickedElement.parentElement)
		: (clickedElement.classList.contains("slick-cell") && clickedElement.classList.contains("r0"));
	if (shouldProcess === false) return;
	return inHTML5PlayerPage
		? clickedElement.closest("[role=row]")
		: clickedElement.parentElement;
}

function execNikoruImpl(row, commentId) {
	if (nikorizumiCIDList.includes(commentId)) return log.info("ニコり済コメントです。"); // ニコり済みの場合は終了
	nikorizumiCIDList.push(commentId); // ニコり済みコメ番リストに追加する
	const rowTooltipStyle = getTooltipStyle(row);

	// ニコるくんを灰色にする
	rowTooltipStyle.disabled = true;
	tooltip.update(row);

	setTimeout(function () {
		setRowStyle(row, inHTML5PlayerPage, originalNimj, nikorizumiCIDList); // 今回のニコりを加味してスタイルを更新する
		// ニコられた数を更新
		rowTooltipStyle.content = getRealNikorare(commentId, originalNimj, nikorizumiCIDList);
		tooltip.update(row);
	}, ms("0.5s"));

	// 送信する
	log.debug("ニコる情報を送信中…", {movieId: mid, commentId: commentId});
	fetch(settings.POST_URL + mid, {
		headers: {
			"Accept": "application/json",
			"Content-Type": "application/json"
		},
		method: "PUT",
		body: JSON.stringify({
			cid: commentId
		}),
	}).then(() => log.debug("ニコる情報の送信に成功しました。"));
}

// ニコる実行
function execNikoru(e) {
	log.info("ニコる処理を開始します。");
	const row = getRowFromTarget(e);
	if (!row) return;

	// ダブルクリック時にシークしない設定の場合、シークを防止する
	if (optionValues.seekByDoubleClick === false) {
		killEvent(e);
	}

	const commentId = getCommentId(row, inHTML5PlayerPage); // コメントIDを取得する
	execNikoruImpl(row, commentId);
}

// 初期化済みかを判定する
function hasInitiated(_mid) {
	return mid === _mid;
}

// オプションを取得する
function loadOptions() {

	// ストレージに格納されているオプションを取得する
	return storage.get({
		seekByDoubleClick: false,  // ダブルクリック時にシークする（デフォルト値：false）
		stopScrollByMouseOver: true  // マウスオーバーでスクロールを停止する（デフォルト値：true）
	});
}

export default GN;
