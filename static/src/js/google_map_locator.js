openerp.crm_lead_extended = function (instance){
    

    //Widget for FormView
    instance.geo = {};
instance.geo.MapFormWidget = instance.web.form.FormWidget.extend({
        template: 'map',

        start: function(){
            var self = this;
            var r = this._super();
            var rendererOptions = {draggable: false};
            try {
                this.directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);
                this.directionsService = new google.maps.DirectionsService();
                this.map;
                this.model = this.view.dataset.model;
                this.country = new google.maps.LatLng(55, -180);
                var orderId = this.view.dataset.ids[0];
                self.mapInit(orderId);

            } catch(err) {
            }
            return r;
        },
        mapInit: function(id){
            var self = this;
            var mapOptions = {zoom: 10, center: this.country, mapTypeId: google.maps.MapTypeId.ROADMAP};
            this.map = new google.maps.Map(document.getElementById('tour-map-canvas'), mapOptions);
            this.directionsDisplay.setMap(this.map);

            this.lines = new instance.web.Model('crm.lead');
            var defs = [];
            this.waypoints = [];
            if (this.model == 'crm.lead'){
                this.lines.call('search', [[['id','in',[id]]]])
                .then(function(results){
                    _.each(results, function(val, index){
                        defs.push(self.lines.call('read', [[val], ['name','phone','city', 'street', 'street2', 'zip','country_id', 'company_id']], {})
                            .then(function(result){
                                self.waypoints.push(result[0]);
                            }));
                    });
                    $.when.apply($, defs).then(function(){
                        self.get_ltlg(self.waypoints);
                    });
                });
            }

            $('#distance').on('click', function(){
                console.log("way pointssss", self.waypoints[0].city);
                if (self.waypoints[0].city){
                    self.calcRoute(self.waypoints);

                    google.maps.event.addListener(self.directionsDisplay, 'directions_changed', function() {
                        self.showSteps(self.directionsDisplay.getDirections());
                    });
                } else {
                    $('#dist').html('<div><b>No Detailed Address specified.</b></div>');
                }
            });
        },
        get_ltlg: function(res){
            var self = this;
            var mapOptions = {zoom: 4, mapTypeId: google.maps.MapTypeId.ROADMAP};
            var map = new google.maps.Map(document.getElementById('tour-map-canvas'), mapOptions);

            //map.setOptions({ minZoom: 2, maxZoom: 10, center: this.country});
            var geocoder =  new google.maps.Geocoder();
            var infowindow = new google.maps.InfoWindow({maxWidth: 300});
            var marker, i;
            
            for (var i=0;i<res.length;i++){
                if (res[i].street || res[i].zip || res[i].city || res[i].street2) {
                    var address = res[i].street
                    if(res[i].street2 != false){
                        address += ', ' + res[i].street2;
                    }
                    if(res[i].zip != false){
                        address += ', ' + res[i].zip;
                    }
                    if(res[i].city != false){
                        
                        address += ', ' + res[i].city;
                    }

                    //var address = (res[i].street + "," + res[i].city
    
                    geocoder.geocode({ 'address': address}, function(results, status) {
                        if (status == google.maps.GeocoderStatus.OK) {
                            var ltlg = results[0].geometry.location.lat() + " , " +results[0].geometry.location.lng();
                            console.log("\n ltlgltlg444444ltlgltlgltlg", typeof(ltlg));
                        }
                        if (ltlg){
                            this.centermap = new google.maps.LatLng(results[0].geometry.location.lat(), results[0].geometry.location.lng());
                            map.setOptions({ minZoom: 2, center: this.centermap});
                            var location = [ltlg];
                            for (i = 0; i < location.length; i++) {
                                var loc = location[0].split(",") ;
                                marker = new google.maps.Marker({
                                    position: new google.maps.LatLng(loc[0],loc[1]),
                                    map: map
                                });
                                google.maps.event.addListener(marker, 'click', (function(marker, i) {
                                    return function() {
                                        console.log("resultsssssssss", results[0]);
                                        infowindow.setContent(res[i].name + "<br/>" + (res[i].street || '') + "<br/>" + (res[i].zip || '') + "<br/>" +results[0].address_components[0].short_name + "," + results[0].address_components[2].long_name);
                                        infowindow.open(map, marker);
                                    }
                                })(marker, i));
                            }
                        }
                    });
                } else {
                    $('#dist').html('<div><b>No Detailed Address specified.</b></div>');
                }
            }
        },
        calcRoute: function(results){
            var self = this;
            var location = [];
            self.request = {
                origin:'',
                destination:'',
                waypoints:[],
                travelMode: google.maps.TravelMode.DRIVING
            };
            this.model = new instance.web.Model('res.company');
            _.each(results, function(val, index){
                 if (!val.city && !val.company_id){
                    return ;
                }
                self.model.call('read', [[val.company_id[0]], ['city', 'street','zip','country_id']], {}).then(function(value){
                        
                        var origin = val.city;
                        var destination = value[0].city;

                        if(val.street != false){
                            var street = val.street.replace(',','')
                            origin += ', ' + val.street;
                        }
                        if(val.zip != false){
                            origin += ', ' + val.zip;
                        }
                        if(val.city != false){
                            var city = val.city.replace(',','')
                            origin += ', ' + val.city;
                        }
                        if(val.country_id != false){
                            origin += ', ' + val.country_id[1];
                        }


                        if(value[0].city != false){
                            var street = value[0].city.replace(',','')
                            destination += ', ' + value[0].city;
                        }
                        if(value[0].zip != false){
                            destination += ', ' + value[0].zip;
                        }
                        if(value[0].country_id != false){
                            destination += ', ' + value[0].country_id[1];
                        }
                        console.log("resultsssssAAAAAAAAAAAAAAAAAAassss", origin);
                        self.request.origin = origin;
                        self.request.destination = destination;

                        self.request.waypoints.push({location: origin, stopover: true});
                        self.request.waypoints.push({location: destination, stopover: true});
                        if(index == results.length-1){
                            self.display();
                        };
                    });
            });

        },
        showSteps: function(response){
			console.log('hhhhhhhh',response);
            var self = this;
            var output = '';
            var route = response.routes[0];

            var distance = self.computeTotalDistance(route);
            if (parseFloat(distance)){
                this.field_manager.fields['km'].set_value(parseFloat(distance.replace(',','.')));
            }
            else{
                this.field_manager.fields['km'].set_value(parseFloat(distance));
            }
            this.field_manager.fields['km']._dirty_flag = true;
            var dist_miles = parseFloat(distance) * 0.621371;
            $('#dist').html('<div><b>Distance:-</b> '+distance+ ' km <span style="color:red">('+dist_miles+' miles)</span></div>');
            //$('#dist').html('<div class="map_titel">Distance</div><br/><div>'+distance+ ' km <span style="color:red">('+dist_miles+' miles)</span></div><br/>');
            self.mapInit();
        },
        computeTotalDistance: function(route){
            var self = this;
            var total = 0;
            for (var i = 0; i < route.legs.length; i++){
                total += route.legs[i].distance.value;
            }
            total = total/1000;
            return total.toFixed(1).toString().replace('.',',');
        },

        display: function(){
            var self = this;
            self.directionsService.route(self.request, function(response, status) {
                if (status == google.maps.DirectionsStatus.OK) {
                     self.directionsDisplay.setDirections(response);
                }
            });
        },



    });

    instance.web.form.custom_widgets.add('map', 'instance.geo.MapFormWidget')
    
};
