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

function displayWaypoint(event){
    /**
     * Function to display a given waypoint in the page. This is triggered
     * when a waypoint is clicked on the list or on the map.
     * The waypoint display is also a form that allows updating the waypoint.
     */
    // Retrieve the associated marker
    var $mapSelector = $("#admin-map");
    var map = $mapSelector.data("map");
    var existingMarkers = $mapSelector.data("markers");
    var draggableMarker = $mapSelector.data("selectedMarker");

    // Retrieve the selector for the latitutde and longitude fields in the
    // update form
    var $waypointLng = $("#waypoint-lng");
    var $waypointLat = $("#waypoint-lat");

    // Clear the previous marker and move it to is previous location if it
    // was moved
    if(draggableMarker){
        var oldMarkerOriginalLocation = new google.maps.LatLng($waypointLat.attr("value"),
                $waypointLng.attr("value"));
        draggableMarker.setPosition(oldMarkerOriginalLocation);
        google.maps.event.clearListeners(draggableMarker, "drag");
    }

    // Retrieve the waypoint from the event's data.
    var waypoint = event.data.waypoint;
    var markerIndex = event.data.index;

    // Retrieve the DOM object for the display container
    var $imageDisplay = $("#waypoint-display");

    // Set the image for the display
    var $imageObject = $("#waypoint-display img");
    $imageObject.attr("src", waypoint.image_url);

    // Set the name for the waypoint in the form text input
    var $waypointName = $("#waypoint-name");
    $waypointName.text(waypoint.name);

    // Set the coordinates in the appropriate fields
    $waypointLng.attr("value", waypoint.longitude);
    $waypointLat.attr("value", waypoint.latitude);
    $waypointLng.val(waypoint.longitude);
    $waypointLat.val(waypoint.latitude);

    //Clear the draggable status from the previous marker
    if(draggableMarker){
        draggableMarker.setDraggable(false);
    }

    // Set the new marker to draggable
    var newDraggableMarker = existingMarkers[markerIndex];
    newDraggableMarker.setDraggable(true);
    google.maps.event.addListener(newDraggableMarker, "drag", function(){
        var newPosition = newDraggableMarker.getPosition();
        $waypointLat.val(newPosition.lat());
        $waypointLng.val(newPosition.lng());
    });
    $mapSelector.data("selectedMarker", newDraggableMarker);
}

function addWaypointToList($list, waypoint, waypoint_index){
    /**
     * Function that appends the information of a waypoint to the given list
     * element in the DOM.
     */
    var $span = $("<span/>", {
        html: waypoint.name
    });
    var waypointId = "waypoint".concat(waypoint_index);
    var $listItem = $("<li/>", {
        "id" : waypointId,
        html : $span
    });
    $list.append($listItem);
    $listItem.on("click", {
        "waypoint" : waypoint,
        "index" : waypoint_index
        }, displayWaypoint);
    return waypointId;
}

function clearList($list){
    /**
     * Function that removes all present list items from the given list
     * element.
     */
    $list.empty();
}

function addMarkerEvents(marker, waypointId){
    /**
     * Function that adds event listeners to the given marker, this
     * requires the name of the marker which is assumed to be equal
     * to the id of the list entry.
     */
    google.maps.event.addListener(marker, "click", function(){
        $("#".concat(waypointId)).trigger("click");
    });
}

function addWaypointsToPage(waypoints){
    /**
     * Function that adds the list of waypoints as markers in the map and
     * list entries in the page.
     */
    var $mapSelector = $("#admin-map");
    var $waypointList = $("#waypoint-list ul")
    var map = $mapSelector.data("map");
    var existingMarkers = $mapSelector.data("markers");
    var all = waypoints.length;
    for(var i = 0; i < all; i++){
        var markerLocation = new google.maps.LatLng(waypoints[i].latitude,
                                                    waypoints[i].longitude);
        var marker = new google.maps.Marker({
            position : markerLocation
        });
        marker.setMap(map);
        existingMarkers.push(marker);
        var listWaypointItemId = addWaypointToList($waypointList, waypoints[i], i);
        addMarkerEvents(marker, listWaypointItemId);
    }
}

function updateWaypoints(dragEvent){
    /**
     * Function that is triggered when the map view is changed in any way.
     * This retrieves the closest waypoints from the server and displays
     * markers for them.
     */
    // Define a few objects needed for all subsequent operations
    var $mapSelector = $("#admin-map");
    var $waypointList = $("#waypoint-list ul")
    var map = $mapSelector.data("map");
    var existingMarkers = $mapSelector.data("markers");
    var boxBounds = map.getBounds();

    // Call the API for waypoints inside the current viewport
    $.ajax({
        url : "/api/waypoints",
        data : { nelatitude : boxBounds.getNorthEast().lat(),
                 nelongitude : boxBounds.getNorthEast().lng(),
                 swlatitude : boxBounds.getSouthWest().lat(),
                 swlongitude : boxBounds.getSouthWest().lng(),
                 bounding_box : "true"
        },
        dataType : "json",
        success : function(requestData, status, jqXHR){
            // Retrieve the waypoints
            var waypoints = requestData.waypoints;

            // Clear the existing markers and list items
            while(existingMarkers.length){
                existingMarkers.pop().setMap(null);
            }
            clearList($waypointList);

            // Add the new markers to the map and to the list
            addWaypointsToPage(waypoints);
        }
    });
}

function setupWaypointUpdatesHandler(){
    /**
     * Function that sets the appropriate handler for the submit button in
     * the waypoint update form.
     */
    $("#waypoint-display-form").on("submit", function(event){
        // Retrieve the waypoint currently being displayed, if any.
        var waypointId = $("#waypoint-name").text();
        if(waypointId){
            $.ajax({
                url : "/api/waypoints/".concat(waypointId),
                accepts : "application/json",
                dataType : "json",
                type : "PUT",
                contentType : "application/json",
                data : JSON.stringify({
                    latitude : $("#waypoint-lat").val(),
                    longitude : $("#waypoint-lng").val()
                })
            })
        }
        event.preventDefault();
        updateWaypoints(null);
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
    google.maps.event.addListener(map, "idle", updateWaypoints);

    // Capture waypoint updates submissions
    setupWaypointUpdatesHandler();
}

// Initialize the map when the DOM is ready
$(window).ready(initialize);
