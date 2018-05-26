
//https://stackoverflow.com/questions/1990512/add-comma-to-numbers-every-three-digits
$.fn.digits = function(){ 
    return this.each(function(){ 
        $(this).text( $(this).text().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,") ); 
    })
}

igf = { 

'update_mined': function (id,tag) {
	$.getJSON( "/mined/"+tag, function( data ) {
		$(id).text(data).digits();
	});
}

}
