var App = angular.module('ta-console');

App.service('MessageService', function($http, $window, $rootScope, $location, $q, $timeout, APIHost) {
    this.messages = [];
    this.addMessage = function(text, type){
        this.messages.push({body: text, type: type});
        $rootScope.$emit('messages-updated');
    };
    this.addInfo = function(text){
        this.addMessage(text, 'alert-info');
    };
    this.addError = function(text){
        this.addMessage(text, 'alert-danger');
    };
    this.addWarning = function(text){
        this.addMessage(text, 'alert-warning');
    };
    this.clear = function(){
        this.messages = [];
        $rootScope.$emit('messages-updated');
    };
    return this;
});
