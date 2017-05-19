function noTicks() {
		return "";
};

function image_overlay(divname, racen, deccen, rasize, decsize, 
											 ellipse) {
		
		// Now create image
		//divframe= document.getElementById(divname+'_img');
		//image= document.createElement('img');
		//image.className = divframe.className;
		//image.setAttribute('src', imageurl);
		//image.style.width=divframe.style.width;
		//image.style.height=divframe.style.height;
		//divframe.appendChild(image);

		ramin = racen - rasize * 0.5
		ramax = racen + rasize * 0.5
		decmin = deccen - decsize * 0.5
		decmax = deccen + decsize * 0.5

		// options for image plotting
		var options_base = {
				grid: { show: true, 
								backgroundColor: null, 
								hoverable: true, 
								labelMargin: 0, minBorderMargin: 0,
								margin: {top: 0, bottom: 0, left:0 ,right: 0}},
				xaxis: { min: ramin, max: ramax, show: false, reserveSpace: false, 
								 tickFormatter: noTicks, labelWidth:0, labelHeight:0,
								 transform: function(v) {
										 return -v;
								 }, 
								 inverseTransform: function(v) {
										 return -v;
								 }
							 },
				yaxis: { min: decmin, max: decmax, show: false, reserveSpace: false, 
								 tickFormatter: noTicks, labelWidth:0, labelHeight:0},
		};

		// run the event handler to show position
		var previousPoint = null;
		$("#"+divname+'_plot').bind("plothover", function (event, pos, item) {
				$("#x").text(pos.x.toFixed(5));
				$("#y").text(pos.y.toFixed(5));
		});

		// function to read in and plot spectroscopic positions
		center=[[racen , deccen]];
		data_center= { points:{ show: true, fill: false, lineWidth: 0.5 },
									 data:center, shadowSize: 0, color: "#01ff01"};
		data_ellipse= { lines:{ show: true, lineWidth: 0.8}, 
										data:ellipse, shadowSize: 0, color: "#01ff01"};
		
		$.plot("#"+divname+'_plot', [data_center, data_ellipse], options_base);

}
