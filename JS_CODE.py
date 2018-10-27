test = '''
var map = new BMap.Map("allmap");
map.centerAndZoom(new BMap.Point(120.404, 39.915), 14);
map.enableScrollWheelZoom(true);'''

focus = '''
map.centerAndZoom(new BMap.Pointckzlt_pos, 17);
var marker = new BMap.Marker(new BMap.Pointckzlt_pos);
map.addOverlay(marker);
'''

removeOverlay = '''
map.removeOverlay(polyline);
'''

rgbPoint = '''
var marker = new BMap.Marker(new BMap.Pointckzlt_pos);
map.addOverlay(marker);
'''

addOverlay = '''
var sy = new BMap.Symbol(BMap_Symbol_SHAPE_BACKWARD_OPEN_ARROW, {
    scale: 0.6,
    strokeColor:'#fff',
    strokeWeight: '2',
});
var icons = new BMap.IconSequence(sy, '10', '30');
var pois = [
	ckzlt_points
];
var polyline =new BMap.Polyline(pois, {
    enableEditing: false,
    enableClicking: true,
    icons:[icons],
    strokeWeight:'8',
    strokeOpacity: 0.8,
    strokeColor:"#18a45b"
});

map.addOverlay(polyline);
'''