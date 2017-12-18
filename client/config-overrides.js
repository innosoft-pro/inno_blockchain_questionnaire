module.exports = function override(config, env) {
    // Add bem-loader in Babel scope
    const babelLoader = config.module.rules[1].oneOf[1];
    const combinedWithBem = {
        test: babelLoader.test,
        include: babelLoader.include,
        use: [
            {
                loader: require.resolve('webpack-bem-loader'),
                options: {
                    techs: ['js', 'css']
                }
            }, {
                loader: babelLoader.loader,
                options: Object.assign({}, babelLoader.options, {
                    presets: [
                        [
                            'env', {
                                "targets": {
                                    "browsers": ["last 2 versions", "safari >= 7"]
                                }
                            }
                        ],
                        'react',
                        'stage-1'
                    ],
                    plugins: [
                        'transform-object-rest-spread',
                        [
                            "transform-runtime", {
                                "polyfill": false,
                                "regenerator": true
                            }
                        ]
                    ]
                })
            }
        ]
    };

    config.module.rules[1].oneOf[1] = combinedWithBem;

    return config;
}