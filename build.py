#!/usr/bin/python3

import re
import os
import json
import glob
import mistune
import minify
from mako.lookup import TemplateLookup

site = {
	"title": "Statik",
	"url": "http://localhost"
}

buildPath  = "./build"
templatePath  = "./templates"
workingPath  = "./working"

templates = TemplateLookup(directories=[templatePath])

files = []

def delete_folder(path):
	if not os.path.isdir(path):
		return

	fs = os.listdir(path)	
	for f in fs:
		fp = os.path.join(path, f)
		if os.path.isdir(fp):
			delete_folder(fp)
		else:
			os.remove(fp)

	os.rmdir(path)

def trim(s, r):
	if len(s) > 0:
		if s[0] == r:
			s = s[1:]
		if s[-1] == r:
			s = s[:-1]

	return s

def stitch_path(*parts):
	parts = list(filter(None, parts))
	ret = "" if not "." in parts[0][0] else "."

	for p in parts:
		p = trim(p, "/")
		p = p.replace("./", "")
		ret += "/" + p

	return ret

def generate_files():
	for f in files:
		if not len(f):
			continue

		filename = f['filename']
		folder = f['folder']

		wp = stitch_path(workingPath, folder, filename)
		with open(wp, "r") as fi:
			data = fi.read()

			if not len(data):
				continue

			bp = stitch_path(buildPath, folder)
			if not os.path.isdir(bp):
				os.makedirs(bp)

			bfp = stitch_path(bp, filename)

			for run in f['engines']:
				data = run(data)

			with open(bfp, "w") as fo:
				fo.write(data)

def render_page(data):
	datalines = data.split("\n", 1)
	meta = json.loads(datalines[0:1][0])
	data = "".join(datalines[1:])
	data = templates.get_template(meta['template']).render(
		meta = meta,
		body = mistune.markdown(data),
	)
	return data

def parse_file(filename, path):
	fp = path.replace(workingPath, "")

	file = {
		"filename": filename,
		"folder": fp,
	}

	if ".md" in filename:
		file["engines"] = [render_page, minify.html]
		file["ext"] = ".html"

	elif ".css" in filename:
		file["engines"] = [minify.css]

	elif ".js" in filename:
		file["engines"] = [minify.js]

	files.append(file)

def parse_folder(path):
	for f in os.listdir(path):
		fp = os.path.join(path, f)
		if os.path.isdir(fp):
			parse_folder(fp)
			continue

		parse_file(f, path)

if __name__ == "__main__":
	parse_folder(workingPath)
	generate_files()
