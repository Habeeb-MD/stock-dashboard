const getContainer = () => {
    return Cypress.config('baseUrl').includes("8501") ? cy.root() : cy.iframe();
}

function waitUntilAppStarts(interval, iteration = 0, maxIteration) {
    if (iteration > maxIteration) {   // set an upper limit to stop infinite retry
        return;
    }

    console.log(iteration, maxIteration);
    cy.wait(interval);

    getContainer().find("[id=\"stock-dashboard-s-p500\"]", {
        timeout: 3 * 60 * 1000,
    }).should("contain", "Stock Dashboard | S&P500");

    getContainer().then(body => console.log(body.text()));
    getContainer().then(body => {
        if (!(body.text().includes("App is starting") || body.text().includes("Background task started")))
            iteration = maxIteration
    });

    cy.reload(true);

    cy.then(() => {
        waitUntilAppStarts(interval, iteration + 1, maxIteration);
    })
}


before(() => {
    cy.visit('/');
    waitUntilAppStarts(10 * 1000, 0, 30);
});


describe('Test Essential Features', () => {
    beforeEach(() => {
        cy.visit('/');
        cy.frameLoaded();
        getContainer().find("[id=\"industry-data\"]", {
            timeout: 10 * 1000
        }).should("contain", "Industry Data");
    })
    it("verify the headers and subheaders", () => {
        getContainer().find("[id=\"stock-dashboard-s-p500\"]").should("contain", "Stock Dashboard | S&P500");
        getContainer().find("[id=\"industry-data\"]").should("contain", "Industry Data");
    })
    it('verify filtering by sector is working', () => {
        getContainer().find("input[aria-label=\"Selected S&P 500 Index. Filter by Sector\"]").click()
        getContainer().find("li[role=\"option\"]").contains("Health Care").click()


        //need to wait until table elements are not changed
        //Now we can check the tickers in table to verify filtering is applied or not
        const expectedCompanyName = "Johnson & Johnson"
        getContainer().find("[data-testid^=\"glide-cell-1-\"]", {
            timeout: 10 * 1000
        }).should("contain.text", expectedCompanyName);
    })

})

describe("Industry data table Content", () => {
    beforeEach(() => {
        cy.visit('/');
        cy.frameLoaded();
        getContainer().find("[id=\"industry-data\"]", {
            timeout: 10 * 1000
        }).should("contain", "Industry Data");
    })
    it("verify the industry data table headers", () => {

        const expectedColumnHeaders = ['Symbol', 'Name', 'Weight (%)', 'Current Price ($)',
            'Price to Earning(PE) Ratio', 'Market Cap ($)', 'Dividend Yield (%)', 'Net Income Latest Qtr (Bil $)',
            'YOY Qtr Profit Growth (%)', 'Sales Latest Qtr (Bil $)', 'Debt to Equity (%)']
        getContainer().find("[role=\"columnheader\"]").then($els => {
            const texts = [...$els].map(el => el.innerText)  // extract texts
            expectedColumnHeaders.forEach(column => expect(texts).contains(column));
        })
    })

    it("verify the stocks name and symbol", () => {
        //assuming that expected tickers/names always remain in top 10 by portfolio wt.

        const expectedTickers = ['MSFT', 'AAPL', 'NVDA', 'AMZN', 'META'];
        getContainer().find("[data-testid^=\"glide-cell-0-\"]").then($els => {
            const texts = [...$els].map(el => el.innerText)  // extract texts
            expectedTickers.forEach(ticker => {
                expect(texts).to.includes(ticker);
            })
        })

        const expectedNames = ['Microsoft Corporation', 'Apple Inc.', 'NVIDIA Corporation', 'Amazon.com, Inc.', 'Meta Platforms, Inc.'];
        getContainer().find("[data-testid^=\"glide-cell-1-\"]").then($els => {
            const texts = [...$els].map(el => el.innerText)  // extract texts
            expectedNames.forEach(name => {
                expect(texts).to.includes(name);
            })
        })
    })

})