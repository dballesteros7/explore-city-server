/**
 * This defines the script file for the admin page.
 * 
 * Requires jQuery and jQuery UI.
 * 
 * @author Diego Ballesteros (diegob)
 */

// Define a global namespace for the admin page
adminNS = {};
//(function(namespace){
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
     * Constant line symbol that represents an arrow
     */
    var LINE_SYMBOL = {
        path : google.maps.SymbolPath.FORWARD_CLOSED_ARROW
    };
    /**
     * Constant string to identify waypoint items
     */
    var BASE_WAYPOINT_ID = "waypoint";
    
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
        $("#mission-name")
                    .text("")
                    .css("display", "initial");
        $("#mission-name-input")
                    .val("")
                    .css("display", "none");
        var $waypointList = $("#waypoints-for-mission");
        $waypointList.empty();

        // Remove any listener from the remove selected button waypoint
        $("#remove-waypoint-from-mission").off("click");

        // Hide the form buttons
        $("#mission-display input[type='button']").css("display", "none");
    }
    
    function addWaypointToMissionList($waypointList, waypointId){
        /**
         * Function to add a waypoint id to the mission's waypoint list.
         * Each of this item is selectable and has an associated handle
         * icon to make the list sortable as well.
         */
        var $span = $("<span/>", {
            html : waypointId
        });
        var $listItem = $("<li/>", {
            html : $span
        });
        $listItem.addClass("ui-selectee");
        $listItem.prepend("<div class='handle'><span class='ui-icon ui-icon-carat-2-n-s'></span></div>");
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
                // Add the list of waypoints to the mission description and the polyline
                waypointsInMission.forEach(function(targetWaypoint){
                    var targetPoint = new google.maps.LatLng(targetWaypoint.latitude,
                            targetWaypoint.longitude);
                    missionPath.push(targetPoint);
                    addWaypointToMissionList($waypointList, targetWaypoint.name);
                });

                // Set the mission name
                var $missionName = $("#mission-name");
                $missionName.text(missionInfo.name);

                // Display anything related to the update operation
                $("#mission-display-form .update-object").css("display", "initial");
            },
            //TODO: Handle error case
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
        $("#waypoint-list ul li").removeClass("ui-selected");
        selectedWaypointIndex = -1;

        // Clear the image
        $("#waypoint-reference-image").attr("src", "").attr("blobkey", "");

        // Clear the name
        var $waypointName = $("#waypoint-name");
        $waypointName.text("");
        
        // Clear the name input value
        var $waypointNameInput = $("#waypoint-name-input");
        $waypointNameInput.val("");

        // Clear the coordinates
        var $waypointLng = $("#waypoint-lng");
        var $waypointLat = $("#waypoint-lat");
        $waypointLng.attr("value", "");
        $waypointLat.attr("value", "");
        $waypointLng.val("");
        $waypointLat.val("");

        // Hide the form buttons
        $("#waypoint-display input[type='button']").css("display", "none");

        // Hide the input text field for the name if present, and display the span.
        $waypointName.css("display", "initial");
        $waypointNameInput.css("display", "none");

        // Disable uploads from the waypoint image
        setupImageUploadHook(false);

        // Clear any new waypoint marker
        if(newWaypointMarker){
            newWaypointMarker.setMap(null);
            newWaypointMarker = null;
        }
    }

    function displayWaypoint(waypointId){
        /**
         * Function to display a given waypoint in the page given its ID.
         * It requests the waypoint information from the server and displays it
         * in a form.
         * This function assumes that the selectedWaypointIndex was updated
         * to the right marker.
         */
        // Retrieve the request information and display it
        $.ajax({
            url : "api/waypoints/".concat(waypointId),
            accepts : "application/json",
            data : {image_size : 400}, // Request images to 400 px max.
            dataType : "json",
            success : function(requestData, status, jXHQR){
                // Retrieve the waypoint from the request data.
                var waypoint = requestData.waypoints[0];

                // Set the image for the display
                var $imageObject = $("#waypoint-reference-image");
                $imageObject.attr("src", waypoint.image_url);

                // Set the name for the waypoint in the span, hide the input field
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

                // Display anything related to the update operation
                $("#waypoint-display-form .update-object").css("display", "initial");
            },
            // TODO: Handle the error case
        });
    }

    // ------------------------------------------------------------------------
    // Handlers for selections of missions and waypoints
    // ------------------------------------------------------------------------
    function waypointSelected(event){
        /**
         * Function that listens to click events in the waypoint list and
         * displays the clicked item.
         */
        // Clear the waypoint display
        clearWaypointDisplay();

        // Retrieve the index of the clicked element, set it as selected
        var selectedListIndex = $("#waypoint-list ul li").index(event.currentTarget);
        selectedWaypointIndex = selectedListIndex;

        // Retrieve the information from this marker and display it
        var waypointId = $(event.currentTarget).find("span").text();
        displayWaypoint(waypointId);

        // Move to the waypoints tab if not already there
        window.location.hash = $("#waypoint-tab a").attr("href");
    }

    function missionSelected(event){
        /**
         * Function that is triggered when a mission item is clicked on the
         * mission list. It displays the given mission.
         */
        // The event was triggered from a list element whose text contains
        // the mission id.
        var missionId = event.currentTarget.textContent;
        displayMission(missionId);
    }

    function missionOrWaypointSelected(event){
        /**
         * Function that handles the selection of an item in the mission and
         * waypoint lists. It triggers the appropriate response depending on
         * the type of object that was selected (i.e. mission or waypoint).
         */
        // The event is expected to bubble up to the li element.
        // This is recorded in target, from this it is possible to know
        // which list is the one that is being interacted with.
        var $targetLi = $(event.currentTarget);
        var listId = $targetLi.parents("div").attr("id");
        // Trigger the appropiate function for the event
        switch (listId) {
        case "mission-list":
            missionSelected(event);
            break;
        case "waypoint-list":
            waypointSelected(event);
            break;
        default:
            break;
        }

        // The current target was the element that initiated the event
        // that will be a li item. Set it as selected and remove selection
        // from other elements.
        $targetLi.addClass("ui-selected");
        $targetLi.siblings().removeClass("ui-selected");
    }

    // ------------------------------------------------------------------------
    // Functions that update the waypoint list and markers
    // ------------------------------------------------------------------------
    function addWaypointToListAndMap(waypoint, waypointIndex){
        /**
         * Function that adds the given waypoint to the list display 
         * in the page and as a marker in the map. The this object is expected
         * to be equal to the waypoint list.
         * The list item is given an id equal to the
         * BASE_WAYPOINT_ID plus the index of the element in the source array.
         * And the marker has an added listener that triggers a click on the
         * corresponding list item.
         */
        // Define the span with the waypoint name and then create
        // the containing list item with the corresponding id.
        var waypointId = BASE_WAYPOINT_ID.concat(waypointIndex);
        var $span = $("<span/>", {
            html : waypoint.name
        });
        var $listItem = $("<li/>", {
            html : $span,
            id : waypointId
        });
        // Make it selectable and add it to the list
        $listItem.addClass("ui-selectee");
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
        $("#waypoint-list ul").empty();
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
        var $span = $("<span/>", {
            html : mission.name
        });
        var $listItem = $("<li/>", {
            html : $span,
        });
        $listItem.addClass("ui-selectee");
        this.append($listItem);
    }

    function clearMissionList(){
        /**
         * Function to clear the current list of missions in the page.
         */
        $("#mission-list ul").empty();
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
                detailed: "false"
            },
            dataType : "json",
            beforeSend : $.blockUI,
            complete: $.unblockUI,
            success : function(requestData, status, jqXHR){
                // Retrieve the missions
                var missions = requestData.missions;

                // Clear the current mission list
                clearMissionList();
                // Clear the mission display
                clearMissionDisplay();

                // Add the missions to the list
                var $list = $("#mission-list ul");
                missions.forEach(addMissionToList, $list);
            }
        });
    }

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
            beforeSend : $.blockUI,
            complete: $.unblockUI,
            success : function(requestData, status, jqXHR){
                // Retrieve the waypoints
                var waypoints = requestData.waypoints;

                // Clear the current display
                clearWaypointDisplay();
                // Clear the existing markers and list items
                clearWaypointListAndMarkers();

                // Add the new markers to the map and to the list
                var $waypointList = $("#waypoint-list ul");
                waypoints.forEach(addWaypointToListAndMap, $waypointList);
            }
        });
    }

    function updateWaypointsAndMissions(){
        /**
         * Function that updates the display of missions and waypoints in the
         * page.
         */
        updateMissions();
        updateWaypoints();
    }

    // ------------------------------------------------------------------------
    // Functions that handle the creation of new waypoints and missions
    // ------------------------------------------------------------------------
    function displayNewWaypointForm(){
        /**
         * Function that prepares the display form for waypoints to create a
         * new waypoint.
         */
        // Deselect and clear the display from any current waypoint
        clearWaypointDisplay();

        // Show the elements for new objects
        $("#waypoint-display-form .new-object").css("display", "initial");

        // Enable image uploads
        setupImageUploadHook(true);

        // Drop a special marker for location in the center of the map
        newWaypointMarker = new google.maps.Marker({
            position : map.getCenter(),
            icon : "http://maps.google.com/mapfiles/ms/micons/blue-dot.png",
            map : map,
            draggable : true,
        });
        google.maps.event.addListener(newWaypointMarker, "drag", function(){
            var newPosition = newWaypointMarker.getPosition();
            $("#waypoint-lat").val(newPosition.lat());
            $("#waypoint-lng").val(newPosition.lng());
        });
    }

    function displayNewMissionForm(){
        /**
         * Function that prepares the display form for missions to create a new
         * mission.
         */
        // Clear the display from any current mission
        clearMissionDisplay();

        // Show the elements for new objects
        $("#mission-display-form .new-object").css("display", "initial");
    }

    // ------------------------------------------------------------------------
    // Setup the handlers for the waypoint and mission forms
    // ------------------------------------------------------------------------

    function setupNewObjectHandlers(){
        /**
         * Function to handle the event when the new mission/waypoint button
         * is pressed.
         */
        // Prepare the new button functionality
        $(".new-button").on("click", function(event){
            var buttonId = $(event.currentTarget).attr("id");
            switch (buttonId) {
            case "new-waypoint-but":
                displayNewWaypointForm();
                break;
            case "new-mission-but":
                displayNewMissionForm();
                break;
            default:
                break;
            }
        });
    }

    function setupImageUploadHook(enable){
        /**
         * Function to enable or disable the upload of images by clicking
         * the reference image for waypoints.
         */
        if(enable){
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
         * Function to configure the listeners for the hidden form used
         * to handle image uploads for new waypoints.
         */
        // Prepare the hidden image form for ajax submissions with the 
        // ajaxSubmit plugin
        var $imageUploadForm = $("#waypoint-image-upload-form");
        $imageUploadForm.ajaxForm({
            success : function(responseData, status, jqXHR){
                $("#waypoint-reference-image")
                    .attr("src", responseData.image_url)
                    .attr("blobkey", responseData.image_key);
            }
        });

        // After a file selection, upload the file using ajax and then display it.
        $("#waypoint-image-upload").on("change", function(event){
            var file = event.target.files[0];
            if(file){
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
        // Option to create a new waypoint
        $("#submit-new-waypoint").on("click", function(event){
            // Retrieve the inputs and send a POST request
            var waypointId = $("#waypoint-name-input").val();
            var latitude = $("#waypoint-lat").val();
            var longitude = $("#waypoint-lng").val();
            var imageKey = $("#waypoint-reference-image").attr("blobkey");
            // TODO: Verify inputs
            if(imageKey){
                $.ajax({
                    url : "/api/waypoints",
                    accepts : "application/json",
                    dataType : "json",
                    type : "POST",
                    contentType : "application/json",
                    data : JSON.stringify({
                        name : waypointId,
                        latitude : latitude,
                        longitude : longitude,
                        image_key : imageKey
                    }),
                    success : updateWaypointsAndMissions,
                    // TODO: Handle error case
                });
            }
        });
        // Option to cancel a waypoint creation
        $("#cancel-new-waypoint").on("click", function(event){
            clearWaypointDisplay();
        });
        // Option to update the waypoint location
        $("#submit-waypoint-update").on("click", function(event){
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
                        longitude : $("#waypoint-lng").val(),
                    }),
                    success : updateWaypointsAndMissions,
                    //TODO: On error, announce that the update was not possible
                });
            }
        });
      
        // Option to delete the currently displayed waypoint
        $("#delete-waypoint").on("click", function(event){
            var waypointId = $("#waypoint-name").text();
            if (waypointId) {
                $.ajax({
                    url : "/api/waypoints/".concat(waypointId),
                    accepts : "application/json",
                    dataType : "json",
                    type : "DELETE",
                    success : updateWaypointsAndMissions
                    //TODO: On error, announce that the delete was not possible
                });
            }
        });
    };

    function setupMissionFormHandlers(){
        /**
         * Function that handles the different actions on the mission form.
         */
        // Option to create a new mission
        $("#submit-new-mission").on("click", function(event){
            event.preventDefault();
            var missionId = $("#mission-name-input").val();
            if(missionId){
                var waypointsForMission = new Array();
                $("#waypoints-for-mission li").each(function(index, ele){
                    var waypointId = $(ele).text();
                    waypointsForMission.push(waypointId);
                });
                if(waypointsForMission.length){
                    $.ajax({
                        url : "/api/missions",
                        accepts : "application/json",
                        contentType : "application/json",
                        dataType : "json",
                        type : "POST",
                        data : JSON.stringify({
                            name : missionId,
                            waypoints : waypointsForMission
                        }),
                        success : updateWaypointsAndMissions,
                        // TODO: Handle error case
                    });
                } else {
                    // TODO: Warn about empty list of waypoints
                }
            } else {
                // TODO: Inform the user of empty id
            }
        });
        // Option to cancel a mission creation
        $("#cancel-new-mission").on("click", function(event){
            clearMissionDisplay();
        });
        // Add item to list
        $("#add-waypoint-to-mission").on("click", function(event){
            var inputWaypoint = $("#new-waypoint-for-mission").val();
            if(inputWaypoint){
                $.ajax({
                    url : "/api/waypoints/".concat(inputWaypoint),
                    accepts : "application/json",
                    dataType : "json",
                    type : "GET",
                    success : function(requestData, status, jqXHR){
                        if(requestData.waypoints.length){
                            addWaypointToMissionList($("#waypoints-for-mission"), requestData.waypoints[0].name);
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

        // Remove item from list, this adds a handler with closure data
        // everytime the selection changes (Seems expensive, check if it's
        // better to just keep a local variable somewhere, although
        // it looks damn cool to use this closure).
        $("#waypoints-for-mission").on("selectablestop", function(){
            // First clear any previous listener
            $("#remove-waypoint-from-mission").off("click");
            var context = this;
            $("#remove-waypoint-from-mission").on("click", function(event){
                $(".ui-selected", context).each(function(){
                    $(this).remove();
                });
            });
        });

        // Delete mission
        $("#delete-mission").on("click", function(event){
            var missionId = $("#mission-name").text();
            if (missionId) {
                $.ajax({
                    url : "/api/missions/".concat(missionId),
                    accepts : "application/json",
                    dataType : "json",
                    type : "DELETE",
                    success : updateWaypointsAndMissions,
                    // TODO: Handle error case
                });
            } else {
                // This should not happen, if the mission Id is empty then
                // the buttons should be disabled.
            }
        });

        // Update mission
        $("#submit-mission-update").on("click", function(event){
            event.preventDefault();
            var missionId = $("#mission-name").text();
            if(missionId){
                var waypointsForMission = new Array();
                $("#waypoints-for-mission li").each(function(index, ele){
                    var waypointId = $(ele).text();
                    waypointsForMission.push(waypointId);
                });
                if(waypointsForMission.length){
                    $.ajax({
                        url : "/api/missions/".concat(missionId),
                        accepts : "application/json",
                        contentType : "application/json",
                        dataType : "json",
                        type : "PUT",
                        data : JSON.stringify({
                            waypoints : waypointsForMission
                        }),
                        success : updateWaypointsAndMissions,
                        // TODO: Handle error case
                    });
                } else {
                    // TODO: Warn about empty list of waypoints
                }
            } else {
                // This should not happen, if the mission Id is empty then
                // the buttons should be disabled.
            }
        });
    };

    // ------------------------------------------------------------------------
    // Map-related functions
    // ------------------------------------------------------------------------

    function centerMap(position){
        /**
         * Set the given position as the center of the maps object registered in
         * the admin page. The positions is expected to be a GeoLocation HTML5
         * object.
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
        $(".inner-list").on("click", "li", missionOrWaypointSelected);

        // Make the waypoint list in a mission sortable and selectable
        $("#waypoints-for-mission").sortable({ handle: ".handle"});
        $("#waypoints-for-mission").selectable();

        // Setup the listener for waypoint update and delete actions
        setupWaypointFormHandlers();

        // Setup the listener for the buttons in the mission form
        setupMissionFormHandlers();

        // Setup the listener for the "new" buttons
        setupNewObjectHandlers();

        // Setup listener for image uploads
        setupHiddenImageUploadHandlers();

        // For development testing
        $(document.body).on("click", function(ev){
            console.log(ev.target);
            console.log(ev.currentTarget);
        });
    };

//}(window.adminNS = window.adminNS || {}));

// Initialize the map when the DOM is ready
$(window).ready(adminNS.initialize);
