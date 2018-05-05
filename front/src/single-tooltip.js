import { px, merge } from "./lib.js";

/**
 * SingleTooltipのオプション
 * @typedef {Object} SingleTooltipOption
 * @prop {string[]} classes - ツールチップのクラス属性
 * @prop {number} margin - ツールチップと対象要素の余白
 * @prop {tooltipContentFunction} content - ツールチップのtextContentを返す関数
 * @prop {tooltipOpenCallback} open - ツールチップが表示される前に実行されるコールバック関数
 */

/**
 * ツールチップのtextContentを返す関数
 * @callback tooltipContentFunction
 * @param {Element} target - ツールチップ対象の要素
 * @returns {string} - ツールチップのtextContentとなる文字列
 */

/**
 * ツールチップが表示される前に実行されるコールバック関数
 * @callback tooltipOpenCallback
 * @param {Element} target - ツールチップ対象の要素
 * @param {Element} tooltip - ツールチップ要素自身
 */

const defaultOption = {
	classes: [],
	margin: 0,
	content: () => "",
	open: () => {},
};

/**
 * 単一のツールチップをページで共有する。
 * 今のところ左側表示のみ対応。
 */
export default class SingleTooltip {
	/**
	 * @param {SingleTooltipOption} option
	 */
	constructor (option = {}) {
		// デフォルトオプションと融合
		this.option = merge(defaultOption, option);

		const dom = document.createElement("div");
		// クラスを設定する
		dom.classList.add(...option.classes);
		dom.setAttribute("role", "tooltip");

		document.body.appendChild(dom);
		this.tooltipDOM = dom;
	}
	/**
	 * 要素をツールチップ対象に設定する
	 * @param {Element} element
	 */
	registerElement (element) {
		element.addEventListener("mouseenter", this._onEntered.bind(this));
		element.addEventListener("mouseleave", this._hideTooltip.bind(this));
	}
	/**
	 * 状態を更新する
	 * @param {Element} element
	 */
	update(element) {
		// カーソルの下にあったらツールチップを再計算して表示
		if (element.matches(":hover")) {
			this._showTooltip(element);
		}
	}
	/**
	 * ツールチップをドキュメントから削除する
	 */
	remove() {
		this.tooltipDOM.remove();
	}
	/**
	 * mouseenterイベントハンドラ
	 * @param {Event} e
	 */
	_onEntered(e) {
		this._showTooltip(e.target);
	}
	/**
	 * mouseleaveイベントハンドラ
	 */
	_onLeaved() {
		this._hideTooltip();
	}
	/**
	 * ツールチップを表示する
	 * @param {Element} target
	 */
	_showTooltip (target) {
		const tooltip = this.tooltipDOM;

		// イベントハンドラを実行
		this.option.open(target, tooltip);

		// ターゲットとツールチップの位置・大きさを取得し、
		// ツールチップの位置を設定する。
		const rect = target.getBoundingClientRect();

		// ツールチップを対象要素の左上にあわせる
		const top = rect.top;
		const left = rect.left - this.option.margin;

		tooltip.style.top = px(top);
		tooltip.style.left = px(left);

		// 内容を更新し表示
		tooltip.textContent = this.option.content(target);
		tooltip.setAttribute("aria-hidden", "false");
		tooltip.hidden = false;
	}
	/**
	 * ツールチップを非表示にする
	 */
	_hideTooltip () {
		this.tooltipDOM.setAttribute("aria-hidden", "true");
		this.tooltipDOM.hidden = true;
	}
}
