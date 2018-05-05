import npm from 'rollup-plugin-node-resolve';
import cjs from 'rollup-plugin-commonjs';

export default [
    {
        input: "src/content.js",
        output: {
            file: "chromeExtension/content.js",
            format: "iife",
            sourcemap: true,
        },
        plugins: [
            npm(),
            cjs(),
        ],
    },
    {
        input: "src/popup.js",
        output: {
            file: "chromeExtension/popup.js",
            format: "iife",
            sourcemap: true,
        },
        plugins: [
            npm(),
            cjs(),
        ],
    },
];
