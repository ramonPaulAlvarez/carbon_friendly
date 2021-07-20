function setCurrentCo2(element_id){
    return $.ajax({
        type: "GET",
        dataType: "json",
        url: "https://global-warming.org/api/co2-api",
        success: function (data) {
            let co2_records = data["co2"];
            latest_record = co2_records[co2_records.length - 1];
            $("#" + element_id).html(latest_record["trend"] + " CO2 PPM");
            $("#" + element_id).attr('title', `Carbon Dioxide in PPM (${latest_record["month"]}/${latest_record["day"]}/${latest_record["year"]})`);
        }
    });
}

function setCurrentTemperatureAnomaly(element_id){
    return $.ajax({
        type: "GET",
        dataType: "json",
        url: "https://global-warming.org/api/temperature-api",
        success: function (data) {
            let temperature_records = data["result"];
            latest_record = temperature_records[temperature_records.length - 1];
            $("#" + element_id).html(latest_record["station"] + " C");
            $("#" + element_id).attr('title', `Temperature Anomaly in Celsius (${latest_record["time"]})`);
        }
    });
}

function setCurrentMethane(element_id){
    return $.ajax({
        type: "GET",
        dataType: "json",
        url: "https://global-warming.org/api/methane-api",
        success: function (data) {
            let methane_records = data["methane"];
            latest_record = methane_records[methane_records.length - 1];
            $("#" + element_id).html(latest_record["average"] + " CH4 PPM");
            $("#" + element_id).attr('title', `Methane in PPM (${latest_record["date"]})`);
        }
    });
}

// Populate Metrics
$(document).ready(function () {
    try {
        $.when(setCurrentCo2("metric_co2"), setCurrentMethane("metric_ch4"), setCurrentTemperatureAnomaly("metric_t")).done(() => {
            $('#metrics').slideDown();
        });
    } catch (err) {
        console.log(err);
    }
});