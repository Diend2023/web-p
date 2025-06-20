// web/vue.config.js
const path = require('path')

module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        pathRewrite: {
          '^/': ''
        }
      }
    }
  },
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    }
  }
}

module.exports = {
  configureWebpack: {
    resolve: {
      alias: {
        '@': resolve('src'),
      },
    },
  },
};

// module.exports = {
//   devServer: {
//     proxy: {
//       '/api': {
//         target: 'http://127.0.0.1:5000',
//         changeOrigin: true,
//         pathRewrite: { '^/api': '' },
//         onProxyReq: function (proxyReq, req, res) {
//           console.log('Proxying request:', req.url);
//         }
//       },
//     },
//   },
// };
