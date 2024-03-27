const HtmlWebPackPlugin = require("html-webpack-plugin");
var path = require('path');
var BundleTracker = require('webpack-bundle-tracker');
module.exports = {
    entry: './src/scripts/index.tsx',
    module: {
        rules: [
            {
                enforce: 'pre',
                test: /\.js$/,
                loader: 'source-map-loader',
                exclude: [/node_modules/]
            },
            {
                test: /\.tsx?$/,
                exclude: /node_modules/,
                loader: 'ts-loader',
                options: {
                    transpileOnly: true
                }
            }
        ]
    },
    watch: true,
    resolve: {
        extensions: ['.tsx', '.ts', '.js']
    },
    output: {
        path: path.resolve('../kore_investment/static/webpack_bundles2/'),
        filename: "[name]-[hash].js"
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        {
            apply: (compiler) => {
              compiler.hooks.done.tap('DonePlugin', (stats) => {
                console.log('Compile is done !')
                setTimeout(() => {
                  process.exit(0)
                })
              });
            }
         }
    ]

};