const config = {
  development: {
    API_BASE_URL: '',
  },
  production: {
    API_BASE_URL: 'http://127.0.0.1:5000',
  }
}

export default config[process.env.NODE_ENV] || config.development