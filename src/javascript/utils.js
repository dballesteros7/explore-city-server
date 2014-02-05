/**
 * Utility module with general-purpose functions.
 * 
 * @author Diego Ballesteros (diegob)
 */

(function(namespace){
    // ------------------------------------------------------------------------
    // Public methods
    // ------------------------------------------------------------------------
    namespace.retrieveLocation = function(setLocation){
        /**
         * This function tries to determine the user's location up to some level
         * of accuracy. It tries to access the HTML5 geolocation option, but in
         * case of error or if it is not supported, it will fix the location to
         * Zurich (47.377455,8.536715). The location is passed as an argument to
         * the set_location function handle. This argument must be a function
         * handle only accepting a single position object as input.
         */
        var browserSupported = false;
        var basePositionLat = 47.377455;
        var basePositionLong = 8.536715;
        var handleError = function(error){
            var mockPosition = {
                coords : {
                    latitude : basePositionLat,
                    longitude : basePositionLong
                }
            };
            if (browserSupported) {
                switch (error.code) {
                case error.PERMISSION_DENIED:
                    console
                            .log("Permission was denied for retrieving the location.");
                    break;
                case error.POSITION_UNAVAILABLE:
                    console.log("The position is not available.");
                    break;
                case error.TIMEOUT:
                    console.log("Position retrieval took too long.");
                    break;
                }
            } else {
                console.log("Browser does not support geolocation.");
            }
            setLocation(mockPosition);
        };
        if (navigator.geolocation) {
            browserSupported = true;
            var options = {
                enableHighAccuracy : false,
                timeout : 30000,
                maximumAge : 3600000
            };
            navigator.geolocation.getCurrentPosition(setLocation, handleError,
                    options);
        } else {
            handleError(null);
        }
    };
})(window.utilsNS = window.utilsNS || {});
