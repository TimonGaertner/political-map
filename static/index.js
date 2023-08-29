const $map = $("#map");
const $bar = $("#bar");

$map.vectorMap({
    map: "world_en",
    enableZoom: false,
    showTooltip: true,
    onRegionClick,
    onRegionDeselect,
});

function onRegionClick(element, code, region) {
    const countryData = dataset[code.toUpperCase()];
    $bar.html(buildBarHtmlCountry(countryData));
}

function onRegionDeselect(event, code, region) {
    $bar.html(buildBarHtmlGlobal());
}

$("#index-select").on("input", (e) => {
    let colorMap;
    if (e.target.value === "pressFreedom") {
        colorMap = getColorMapPressFreedom();
    } else if (e.target.value === "fragileStates") {
        colorMap = getColorMapFragileStates();
    } else if (e.target.value === "globalPeace") {
        colorMap = getColorMapGlobalPeace();
    } else if (e.target.value === "gdpPerCapita") {
        colorMap = getColorMapGdpPerCapita();
    } else if (e.target.value === "population") {
        colorMap = getColorMapPopulation();
    }
    $map.vectorMap("set", "colors", colorMap);
});

$("#index-select").val("pressFreedom").trigger("input");

$bar.html(buildBarHtmlGlobal());

$map.mousewheel(function (event) {
    if (event.deltaY > 0) {
        $map.vectorMap("zoomIn");
    } else {
        $map.vectorMap("zoomOut");
    }
});
