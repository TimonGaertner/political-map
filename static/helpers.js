const colors = [
    "ffe297",
    "ffba08",
    "faa307",
    "f48c06",
    "e85d04",
    "dc2f02",
    "d00000",
    "9d0208",
    "6a040f",
    "370617",
    "03071e",
];

function getColorMap(key, increment, addToScore) {
    const colorMap = {};

    for (const [countryCode, countryData] of Object.entries(dataset)) {
        let score;
        try {
            score = key.split(".").reduce((o, i) => o[i], countryData);
        } catch {
            colorMap[countryCode.toLowerCase()] = "#ffffff";
            continue;
        }

        if (addToScore) {
            score += addToScore;
        }

        for (
            let currScore = 0, colorIdx = 0;
            !(
                (score >= currScore && score <= currScore + increment) ||
                currScore > increment * colors.length
            );
            currScore += increment, colorIdx++
        ) {
            colorMap[countryCode.toLowerCase()] = "#" + colors[colorIdx];
        }
    }

    return colorMap;
}

function getColorMapPressFreedom() {
    return getColorMap("pressFreedomIndex.score2020", 5.5);
}

function getColorMapGlobalPeace() {
    return getColorMap("globalPeaceIndex.score2021", 0.18, -1);
}
function getColorMapFragileStates() {
    return getColorMap("fragileStatesIndex.score2021", 9.5);
}

// temporary code
// the getColorMap function will be rewritten to also work for
// GDP per capita (and potentially other indices)
function getColorMapGdpPerCapita() {
    const colorMap = {};

    for (const countryCode of Object.keys(dataset)) {
        if (
            !dataset[countryCode].economy ||
            !dataset[countryCode].economy.gdpPerCapita
        ) {
            colorMap[countryCode.toLowerCase()] = "#ffffff";
            continue;
        }

        const gdp = dataset[countryCode].economy.gdpPerCapita;
        let color;

        if (gdp < 1000) {
            color = colors[10];
        } else if (gdp < 2000) {
            color = colors[9];
        } else if (gdp < 4000) {
            color = colors[8];
        } else if (gdp < 6000) {
            color = colors[7];
        } else if (gdp < 8000) {
            color = colors[6];
        } else if (gdp < 12000) {
            color = colors[5];
        } else if (gdp < 15000) {
            color = colors[4];
        } else if (gdp < 20000) {
            color = colors[3];
        } else if (gdp < 30000) {
            color = colors[2];
        } else if (gdp < 40000) {
            color = colors[1];
        } else if (gdp >= 40000) {
            color = colors[0];
        }

        colorMap[countryCode.toLowerCase()] = "#" + color;
    }

    return colorMap;
}
function getColorMapPopulation() {
    return getColorMap("population.worldShare", 0.2);
}

function calculateChange(oldValue, newValue) {
    return (oldValue - newValue > 0 ? "+" : "") + (oldValue - newValue);
}

function formatNumber(num) {
    // 1 billion
    if (num >= 1000000000) {
        return (num / 1000000000).toFixed(3) + "b";
    }
    // 1 million
    else if (num >= 1000000) {
        return (num / 1000000).toFixed(3) + "m";
    }
    // 1 thousand
    else if (num >= 1000) {
        return (num / 1000).toFixed(3) + "k";
    }
    // less than 1k, no abbrv. needed
    else {
        return num;
    }
}
