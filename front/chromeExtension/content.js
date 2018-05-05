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
	logLevel: loglevel.levels.SILENT,

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
settings.NICORARETA_PAGE_URL = `http://${settings.API_HOST}/viewNikorareta.php`;

// LICENSE : MIT
"use strict";
/**
 * @param {string} selector the css selector
 * @param {number} timeout the timeout is millisecond
 * @returns {Promise}
 */
function waitForElement(selector, timeout) {
    var _resolve, _reject;
    var promise = new Promise(function (resolve, reject) {
        _resolve = resolve;
        _reject = reject;
    });


    var observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            for (var i = 0; i < mutation.addedNodes.length; i++) {
                var addedNode = mutation.addedNodes[i];
                if (typeof addedNode.matches === "function" && addedNode.matches(selector)) {
                    _resolve(addedNode);
                    observer.disconnect();
                    clearTimeout(timerId);
                }
            }
        });
    });
    // first time check
    var element = document.querySelector(selector);
    if (element != null) {
        _resolve(element);
        return promise;
    }
    var timeoutOption = timeout || 2000;// 2s
    // start
    observer.observe(document.body, {
        childList: true, subtree: true
    });
    // timeout
    var timerId = setTimeout(function () {
        _reject(new Error("Not found element match the selector:" + selector));
        observer.disconnect();
    }, timeoutOption);

    return promise;
}
var waitByObserver = waitForElement;

/**
 * Helpers.
 */

var s = 1000;
var m = s * 60;
var h = m * 60;
var d = h * 24;
var y = d * 365.25;

/**
 * Parse or format the given `val`.
 *
 * Options:
 *
 *  - `long` verbose formatting [false]
 *
 * @param {String|Number} val
 * @param {Object} [options]
 * @throws {Error} throw an error if val is not a non-empty string or a number
 * @return {String|Number}
 * @api public
 */

var ms = function(val, options) {
  options = options || {};
  var type = typeof val;
  if (type === 'string' && val.length > 0) {
    return parse(val);
  } else if (type === 'number' && isNaN(val) === false) {
    return options.long ? fmtLong(val) : fmtShort(val);
  }
  throw new Error(
    'val is not a non-empty string or a valid number. val=' +
      JSON.stringify(val)
  );
};

/**
 * Parse the given `str` and return milliseconds.
 *
 * @param {String} str
 * @return {Number}
 * @api private
 */

function parse(str) {
  str = String(str);
  if (str.length > 100) {
    return;
  }
  var match = /^((?:\d+)?\.?\d+) *(milliseconds?|msecs?|ms|seconds?|secs?|s|minutes?|mins?|m|hours?|hrs?|h|days?|d|years?|yrs?|y)?$/i.exec(
    str
  );
  if (!match) {
    return;
  }
  var n = parseFloat(match[1]);
  var type = (match[2] || 'ms').toLowerCase();
  switch (type) {
    case 'years':
    case 'year':
    case 'yrs':
    case 'yr':
    case 'y':
      return n * y;
    case 'days':
    case 'day':
    case 'd':
      return n * d;
    case 'hours':
    case 'hour':
    case 'hrs':
    case 'hr':
    case 'h':
      return n * h;
    case 'minutes':
    case 'minute':
    case 'mins':
    case 'min':
    case 'm':
      return n * m;
    case 'seconds':
    case 'second':
    case 'secs':
    case 'sec':
    case 's':
      return n * s;
    case 'milliseconds':
    case 'millisecond':
    case 'msecs':
    case 'msec':
    case 'ms':
      return n;
    default:
      return undefined;
  }
}

/**
 * Short format for `ms`.
 *
 * @param {Number} ms
 * @return {String}
 * @api private
 */

function fmtShort(ms) {
  if (ms >= d) {
    return Math.round(ms / d) + 'd';
  }
  if (ms >= h) {
    return Math.round(ms / h) + 'h';
  }
  if (ms >= m) {
    return Math.round(ms / m) + 'm';
  }
  if (ms >= s) {
    return Math.round(ms / s) + 's';
  }
  return ms + 'ms';
}

/**
 * Long format for `ms`.
 *
 * @param {Number} ms
 * @return {String}
 * @api private
 */

function fmtLong(ms) {
  return plural(ms, d, 'day') ||
    plural(ms, h, 'hour') ||
    plural(ms, m, 'minute') ||
    plural(ms, s, 'second') ||
    ms + ' ms';
}

/**
 * Pluralization helper.
 */

function plural(ms, n, name) {
  if (ms < n) {
    return;
  }
  if (ms < n * 1.5) {
    return Math.floor(ms / n) + ' ' + name;
  }
  return Math.ceil(ms / n) + ' ' + name + 's';
}

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

var tokensToBeShortedPattern = /MMMM|MM|DD|dddd/g;

function buildShortLongFormat (format) {
  return format.replace(tokensToBeShortedPattern, function (token) {
    return token.slice(1)
  })
}

/**
 * @name buildFormatLongFn
 * @category Locale Helpers
 * @summary Build `formatLong` property for locale used by `format`, `formatRelative` and `parse` functions.
 *
 * @description
 * Build `formatLong` property for locale used by `format`, `formatRelative` and `parse` functions.
 * Returns a function which takes one of the following tokens as the argument:
 * `'LTS'`, `'LT'`, `'L'`, `'LL'`, `'LLL'`, `'l'`, `'ll'`, `'lll'`, `'llll'`
 * and returns a long format string written as `format` token strings.
 * See [format]{@link https://date-fns.org/docs/format}
 *
 * `'l'`, `'ll'`, `'lll'` and `'llll'` formats are built automatically
 * by shortening some of the tokens from corresponding unshortened formats
 * (e.g., if `LL` is `'MMMM DD YYYY'` then `ll` will be `MMM D YYYY`)
 *
 * @param {Object} obj - the object with long formats written as `format` token strings
 * @param {String} obj.LT - time format: hours and minutes
 * @param {String} obj.LTS - time format: hours, minutes and seconds
 * @param {String} obj.L - short date format: numeric day, month and year
 * @param {String} [obj.l] - short date format: numeric day, month and year (shortened)
 * @param {String} obj.LL - long date format: day, month in words, and year
 * @param {String} [obj.ll] - long date format: day, month in words, and year (shortened)
 * @param {String} obj.LLL - long date and time format
 * @param {String} [obj.lll] - long date and time format (shortened)
 * @param {String} obj.LLLL - long date, time and weekday format
 * @param {String} [obj.llll] - long date, time and weekday format (shortened)
 * @returns {Function} `formatLong` property of the locale
 *
 * @example
 * // For `en-US` locale:
 * locale.formatLong = buildFormatLongFn({
 *   LT: 'h:mm aa',
 *   LTS: 'h:mm:ss aa',
 *   L: 'MM/DD/YYYY',
 *   LL: 'MMMM D YYYY',
 *   LLL: 'MMMM D YYYY h:mm aa',
 *   LLLL: 'dddd, MMMM D YYYY h:mm aa'
 * })
 */
function buildFormatLongFn (obj) {
  var formatLongLocale = {
    LTS: obj.LTS,
    LT: obj.LT,
    L: obj.L,
    LL: obj.LL,
    LLL: obj.LLL,
    LLLL: obj.LLLL,
    l: obj.l || buildShortLongFormat(obj.L),
    ll: obj.ll || buildShortLongFormat(obj.LL),
    lll: obj.lll || buildShortLongFormat(obj.LLL),
    llll: obj.llll || buildShortLongFormat(obj.LLLL)
  };

  return function (token) {
    return formatLongLocale[token]
  }
}

var formatLong = buildFormatLongFn({
  LT: 'h:mm aa',
  LTS: 'h:mm:ss aa',
  L: 'MM/DD/YYYY',
  LL: 'MMMM D YYYY',
  LLL: 'MMMM D YYYY h:mm aa',
  LLLL: 'dddd, MMMM D YYYY h:mm aa'
});

/**
 * @name buildLocalizeFn
 * @category Locale Helpers
 * @summary Build `localize.weekday`, `localize.month` and `localize.timeOfDay` properties for the locale.
 *
 * @description
 * Build `localize.weekday`, `localize.month` and `localize.timeOfDay` properties for the locale
 * used by `format` function.
 * If no `type` is supplied to the options of the resulting function, `defaultType` will be used (see example).
 *
 * `localize.weekday` function takes the weekday index as argument (0 - Sunday).
 * `localize.month` takes the month index (0 - January).
 * `localize.timeOfDay` takes the hours. Use `indexCallback` to convert them to an array index (see example).
 *
 * @param {Object} values - the object with arrays of values
 * @param {String} defaultType - the default type for the localize function
 * @param {Function} [indexCallback] - the callback which takes the resulting function argument
 *   and converts it into value array index
 * @returns {Function} the resulting function
 *
 * @example
 * var timeOfDayValues = {
 *   uppercase: ['AM', 'PM'],
 *   lowercase: ['am', 'pm'],
 *   long: ['a.m.', 'p.m.']
 * }
 * locale.localize.timeOfDay = buildLocalizeFn(timeOfDayValues, 'long', function (hours) {
 *   // 0 is a.m. array index, 1 is p.m. array index
 *   return (hours / 12) >= 1 ? 1 : 0
 * })
 * locale.localize.timeOfDay(16, {type: 'uppercase'}) //=> 'PM'
 * locale.localize.timeOfDay(5) //=> 'a.m.'
 */

/**
 * @name buildLocalizeArrayFn
 * @category Locale Helpers
 * @summary Build `localize.weekdays`, `localize.months` and `localize.timesOfDay` properties for the locale.
 *
 * @description
 * Build `localize.weekdays`, `localize.months` and `localize.timesOfDay` properties for the locale.
 * If no `type` is supplied to the options of the resulting function, `defaultType` will be used (see example).
 *
 * @param {Object} values - the object with arrays of values
 * @param {String} defaultType - the default type for the localize function
 * @returns {Function} the resulting function
 *
 * @example
 * var weekdayValues = {
 *   narrow: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
 *   short: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
 *   long: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
 * }
 * locale.localize.weekdays = buildLocalizeArrayFn(weekdayValues, 'long')
 * locale.localize.weekdays({type: 'narrow'}) //=> ['Su', 'Mo', ...]
 * locale.localize.weekdays() //=> ['Sunday', 'Monday', ...]
 */

/**
 * @name buildMatchFn
 * @category Locale Helpers
 * @summary Build `match.weekdays`, `match.months` and `match.timesOfDay` properties for the locale.
 *
 * @description
 * Build `match.weekdays`, `match.months` and `match.timesOfDay` properties for the locale used by `parse` function.
 * If no `type` is supplied to the options of the resulting function, `defaultType` will be used (see example).
 * The result of the match function will be passed into corresponding parser function
 * (`match.weekday`, `match.month` or `match.timeOfDay` respectively. See `buildParseFn`).
 *
 * @param {Object} values - the object with RegExps
 * @param {String} defaultType - the default type for the match function
 * @returns {Function} the resulting function
 *
 * @example
 * var matchWeekdaysPatterns = {
 *   narrow: /^(su|mo|tu|we|th|fr|sa)/i,
 *   short: /^(sun|mon|tue|wed|thu|fri|sat)/i,
 *   long: /^(sunday|monday|tuesday|wednesday|thursday|friday|saturday)/i
 * }
 * locale.match.weekdays = buildMatchFn(matchWeekdaysPatterns, 'long')
 * locale.match.weekdays('Sunday', {type: 'narrow'}) //=> ['Su', 'Su', ...]
 * locale.match.weekdays('Sunday') //=> ['Sunday', 'Sunday', ...]
 */

/**
 * @name buildParseFn
 * @category Locale Helpers
 * @summary Build `match.weekday`, `match.month` and `match.timeOfDay` properties for the locale.
 *
 * @description
 * Build `match.weekday`, `match.month` and `match.timeOfDay` properties for the locale used by `parse` function.
 * The argument of the resulting function is the result of the corresponding match function
 * (`match.weekdays`, `match.months` or `match.timesOfDay` respectively. See `buildMatchFn`).
 *
 * @param {Object} values - the object with arrays of RegExps
 * @param {String} defaultType - the default type for the parser function
 * @returns {Function} the resulting function
 *
 * @example
 * var parseWeekdayPatterns = {
 *   any: [/^su/i, /^m/i, /^tu/i, /^w/i, /^th/i, /^f/i, /^sa/i]
 * }
 * locale.match.weekday = buildParseFn(matchWeekdaysPatterns, 'long')
 * var matchResult = locale.match.weekdays('Friday')
 * locale.match.weekday(matchResult) //=> 5
 */

/**
 * @name buildMatchPatternFn
 * @category Locale Helpers
 * @summary Build match function from a single RegExp.
 *
 * @description
 * Build match function from a single RegExp.
 * Usually used for building `match.ordinalNumbers` property of the locale.
 *
 * @param {Object} pattern - the RegExp
 * @returns {Function} the resulting function
 *
 * @example
 * locale.match.ordinalNumbers = buildMatchPatternFn(/^(\d+)(th|st|nd|rd)?/i)
 * locale.match.ordinalNumbers('3rd') //=> ['3rd', '3', 'rd', ...]
 */

/**
 * @name parseDecimal
 * @category Locale Helpers
 * @summary Parses the match result into decimal number.
 *
 * @description
 * Parses the match result into decimal number.
 * Uses the string matched with the first set of parentheses of match RegExp.
 *
 * @param {Array} matchResult - the object returned by matching function
 * @returns {Number} the parsed value
 *
 * @example
 * locale.match = {
 *   ordinalNumbers: (dirtyString) {
 *     return String(dirtyString).match(/^(\d+)(th|st|nd|rd)?/i)
 *   },
 *   ordinalNumber: parseDecimal
 * }
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
const $$ = (selector, root = document) => root.querySelectorAll(selector);

/**
 * 要素が存在するか判定する
 * @param {string} selector - 要素のCSSセレクターの文字列
 * @param {Element} [root] - ルートとなる要素
 * @returns {boolean} - 存在すればtrueそうでなければfalse
 */
function exists(selector, root) {
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
loglevel.setLevel(settings.logLevel);
// イベントを無効化する
function killEvent(event) {
	event.preventDefault();
	event.stopPropagation();
}

// 合計ニコられ数表示を更新する
async function setVideoTotalNikoru(inHTML5PlayerPage, myNimj) {
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
		const targetElement = await waitByObserver(target, ms("1min"));
		targetElement.insertAdjacentHTML(
			"beforeend",
			`<span style="margin-left: 5px;">/<img id="nikoruKun_total" src="${settings.nikoruImage_tate}"><span id="videoTotalNikorare"></span></span>`
		);
	}

	// 表示中の合計ニコられ数を更新する
	$("#videoTotalNikorare").textContent = videoTotalNikoru_commaSeparated;
}

// get nicoru data of current video from GijiNikoru server
async function getNimj(mid) {
	const response = await fetch(`http://${settings.API_HOST}/nicoru/${mid}`);
	return response.json();
}

function isHereHTML5PlayerPage() {
	const inHTML5PlayerPage = exists("#js-app");
	loglevel.info(inHTML5PlayerPage ? "HTML5版プレイヤーページです" : "Flash版プレイヤーページです");
	return inHTML5PlayerPage;
}

/**
 * HTML要素のstyle属性を上書きする
 * @param {Element} element - 対象の要素
 * @param {Object} css - プロパティがキャメライズされたCSSライクなオブジェクト
 */
function addStyle(element, css = {}) {
	Object.entries(css).forEach(([prop, value]) => {
		element.style[prop] = value;
	});
}

// 行を受け取り、スタイルを設定する
function setRowStyle(row, inHTML5PlayerPage, originalNimj, nikorizumiCIDList) {
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
function getTooltipStyle(row) {
	return new Proxy({
		disabled: row.dataset.gijinikoruDisabled === "true",
		content: row.dataset.gijinikoruCount,
	}, tooltipStyleSetterCreater(row));
}

// コメント行DOMからコメ番を取得する
function getCommentId(row, inHTML5PlayerPage) {
	return inHTML5PlayerPage ? $("[data-name=no] .CommentPanelDataGrid-cell", row).textContent : $(".r3", row).textContent;
}

/**
 * コメント行DOMが処理可能であるかを判定する
 * @param row コメント行DOM
 * @param inHTML5PlayerPage HTML5ページか
 * @returns {boolean} 処理可能である場合、 true。そうでなければ、false。
 */
function rowIsProcessable(row, inHTML5PlayerPage) {
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


// コメント行DOMから再生時間を取得する


// コメントの現在ニコられを取得する。サーバーを参照するのではなく、このページでニコられていれば、取得時点の数に1を足すだけ。
function getRealNikorare(cid, originalNimj, nikorizumiCIDList) {
	const originalNikorare = originalNimj[cid] || 0;
	const realNikorare = nikorizumiCIDList.includes(cid) ? originalNikorare + 1 : originalNikorare;

	// 3桁までに制限する
	return Math.min(realNikorare, settings.maxDisplayNikorare);
}

const storage = chrome.storage.sync || chrome.storage.local; // ストレージ参照
const promisifiedStorage = pify(storage, { errorFirst: false });
/**
 * 数をピクセル表示にする
 * @param {number} num - 数値
 * @returns {string} - px表示の文字列
 */
const px = num => `${num}px`;

/**
 * 複数のオブジェクトを融合する
 * 引数のオブジェクトは変更されない
 * @param {...Object} obj - 融合されるオブジェクト
 * @returns {Object} - 融合されたオブジェクト
 */
const merge = (...obj) => Object.assign({}, ...obj);

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
class SingleTooltip {
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

const GN = {};
let nikorizumiCIDList = []; // ニコり済みコメ番リスト
let mid = null; // 動画番号
let myNimj = null; // NIJ
let originalNimj = null; // 初期NIJ
let gridCanvasDOM = null; // グリッドカンバスDOM
let optionValues = null; // オプション
let canvasTicket = null; // グリッドカンバスDOM監視処理チケット
let inHTML5PlayerPage = false; // HTML5版プレイヤーページか
let debugTooltipIsSet = false; // デバッグ用ツールチップセットフラグ
let tooltip = null;

// 初期化処理
GN.init = async function (movieId) {
	loglevel.info("初期化中…");
	inHTML5PlayerPage = isHereHTML5PlayerPage(); // HTML5版プレイヤーであるかを判定・記録する

	// 初期化済みであれば何もしない
	if (hasInitiated(movieId)) {
		loglevel.info("このページでは既に初期化済です。初期化を行いませんでした。");
		return;
	}
	loglevel.debug("初期化を開始します。");
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
	loglevel.info(`userId -> ${userId}`);
	if (userId != null) {
		promisifiedStorage.set({"userId": userId});
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
	waitByObserver(target, ms("1min"))
		.then(targetElement => {
			targetElement.removeEventListener("click", onRefreshButtonClick);
			targetElement.addEventListener("click", onRefreshButtonClick);
		});

	// すでにあるツールチップを削除
	if (tooltip !== null) {
		tooltip.remove();
	}
	// ツールチップを初期化
	tooltip = new SingleTooltip({
		content: row => getTooltipStyle(row).content,
		open: (row, tooltip) => {
			// 行DOMの属性をツールチップに反映する
			tooltip.dataset.disabled = getTooltipStyle(row).disabled ? "true" : "false";
		},
		margin: 52,
		classes: ["nikoruTooltip"],
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

	// if (commentPostObserverIsSet === false) {
	// 	const process = () => {
	//
	// 		/* 取得する */
	// 		var nico = require('playerapp/player/Nicoplayer');
	//
	// 		/* イベントハンドラを設定する */
	// 		nico.onVideoSeeked = function (e) {
	// 			console.log(e);
	// 		};
	// 	};
	//
	// 	location.href = `javascript: (${process})();`;
	//
	// 	commentPostObserverIsSet = true;
	// }
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
	loglevel.debug("ニコる情報を取得しました。", nimj);
	myNimj = nimj; // 取得したNIMJを保存する

	// 初期NIMJを複製して保存する
	if (originalNimj == null) {
		originalNimj = Object.assign({}, nimj);
	}
	setVideoTotalNikoru(inHTML5PlayerPage, myNimj); // 合計ニコられ数表示を更新する

	loglevel.debug("コメントリスト表示待ち中…");
	const target = inHTML5PlayerPage ? ".___table___3Fnci" : ".player-tab-content-item.comment .grid-canvas";
	const element = await waitByObserver(target, ms("1min"));
	loglevel.debug("コメントリストが表示されました。");
	const gridCanvas = gridCanvasDOM = element;

	// コメント枠内部の監視方法を定義する
	const observer = new MutationObserver(function (mutations) {
		mutations.forEach(function (mutation) {
			const target = inHTML5PlayerPage
				? $$("[role=row]:not(.nikoru)", mutation.target)
				: mutation.addedNodes;
			canvasObserver(target);
		});
	});

	let config = {childList: true};
	observer.observe(gridCanvasDOM, config); // コメント枠内部の監視を開始する

	// 監視前に追加された行を処理する
	const rowDOM = inHTML5PlayerPage
		? $$("[role=row]", gridCanvas)
		: $$(":scope > .slick-row", gridCanvas);
	canvasObserver(rowDOM);
}

// コメントマーク処理
const markComment = async (e, comment, commentId, storage) => {

	if (e.ctrlKey) {

		// マーク済みコメントをストレージから取得して処理する
		const items = await storage.get({"markedComment": {}});

		// 動画IDに対応したマーク済みコメント情報を取得する
		let markedComment = items["markedComment"][mid];

		// 動画IDに対応したマーク済みコメントリストが保存されていなければ初期化する
		if (markedComment == null) {
			markedComment = [];
		}

		// 既にマーク済みであれば何もしない
		if (markedComment.includes(commentId)) {
			return;
		}

		markedComment.push(commentId);
		items["markedComment"][mid] = markedComment;

		// ストレージにコメント情報を保存する
		storage.set({"markedComment": items["markedComment"]});

		// TODO: 視覚効果

		// 送信する
		// $.post(`http://flapi.nicovideo.jp/api/getflv/sm26692123`, function(data, status) {
		// 	console.log(300, data);
		// }, "json");
	}
};

// DOM変更時処理
function canvasObserver(rows) {
	loglevel.info("コメントリスト処理を開始します。");

	if (rows.length === 0) {
		loglevel.info("処理対象コメントが見つかりませんでした。");
		return;
	}

	// ツールチップとニコる処理を付与する
	rows.forEach(row => {
		// 行が対象外であれば、処理をしない
		if (!rowIsProcessable(row, inHTML5PlayerPage)) {
			return;
		}

		setRowStyle(row, inHTML5PlayerPage, originalNimj, nikorizumiCIDList);
		const comment = inHTML5PlayerPage
			? $("[data-name=content] .CommentPanelDataGrid-cell", row).textContent
			: $(".r0", row).textContent;
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
			$(".nikoruTooltip")
				.style.setProperty("display", "block", "important");
			debugTooltipIsSet = true;
		}

		// ニコられていなければニコるイベントハンドラを付加する
		if (isNikorared === false) {
			row.addEventListener("dblclick", execNikoru); // ニコるイベントハンドラを付加する

			// コメントマーク用イベントハンドラを付加する
			row.addEventListener("click", (e) => {
				markComment(e, comment, commentId, promisifiedStorage);
			});
		}
	});
}

// ニコる実行
function execNikoru(e) {
	loglevel.info("ニコる処理を開始します。");
	const clickedElement = e.target; // クリックされた要素を取得する
	const shouldProcess = inHTML5PlayerPage
		? exists(".CommentPanelDataGrid-cell", clickedElement.parentElement)
		: (clickedElement.classList.contains("slick-cell") && clickedElement.classList.contains("r0")); // 処理対象かを判定する
	if (shouldProcess === false) return loglevel.info("ニコる処理対象外です。"); // 処理対象でなければ終了する

	// ダブルクリック時にシークしない設定の場合、シークを防止する
	if (optionValues.seekByDoubleClick === false) {
		killEvent(e);
	}

	const row = inHTML5PlayerPage
		? clickedElement.closest("[role=row]")
		: clickedElement.parentElement; // 行DOMを取得する
	const commentId = getCommentId(row, inHTML5PlayerPage); // コメントIDを取得する
	if (nikorizumiCIDList.includes(commentId)) return loglevel.info("ニコり済コメントです。"); // ニコり済みの場合は終了
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
	loglevel.debug("ニコる情報を送信中…", {movieId: mid, commentId: commentId});
	fetch(settings.POST_URL + mid, {
		headers: {
		  "Accept": "application/json",
		  "Content-Type": "application/json"
		},
		method: "PUT",
		body: JSON.stringify({
			cid: commentId
		}),
	}).then(() => loglevel.debug("ニコる情報の送信に成功しました。"));
}

// 初期化済みかを判定する
function hasInitiated(_mid) {
	return mid === _mid;
}

// オプションを取得する
function loadOptions() {

	// ストレージに格納されているオプションを取得する
	return promisifiedStorage.get({
		seekByDoubleClick: false,  // ダブルクリック時にシークする（デフォルト値：false）
		stopScrollByMouseOver: true  // マウスオーバーでスクロールを停止する（デフォルト値：true）
	});
}

// Listen for messages
chrome.runtime.onMessage.addListener(function (msg) {
	GN.init(msg.movieId);
});

}());
//# sourceMappingURL=content.js.map
