from objc_util import *
import objc_util
import ui, ctypes
import swizzle
''' improved tableview:
	support for tableViewheightForRowAtIndexPath_
	
	'''
@on_main_thread
def tableView_willDisplayHeaderView_forSection_(_self,_sel,tv, v,section):
	tv_o=objc_util.ObjCInstance(_self)
	pyo=tv_o.pyObject(restype=c_void_p,argtypes=[])
	tv_py=ctypes.cast(pyo.value,ctypes.py_object).value
	if tv_py.delegate and hasattr(tv_py.delegate,'will_display_header'):
			tv_py.delegate.will_display_header(v,section)

@on_main_thread
def tableView_heightForRowAtIndexPath_(_self,_sel,tv,path):
	try:
		import sys, objc_util, ctypes
		# For some reason, tv returns a NSNumber.  But, our tableview is in _self
		tv_o=objc_util.ObjCInstance(_self)
		# get row and section from the path
		indexPath=objc_util.ObjCInstance(path)
		row=indexPath.row()
		section=indexPath.section()
		# get the pyObject.  get as an opaque pointer, then cast to py_object and deref 
		pyo=tv_o.pyObject(restype=ctypes.c_void_p,argtypes=[])
		tv_py=ctypes.cast(pyo.value,ctypes.py_object).value
		# if the delegate has the right method, call it
		if tv_py.delegate and hasattr(tv_py.delegate,'tableview_height_for_section_row'):
			return tv_py.delegate.tableview_height_for_section_row(tv_py,section,row)
		else:
			return tv_py.row_height
	except Exception as e:
		import traceback
		traceback.print_exc()
		return 44
# set up the swizzle.. only needs to be do e once
def setup_tableview_swizzle(override=False):
	t=ui.TableView()
	t_o=ObjCInstance(t)

	encoding=ObjCInstanceMethod(t_o,'rowHeight').encoding[0:1]+b'@:@@'
	if hasattr(t_o,'tableView_heightForRowAtIndexPath_') and not override:
		return
	swizzle.swizzle(ObjCClass(t_o._get_objc_classname()),
								('tableView:heightForRowAtIndexPath:'),
								tableView_heightForRowAtIndexPath_,encoding)

	encoding=b'v@:@@i'
	swizzle.swizzle(ObjCClass(t_o._get_objc_classname()),
		('tableView:willDisplayHeaderView:forSection:'),
		tableView_willDisplayHeaderView_forSection_,encoding)
#upon import, swizzle the textview class. this only ever needs to be done once, 
setup_tableview_swizzle(1)								


if __name__== '__main__':
	#import textview_rowheight

	#create tableview and delegate
	t=ui.TableView()
	t.frame=(0,0,200,576)
	d=ui.ListDataSource([str(x) for x in range(100)])
	t.data_source=d
	t.delegate=d
	
	# create custom height callback, add to delegate.  
	import random
	heights=[random.randrange(11,72) for x in range(100)]
	def tableview_height_for_section_row(tv,section,row):
		return heights[row]
	def tableview_number_of_sections(tv):
		return 2
	def tableview_title_for_header( tv,sec):
		return 'hoo'
	def will_display_header(v,section):
		ObjCInstance(v).contentView().backgroundColor=UIColor.redColor()
		
	d.tableview_height_for_section_row=tableview_height_for_section_row
	d.tableview_number_of_sections=tableview_number_of_sections
	d.tableview_title_for_header=tableview_title_for_header
	d.will_display_header=will_display_header
	# add an estimatedRowHeight. this is optional, but in theory improves performance
	t_o=ObjCInstance(t)
	t_o.estimatedRowHeight=44
	
	t.present('sheet')
