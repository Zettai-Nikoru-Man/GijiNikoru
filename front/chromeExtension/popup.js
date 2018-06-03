(function () {
'use strict';

var commonjsGlobal = typeof window !== 'undefined' ? window : typeof global !== 'undefined' ? global : typeof self !== 'undefined' ? self : {};





function createCommonjsModule(fn, module) {
	return module = { exports: {} }, fn(module, module.exports), module.exports;
}

var loglevel = createCommonjsModule(function (module) {
/*
* loglevel - https://github.com/pimterry/loglevel
*
* Copyright (c) 2013 Tim Perry
* Licensed under the MIT license.
*/
(function (root, definition) {
    "use strict";
    if (typeof undefined === 'function' && undefined.amd) {
        undefined(definition);
    } else if ('object' === 'object' && module.exports) {
        module.exports = definition();
    } else {
        root.log = definition();
    }
}(commonjsGlobal, function () {
    "use strict";

    // Slightly dubious tricks to cut down minimized file size
    var noop = function() {};
    var undefinedType = "undefined";

    var logMethods = [
        "trace",
        "debug",
        "info",
        "warn",
        "error"
    ];

    // Cross-browser bind equivalent that works at least back to IE6
    function bindMethod(obj, methodName) {
        var method = obj[methodName];
        if (typeof method.bind === 'function') {
            return method.bind(obj);
        } else {
            try {
                return Function.prototype.bind.call(method, obj);
            } catch (e) {
                // Missing bind shim or IE8 + Modernizr, fallback to wrapping
                return function() {
                    return Function.prototype.apply.apply(method, [obj, arguments]);
                };
            }
        }
    }

    // Build the best logging method possible for this env
    // Wherever possible we want to bind, not wrap, to preserve stack traces
    function realMethod(methodName) {
        if (methodName === 'debug') {
            methodName = 'log';
        }

        if (typeof console === undefinedType) {
            return false; // No method possible, for now - fixed later by enableLoggingWhenConsoleArrives
        } else if (console[methodName] !== undefined) {
            return bindMethod(console, methodName);
        } else if (console.log !== undefined) {
            return bindMethod(console, 'log');
        } else {
            return noop;
        }
    }

    // These private functions always need `this` to be set properly

    function replaceLoggingMethods(level, loggerName) {
        /*jshint validthis:true */
        for (var i = 0; i < logMethods.length; i++) {
            var methodName = logMethods[i];
            this[methodName] = (i < level) ?
                noop :
                this.methodFactory(methodName, level, loggerName);
        }

        // Define log.log as an alias for log.debug
        this.log = this.debug;
    }

    // In old IE versions, the console isn't present until you first open it.
    // We build realMethod() replacements here that regenerate logging methods
    function enableLoggingWhenConsoleArrives(methodName, level, loggerName) {
        return function () {
            if (typeof console !== undefinedType) {
                replaceLoggingMethods.call(this, level, loggerName);
                this[methodName].apply(this, arguments);
            }
        };
    }

    // By default, we use closely bound real methods wherever possible, and
    // otherwise we wait for a console to appear, and then try again.
    function defaultMethodFactory(methodName, level, loggerName) {
        /*jshint validthis:true */
        return realMethod(methodName) ||
               enableLoggingWhenConsoleArrives.apply(this, arguments);
    }

    function Logger(name, defaultLevel, factory) {
      var self = this;
      var currentLevel;
      var storageKey = "loglevel";
      if (name) {
        storageKey += ":" + name;
      }

      function persistLevelIfPossible(levelNum) {
          var levelName = (logMethods[levelNum] || 'silent').toUpperCase();

          if (typeof window === undefinedType) return;

          // Use localStorage if available
          try {
              window.localStorage[storageKey] = levelName;
              return;
          } catch (ignore) {}

          // Use session cookie as fallback
          try {
              window.document.cookie =
                encodeURIComponent(storageKey) + "=" + levelName + ";";
          } catch (ignore) {}
      }

      function getPersistedLevel() {
          var storedLevel;

          if (typeof window === undefinedType) return;

          try {
              storedLevel = window.localStorage[storageKey];
          } catch (ignore) {}

          // Fallback to cookies if local storage gives us nothing
          if (typeof storedLevel === undefinedType) {
              try {
                  var cookie = window.document.cookie;
                  var location = cookie.indexOf(
                      encodeURIComponent(storageKey) + "=");
                  if (location) {
                      storedLevel = /^([^;]+)/.exec(cookie.slice(location))[1];
                  }
              } catch (ignore) {}
          }

          // If the stored level is not valid, treat it as if nothing was stored.
          if (self.levels[storedLevel] === undefined) {
              storedLevel = undefined;
          }

          return storedLevel;
      }

      /*
       *
       * Public logger API - see https://github.com/pimterry/loglevel for details
       *
       */

      self.levels = { "TRACE": 0, "DEBUG": 1, "INFO": 2, "WARN": 3,
          "ERROR": 4, "SILENT": 5};

      self.methodFactory = factory || defaultMethodFactory;

      self.getLevel = function () {
          return currentLevel;
      };

      self.setLevel = function (level, persist) {
          if (typeof level === "string" && self.levels[level.toUpperCase()] !== undefined) {
              level = self.levels[level.toUpperCase()];
          }
          if (typeof level === "number" && level >= 0 && level <= self.levels.SILENT) {
              currentLevel = level;
              if (persist !== false) {  // defaults to true
                  persistLevelIfPossible(level);
              }
              replaceLoggingMethods.call(self, level, name);
              if (typeof console === undefinedType && level < self.levels.SILENT) {
                  return "No console available for logging";
              }
          } else {
              throw "log.setLevel() called with invalid level: " + level;
          }
      };

      self.setDefaultLevel = function (level) {
          if (!getPersistedLevel()) {
              self.setLevel(level, false);
          }
      };

      self.enableAll = function(persist) {
          self.setLevel(self.levels.TRACE, persist);
      };

      self.disableAll = function(persist) {
          self.setLevel(self.levels.SILENT, persist);
      };

      // Initialize with the right level
      var initialLevel = getPersistedLevel();
      if (initialLevel == null) {
          initialLevel = defaultLevel == null ? "WARN" : defaultLevel;
      }
      self.setLevel(initialLevel, false);
    }

    /*
     *
     * Top-level API
     *
     */

    var defaultLogger = new Logger();

    var _loggersByName = {};
    defaultLogger.getLogger = function getLogger(name) {
        if (typeof name !== "string" || name === "") {
          throw new TypeError("You must supply a name when creating a logger.");
        }

        var logger = _loggersByName[name];
        if (!logger) {
          logger = _loggersByName[name] = new Logger(
            name, defaultLogger.getLevel(), defaultLogger.methodFactory);
        }
        return logger;
    };

    // Grab the current global log variable in case of overwrite
    var _log = (typeof window !== undefinedType) ? window.log : undefined;
    defaultLogger.noConflict = function() {
        if (typeof window !== undefinedType &&
               window.log === defaultLogger) {
            window.log = _log;
        }

        return defaultLogger;
    };

    return defaultLogger;
}));
});

const settings = {
	// APIホスト名
	API_HOST: "localhost",

	// ログレベル指定
	logLevel: loglevel.levels.INFO,

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

var pify = createCommonjsModule(function (module) {
'use strict';

const processFn = (fn, opts) => function () {
	const P = opts.promiseModule;
	const args = new Array(arguments.length);

	for (let i = 0; i < arguments.length; i++) {
		args[i] = arguments[i];
	}

	return new P((resolve, reject) => {
		if (opts.errorFirst) {
			args.push(function (err, result) {
				if (opts.multiArgs) {
					const results = new Array(arguments.length - 1);

					for (let i = 1; i < arguments.length; i++) {
						results[i - 1] = arguments[i];
					}

					if (err) {
						results.unshift(err);
						reject(results);
					} else {
						resolve(results);
					}
				} else if (err) {
					reject(err);
				} else {
					resolve(result);
				}
			});
		} else {
			args.push(function (result) {
				if (opts.multiArgs) {
					const results = new Array(arguments.length - 1);

					for (let i = 0; i < arguments.length; i++) {
						results[i] = arguments[i];
					}

					resolve(results);
				} else {
					resolve(result);
				}
			});
		}

		fn.apply(this, args);
	});
};

module.exports = (obj, opts) => {
	opts = Object.assign({
		exclude: [/.+(Sync|Stream)$/],
		errorFirst: true,
		promiseModule: Promise
	}, opts);

	const filter = key => {
		const match = pattern => typeof pattern === 'string' ? key === pattern : pattern.test(key);
		return opts.include ? opts.include.some(match) : !opts.exclude.some(match);
	};

	let ret;
	if (typeof obj === 'function') {
		ret = function () {
			if (opts.excludeMain) {
				return obj.apply(this, arguments);
			}

			return processFn(obj, opts).apply(this, arguments);
		};
	} else {
		ret = Object.create(Object.getPrototypeOf(obj));
	}

	for (const key in obj) { // eslint-disable-line guard-for-in
		const x = obj[key];
		ret[key] = typeof x === 'function' && filter(key) ? processFn(x, opts) : x;
	}

	return ret;
};
});

// LICENSE : MIT
"use strict";

/**
 * Helpers.
 */

/**
 * @param {string} selector
 * @param {Node} [root=document]
 * @returns {?Node}
 */
const $ = (selector, root = document) => root.querySelector(selector);

/**
 * @param {string} selector
 * @param {Node} [root=document]
 * @returns {NodeList}
 */


/**
 * 要素が存在するか判定する
 * @param {string} selector - 要素のCSSセレクターの文字列
 * @param {Element} [root] - ルートとなる要素
 * @returns {boolean} - 存在すればtrueそうでなければfalse
 */


// ログレベルを設定したloglevelをexportする
loglevel.setLevel(settings.logLevel);
// イベントを無効化する


// 合計ニコられ数表示を更新する


// get nicoru data of current video from GijiNikoru server




// 行を受け取り、スタイルを設定する


/**
 * 行要素のツールチップに関する情報を返す。
 * Proxyなので、値が変更されると行要素の属性も更新される。
 * @param {Element} row - 行要素のDOM
 * @returns {Proxy} - 行要素の状態を表すプロキシ
 */


// コメント行DOMからコメ番を取得する


/**
 * コメント行DOMが処理可能であるかを判定する
 * @param row コメント行DOM
 * @param inHTML5PlayerPage HTML5ページか
 * @returns {boolean} 処理可能である場合、 true。そうでなければ、false。
 */


/**
 * コメント行DOMから書込時刻を取得する
 *
 * 2017/12/16 現在、niconico では、一年以内のコメントの書込時刻については、年の情報が記載されず、"mm/dd hh:mm" の形式で表示される。
 * 一年より前のコメントの書込時刻については、"yyyy/mm/dd" の形式で表示される。
 * これを利用し、"yyyy/mm/dd" 形式に統一して返却する。
 * 解釈に失敗した場合、表示値をそのまま返却する。
 */


// コメント行DOMから再生時間を取得する


// コメントの現在ニコられを取得する。サーバーを参照するのではなく、このページでニコられていれば、取得時点の数に1を足すだけ。


const storage = chrome.storage.sync || chrome.storage.local; // ストレージ参照
const promisifiedStorage = pify(storage, { errorFirst: false });
/**
 * 数をピクセル表示にする
 * @param {number} num - 数値
 * @returns {string} - px表示の文字列
 */


/**
 * 複数のオブジェクトを融合する
 * 引数のオブジェクトは変更されない
 * @param {...Object} obj - 融合されるオブジェクト
 * @returns {Object} - 融合されたオブジェクト
 */

"use strict";

async function onNicoraretaButtonClick() {
	const userData = await getUserData(); // オプションをロード
	const userId = userData.userId;
	loglevel.info(userId);
	if (userId == null) {
		$("#error_nicorareta").innerText = "ユーザIDの取得に失敗しました。ログイン状態で動画ページにアクセスしてから、もう一度試してください。";
		return;
	}
	window.open(`${settings.NICORARETA_PAGE_URL}${userId}`, "_blank");
}

// オプションを取得する
function getUserData() {
	// ストレージに格納されているオプションを取得する
	return promisifiedStorage.get({userId: null});
}

$("#view_nicorareta_button").addEventListener("click", onNicoraretaButtonClick);

}());
//# sourceMappingURL=popup.js.map
