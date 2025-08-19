module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Find and remove fork-ts-checker-webpack-plugin
      webpackConfig.plugins = webpackConfig.plugins.filter(
        plugin => plugin.constructor.name !== 'ForkTsCheckerWebpackPlugin'
      );
      return webpackConfig;
    },
  },
};