describe('Test Essential Features', () => {
    beforeEach(() => {
        cy.visit('/');
        cy.frameLoaded();
        cy.iframe().find("[id=\"industry-data\"]", {
            timeout: 10 * 1000
        }).should("contain", "Industry Data");
    })
    it("verify the headers and subheaders", () => {
        cy.iframe().find("[id=\"stock-dashboard-s-p500\"]").should("contain", "Stock Dashboard | S&P500");
        cy.iframe().find("[id=\"industry-data\"]").should("contain", "Industry Data");
    })
    it('verify filtering by sector is working', () => {
        cy.iframe().find("input[aria-label=\"Selected S&P 500 Index. Filter by Sector\"]").click()
        cy.iframe().find("li[role=\"option\"]").contains("Health Care").click()


        //need to wait until table elements are not changed
        //Now we can check the tickers in table to verify filtering is applied or not
        const expectedCompanyName = "Johnson & Johnson"
        cy.iframe().find("[data-testid^=\"glide-cell-1-\"]", {
            timeout: 10 * 1000
        }).should("contain.text", expectedCompanyName);
    })

})

describe("Industry data table Content", () => {
    beforeEach(() => {
        cy.visit('/');
        cy.frameLoaded();
        cy.iframe().find("[id=\"industry-data\"]", {
            timeout: 10 * 1000
        }).should("contain", "Industry Data");
    })
    it("verify the industry data table headers", () => {
        const expectedColumnHeaders = ['Symbol', 'Name', 'Weight (%)', 'Current Price ($)', 'Price to Earning(PE) Ratio', 'Market Cap ($)', 'Dividend Yield (%)', 'Net Income Latest Qtr (Bil $)', 'YOY Qtr Profit Growth (%)', 'Sales Latest Qtr (Bil $)', 'Debt to Equity (%)']
        cy.iframe().find("[role=\"columnheader\"]").then($els => {
            const texts = [...$els].map(el => el.innerText)  // extract texts
            expect(JSON.stringify(texts)).to.eq(JSON.stringify(expectedColumnHeaders));
        })
    })

    it("verify the stocks name and symbol", () => {
        //assuming that expected tickers/names always remain in top 10 by portfolio wt.

        const expectedTickers = ['MSFT', 'AAPL', 'NVDA', 'AMZN', 'META'];
        cy.iframe().find("[data-testid^=\"glide-cell-0-\"]").then($els => {
            const texts = [...$els].map(el => el.innerText)  // extract texts
            expectedTickers.forEach(ticker => {
                expect(texts).to.includes(ticker);
            })
        })

        const expectedNames = ['Microsoft Corporation', 'Apple Inc.', 'NVIDIA Corporation', 'Amazon.com, Inc.', 'Meta Platforms, Inc.'];
        cy.iframe().find("[data-testid^=\"glide-cell-1-\"]").then($els => {
            const texts = [...$els].map(el => el.innerText)  // extract texts
            expectedNames.forEach(name => {
                expect(texts).to.includes(name);
            })
        })
    })

})