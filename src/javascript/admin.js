/**
 * This defines the script file for the admin page.
 * 
 * @author Diego Ballesteros (diegob)
 */

// Define a global namespace for the admin page
(function(namespace){
    // ------------------------------------------------------------------------
    // Private properties
    // ------------------------------------------------------------------------
    /**
     * Map displayed in the page
     */
    var map = null;
    /**
     * Array of markers that represent the waypoints currently displayed in the
     * page.
     */
    var waypointMarkers = null;
    /**
     * Index of the currently selected marker.
     */
    var selectedWaypointIndex = -1;
    /**
     * Represents the current polyline displayed in the map that represents a
     * selected mission.
     */
    var missionInMap = null;
    /**
     * Constant line symbol that represents an arrow
     */
    var LINE_SYMBOL = {
        path : google.maps.SymbolPath.FORWARD_CLOSED_ARROW
    };

    // ------------------------------------------------------------------------
    // Private methods
    // ------------------------------------------------------------------------
    function clearDisplayedMission(){
        /**
         * Function that cleans the displayed mission if any is present.
         */
        // Clear the mission in map if any is present
        if (missionInMap) {
            missionInMap.setMap(null);
            missionInMap = null;
        }
    };

    function handleMissionGET(requestData, status, jqXHR){
        /**
         * Draw the mission in the map contained in the requestData object. This
         * function is called when a successful request is made to the missions
         * API.
         */
        // Clear the map of previous missions
        clearDisplayedMission();

        // Create a new polyline and set it in the map
        var missionInfo = requestData.missions[0];
        var waypointsInMission = missionInfo.waypoints;
        var all = waypointsInMission.length;
        missionInMap = new google.maps.Polyline({
            icons : [ {
                icon : LINE_SYMBOL,
                offset : "100%"
            } ]
        })
        var missionPath = missionInMap.getPath();
        for (var i = 0; i < all; ++i) {
            var targetWaypoint = waypointsInMission[i];
            var targetPoint = new google.maps.LatLng(targetWaypoint.latitude,
                    targetWaypoint.longitude);
            missionPath.push(targetPoint);
        }
        missionInMap.setMap(map);
    };

    function paintMission(missionId){
        /**
         * Paint a mission in the map given its id.
         */
        $.ajax({
            url : "/api/missions/".concat(missionId),
            accepts : "application/json",
            dataType : "json",
            type : "GET",
            success : handleMissionGET
        });
    };

    function centerMap(position){
        /**
         * Set the given position as the center of the maps object registered in
         * the admin page. The positions is expected to be a GeoLocation HTML5
         * object.
         */
        map.setCenter(new google.maps.LatLng(position.coords.latitude,
                position.coords.longitude));
    };

    function clearWaypointDisplay(){
        /**
         * Function that clears the currently displayed waypoint.
         */
        // Clear the image
        var $imageObject = $("#waypoint-display img");
        $imageObject.attr("src", "");

        // Clear the name
        var $waypointName = $("#waypoint-name");
        $waypointName.text("");

        // Clear the coordinates
        var $waypointLng = $("#waypoint-lng");
        var $waypointLat = $("#waypoint-lat");
        $waypointLng.attr("value", "");
        $waypointLat.attr("value", "");
        $waypointLng.val("");
        $waypointLat.val("");
    };

    function clearWaypointList(){
        /**
         * Function that removes all items from the waypoint list
         */
        $("#waypoint-list ul").empty();
    };

    function addWaypointToList($list, waypoint, waypointIndex){
        /**
         * Function that appends the information of a waypoint to the given list
         * element in the DOM.
         */
        var $span = $("<span/>", {
            html : waypoint.name
        });
        var waypointId = "waypoint".concat(waypointIndex);
        var $listItem = $("<li/>", {
            "id" : waypointId,
            html : $span
        });
        $list.append($listItem);
        return waypointId;
    };

    function addMarkerEvents(marker, waypointId){
        /**
         * Function that adds event listeners to the given marker, this requires
         * the name of the marker which is assumed to be equal to the id of the
         * list entry.
         */
        google.maps.event.addListener(marker, "click", function(){
            $("#".concat(waypointId)).trigger("click");
        });
    };

    function displayWaypoint(requestData, status, jqXHR){
        /**
         * Function to display a given waypoint in the page. This is triggered
         * when a waypoint is clicked on the list or on the map. The waypoint
         * display is also a form that allows updating the waypoint.
         */

        // Retrieve the waypoint from the request data.
        var waypoint = requestData.waypoints[0];

        // Set the image for the display
        var $imageObject = $("#waypoint-display img");
        $imageObject.attr("src", waypoint.image_url);

        // Set the name for the waypoint in the form text input
        var $waypointName = $("#waypoint-name");
        $waypointName.text(waypoint.name);

        // Set the coordinates in the appropriate fields
        var $waypointLng = $("#waypoint-lng");
        var $waypointLat = $("#waypoint-lat");
        $waypointLng.attr("value", waypoint.longitude);
        $waypointLat.attr("value", waypoint.latitude);
        $waypointLng.val(waypoint.longitude);
        $waypointLat.val(waypoint.latitude);

        // Set the new marker to draggable
        var selectedMarker = waypointMarkers[selectedWaypointIndex];
        selectedMarker.setDraggable(true);
        selectedMarker
                .setIcon("http://maps.google.com/mapfiles/ms/micons/green-dot.png");
        google.maps.event.addListener(selectedMarker, "drag", function(){
            var newPosition = selectedMarker.getPosition();
            $waypointLat.val(newPosition.lat());
            $waypointLng.val(newPosition.lng());
        });
    };

    function waypointSelected(event){
        /**
         * Function that listens to click events in the waypoint list and
         * displays the clicked item.
         */
        // Retrieve the index of the clicked element
        var target = event.currentTarget;
        var selectedListIndex = $("#waypoint-list ul li").index(target);

        // Highlight the selected item
        $(target).css("background-color", "#0D8800");

        // First clear the selection of the previous marker if any
        if (selectedWaypointIndex > -1) {
            var $waypointLng = $("#waypoint-lng");
            var $waypointLat = $("#waypoint-lat");
            var selectedMarker = waypointMarkers[selectedWaypointIndex];
            var oldMarkerOriginalLocation = new google.maps.LatLng($waypointLat
                    .attr("value"), $waypointLng.attr("value"));
            selectedMarker.setPosition(oldMarkerOriginalLocation);
            selectedMarker
                    .setIcon("http://maps.google.com/mapfiles/ms/micons/red-dot.png")
            google.maps.event.clearListeners(selectedMarker, "drag");
            selectedMarker.setDraggable(false);
            var $previousSelectedItem = $("#waypoint-list ul li").eq(
                    selectedWaypointIndex);
            $previousSelectedItem.css("background-color", "#FFF");
        }

        // Mark a new marker as selected
        selectedWaypointIndex = selectedListIndex;

        // Retrieve the information from this marker and display it
        var waypointId = $(target).text();
        $.ajax({
            url : "api/waypoints/".concat(waypointId),
            accepts : "application/json",
            dataType : "json",
            success : displayWaypoint
        });
    };

    function missionSelected(event){
        /**
         * Function that listens to click events on the mission list and
         * displays the clicked item.
         */
        var target = event.currentTarget;
        // Highlight the selected item, clear highlight from all the others
        $("#mission-list ul li").css("background-color", "#FFF");
        $(target).css("background-color", "#0D8800");
        // Display the mission in the map
        var missionId = $(target).text();
        paintMission(missionId);
    };

    function addWaypointsToPage(waypoints){
        /**
         * Function that adds the list of waypoints as markers in the map and
         * list entries in the page.
         */
        // Retrieve the list for waypoints
        var $waypointList = $("#waypoint-list ul");

        // Add all the waypoints to the map and list
        var all = waypoints.length;
        for (var i = 0; i < all; i++) {
            var markerLocation = new google.maps.LatLng(waypoints[i].latitude,
                    waypoints[i].longitude);
            var marker = new google.maps.Marker({
                position : markerLocation,
                icon : "http://maps.google.com/mapfiles/ms/micons/red-dot.png"
            });
            marker.setMap(map);
            waypointMarkers.push(marker);
            var listWaypointItemId = addWaypointToList($waypointList,
                    waypoints[i], i);
            addMarkerEvents(marker, listWaypointItemId);
        }
    };

    function updateWaypoints(){
        /**
         * Function that is triggered when the map viewport is changed. This
         * retrieves the closest waypoints from the server and displays markers
         * for them.
         */
        // Define a few objects needed for all subsequent operations
        var boxBounds = map.getBounds();

        // Call the API for waypoints inside the current viewport
        $.ajax({
            url : "/api/waypoints",
            data : {
                nelatitude : boxBounds.getNorthEast().lat(),
                nelongitude : boxBounds.getNorthEast().lng(),
                swlatitude : boxBounds.getSouthWest().lat(),
                swlongitude : boxBounds.getSouthWest().lng(),
                bounding_box : "true"
            },
            dataType : "json",
            success : function(requestData, status, jqXHR){
                // Retrieve the waypoints
                var waypoints = requestData.waypoints;

                // Clear the current display
                clearWaypointDisplay();

                // Clear the existing markers and list items
                while (waypointMarkers.length) {
                    waypointMarkers.pop().setMap(null);
                }
                selectedWaypointIndex = -1;
                clearWaypointList();

                // Add the new markers to the map and to the list
                addWaypointsToPage(waypoints);
            }
        });
    };

    function clearMissionList(){
        /**
         * Function to clear the current list of missions in the page.
         */
        $("#mission-list ul").empty();
    };

    function addMissionToList(mission){
        /**
         * Function that adds the given mission to the list display in the page.
         */
        var $list = $("#mission-list ul");
        var $span = $("<span/>", {
            html : mission.name
        });
        var $listItem = $("<li/>", {
            html : $span
        });
        $list.append($listItem);
    };

    function updateMissions(){
        /**
         * Function that retrieves the list of missions that start inside the
         * current map viewport and adds them to the mission list in the page.
         */
        // Define a few objects needed for all subsequent operations
        var boxBounds = map.getBounds();

        // Call the API for missions starting inside the current viewport
        $.ajax({
            url : "/api/missions",
            data : {
                nelatitude : boxBounds.getNorthEast().lat(),
                nelongitude : boxBounds.getNorthEast().lng(),
                swlatitude : boxBounds.getSouthWest().lat(),
                swlongitude : boxBounds.getSouthWest().lng(),
                bounding_box : "true"
            },
            dataType : "json",
            success : function(requestData, status, jqXHR){
                // Retrieve the missions
                var missions = requestData.missions;

                // Clear the current mission list
                clearMissionList();
                // Clear the mission display
                clearDisplayedMission();

                // Add the missions to the list
                missions.forEach(addMissionToList);
            }
        });
    };

    function updateWaypointsAndMissions(){
        /**
         * Function that updates the display of missions and waypoints in the
         * page.
         */
        updateMissions();
        updateWaypoints();
    };

    function setupWaypointUpdatesHandler(){
        /**
         * Function that sets the appropriate handler for the submit button in
         * the waypoint update form.
         */
        $("#waypoint-display-form").on("submit", function(event){
            // Retrieve the waypoint currently being displayed, if any.
            var waypointId = $("#waypoint-name").text();
            if (waypointId) {
                $.ajax({
                    url : "/api/waypoints/".concat(waypointId),
                    accepts : "application/json",
                    dataType : "json",
                    type : "PUT",
                    contentType : "application/json",
                    data : JSON.stringify({
                        latitude : $("#waypoint-lat").val(),
                        longitude : $("#waypoint-lng").val()
                    }),
                    success : updateWaypointsAndMissions
                });

            }
            event.preventDefault();
        });
    };

    function setupWaypointDeleteHandler(){
        /**
         * Function that handles the deletion of a waypoint being displayed in
         * the update form.
         */
        $("#delete-waypoint").on("click", function(event){
            var waypointId = $("#waypoint-name").text();
            if (waypointId) {
                $.ajax({
                    url : "/api/waypoints/".concat(waypointId),
                    accepts : "application/json",
                    dataType : "json",
                    type : "DELETE",
                    success : updateWaypointsAndMissions
                });
            }
            event.preventDefault();
        });
    };

    // ------------------------------------------------------------------------
    // Public properties
    // ------------------------------------------------------------------------

    // ------------------------------------------------------------------------
    // Public methods
    // ------------------------------------------------------------------------

    namespace.initialize = function(){
        /**
         * Initialization function for the admin page.
         */
        // Initialize the map in the page
        var mapOptions = {
            zoom : 15
        };
        map = new google.maps.Map($("#admin-map")[0], mapOptions);
        waypointMarkers = new Array();

        // Retrieve the location and center the map to this location
        utilsNS.retrieveLocation(centerMap);

        // Add a listener that updates the waypoints markers and missions
        // upon changes to the map viewport
        google.maps.event.addListener(map, "idle", updateWaypointsAndMissions);

        // Add listener for click events on the waypoint list
        var $waypointList = $("#waypoint-list ul");
        $waypointList.on("click", "li", waypointSelected);

        // Add listener for click events on the mission list
        var $missionList = $("#mission-list ul");
        $missionList.on("click", "li", missionSelected);

        // Setup the listener for waypoint update and delete actions
        setupWaypointUpdatesHandler();
        setupWaypointDeleteHandler();
    };

}(window.adminNS = window.adminNS || {}));

// Initialize the map when the DOM is ready
$(window).ready(adminNS.initialize);
