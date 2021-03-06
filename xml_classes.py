#xml classes
import xml.etree.ElementTree as ET
from xml.dom.minidom import parse, parseString
import pickle
from lxml import etree
from datetime import datetime

def from_binary(file):
	return pickle.loads(file)

def read_xml(file):
	tree = ET.parse(file)
	return tree.getroot()

def get_dss_path(dae_file):
	root = read_xml(dae_file)
	textures = root.findall(".//image")
	ddss = []
	for texture in textures:
		dds = texture[0].text
		ddss.append(dds)
	return ddss

def gen_index_macros(path):
	diff = ET.Element("diff")
	add = ET.Element('add', sel='/index')
	add.append(ET.Element('entry', name=path.split('/')[-1], value=path))
	diff.append(add)
	return diff

def gen_index_components(path):
	diff = ET.Element("diff")
	add = ET.Element('add', sel='/index')
	add.append(ET.Element('entry', name=path.split('/')[-1], value=path))
	diff.append(add)
	return diff

def gen_content(name):
	date = datetime.today().strftime('%Y-%m-%d')
	content = ET.Element("content", id=name, description="", author="", version="1", date=date, save="0", enabled="1")
	return content

def to_xml_string(xml):
	parser = etree.XMLParser(remove_blank_text=True)
	xml_string = ET.tostring(xml)
	xml_string = etree.tostring(etree.XML(xml_string, parser=parser))
	xml_string = parseString(xml_string)
	xml_string = xml_string.toprettyxml()
	return xml_string

# class ware_xml()
class Ware():
	root = ""
	ware = ""
	def __init__(self, file="ware_template.xml"):
		self.ware = read_xml(file)
		self.price = self.ware.find(".//price")
		self.production = self.ware.find(".//production")
		self.primary = self.production.find(".//primary")
		self.component = self.ware.find(".//component")
		self.restriction = self.ware.find(".//restriction")
		self.owner = self.ware.find(".//owner")
		self.root = self.ware

	def set_ware(self, id, name_ref, description_ref, group):
		self.ware.set('id', id)
		self.ware.set('name', name_ref)
		self.ware.set('description', description_ref)
		self.ware.set('group', group)
		self.production.set('name', name_ref)

	def set_price(self, min, average, max):
		self.price.set('min', min)
		self.price.set('average', average)
		self.price.set('max', max)
		

	def set_production(self, time):
		self.production.set('time', time)

	def add_production_comp(self, ware, amount):
		self.primary.append(ET.Element('ware', ware=ware, amount=amount))

	def clear_production_comp(self):
		for child in self.primary:
			self.primary.remove(child)

	def set_component(self, ref):
		self.component.set('ref', ref)

	def set_restriction(self, license):
		self.restriction.set('licence', license)

	def set_owner(self, faction):
		self.owner.set('faction', faction)

	def get_ware(self):
		return (
			self.ware.get('id'),
			self.ware.get('name'),
			self.ware.get('description'),
			self.ware.get('group')
			)

	def get_price(self):
		return(
			self.price.get('min'),
			self.price.get('average'),
			self.price.get('max')
			)

	def get_production(self):
		return(self.production.get('time'))

	def get_production_comps(self):
		comps = []
		for comp in self.primary:
			comps.append([comp.get('ware'), comp.get('amount')])
		return comps

	def get_component(self):
		return self.component.get('ref')

	def get_restriction(self):
		return self.restriction.get('licence')

	def get_owner(self):
		return self.owner.get('faction')

	#Generate a add diff to encapsulate the ware
	def to_xml_diff_string(self):
		root = ET.Element("diff")
		add = ET.Element('add', sel="/wares")
		root.append(add)
		add.append(self.ware)
		return to_xml_string(root)

	def to_xml_string(self):		
		return to_xml_string(self.ware)

class ship_xml:
	root = ET.Element("root")
	connections = ET.Element("connections")

	def add_connections(self, file):
		root = read_xml(file)
		for connection in root.findall(".//connection"):
			self.add_connection(connection)

	def add_connection(self, connection):
		self.connections.append(connection)

	def get_connections(self):
		pass

	def get_binary(self):
		return pickle.dumps(self)

	def get_name(self):
		pass

	def get_class(self):
		pass

	def reset_connections(self):
		for child in self.connections:
			self.connections.remove(child)

	def to_xml_string(self):
		return to_xml_string(self.root)

class ship_component(ship_xml):
	def __init__(self, file="component_template.xml"):
		super().__init__()
		self.components = read_xml(file)
		self.component = self.components.find(".//component")
		self.source = self.component.find(".//source")
		self.layers = self.component.find(".//layers")
		self.connections = self.component.find(".//connections")

		self.layer = self.layers.find(".//layer")
		self.waypoints = self.layer.find(".//waypoints")
		self.lights = self.layer.find(".//lights")
		self.cockpit = self.layer.find(".//connection[@ref='con_cockpit']/macro")
		self.root = self.components

	#some hidden stuff in here to fill manditory fields
	def set_name_class(self, ship_name, ship_class):
		self.component.set('name', ship_name)
		self.component.set('class', ship_class)

	def add_connection(self, connection):
		self.connections.append(connection)

	def add_waypoint(self, waypoint):
		self.waypoints.append(waypoint)

	def add_light(self, light):
		self.lights.append(light)

	def add_connections(self, connections):
		self.connections.extend(connections.findall(".//connection"))

	def add_waypoints(self, waypoints):
		self.waypoints.extend(waypoints.findall(".//waypoints"))

	def get_name(self):
		return self.component.get('name')

	def get_class(self):
		return self.component.get('class')

	def get_connections(self):
		connections_list = []
		for child in self.connections:
			name = child.get('name')
			tags = child.get('tags')
			connections_list.append("Name:%s Tags:%s" % (name, tags))
		return connections_list

	def to_xml_string(self):
		#Before we export we want to add some stuff (but only if its not already there)
		ship_name = self.get_name()
		ship_class = self.get_class()

		#This is ugly must be a better way
		has_container = False
		has_position = False
		has_space = False
		for child in self.connections:
			name = child.get('name')
			if name == "container":
				has_container = True
			elif name == "position":
				has_position = True
			elif name == "space":
				has_space = True
		if not has_container:
			ET.SubElement(self.connections, "connection", name="container", tags="contents", value="0")
		if not has_position:
			ET.SubElement(self.connections, "connection", name="position", tags="position", value="1")
		if not has_space:
			element = ET.SubElement(self.connections, "connection", name="space", tags="ship %s" % (ship_class))
			#This seems to be needed for some reason.
			ET.SubElement(element, "offset")

		ship_class = 'size_%s' % (ship_class.split('_')[-1])
		path = 'assets\\units\\%s\\%s_data' % (ship_class, ship_name)
		self.source.set('geometry', path)

		return super().to_xml_string()

	def get_materials(self):
		materials = []
		for material in self.connections.findall(".//material"):
			materials.append(material.get("ref"))
		return materials

class ship_macro(ship_xml):
	def __init__(self, file="macro_template.xml"):
		super().__init__()
		self.macros = read_xml(file)
		self.macro = self.macros.find(".//macro")
		self.component = self.macro.find(".//component")
		self.properties = self.macro.find(".//properties")
		self.connections = self.macro.find(".//connections")
		self.identification = self.properties.find(".//identification")
		self.software = self.properties.find(".//software")
		self.explosiondamage = self.properties.find(".//explosiondamage")
		self.storage = self.properties.find(".//storage")
		self.hull = self.properties.find(".//hull")
		self.secrecy = self.properties.find(".//secrecy")
		self.purpose = self.properties.find(".//purpose")
		self.people = self.properties.find(".//people")
		self.physics = self.properties.find(".//physics")
		self.inertia = self.physics.find(".//inertia")
		self.drag = self.physics.find(".//drag")
		self.thruster = self.properties.find(".//thruster")
		self.ship = self.properties.find(".//ship")
		self.root = self.macros

	def set_name_class(self, ship_name, ship_class):
		self.macro.set('name', ship_name + "_macro")
		self.macro.set('class', ship_class)
		self.set_component(ship_name)

	def set_component(self, ref):
		self.component.set('ref', ref)

	def set_id(self, name, base_name, desc, variation, short_variation, icon):
		for element in self.properties.findall(".//identification"):
			self.properties.remove(element)
		self.identification = ET.Element('identification',
			name=name,
			basename=base_name, 
			description=desc, 
			variation=variation, 
			shortvariation=short_variation,
			icon=icon
			)
		#use insert here cause.. it looks better in the macro
		self.properties.insert(0, self.identification)

	#marks manditory software ?
	def add_software(self, software):
		self.software.append(software)

	def add_connection(self, ref, comp_ref, comp_con):
		connection = ET.Element('connection', ref=ref)
		macro = ET.Element('macro')
		component = ET.Element('component', ref=comp_ref, connection=comp_con)
		macro.append(component)
		connection.append(macro)
		super().add_connection(connection)

	def set_explosiondamage(self, value):
		self.explosiondamage.set('value', value)

	def set_storage(self, missile, drones, people):
		self.storage.set('missile', missile)
		self.storage.set('unit', drones)
		self.people.set('capacity', people)

	def set_hp(self, max):
		self.hull.set('max', max)

	def set_secrecy(self, level):
		self.secrecy.set('level', level)

	def set_purpose(self, primary):
		self.purpose.set('primary', primary)

	def set_physics(self, mass, i_pitch, i_yaw, i_roll, d_forward, d_reverse, d_hor, d_vert, d_pitch, d_yaw, d_roll):
		#this is ugly and can be done better, but its late, I don;t wanna think and this works.
		self.physics.set('mass', mass)
		for child in self.physics:
			self.physics.remove(child)
		self.inertia = ET.Element('inertia',
			pitch=i_pitch,
			yaw=i_yaw,
			roll=i_roll
			)
		self.drag = ET.Element('drag',
			forward=d_forward,
			reverse=d_reverse,
			horizontal=d_hor,
			vertical=d_vert,
			pitch=d_pitch,
			yaw=d_yaw,
			roll=d_roll
			)
		self.physics.append(self.inertia)
		self.physics.append(self.drag)

	def set_people(self, capacity):
		self.people.set('capacity', capacity)

	def set_thruster(self, tags):
		self.thruster.set('tags', tags)
	
	def set_type(self, type):
		self.ship.set('type', type)

	#we want the name not name + _macro
	def get_name(self):
		return self.macro.get('name').replace('_macro', '')

	def get_class(self):
		return self.macro.get('class')

	def get_name_ref(self):
		return self.identification.get('name')

	def get_basename_ref(self):
		return self.identification.get('basename')

	def get_desc_ref(self):
		return self.identification.get('description')

	def get_variation_ref(self):
		return self.identification.get('variation')

	def get_short_variation_ref(self):
		return self.identification.get('shortvariation')

	def get_icon_ref(self):
		return self.identification.get('icon')

	def get_expl_dam(self):
		return self.explosiondamage.get('value')

	def get_storage_missile(self):
		return self.storage.get('missile')

	def get_storage_drone(self):
		return self.storage.get('unit')

	def get_storage_crew(self):
		return self.people.get('capacity')

	def get_mass(self):
		return self.physics.get('mass')

	def get_inertia(self):
		return self.inertia.get('pitch'), self.inertia.get('yaw'), self.inertia.get('roll')

	def get_drag(self):
		return (
			self.drag.get('forward'), 
			self.drag.get('reverse'), 
			self.drag.get('horizontal'),
			self.drag.get('vertical'),
			self.drag.get('pitch'),
			self.drag.get('yaw'),
			self.drag.get('roll')
			)

	def get_ship_type(self):
		return self.ship.get('type')

	def get_engine(self):
		return self.thruster.get('tags')

	def get_hp(self):
		return self.hull.get('max')

	def get_secrecy(self):
		return self.secrecy.get('level')

	def get_purpose(self):
		return self.purpose.get('primary')

	#The code in here is amost a duplicate of that in gui_support.py look for a way to get rid of this.
	def get_connections(self):
		connections_list = []
		for child in self.connections:
			con = child.get('ref')
			macro = child[0].get('ref')
			macro_connection = child[0].get('connection')
			connection = "macro:%s    ship_con:%s    macro_con:%s" % (macro, con, macro_connection)
			connections_list.append(connection)
		return connections_list

	#Sinse we monitor connections now we don't need this anymore
	# def to_xml_string(self):
	# 	# playercontrol = False
	# 	cockpit = False
	# 	for child in connections:
	# 		# if child.get('name') == 'con_playercontrol':
	# 		# 	playercontrol = True
	# 		if child.get('ref') == 'con_cockpit':
	# 			cockpit = True
	# 	if not cockpit:
	# 		element = ET.Element('connection', ref="con_cockpit")
	# 		ET.SubElement(element, 'macro', ref=self.cockpit_macro, connection='ship')


# component = ship_component()
# macro = ship_macro()

# macro.set_name_class("test_ship", "ship_xl")

# print(ET.dump(macro.root))

# file = open("component_template.bin","wb")
# file.write(component.get_binary())
# file.close()

# file = open("macro_template.bin","wb")
# file.write(macro.get_binary())
# file.close()