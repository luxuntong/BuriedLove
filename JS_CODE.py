test = '''
var map = new BMap.Map("allmap");
map.centerAndZoom(new BMap.Point(120.404, 39.915), 14);
map.enableScrollWheelZoom(true);'''

test1 = '''
map.centerAndZoom(new BMap.Point(118.404, 39.915), 14);
'''

test2 = '''
map.removeOverlay(polyline);
'''