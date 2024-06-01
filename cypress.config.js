const {defineConfig} = require("cypress");

module.exports = defineConfig({
    "chromeWebSecurity": false,
    e2e: {
        viewportWidth: 1920,
        viewportHeight: 1080,
        baseUrl: 'https://stock-dashboard-sp500.streamlit.app',
        setupNodeEvents(on, config) {
            // implement node event listeners here
        },
    },
});
