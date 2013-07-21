(function ($, L) {
    $(function () {
        var origin = [52.634626, 13.313749];
        var target = [52.638, 13.31374];

        var bounds = L.latLngBounds([origin, target]);
        var map = L.map('map').fitBounds(bounds);

        L.tileLayer('http://{s}.tile.cloudmade.com/d4fc77ea4a63471cab2423e66626cbb6/997/256/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>'
        }).addTo(map);

        L.tileLayer('http://openfiremap.org/hytiles/{z}/{x}/{y}.png').addTo(map);
        L.tileLayer('http://openfiremap.org/eytiles/{z}/{x}/{y}.png').addTo(map);

        L.marker(origin, {icon: L.AwesomeMarkers.icon({
            icon: 'home',
            color: 'blue'
        })}).addTo(map);

        L.marker(target, {icon: L.AwesomeMarkers.icon({
            icon: 'fire',
            color: 'red'
        })}).addTo(map);
    });
})(jQuery, L);