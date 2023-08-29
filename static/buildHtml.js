function buildBarHtmlGlobal() {
    return `
<div class="flex flex-col w-full p-4 items-center overflow-y-auto">
    <h1 class="text-2xl mb-2 font-bold">World-Wide information</h1>
    <p class="mb-4">Click on a country to learn more!</p>
    <div class="w-full h-full flex flex-col gap-8 text-gray-900">
        ${dataset.worldwide.population ? buildBarSectionHtml(
            "Population",
            "https://www.worldometers.info/world-population/",
            [
                { name: "Population", info: formatNumber(dataset.worldwide.population)},
                { name: "Yearly population change", info: dataset.worldwide.yearlyChangePercent.toString()+"%"}
            ]) : ""
        }
    </div>
</div>`;
}


function buildBarSectionHtml(heading, methodologyUrl, categories, colSpanFullLastIfOdd) {
    return `    
<div>      
    <h3 class="pb-2 font-bold">
        ${heading}
        ${methodologyUrl ? `<a href=${methodologyUrl} target="_blank" class="ml-1 text-gray-600">(?)</a>` : ""}
    </h3>

    <div class="grid grid-cols-2 gap-4">
        ${categories.map((category, index) => `
            <div
                ${colSpanFullLastIfOdd && index === categories.length - 1 && index % 2 === 0
                    ? `class="col-span-full"`
                    : ""
                }
            >
                <p class="text-xs pb-1">${category.name}</p>
                <div class="card w-full">
                    <p>${category.info}</p>
                </div>
            </div>`).join("")
        }
    </div>
</div>`;
}


function buildBarometerHtml(data, heading) {
    if (!(data && Array.isArray(data))) {
        return ""
    }

    return  `
<div>
    <h3 class="pb-2 font-bold">${heading}</h3>
    <div class="flex flex-col gap-4">
        ${data.map((journalist) => `
            <div class="card w-full flex flex-col gap-1">
                <p>${journalist.name}</p>
                <p class="text-xs">${journalist.date} - ${journalist.job}</p>
            </div>`).join("")
        }
    </div>
</div>`;
}


function buildBarHtmlCountry(country) {
    return `
<div class="flex flex-col w-full h-full p-4 items-center overflow-y-auto">
    
    <a href=${country.url} target="_blank">
        <h1 class="text-2xl mb-4 font-bold hover:underline">${country.name}</h1>
    </a>
    
    <div class="w-full h-full flex flex-col gap-8 text-gray-900">
        ${country.population ? buildBarSectionHtml(
            "Population",
            "",
            [
                { name: "Population", info: formatNumber(country.population.population)},
                { name: "Yearly population change", info: country.population.yearlyPopulationChangePercent.toString()+"%"},
                { name: "Share of world population", info: country.population.worldShare.toString()+"%"}
            ]) : ""
        }
        ${country.systemOfGovernment ? buildBarSectionHtml( 
            "System of government",
            "https://en.wikipedia.org/wiki/List_of_countries_by_system_of_government",
            [
                { name: "Constitutional form", info: country.systemOfGovernment.constitutionalForm },
                { name: "Head of state", info: country.systemOfGovernment.headOfState },
                { name: "Basis of executive Legitimacy", info: country.systemOfGovernment.basisOfExecutiveLegitimacy }    
            ], true) : ""
        }
        ${country.economy ? buildBarSectionHtml(
            "Economy",
            "https://www.worldometers.info/gdp/gdp-by-country/",
            [
                { name: "GDP", info: "$"+formatNumber(country.economy.gdp)},
                { name: "Yearly GDP growth", info: country.economy.yearlyGdpGrowthPercent.toString()+"%" },
                { name: "GDP per capita", info: "$"+country.economy.gdpPerCapita.toString() },
                { name: "Share of World GDP", info: country.economy.worldShare.toString()+"%" }
            ]) : ""
        }
        ${country.pressFreedomIndex ? buildBarSectionHtml(
            "World press freedom index",
            "https://rsf.org/en/detailed-methodology",
            [
                { name: "Rank", info: country.pressFreedomIndex.rank2021 },
                { name: "Score", info: country.pressFreedomIndex.score2020 },
                { name: "Rank change", info: calculateChange(country.pressFreedomIndex.rank2020, country.pressFreedomIndex.rank2021) } 
            ]) : ""
        }
        ${country.fragileStatesIndex ? buildBarSectionHtml(
            "Fragile states index",
            "https://en.wikipedia.org/wiki/List_of_countries_by_Fragile_States_Index#Indicators_of_a_fragile_state",
            [
                { name: "Rank", info: country.fragileStatesIndex.rank },
                { name: "Score", info: country.fragileStatesIndex.score2021 }
            ]) : ""
        }
        ${country.globalPeaceIndex ? buildBarSectionHtml(
            "Global peace index",
            "https://en.wikipedia.org/wiki/Global_Peace_Index#Methodology",
            [
                { name: "Rank", info: country.globalPeaceIndex.rank2021 },
                { name: "Score", info: country.globalPeaceIndex.score2021 }
            ]): ""
        }
        
        ${
            country.barometer ? `
                ${buildBarometerHtml(country.barometer.journalistsKilled, "Journalists killed")}
                ${buildBarometerHtml(country.barometer.citizensJournalistsKilled, "Citizens journalists killed")}
                ${buildBarometerHtml(country.barometer.mediaAssistantsKilled, "Media Assistants killed")}
                ${buildBarometerHtml(country.barometer.journalistsImprisoned, "Journalists imprisoned")}
                ${buildBarometerHtml(country.barometer.citizensJournalistsImprisoned, "Citizens journalists imprisoned")}
                ${buildBarometerHtml(country.barometer.mediaAssistantsImprisoned, "Media Assistants imprisoned")}
            ` : ""
        }
    </div>
</div>`;
}
