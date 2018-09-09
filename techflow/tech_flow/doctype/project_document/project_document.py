# -*- coding: utf-8 -*-
# Copyright (c) 2018, QuasarPM.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe 
from frappe.model.document import Document

from frappe.desk.form.load import get_attachments, get_versions, get_badge_info, get_view_logs, get_docinfo
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from frappe.utils import strip, get_files_path, get_url, file_manager
import os

@frappe.whitelist()
def load_pages(doc):
	pages_list = frappe.get_all("Project Document Pages", fields=["name","pdf_preview","page_name"],
		filters={
			"parent": doc
	})
	print('List of Pages Len:', len(pages_list))

	file_info = "something other useful"
	return pages_list, file_info


class ProjectDocument(Document):
	def onload(self):
		print('function on load************************************')
		pages_list, file_info = load_pages(self.name)
		self.get("__onload").pages_list = pages_list
		self.get("__onload").file_info = self.name




		

@frappe.whitelist()
def split_pages(args):
	self = frappe.get_doc("Project Document", args)
	this_args = frappe.get_all("Project Document Pages", filters= {
		'parent':args
	})
	for doc in this_args:
		print(doc.name)
		print(type(doc))
		try:
			frappe.delete_doc("Project Document Pages", doc.name)
		except Exception:
				frappe.throw(""" Not permitted. Do Not Know Why. """)

	
	
	


	

	###
	### Find the right public/private folder for attachments
	###

	files = get_attachments(self.doctype, self.name)
	path = frappe.get_app_path('techflow').split('/')
	
	folders = []
	
	for folder in path:
		
		if (folder != 'apps'):
			folders.append(folder)
		else:
			folders.append('sites')
			break
	
	fp_url =  get_files_path(files[0]['file_name'])
	file_path = '/'.join(folders) + fp_url[1:]

	##
	## PyPDF2 at Work
	##

	
	pdf_file = PdfFileReader(file_path)
	print('Number of Pages: ', pdf_file.getNumPages())
	print(self.get_value('project'))

	prj_folder = "ProjectDocuments"
	print('Folder Project Document Exists:',bool(frappe.db.exists('File', {'name': r"Home/ProjectDocuments", 'is_folder': 1})))
	
	if frappe.db.exists('File', {'name': r"Home/ProjectDocuments", 'is_folder': 1}):
		print('the folder exists')
	else:
		print('try to create folder...........')
		home = frappe.get_doc("File","Home")
		print(home.name)
		prj_doc_folder = frappe.get_doc({
			"doctype": "File",
			"is_folder": 1,
			"folder": home.name,
			"file_name": "ProjectDocuments"
		})
		prj_doc_folder.save()
	##
	##  Create the Project Folder
	##
	prj_path = r"/"+self.get_value('project')
	if frappe.db.exists('File', {'name': r"Home/ProjectDocuments"+prj_path, 'is_folder': 1}):
		print('the Project folder exists')
	else:
		print('try to create Project folder...........')
		parent_folder = frappe.get_doc("File",r"Home/ProjectDocuments")
		print(parent_folder.name)
		prj_folder = frappe.get_doc({
			"doctype": "File",
			"is_folder": 1,
			"folder": parent_folder.name,
			"file_name": self.get_value('project')
		})
		prj_folder.save()
	
	##
	##  Create the Document Folder
	##
	doc_path = r"/"+self.name
	if frappe.db.exists('File', {'name': r"Home/ProjectDocuments"+prj_path+doc_path, 'is_folder': 1}):
		print('the Document folder exists')
	else:
		print('try to create Document folder...........')
		parent_folder = frappe.get_doc("File",r"Home/ProjectDocuments"+prj_path)
		print(parent_folder.name)
		doc_folder = frappe.get_doc({
			"doctype": "File",
			"is_folder": 1,
			"folder": parent_folder.name,
			"file_name": self.name
		})
		doc_folder.save()
	
	##
	##  PDF Split and Save Single PDF Pages
	##


	#folder_path = r"Home/ProjectDocuments"+prj_path+doc_path
	#print(folder_path)
	
	page_count = 0
	for page in range(pdf_file.getNumPages()):
		page_count += 1
		page_file = pdf_file.getPage(page)
		
		output = PdfFileWriter()
		output.addPage(page_file)

		public_files = frappe.get_site_path('public', 'files')
		#public_files = r"/files/"
		abs_path = os.path.abspath(public_files) + r"/"
		file_path = r"/" + self.name +"_page_" + str(page) + ".pdf"
		output_path = abs_path + file_path

		output_stream = open(output_path, 'wb')

		output.write(output_stream)
		output_stream.close()
		
		##
		##  Create New Document Page for every PDF page
		##

		print('inside the loop', page)
		p_document_page = frappe.get_doc({
			"doctype": "Project Document Pages",
			"parenttype": "Project Document",
			"parentfield": "document_pages",
			"parent": self.name,
			"idx": page,
			"page_name": str(page) +" "+self.get_title(),
			#"file_url": output_path
			})
		
		p_document_page.insert()


		##
		##  Create New File Doc for every PDF page
		##
		
		
		print('The cached key for Project Document Pages')
		frappe.get_document_cache_key("Project Document Pages", p_document_page.name)
		
		#print(type(p_document_page_name))
		#print(p_document_page_name)
		last = frappe.get_last_doc("Project Document Pages")
		print('cache:', p_document_page.name)
		print('last:', last.name)

		
		frappe.get_doc({
			"doctype": "File",
			"attached_to_doctype": "Project Document Pages",
			"attached_to_name": p_document_page.name,
			"file_url": r"/files" + file_path,
			"file_name": file_path[1:],
			"folder": r"Home/ProjectDocuments"+prj_path+doc_path
			}).save()
	frappe.msgprint("The document has been splitted in {} pages.".format(page_count))
	
	
			
	return args