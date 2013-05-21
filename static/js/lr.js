$(document).on("pageinit",function() {
    function applyUserPrefs() {
    	var custDistance = "{{chkDefaultCustDist}}";
    	if (custDistance) {
    		$('#CustDistance').removeClass("hidden");
    		$("#PreDistance").addClass("hidden");
	    	}
		}
	applyUserPrefs();

	function custUnits() {
		
		var mileUnits = {{rdioDefaultUnits_miles}};
		console.log("var mileUnits = %s",  mileUnits);
		if (mileUnits == "true"){
			$('#customUnitsMiles').attr("checked", "checked");
			$('#customUnitsKm').removeAttr("checked");
		}
	}
	custUnits();
});
