"use strict";

import settings from "./content.settings.js";
import {
	$,
	log,
	storage
} from "./lib.js";

async function onNicoraretaButtonClick() {
	const userData = await getUserData(); // オプションをロード
	const userId = userData.userId;
	log.info(userId);
	if (userId == null) {
		$("#error_nicorareta").innerText = "ユーザIDの取得に失敗しました。ログイン状態で動画ページにアクセスしてから、もう一度試してください。";
		return;
	}
	window.open(`${settings.NICORARETA_PAGE_URL}${userId}`, "_blank");
}

// オプションを取得する
function getUserData() {
	// ストレージに格納されているオプションを取得する
	return storage.get({userId: null});
}

$("#view_nicorareta_button").addEventListener("click", onNicoraretaButtonClick);
