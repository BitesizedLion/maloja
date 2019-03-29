import os
import shutil

from ._internal import defaultarguments


_config = {}

# set configuration
# defaultextension	unused
# files				list of all files that will be used for configuration. high indicies overwrite low indicies
# comment			symbols that indicate comments. careful!
# category			symbols that indicate start and end of category name. only works at start of line
# onlytext			interpret everything as a string. if False, strings can be put into quotes to avoid confusion
def config(defaultextension=".ini",files=["settings.ini","settings.conf","configuration.ini","configuration.conf"],
			comment=["#","//"],category=("[","]"),onlytext=False):

	global _config
	_config["defaultextension"] = defaultextension
	_config["files"] = files
	_config["comment"] = comment
	_config["category"] = category
	_config["onlytext"] = onlytext

# initial config on import, set everything to default
config()




def _interpret(text):
	if _config["onlytext"]: return text

	if text.lower() in ["true","yes"]: return True
	if text.lower() in ["false","no"]: return False
	if text.lower() in ["none","nan","n/a",""]: return None
	if text.startswith("'") and text.endswith("'"): return text[1:-1]
	if text.startswith('"') and text.endswith('"'): return text[1:-1]
	try:
		return int(text)
	except:
		pass
	try:
		return float(text)
	except:
		pass
	return text


# get settings
# keys			list of requested keys. if present, will return list of according values, if not, will return dict of key-value pairs
# files			which files to parse. later files (higher indicies) will overload earlier ones
# prefix		only request keys with a certain prefix. key filter will still be applied if present
# cut_prefix	return keys without the prefix
# category		return only keys of specific category
# raw			do not interpret data type, only return strings
@defaultarguments(_config,files="files")
def get_settings(*keys,files,prefix="",cut_prefix=False,category=None,raw=False):

	allsettings = {}

	for f in files:
		if not os.path.exists(f): continue

		# if category is specified, ignore all entries by default and switch when we encounter the right heading
		ignore = False if category is None else True

		with open(f) as file:
			lines = file.readlines()


		for l in lines:
			# clean up line
			l = l.replace("\n","")
			for symbol in _config["comment"]:
				l = l.split(symbol)[0]
			l = l.strip()

			# check if valid settings entry
			if l == "": continue
			if l.startswith(_config["category"][0]):
				# ignore category headers if we don't care
				if category is None: continue
				# otherwise, find out if this is the category we want
				else:
					if l.endswith(_config["category"][1]):
						cat = l[len(_config["category"][0]):-len(_config["category"][1])]
						ignore = not (cat == category) #if this is the right heading, set ignore to false
					continue

			if ignore: continue

			if "=" not in l: continue

			# read
			(key,val) = l.split("=")
			key = key.strip()
			val = val.strip() if raw else _interpret(val.strip())

			if key.startswith(prefix):
				# return keys without the common prefix
				if cut_prefix:
					allsettings[key[len(prefix):]] = val

				# return full keys
				else:
					allsettings[key] = val

	# no arguments means all settings
	if len(keys) == 0:
		return allsettings

	# specific keys requested
	else:
		if len(keys) == 1: return allsettings.get(keys[0])
		else: return [allsettings.get(k) for k in keys]


def update_settings(file,settings,create_new=False):

	if not os.path.exists(file): open(file,"w").close()

	with open(file,"r") as origfile:
		lines = origfile.readlines()

	newlines = []

	for origline in lines:
		l = origline
		# clean up line
		l = l.replace("\n","")
		for symbol in _config["comment"]:
			l = l.split(symbol)[0]
		l = l.strip()

		# check if valid settings entry
		if l == "":
			newlines.append(origline)
			continue
		if l.startswith(_config["category"][0]):
			newlines.append(origline)
			continue
		if "=" not in l:
			newlines.append(origline)
			continue

		# read
		(key,val) = l.split("=")
		key = key.strip()
		val = val.strip()


		if key not in settings:
			newlines.append(origline)
			continue

		else:
			#print("Found key")
			newline = origline.split("=",1)
			#print({"linepart":newline[1],"keytoreplace":val,"new":settings[key]})
			newline[1] = newline[1].replace(val,str(settings[key]),1)
			newline = "=".join(newline)
			newlines.append(newline)

			del settings[key]

	if create_new:
		# settings that were not present in the file
		for key in settings:
			newlines.append(key + " = " + settings[key] + "\n")

	with open(file,"w") as newfile:
		newfile.write("".join(newlines))




# updates a user settings file to a newer format from a default file without overwriting user's settings
def update(source="default_settings.ini",target="settings.ini"):

	if not os.path.exists(target):
		shutil.copyfile(source,target)
	else:
		usersettings = get_settings(files=[target],raw=True)
		shutil.copyfile(source,target)
		update_settings(target,usersettings)
