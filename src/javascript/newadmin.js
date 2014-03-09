/**
 * This defines the script file for the admin page.
 * 
 * Requires jQuery and jQuery UI.
 * 
 * @author Diego Ballesteros (diegob)
 */

// Define a global namespace for the admin page
adminNS = {};
// (function(namespace){
// ------------------------------------------------------------------------
// State variables
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
 * Marker used to indicate the location of a new waypoint
 */
var newWaypointMarker = null;
/**
 * Represents the current polyline displayed in the map that represents a
 * selected mission.
 */
var missionInMap = null;
/**
 * State variable that indicates if the current waypoint on display is new or an
 * existing one.
 */
var creatingNewWaypoint = false;
/**
 * State variable that indicates if the current mission in display is new or an
 * existing one
 */
var creatingNewMission = false;
/**
 * Constant line symbol that represents an arrow
 */
var LINE_SYMBOL = {
    path : google.maps.SymbolPath.FORWARD_CLOSED_ARROW
};
/**
 * Constant string to identify waypoint items
 */
var BASE_WAYPOINT_ID = "waypoint";

/**
 * Default stock image for the waypoint list
 */
var DEFAULT_WAYPOINT_IMG = "/img/warlords-of-draenor-1600x900.jpg"

// ------------------------------------------------------------------------
// Functions that modify the mission display
// ------------------------------------------------------------------------
function clearMissionDisplay(){
    /**
     * Function that cleans the displayed mission if any is present.
     */
    // Clear the mission in map if any is present
    if (missionInMap) {
        missionInMap.setMap(null);
        missionInMap = null;
    }
    // Clear the list of missions and the name
    $("#mission-name-input").val("").attr("value", "");
    var $waypointList = $("#waypoints-for-mission");
    $waypointList.empty();

    // Disable all buttons but the new mission one
    $("#mission-display-form button").attr("disabled", "disabled");
    $("#new-mission").removeAttr("disabled");

    // Remove any flag of new mission
    creatingNewMission = false;
}

function addWaypointToMissionList($waypointList, waypointId){
    /**
     * Function to add a waypoint id to the mission's waypoint list. Each of
     * this item is selectable and has an associated handle icon to make the
     * list sortable as well.
     */
    var $listItem = $("<a/>", {
        href : "#",
        html : waypointId,
    });
    $listItem.addClass("list-group-item");
    $waypointList.append($listItem);
}

function displayMission(missionId){
    /**
     * Paint a mission in the map given its id.
     */
    $.ajax({
        url : "/api/missions/".concat(missionId),
        accepts : "application/json",
        dataType : "json",
        type : "GET",
        success : function(requestData, status, jqXHR){
            // Clear the map of previous missions
            clearMissionDisplay();

            // Create a new polyline and set it in the map
            var missionInfo = requestData.missions[0];
            var waypointsInMission = missionInfo.waypoints;
            missionInMap = new google.maps.Polyline({
                icons : [ {
                    icon : LINE_SYMBOL,
                    offset : "100%"
                } ],
                map : map
            });
            var missionPath = missionInMap.getPath();
            var $waypointList = $("#waypoints-for-mission");
            // Add the list of waypoints to the mission description and
            // the polyline
            waypointsInMission.forEach(function(targetWaypoint){
                var targetPoint = new google.maps.LatLng(
                        targetWaypoint.latitude, targetWaypoint.longitude);
                missionPath.push(targetPoint);
                addWaypointToMissionList($waypointList, targetWaypoint.name);
            });

            // Set the mission name
            var $missionName = $("#mission-name-input");
            $missionName.val(missionInfo.name);
            $missionName.attr("value", missionInfo.name);

            // Enable all buttons
            $("#mission-display-form button").removeAttr("disabled");

            // Indicate that a new mission is NOT being created
            creatingNewWaypoint = false;
        },
    // TODO: Handle error case
    });
}

// ------------------------------------------------------------------------
// Functions that modify the waypoint display
// ------------------------------------------------------------------------

function deselectWaypoint(){
    /**
     * Function that handles the deselection of a waypoint.
     */
    // First clear the selection of the previous marker if any
    if (selectedWaypointIndex > -1) {
        var $waypointLng = $("#waypoint-lng");
        var $waypointLat = $("#waypoint-lat");
        var selectedMarker = waypointMarkers[selectedWaypointIndex];
        var oldMarkerOriginalLocation = new google.maps.LatLng($waypointLat
                .attr("value"), $waypointLng.attr("value"));
        selectedMarker.setPosition(oldMarkerOriginalLocation);
        selectedMarker
                .setIcon("http://maps.google.com/mapfiles/ms/micons/red-dot.png");
        google.maps.event.clearListeners(selectedMarker, "drag");
        selectedMarker.setDraggable(false);
    }
}

function clearWaypointDisplay(){
    /**
     * Function that clears the currently displayed waypoint.
     */
    // Clear any selected list item
    deselectWaypoint();
    $("#waypoint-list a").removeClass("active");
    selectedWaypointIndex = -1;

    // Clear the image
    $("#waypoint-reference-image").attr("src", DEFAULT_WAYPOINT_IMG).attr(
            "blobkey", "");

    // Clear the name input value
    var $waypointNameInput = $("#waypoint-name-input");
    $waypointNameInput.attr("value", "");
    $waypointNameInput.val("");

    // Clear the coordinates
    var $waypointLng = $("#waypoint-lng");
    var $waypointLat = $("#waypoint-lat");
    $waypointLng.attr("value", "");
    $waypointLat.attr("value", "");
    $waypointLng.val("");
    $waypointLat.val("");

    // Disable the form buttons
    $("#waypoint-display-form button").attr("disabled", "disabled");
    // Except the new button
    $("#new-waypoint").removeAttr("disabled");

    // Disable uploads from the waypoint image
    setupImageUploadHook(false);

    // Clear any new waypoint marker
    if (newWaypointMarker) {
        newWaypointMarker.setMap(null);
        newWaypointMarker = null;
    }

    // Remove any flag of new waypoints
    creatingNewWaypoint = false;
}

function displayWaypoint(waypointId){
    /**
     * Function to display a given waypoint in the page given its ID. It
     * requests the waypoint information from the server and displays it in a
     * form. This function assumes that the selectedWaypointIndex was updated to
     * the right marker.
     */
    // Retrieve the request information and display it
    $
            .ajax({
                url : "api/waypoints/".concat(waypointId),
                accepts : "application/json",
                data : {
                // image_size : 400
                }, // Request images to 400 px max.
                dataType : "json",
                success : function(requestData, status, jXHQR){
                    // Retrieve the waypoint from the request data.
                    var waypoint = requestData.waypoints[0];

                    // Set the image for the display
                    var $imageObject = $("#waypoint-reference-image");
                    $imageObject.attr("src", waypoint.image_url);
                    $imageObject.attr("blobkey", waypoint.image_key)

                    // Set the name for the waypoint in the span, hide the input
                    // field
                    var $waypointName = $("#waypoint-name-input");
                    $waypointName.attr("value", waypoint.name);
                    $waypointName.val(waypoint.name);

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
                    google.maps.event.addListener(selectedMarker, "drag",
                            function(){
                                var newPosition = selectedMarker.getPosition();
                                $waypointLat.val(newPosition.lat());
                                $waypointLng.val(newPosition.lng());
                            });

                    // Activate the buttons
                    $("#waypoint-display-form button").removeAttr("disabled")

                    // Reactivate the image upload hook
                    setupImageUploadHook(true);
                },
            // TODO: Handle the error case
            });
}

// ------------------------------------------------------------------------
// Handlers for selections of missions and waypoints
// ------------------------------------------------------------------------
function waypointSelected(event){
    /**
     * Function that listens to click events in the waypoint list and displays
     * the clicked item.
     */
    // Clear the waypoint display
    clearWaypointDisplay();

    // Retrieve the index of the clicked element, set it as selected
    var selectedListIndex = $("#waypoint-list a").index(event.currentTarget);
    selectedWaypointIndex = selectedListIndex;

    // Retrieve the information from this marker and display it
    var waypointId = $(event.currentTarget).text();
    displayWaypoint(waypointId);
}

function missionSelected(event){
    /**
     * Function that is triggered when a mission item is clicked on the mission
     * list. It displays the given mission.
     */
    // Clear the mission display
    clearMissionDisplay();
    // The event was triggered from a list element whose text contains
    // the mission id.
    var missionId = $(event.currentTarget).text();
    displayMission(missionId);
}

function missionOrWaypointSelected(event){
    /**
     * Function that handles the selection of an item in the mission and
     * waypoint lists. It triggers the appropriate response depending on the
     * type of object that was selected (i.e. mission or waypoint).
     */
    // The event is expected to bubble up to the li element.
    // This is recorded in target, from this it is possible to know
    // which list is the one that is being interacted with.
    var $targetLi = $(event.currentTarget);
    var $parentDiv = $targetLi.parents("div");
    var listId = $parentDiv.attr("id");
    // Trigger the appropiate function for the event
    switch (listId) {
    case "mission-list":
        // Move to the missions tab if not already there
        $('#selection-tabs a[href="#missions"]').tab('show');
        // Trigger the selection event
        missionSelected(event);
        break;
    case "waypoint-list":
        // Move to the waypoints tab if not already there
        $('#selection-tabs a[href="#waypoints"]').tab('show');
        // Trigger the selection event
        waypointSelected(event);
        break;
    default:
        break;
    }

    // The current target was the element that initiated the event
    // that will be a li item. Set it as selected and remove selection
    // from other elements.
    $targetLi.addClass("active");
    $targetLi.siblings().removeClass("active");
}

// ------------------------------------------------------------------------
// Functions that update the waypoint list and markers
// ------------------------------------------------------------------------
function addWaypointToListAndMap(waypoint, waypointIndex){
    /**
     * Function that adds the given waypoint to the list display in the page and
     * as a marker in the map. The this object is expected to be equal to the
     * waypoint list. The list item is given an id equal to the BASE_WAYPOINT_ID
     * plus the index of the element in the source array. And the marker has an
     * added listener that triggers a click on the corresponding list item.
     */
    // Define the span with the waypoint name and then create
    // the containing list item with the corresponding id.
    var waypointId = BASE_WAYPOINT_ID.concat(waypointIndex);

    var $listItem = $("<a/>", {
        href : "#",
        html : waypoint.name,
        id : waypointId
    });
    // Make it selectable and add it to the list
    $listItem.addClass("list-group-item");
    this.append($listItem);
    // Create a new marker with the waypoint location and add it to the map
    var markerLocation = new google.maps.LatLng(waypoint.latitude,
            waypoint.longitude);
    var marker = new google.maps.Marker({
        position : markerLocation,
        icon : "http://maps.google.com/mapfiles/ms/micons/red-dot.png",
        map : map
    });
    // Add the marker to the marker list and add the corresponding listener
    waypointMarkers.push(marker);
    google.maps.event.addListener(marker, "click", function(){
        $("#".concat(waypointId)).trigger("click");
    });
}

function clearWaypointListAndMarkers(){
    /**
     * Function that removes all items from the waypoint list and the markers
     * from the map.
     */
    // Clear the list
    $("#waypoint-list").empty();
    // Deselect any index
    selectedWaypointIndex = -1;
    // Clean the map
    waypointMarkers.forEach(function(marker){
        marker.setMap(null);
    });
    // Clean the marker array
    waypointMarkers.length = 0;
}

// ------------------------------------------------------------------------
// Functions that update the mission list
// ------------------------------------------------------------------------
function addMissionToList(mission){
    /**
     * Function to add each mission id to the list given in the this object.
     */
    var $listItem = $("<a/>", {
        href : "#",
        html : mission.name,
    });
    $listItem.addClass("list-group-item");
    this.append($listItem);
}

function clearMissionList(){
    /**
     * Function to clear the current list of missions in the page.
     */
    $("#mission-list").empty();
};

// ------------------------------------------------------------------------
// Functions to handle the update of the mission and waypoint lists
// ------------------------------------------------------------------------
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
            bounding_box : "true",
            detailed : "false"
        },
        dataType : "json",
        beforeSend : $.blockUI,
        complete : $.unblockUI,
        success : function(requestData, status, jqXHR){
            // Retrieve the missions
            var missions = requestData.missions;

            // Clear the current mission list
            clearMissionList();
            // Clear the mission display
            clearMissionDisplay();

            // Add the missions to the list
            var $list = $("#mission-list");
            missions.forEach(addMissionToList, $list);
        }
    });
}

function updateWaypoints(){
    /**
     * Function that is triggered when the map viewport is changed. This
     * retrieves the closest waypoints from the server and displays markers for
     * them.
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
        beforeSend : $.blockUI,
        complete : $.unblockUI,
        success : function(requestData, status, jqXHR){
            // Retrieve the waypoints
            var waypoints = requestData.waypoints;

            // Clear the current display
            clearWaypointDisplay();
            // Clear the existing markers and list items
            clearWaypointListAndMarkers();

            // Add the new markers to the map and to the list
            var $waypointList = $("#waypoint-list");
            waypoints.forEach(addWaypointToListAndMap, $waypointList);
        }
    });
}

function updateWaypointsAndMissions(){
    /**
     * Function that updates the display of missions and waypoints in the page.
     */
    updateMissions();
    updateWaypoints();
}

// ------------------------------------------------------------------------
// Functions that handle the creation of new waypoints and missions
// ------------------------------------------------------------------------
function displayNewWaypointForm(){
    /**
     * Function that prepares the display form for waypoints to create a new
     * waypoint.
     */
    // Clear the waypoint display
    clearWaypointDisplay();

    // Disable the delete button, enabled the others
    $("#waypoint-display-form button").removeAttr("disabled");
    $("#delete-waypoint").attr("disabled", "disabled");

    // Enable image uploads
    setupImageUploadHook(true);

    // Drop a special marker for location in the center of the map
    newWaypointMarker = new google.maps.Marker({
        position : map.getCenter(),
        icon : "http://maps.google.com/mapfiles/ms/micons/blue-dot.png",
        map : map,
        draggable : true,
    });
    $("#waypoint-lat").val(map.getCenter().lat());
    $("#waypoint-lng").val(map.getCenter().lng());
    google.maps.event.addListener(newWaypointMarker, "drag", function(){
        var newPosition = newWaypointMarker.getPosition();
        $("#waypoint-lat").val(newPosition.lat());
        $("#waypoint-lng").val(newPosition.lng());
    });
    // Indicate that we are creating a new waypoint
    creatingNewWaypoint = true;
}

function displayNewMissionForm(){
    /**
     * Function that prepares the display form for missions to create a new
     * mission.
     */
    // Clear the display from any current mission
    clearMissionDisplay();

    // Disable the delete button, enable the others
    $("#mission-display-form button").removeAttr("disabled");
    $("#delete-mission").attr("disabled", "dissabled");

    // Indicate that a new mission is being created
    creatingNewMission = true;
}

// ------------------------------------------------------------------------
// Setup the handlers for the waypoint and mission forms
// ------------------------------------------------------------------------

function setupImageUploadHook(enable){
    /**
     * Function to enable or disable the upload of images by clicking the
     * reference image for waypoints.
     */
    if (enable) {
        // Add functionality to upload images for waypoints
        $("#waypoint-reference-image").on("click", function(event){
            $("#waypoint-image-upload").trigger("click");
        });
        $("#waypoint-reference-image").attr("alt", "Click to upload image...");
    } else {
        $("#waypoint-reference-image").off("click");
        $("#waypoint-reference-image").attr("alt", "");
    }
}

function setupHiddenImageUploadHandlers(){
    /**
     * Function to configure the listeners for the hidden form used to handle
     * image uploads for new waypoints.
     */
    // Prepare the hidden image form for ajax submissions with the
    // ajaxSubmit plugin
    var $imageUploadForm = $("#waypoint-image-upload-form");
    $imageUploadForm.ajaxForm({
        success : function(responseData, status, jqXHR){
            $("#waypoint-reference-image").attr("src", responseData.image_url)
                    .attr("blobkey", responseData.image_key);
        }
    });

    // After a file selection, upload the file using ajax and then display it.
    $("#waypoint-image-upload").on("change", function(event){
        var file = event.target.files[0];
        if (file) {
            // Request a blob url and add a listener for image upload
            $.ajax({
                url : "/api/upload",
                accepts : "application/json",
                dataType : "json",
                type : "GET",
                success : function(requestData, status, jqXHR){
                    // Retrieve the image key from the request data
                    var uploadUrl = requestData.upload_url;
                    // Set the appriopriate target for the upload form
                    $imageUploadForm.attr("action", uploadUrl);
                    // Trigger the upload submission
                    $imageUploadForm.trigger("submit");
                }
            });
        }
    });
}

function setupWaypointFormHandlers(){
    /**
     * Function that handles the different actions on the waypoint form.
     */
    // Present the interface to create a new waypoint
    $("#new-waypoint").on("click", function(event){
        // Prepare the form for a new waypoint
        displayNewWaypointForm();
    });
    // Option to cancel a waypoint creation
    $("#cancel-waypoint").on("click", function(event){
        clearWaypointDisplay();
    });
    // Option to save a new waypoint or update an existing one
    $("#save-waypoint").on(
            "click",
            function(event){
                // Act accordingly to the state of creatingNewWaypoint
                var waypointId = $("#waypoint-name-input").val();
                var newImage = $("#waypoint-reference-image").attr("blobkey");
                var latitude = $("#waypoint-lat").val();
                var longitude = $("#waypoint-lng").val();
                var updateData = {
                    latitude : latitude,
                    longitude : longitude,
                    image_key : newImage,
                    name : waypointId,
                };
                if (waypointId) {
                    if (creatingNewWaypoint) {
                        $.ajax({
                            url : "/api/waypoints",
                            accepts : "application/json",
                            dataType : "json",
                            type : "POST",
                            contentType : "application/json",
                            data : JSON.stringify(updateData),
                            success : updateWaypointsAndMissions,
                        });
                    } else {
                        var originalWaypointId = $("#waypoint-name-input")
                                .attr("value");
                        $.ajax({
                            url : "/api/waypoints/".concat(originalWaypointId),
                            accepts : "application/json",
                            dataType : "json",
                            type : "PUT",
                            contentType : "application/json",
                            data : JSON.stringify(updateData),
                            success : updateWaypointsAndMissions,
                        // TODO: On error, announce that the update was not
                        // possible
                        });
                    }
                }
            });

    // Option to delete the currently displayed waypoint
    $("#delete-waypoint").on("click", function(event){
        event.preventDefault();
        var waypointId = $("#waypoint-name-input").val();
        var originalWaypointId = $("#waypoint-name-input").attr("value");
        if (creatingNewWaypoint) {
            // TODO: Indicate the user that this is not a valid operation
            // Actually the button should be disabled here!
        }
        if (waypointId && waypointId == originalWaypointId) {
            $.ajax({
                url : "/api/waypoints/".concat(waypointId),
                accepts : "application/json",
                dataType : "json",
                type : "DELETE",
                success : updateWaypointsAndMissions
            // TODO: On error, announce that the delete was not possible
            });
            // TODO: Indicate what happens if the name has been changed.
        }
    });
};

function setupMissionFormHandlers(){
    /**
     * Function that handles the different actions on the mission form.
     */
    // Option to create a new mission
    $("#new-mission").on("click", function(event){
        event.preventDefault();
        // Display a new mission form
        displayNewMissionForm();
    });
    // Option to cancel a mission creation
    $("#cancel-mission").on("click", function(event){
        event.preventDefault();
        clearMissionDisplay();
    });
    // Add item to list
    $("#add-waypoint-to-mission").on(
            "click",
            function(event){
                event.preventDefault();
                var inputWaypoint = $("#new-waypoint-for-mission").val();
                if (inputWaypoint) {
                    $.ajax({
                        url : "/api/waypoints/".concat(inputWaypoint),
                        accepts : "application/json",
                        dataType : "json",
                        type : "GET",
                        success : function(requestData, status, jqXHR){
                            if (requestData.waypoints.length) {
                                addWaypointToMissionList(
                                        $("#waypoints-for-mission"),
                                        requestData.waypoints[0].name);
                            } else {
                                // TODO: Indicate that there is no waypoint with
                                // that id.
                            }
                            // Clear the name from the form
                            $("#new-waypoint-for-mission").val("");
                        },
                    // TODO: Handle error case
                    });
                } else {
                    // TODO: Warn of empty id names
                }
            });

    // Remove item from list
    $("#remove-waypoint-from-mission").on("click", function(event){
        $("#waypoints-for-mission a.active").remove();
    });

    // Delete mission
    $("#delete-mission").on("click", function(event){
        event.preventDefault();
        var missionId = $("#mission-name-input").val();
        var originalMissionId = $("#mission-name-input").attr("value");
        if (creatingNewMission) {
            // TODO: Indicate the user that this is not a valid operation
            // Actually the button should be disabled here!
        }
        if (missionId && missionId == originalMissionId) {
            $.ajax({
                url : "/api/missions/".concat(missionId),
                accepts : "application/json",
                dataType : "json",
                type : "DELETE",
                success : updateWaypointsAndMissions
            // TODO: On error, announce that the delete was not possible
            });
            // TODO: Indicate what happens if the name has been changed.
        }
    });

    // Update mission
    $("#save-mission").on("click", function(event){
        event.preventDefault();
        var missionId = $("#mission-name-input").val();
        var originalMissionId = $("#mission-name-input").attr("value");
        if (missionId) {
            var waypointsForMission = new Array();
            $("#waypoints-for-mission a").each(function(index, ele){
                var waypointId = $(ele).text();
                waypointsForMission.push(waypointId);
            });
            if (waypointsForMission.length) {
                if (creatingNewMission) {
                    $.ajax({
                        url : "/api/missions",
                        accepts : "application/json",
                        contentType : "application/json",
                        dataType : "json",
                        type : "POST",
                        data : JSON.stringify({
                            waypoints : waypointsForMission,
                            name : missionId
                        }),
                        success : updateWaypointsAndMissions,
                    // TODO: Handle error case
                    });
                } else {
                    $.ajax({
                        url : "/api/missions/".concat(originalMissionId),
                        accepts : "application/json",
                        contentType : "application/json",
                        dataType : "json",
                        type : "PUT",
                        data : JSON.stringify({
                            waypoints : waypointsForMission,
                            name : missionId
                        }),
                        success : updateWaypointsAndMissions,
                    // TODO: Handle error case
                    });
                }
            } else {
                // TODO: Warn about empty list of waypoints
            }
        } else {
            // TODO: Warn of empty mission id
        }
    });
};

// ------------------------------------------------------------------------
// Map-related functions
// ------------------------------------------------------------------------

function centerMap(position){
    /**
     * Set the given position as the center of the maps object registered in the
     * admin page. The positions is expected to be a GeoLocation HTML5 object.
     */
    map.setCenter(new google.maps.LatLng(position.coords.latitude,
            position.coords.longitude));
};

// ------------------------------------------------------------------------
// Public methods
// ------------------------------------------------------------------------

adminNS.initialize = function(){
    /**
     * Initialization function for the admin page.
     */
    // Initialize the map object and set it in its corresponding div.
    // Also initialize the array that holds the list of waypoint markers
    // in the map.
    var mapOptions = {
        zoom : 15
    };
    map = new google.maps.Map($("#admin-map")[0], mapOptions);
    waypointMarkers = new Array();

    // Retrieve the user's location and center the map to this location
    utilsNS.retrieveLocation(centerMap);

    // Add a listener that updates the waypoints markers and missions
    // upon changes to the map viewport
    google.maps.event.addListener(map, "idle", updateWaypointsAndMissions);

    // Add a listener for the waypoint and mission lists
    $(".xplore-object-list").on("click", "a", missionOrWaypointSelected);

    // Make the waypoint list in a mission sortable and selectable
    $("#waypoints-for-mission").sortable({
        handle : ".handle"
    });
    $("#waypoints-for-mission").selectable();

    // Setup the listener for waypoint update and delete actions
    setupWaypointFormHandlers();

    // Setup the listener for the buttons in the mission form
    setupMissionFormHandlers();

    // Setup listener for image uploads
    setupHiddenImageUploadHandlers();

    // For development testing
    $(document.body).on("click", function(ev){
        console.log(ev.target);
        console.log(ev.currentTarget);
    });
};

// }(window.adminNS = window.adminNS || {}));

// Initialize the map when the DOM is ready
$(window).ready(adminNS.initialize);
