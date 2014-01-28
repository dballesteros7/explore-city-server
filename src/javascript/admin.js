/**
 * This defines the script file for the admin page.
 * @author Diego Ballesteros (diegob)
 */

function setLocation(position){
    /**
     * Set the given position as the center of the maps object registered in
     * the admin page. The maps object is expected to be attached as jQuery
     * data to the #admin-map div.
     * 
     * This requires the Google Maps JavaScript API to be loaded.
     */
    var divObject = $("#admin-map");
    var mapObject = divObject.data("map");
    mapObject.setCenter( new google.maps.LatLng(position.coords.latitude,
                                                position.coords.longitude))
}

function updateWaypoints(dragEvent){
    /**
     * Function that is triggered when the map view is changed in any way.
     * This retrieves the closest waypoints from the server and displays
     * markers for them.
     */
    var $mapSelector = $("#admin-map");
    var map = $mapSelector.data("map");
    var existingMarkers = $mapSelector.data("markers");
    while(existingMarkers.length){
        existingMarkers.pop().setMap(null);
    }
    var box_bounds = map.getBounds();
    $.ajax({
        url : "/api/waypoints",
        data : { nelatitude : box_bounds.getNorthEast().lat(),
                 nelongitude : box_bounds.getNorthEast().lng(),
                 swlatitude : box_bounds.getSouthWest().lat(),
                 swlongitude : box_bounds.getSouthWest().lng(),
                 bounding_box : "true"
        },
        dataType : "json",
        success : function(requestData, status, jqXHR){
            var waypoints = requestData.waypoints;
            for(i = 0; i < waypoints.length; i++){
                var markerLocation = new google.maps.LatLng(waypoints[i].latitude,
                                                            waypoints[i].longitude);
                var marker = new google.maps.Marker({
                    position : markerLocation
                });
                marker.setMap(map);
                existingMarkers.push(marker);
            }
        }
    });
}

function initialize(){
    /**
     * Initialization function for the admin page.
     */
    // Initialize a simple map with zoom 15 and the current location as center
    var mapOptions = {
            zoom: 15
        };
    var map = new google.maps.Map(document.getElementById("admin-map"),
                                  mapOptions);
    $("#admin-map").data("map", map)
    $("#admin-map").data("markers", new Array())
    retrieveLocation(setLocation);

    // Add listeners that update the location markers on changes of the
    // map viewport.
    google.maps.event.addListener(map, 'idle', updateWaypoints);
}

// Initialize the map when the DOM is ready
$(window).ready(initialize);
