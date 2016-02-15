import glob
import sys
from sys import argv
import os
import re
import itertools

dirname, filename = os.path.split(os.path.abspath(__file__))
sys.path.append(dirname)

def get_image_info(data):
	if is_png(data):
		w, h = struct.unpack('>LL', data[16:24])
		width = int(w)
		height = int(h)
	else:
		raise Exception('not a png image')
	return width, height

def is_png(data):
	return (data[:8] == '\211PNG\r\n\032\n'and (data[12:16] == 'IHDR'))
	
def init():
		
	print ("Choose a Directory to Generate the Plugin:")
	prompt = "> "
	arg_dir = argv
	arg_dir = input(prompt)
	arg_dir = arg_dir.replace('"','')
	arr = ''
	if len(arg_dir) >= 1:
		direct = arg_dir
		direct = direct.rsplit('/', 1)[0]

		if not os.path.exists(direct):
			os.makedirs(direct)

		print ("Plugin Name:")
		plugin_name = argv
		plugin_name = input(prompt)

		print ("Plugin Controls, Comma Separated if Multiple:")
		plugin_ctrl_list = []
		plugin_ctrl = argv
		plugin_ctrl = input(prompt)

		if ',' in plugin_ctrl:
			plugin_list = plugin_ctrl.split(',')
			plugin_ctrl_list = [x.strip().upper() for x in plugin_list]

			print ("Your List Controls:" + str(plugin_ctrl_list))
		else:
			plugin_ctrl_list = plugin_ctrl
			print ("Your Controls:" + str(plugin_ctrl_list))

		print ("Plugin ID:")
		plugin_id = argv
		plugin_id = input(prompt)
		#
				#
		dir_target = direct +'\\'+ plugin_name
		os.makedirs(dir_target)
		#res directory
		dir_res = dir_target+'\\'+'res'
		os.makedirs(dir_res)
		#strings directory
		dir_str = dir_res+'\\'+'strings_us'
		os.makedirs(dir_str)
		#blank image
		gen_image = open(dir_target+'\\'+'res'+'\\'+plugin_name+'.tif', 'w')
		#res description and string_us description
		makedir_desc = [[dir_str, dir_res],['description']]
		for item in itertools.product(*makedir_desc):
			os.makedirs(os.path.join(*item))
		#c4d_symbols
		res = ''
		gen_symbols = open(dir_target+'\\'+'res'+'\\'+'c4d_symbols.h', 'w')
		contents_sym = ''
		o = len(plugin_ctrl_list);
		for ctrl in reversed(plugin_ctrl_list):
			contents_sym = '\t'+plugin_name.upper()+'_'+ctrl.upper()+','+'\n'+contents_sym
			o = o - 1

		res = res +'''enum
{
'''+contents_sym+'''
	// End of symbol definition
	_DUMMY_ELEMENT_
};
'''	
		gen_symbols.write( res + "\n"  )
		gen_symbols.close()

		#.str and .pyp
		makedir_desc = [[dir_target, dir_str+'\\'+'description'],[plugin_name]]
		i = 0
		for item in itertools.product(*makedir_desc):
			contents = ''
			if i == 1:
				for ctrl in reversed(plugin_ctrl_list):
					contents = '\t'+plugin_name.upper()+'_'+ctrl+' "'+ctrl.lower()+'";\n' + contents
					i = i - 1
				res = '''STRINGTABLE '''+plugin_name+'''
{
	'''+plugin_name+''' "'''+plugin_name+'''";

	'''+'\n'+contents+'''
}'''
				gen_file = open(os.path.join(*item)+'.str', 'w')
				gen_file.write( res + "\n"  )
				gen_file.close()
			else:
				res = '''import math
import os
import c4d
from c4d import plugins, utils, bitmaps
# for a Unique ID go to www.plugincafe.com
PLUGIN_ID = '''+plugin_id+'''\n'''

				o = len(plugin_ctrl_list);
				for ctrl in reversed(plugin_ctrl_list):
					contents = plugin_name.upper()+'_'+ctrl+' = '+str(10000+o)+'\n' + contents
					o = o - 1

				res = res +'\n'+ contents

				#adding rest of the plugin dummy code
				#dummy function arguments
				arguments = ''
				u = len(plugin_ctrl_list);
				for ctrl in reversed(plugin_ctrl_list):
					arguments = ctrl.lower()+','+ arguments
					u = u - 1

				new = arguments.rfind(",")
				arg = arguments[:new] + "" + arguments[new+1:]


				res = res + '''class '''+plugin_name+'''(plugins.ObjectData):'''+'''
	def DummyFunction(self, '''+arg+'''):
		print '''+arg+'''
	
	def Message(self, node, type, data):
		if type==c4d.MSG_MENUPREPARE:
			doc = data
		return True

	def Init(self, node):
		data = node.GetDataInstance()

'''		
				#initiate control values
				contents_a = ''
				o = len(plugin_ctrl_list);
				for ctrl in reversed(plugin_ctrl_list):
					contents_a = '\t\tself.InitAttr(node, float, [c4d.'+plugin_name.upper()+'_'+ctrl+'])'+'\n' + contents_a
					o = o - 1
				
				res = res + contents_a+'\n'
				#change control values
				contents_b = ''
				o = len(plugin_ctrl_list);
				for ctrl in reversed(plugin_ctrl_list):
					contents_b = '\t\tdata.SetReal(c4d.'+plugin_name.upper()+'_'+ctrl+','+str(o)+'0.0)'+'\n' + contents_b
					o = o - 1
				
				res = res + contents_b+'\n'

				#change values b
				contents_c = ''
				o = len(plugin_ctrl_list);
				for ctrl in reversed(plugin_ctrl_list):
					contents_c = '\t\t#node[c4d.'+plugin_name.upper()+'_'+ctrl+'] = '+str(o)+'0.0)'+'\n' + contents_c
					o = o - 1
				
				res = res + contents_c+'\n\t\treturn True'
				
				#draw function
				res = res + '''
	def Draw(self, op, drawpass, bd, bh):
		return c4d.DRAWRESULT_OK

'''
				#contour function
				contents_c = ''
				o = len(plugin_ctrl_list);
				for ctrl in reversed(plugin_ctrl_list):
					contents_c = 'ba.GetReal(c4d.'+plugin_name.upper()+'_'+ctrl+')'+', '+ contents_c
					o = o - 1
				
				new = contents_c.rfind(",")
				contents_c = contents_c[:new] + "" + contents_c[new+1:]
				contents_func = '''bb = self.DummyFunction('''+contents_c+''')'''

				res = res + '''
	def GetContour(self, op, doc, lod, bt):
		ba = op.GetDataInstance()
		'''+contents_func+'''

		if not bb: return None

		return bb'''

				#name
				res = res + '''
if __name__ == "__main__":
	path, file = os.path.split(__file__)
	bmp = bitmaps.BaseBitmap()
	bmp.InitWith(os.path.join(path, "res", "'''+plugin_name+'''.tif"))
	plugins.RegisterObjectPlugin(id=PLUGIN_ID, str="'''+plugin_name+'''",
								g='''+plugin_name+''',
								description="'''+plugin_name+'''", icon=bmp,
								info=c4d.OBJECT_GENERATOR|c4d.OBJECT_ISSPLINE)'''
				#
				gen_file = open(os.path.join(*item)+'.pyp', 'w')
				gen_file.write( res + "\n"  )
				gen_file.close()

			i = i + 1
		#.h and .res
		makedir_desc = [[dir_res+'\\'+'description'],[plugin_name+'.h', plugin_name+'.res']]
		i = 0
		for item in itertools.product(*makedir_desc):
			contents = ''
			if i == 1:
				for ctrl in reversed(plugin_ctrl_list):
					contents = '\t\tREAL '+plugin_name.upper()+'_'+ctrl+' { UNIT REAL; MIN 0.0; }'+ '\n' + contents
				res = '''CONTAINER '''+plugin_name+'''
{
	NAME '''+plugin_name+''';
	INCLUDE Obase;

	GROUP ID_OBJECTPROPERTIES
	{'''+'\n'+contents+'''	}
}'''
			else:
				u = len(plugin_ctrl_list);
				for ctrl in reversed(plugin_ctrl_list):
					contents = '\t'+plugin_name.upper()+'_'+ctrl+' = '+str(10000+u)+','+ '\n' + contents
					u = u - 1
				res = '''#ifndef _'''+plugin_name+'''_H_
#define _'''+plugin_name+'''_H_

enum
{
	'''+'\n'+contents+'''
};

#endif'''
				new = res.rfind(",")
				res = res[:new] + "" + res[new+1:]

			gen_file = open(os.path.join(*item), 'w')
			gen_file.write( res + "\n"  )
			gen_file.close()		

			i = i + 1
		#
		#struct_folder(plugin_name, target_directory)
		#
	# 	struct_3 = plugin_name+'''
	# res
	# 	'''+plugin_name+'''.pyp
	# 	description
	# 		'''+plugin_name+'''.h
	# 		'''+plugin_name+'''.res
	# 	strings_us
	# 		description
	# 			'''+plugin_name+'''.str
	# 	c4d_symbols.h'''


	# 	print(parse(struct_3))

	# 	for item in parse(struct_3):
	# 		try:
	# 			if isinstance(item, list):
	# 				#print ('\t'+'f '+str(item[0])+'\n')
	# 				for items in item:
	# 					if isinstance(items, list):
	# 						print ('\t'+'fs '+str(items[0])+'\n')
	# 					else:
	# 						print ('\t'+'fx '+str(items)+'\n')
	# 			else:
	# 				print ('f '+str(item)+'\n')

	# 		except IndexError:
	# 			pass
########################################################
		#make plugin folder
			#make res folder
				#make description folder
					#make plugin.h
					#make plugin.res
				#make string_language
					#make description folder
					#make plugin.str
					#make c4d_symbols.h
					#add plugin.tif
				#make plugin.pyp
########################################################

	# 	print('Batch Replacing')
	# 	url_list = ''

	# 	print ("String to Replace :")
	# 	prompt = "> "
	# 	string_replacement = argv
	# 	string_replacement = input(prompt)

	# 	for filename in os.listdir(lbf):

	# 		direct = lbf+'\\'+'replaced\\'

	# 		if not os.path.exists(direct):
	# 			os.makedirs(direct)
	# 		tempfile = open( direct+filename, 'a')

	# 		with open (lbf+'\\'+filename, "r") as myfile:
	# 			data=myfile.read().replace( string_replacement, 'E :')
	# 			tempfile.write(data)
		
	else:
		print("[EXITING]")

init()