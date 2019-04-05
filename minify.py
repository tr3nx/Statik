import sys
import re

def css(css):
	css = re.sub(r'/\*[\s\S]*?\*/', "", css)
	css = re.sub(r'url\((["\'])([^)]*)\1\)', r'url(\2)', css)
	css = re.sub(r'\s+', ' ', css)
	css = re.sub(r':\s*0(\.\d+([cm]m|e[mx]|in|p[ctx]))\s*;', r':\1;', css)

	mincss = ""
	for rule in re.findall(r'([^{]+){([^}]*)}', css):
		selectors = [re.sub(r'(?<=[\[\(>+=])\s+|\s+(?=[=~^$*|>+\]\)])', r'', selector.strip()) for selector in rule[0].split(',')]
		properties = {}
		porder = []
		for prop in re.findall('(.*?):(.*?)(;|$)', rule[1]):
			key = prop[0].strip().lower()
			if key not in porder:
				porder.append(key)
			properties[key] = prop[1].strip()

		if properties:
			mincss = "{}{}{{{}}}".format(
				mincss,
				",".join(selectors),
				"".join(["{}:{};".format(key, properties[key]) for key in porder])
			)

	return mincss

def js(j):
	j = re.sub(r'\{\s+', '{', j)
	j = re.sub(r'\;\s+', ';', j)
	return j

def html(h):
	h = re.sub(r'\>\s+', '>', h)
	return h
