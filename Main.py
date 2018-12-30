#Main.py
from tkinter import filedialog, Tk, messagebox
import xml_classes
import pickle
import x3d_parser
import os
import subprocess

class Main:
	project_file = ""
	mesh_file = ""
	mesh_file_path = ""
	x3d_file = ""
	x3d_file_path = ""

	def __init__(self):
	#Generate ship and component
		self.component = xml_classes.ship_component()
		self.macro = xml_classes.ship_macro()
		self.ware = xml_classes.Ware()

	def import_component(self,file):
		self.component = xml_classes.ship_component(file)
		self.component.set_name_class(self.macro.get_name, self.macro.get_class)

	def import_macro(self,file):
		self.macro = xml_classes.ship_macro(file)
		self.component.set_name_class(self.macro.get_name, self.macro.get_class)

	def import_x3d(self, file):
		with open(file, 'r') as f:
			self.x3d_file = f.read()
		self.x3d_file_path = file.split('/')[-1]

	def import_mesh(self, file):
		with open(file, 'r') as f:
			self.mesh_file = f.read()
		self.mesh_file_path = file.split('/')[-1]

	def import_project(self, file):
		project = ""
		with open(file, "rb") as f:
			project = pickle.load(f)
		self.component = project["component"]
		self.macro = project["macro"]
		self.x3d_file = project['x3d_file']
		self.mesh_file = project['mesh_file']
		self.x3d_file_path = project['x3d_file_path']
		self.mesh_file_path = project['mesh_file_path']
		self.ware = project['ware']

	def save_project(self):
		project = {
		"component":self.component,
		"macro":self.macro,
		"ware" : self.ware,
		"mesh_file":self.mesh_file,
		"x3d_file":self.x3d_file,
		"mesh_file_path":self.mesh_file_path,
		"x3d_file_path":self.x3d_file_path
		}

		f = open(self.project_file, "wb+")
		binary = pickle.dump(project, f)
		f.close()

	def clear_project(self):
		self.component = xml_classes.ship_component()
		self.macro = xml_classes.ship_macro()
		self.ware = xml_classes.Ware()
		self.project_file = ""
		self.mesh_file = ""
		self.mesh_file_path = ""
		self.x3d_file = ""
		self.x3d_file_path = ""

	def set_project_file(self, file):
		self.project_file = file

	def get_project_file(self):
		return self.project_file

	def export_macro(self, file):
		macro = self.macro.to_xml_string()
		with open(file, 'w+') as f:
			f.write(macro)

	def export_component(self, file):
		component = self.component.to_xml_string()
		with open(file, 'w+') as f:
			f.write(component)

	def export_ware(self, file):
		ware = self.ware.to_xml_string()
		with open(file, 'w+') as f:
			f.write(ware)

	#Should probably use bindings to update when stuff gets typed
	def update_vars(self, var_dict):
		#Macro Vars
		var_dict['engine_size_var'].set(self.macro.get_engine())
		var_dict['expl_damage_var'].set(self.macro.get_expl_dam())
		var_dict['missile_storage_var'].set(self.macro.get_storage_missile())
		var_dict['drone_storage_var'].set(self.macro.get_storage_drone())
		var_dict['crew_compliment_var'].set(self.macro.get_storage_crew())
		var_dict['hitpoints_var'].set(self.macro.get_hp())
		var_dict['secrecy_var'].set(self.macro.get_secrecy())
		var_dict['purpose_var'].set(self.macro.get_purpose())
		var_dict['mass_var'].set(self.macro.get_mass())
		yaw, pitch, roll = self.macro.get_inertia()
		var_dict['inertia_yaw_var'].set(yaw)
		var_dict['inertia_roll_var'].set(roll)
		var_dict['inertia_pitch_var'].set(pitch)
		forward, reverse, horizontal, vertical, pitch, yaw, roll = self.macro.get_drag()
		var_dict['drag_forward_var'].set(forward)
		var_dict['drag_reverse_var'].set(reverse)
		var_dict['drag_vertical_var'].set(horizontal)
		var_dict['drag_hor_var'].set(vertical)
		var_dict['drag_pitch_var'].set(pitch)
		var_dict['drag_yaw_var'].set(yaw)
		var_dict['drag_roll_var'].set(roll)
		var_dict['name_var'].set(self.macro.get_name())
		var_dict['class_var'].set(self.macro.get_class())
		var_dict['type_var'].set(self.macro.get_ship_type())
		var_dict['name_ref_var'].set(self.macro.get_name_ref())
		var_dict['base_name_ref_var'].set(self.macro.get_basename_ref())
		var_dict['desc_ref_var'].set(self.macro.get_desc_ref())
		var_dict['variant_ref_var'].set(self.macro.get_variation_ref())
		var_dict['short_variant_ref_var'].set(self.macro.get_short_variation_ref())
		var_dict['icon_ref_var'].set(self.macro.get_icon_ref())
		#Ware Vars
		id, name, desc, group = self.ware.get_ware()
		var_dict["ware_group_var"].set(group)
		min, max, everage = self.ware.get_price()
		var_dict["ware_price_min_var"].set(min)
		var_dict["ware_price_max_var"].set(max)
		var_dict["ware_price_average_var"].set(everage)
		var_dict["ware_production_time_var"].set(self.ware.get_production())
		var_dict["ware_licence_var"].set(self.ware.get_restriction())
		var_dict["ware_faction_var"].set(self.ware.get_owner())
		var_dict["ware_comp_list_var"].set(self.ware.get_production_comps())

	def update_xml(self, var_dict):
		##Macro
		ship_name = var_dict['name_var'].get()
		ship_class = var_dict['class_var'].get()
		self.macro.set_name_class(ship_name, ship_class)
		##Comp
		self.component.set_name_class(ship_name, ship_class)

		name_var = var_dict['name_ref_var'].get()
		base_name = var_dict['base_name_ref_var'].get()
		desc = var_dict['desc_ref_var'].get()
		variation = var_dict['variant_ref_var'].get()
		short_variation = var_dict['short_variant_ref_var'].get()
		icon = var_dict['icon_ref_var'].get()
		self.macro.set_id(name_var, base_name, desc, variation, short_variation, icon) 

		value = var_dict['expl_damage_var'].get()
		self.macro.set_explosiondamage(value) 

		missile = var_dict['missile_storage_var'].get()
		drones = var_dict['drone_storage_var'].get()
		people = var_dict['crew_compliment_var'].get()
		self.macro.set_storage(missile, drones, people) 

		hp = var_dict['hitpoints_var'].get()
		self.macro.set_hp(hp) 

		level = var_dict['secrecy_var'].get()
		self.macro.set_secrecy(level)

		primary = var_dict['purpose_var'].get()
		self.macro.set_purpose(primary) 

		mass = var_dict['mass_var'].get()
		i_pitch = var_dict['inertia_pitch_var'].get()
		i_yaw = var_dict['inertia_yaw_var'].get()
		i_roll = var_dict['inertia_roll_var'].get()
		d_forward = var_dict['drag_forward_var'].get()
		d_reverse = var_dict['drag_reverse_var'].get()
		d_hor = var_dict['drag_hor_var'].get()
		d_vert = var_dict['drag_vertical_var'].get()
		d_pitch = var_dict['drag_pitch_var'].get()
		d_yaw = var_dict['drag_yaw_var'].get()
		d_roll = var_dict['drag_roll_var'].get()
		self.macro.set_physics(mass, i_pitch, i_yaw, i_roll, d_forward, d_reverse, d_hor, d_vert, d_pitch, d_yaw, d_roll) 
		
		capacity = var_dict['crew_compliment_var'].get()
		self.macro.set_people(capacity) 

		tags = var_dict['engine_size_var'].get()
		self.macro.set_thruster(tags) 

		type = var_dict['type_var'].get()
		self.macro.set_type(type)

		#ware vars
		id = self.macro.get_name()
		name = self.macro.get_name_ref()
		desc = self.macro.get_desc_ref()
		group = var_dict['ware_group_var'].get()
		self.ware.set_ware(id, name, desc, group)

		self.ware.set_component('%s_macro' % (self.macro.get_name()))

		min = var_dict["ware_price_min_var"].get()
		max = var_dict["ware_price_max_var"].get()
		average = var_dict["ware_price_average_var"].get()
		self.ware.set_price(min, average, max)

		time = var_dict["ware_production_time_var"].get()
		self.ware.set_production(time)

		licence = var_dict["ware_licence_var"].get()
		self.ware.set_restriction(licence)

		owner = var_dict["ware_faction_var"].get()
		self.ware.set_owner(owner)

		self.ware.clear_production_comp()
		if var_dict["ware_comp_list_var"].get() != "":
			for item in list(eval(var_dict["ware_comp_list_var"].get())):
				self.ware.add_production_comp(item[0], item[1])

	def output(self, folder, mirror, index, content):
		#TODO break this up into defs
		#Make sure to update the xml before calling this! DONE!

		#Generate file structure
		ship_class = self.macro.get_class()
		ship_class = 'size_%s' % (ship_class.split('_')[-1])
		ship_name = self.macro.get_name()

		dirs = [
		'/assets',
		'/assets/units',
		'/assets/units/%s' % (ship_class),
		'/assets/units/%s/macros' % (ship_class),
		'/index',
		'/libraries'
		]
		for path in dirs:
			try:
				print(folder+path)
				os.makedirs(folder + path)
			except FileExistsError:
				continue

		#Write DAE file to folder:
		if self.mesh_file != "":
			file = folder + '/assets/units/%s/%s.dae' % (ship_class, ship_name)
			with open(file, 'w+') as f:
				f.write(self.mesh_file)
			#Get dds files (textures)
			#ddss = get_dss_path(file)

		#Write macro
		file = folder + '/assets/units/%s/macros/%s_macro.xml' % (ship_class, ship_name)
		with open(file, 'w+') as f:
			f.write(self.macro.to_xml_string())

		if self.x3d_file != "":
			#Process connections from loaded file x3d file
			connections, waypoints = x3d_parser.parse_connections(self.x3d_file, mirror)
			self.component.add_connections(connections)
			self.component.add_waypoints(waypoints)

		#Write component
		file = folder + '/assets/units/%s/%s.xml' % (ship_class, ship_name)
		with open(file, 'w+') as f:
			f.write(self.component.to_xml_string())

		#run converter if we have a mesh to convert that is.
		materials = []
		if self.mesh_file != "":
			program='%s/XRConvertersMain.exe' % (os.getcwd())
			dae_file = folder + '/assets/units/%s/%s.dae' % (ship_class, ship_name)
			arguments=('exportxmf "%s" "%s"' % (folder, dae_file))
			print(program, arguments)
			subprocess.call('%s %s' % (program, arguments))

			#Inform users about possible material properties.
			new_component = xml_classes.ship_component(file)
			materials = new_component.get_materials()

		#Generate index patches?
		if index:
			file = folder + '/index/macros.xml'
			index_macros = xml_classes.gen_index_macros('/assets/units/%s/macros/%s_macro' % (ship_class, ship_name))
			with open(file, 'w+') as f:
				f.write(xml_classes.to_xml_string(index_macros))
			
			file = folder + '/index/components.xml'
			index_components = xml_classes.gen_index_components('/assets/units/%s/%s' % (ship_class, ship_name))
			with open(file, 'w+') as f:
				f.write(xml_classes.to_xml_string(index_components))

			file = folder + '/libraries/wares.xml'
			with open(file, 'w+') as f:
				f.write(self.ware.to_xml_diff_string())

		#Generate content?
		if content:
			file = folder + '/content.xml'
			content = xml_classes.gen_content(ship_name)
			with open(file, 'w+') as f:
				f.write(xml_classes.to_xml_string(content))

		return materials