var tourer = angular.module('xploreTourer', ['google-maps']);

tourer.filter('selected', function(){
    return function(input){
        input = input || [];
        var formattedInput = new Array();
        input.forEach(function(inputElement){
            if(inputElement.selected){
                formattedInput.push(inputElement.name);
            }
        });
        return formattedInput;
    }
});