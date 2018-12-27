import xml.etree.ElementTree as ET
from pyquaternion import Quaternion as quat
import elements as el

def parse_connections(file, mirror):
	#tree = ET.parse(file)
	tree = ET.fromstring(file)
	root = tree.getroot()
	connections = ET.Element("connections")
	waypoints = ET.Element("waypoints")
	
	for node in root.iter('Transform'):
		id, x, y ,z, rot = parsex3d(node)
		q = [0,0,0,0]
		try:
		    q = quat(axis=[float(rot[0]), float(rot[1]), float(rot[2])], angle=float(rot[3]))
		except ZeroDivisionError:
		    q = [1,0,0,0]

		q = [q[0]*-1,q[1]*-1,q[3],q[2]*-1]

		if 'waypoint' in id:
			waypoints.append(el.get_waypoint(id, [x,y,z], q))
		else:
			connections.append(el.get_connection(id, [x,y,z], q))

		if not mirror:
			continue

		if not 'left' in id and not 'right' in id:
			continue

		#Mirror
		id, x, q = xmirror(id, x, q)

		if 'waypoint' in id:
			waypoints.append(el.get_waypoint(id, [x,y,z], q))
		else:
			connections.append(el.get_connection(id, [x,y,z], q))

	return connections, waypoints

#Parse a node from the input.
#Read information from relervant atributes and transform the location to ingame view.
def parsex3d(node):
    id = node.get('DEF').replace('_ifs_TRANSFORM','')
    loc = node.get('translation')
    rot = node.get('rotation')
    loc = loc.split()
    rot = rot.split()
    x = float(loc[0]) * -100
    y = float(loc[2]) * 100
    z = float(loc[1]) * -100
    return id, x, y, z, rot

def xmirror(id, x, q):
    #Mirror over x source : https://stackoverflow.com/questions/32438252/efficient-way-to-apply-mirror-effect-on-quaternion-rotation
    x = x * -1
    q = [q[0], q[1],q[2]*-1,q[3]*-1]

    if "left" in id:
        id = id.replace("left", "right")
    else:
        id = id.replace("right", "left")
    return id, x, q