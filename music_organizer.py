import os, sys

id3TagMap = {"title": "TIT2",
			"artist": "TPE2",
			"album": "TALB"}

mp4TagMap = {"title": "\xa9nam",
			"artist": "\xa9ART",
			"album": "\xa9alb"}


class MusicOrganizer:

	def __init__(self, musicLib, verbose):
		if not os.path.isdir(musicLib):
			print(musicLib + " cannot be found.")
			sys.exit()
		self.musicLib = musicLib
		self.verbose = verbose
		self.filesNotMoved = []
		self.filesMovedCount = 0

	def organize(self, path):
		if os.path.isdir(path):
			self.organizeFolder(path)
		elif os.path.isfile(path):
			self.organizeFile(path)
		else:
			return

		if self.verbose >= 1:
			self.displayStats()


	def organizeFolder(self, folder):
		for item in os.listdir(folder):
			fpath = os.path.join(folder, item)
			if os.path.isdir(fpath):
				self.organizeFolder(fpath)
			elif os.path.isfile(fpath):
				self.organizeFile(fpath)


	def organizeFile(self, songPath):
		from shutil import copyfile
		try:
			s = Song(songPath)
			s.load()
			if not s.ok:
				print("Error creating Song Object for " + songPath)
				return

			title = str(s.title).strip()
			artist = str(s.artist).strip()
			album = str(s.album).strip()

			albumDir = self.makeAlbumDir(artist, album)
			newSongPath = os.path.join(albumDir, title) if title != 'None' else os.path.join(albumDir, self.uniqueSongName(albumDir, s.ext))
			
			if not os.path.exists(newSongPath):
				copyfile(songPath, newSongPath)
				self.filesMovedCount += 1

		except Exception as e:
			self.filesNotMoved.append(songPath)

	def makeAlbumDir(self, artist, album):
		artistDir = os.path.join(self.musicLib, artist) if artist != 'None' else os.path.join(self.musicLib, "Unknown Artist")
		if not os.path.isdir(artistDir):
			os.mkdir(artistDir)

		albumDir = os.path.join(artistDir, album) if album != 'None' else os.path.join(artistDir, "Unknown Album")
		if not os.path.isdir(albumDir):
			os.mkdir(albumDir)

		return albumDir


	def uniqueSongName(self, albumpath, extenstion):
		count = len(os.listdir(albumpath))
		name = "unknown_" + str(count) + extenstion
		return name

	def displayStats(self):
		numNotMoved = len(self.filesNotMoved)
		print(str(self.filesMovedCount) + " files moved.")
		print(str(numNotMoved) + " not moved.")
		if numNotMoved > 0 and verbose == 2:
			print("Files not moved:")
			for f in self.filesNotMoved:
				print(f)


class Song:
	def __init__(self, path):
		if not os.path.exists(path):
			print(path + " does not exist.")
			sys.exit()
		self.path = path
		self.funcMap = None
		self.ext = os.path.splitext(self.path)[1]
		self.ok = True

	def load(self):
		if self.funcMap == None:
			self.createFuncMap()
		self.funcMap[self.ext]()

	def loadMP3(self):
		from mutagen.mp3 import MP3
		try:
			mp3 = MP3(self.path)
			self.title = self.safeAssign("TIT2", mp3)
			self.artist =self.safeAssign("TPE1", mp3)
			self.album = self.safeAssign("TALB", mp3)
		except Exception as e:
			self.ok = False
			print("Error createing MP3")
			print(e.args)

	def loadMP4(self):
		from mutagen.mp4 import MP4
		try:
			mp4 = MP4(self.path)
			self.title = self.safeAssign("\xa9nam", mp4)
			self.artist =self.safeAssign("\xa9ART", mp4)
			self.album = self.safeAssign("\xa9alb", mp4)
		except Exception as e:
			self.ok = False
			print("Error createing M4P")
			print(e.args)

	def loadFLAC(self):
		from mutagen.flac import FLAC
		try:
			flac = FLAC(self.path)
			tags = flac.tags
			self.title = self.safeAssign("title", tags)
			self.artist = self.safeAssign("artist", tags)
			self.album = self.safeAssign("album", tags)
		except Exception as e:
			self.ok = False
			print("Error createing FLAC")
			print(e.args)


	def safeAssign(self, key, obj):
		try:
			 value = obj[key]
			 if type(value) == list:
			 	value = str(value[0])
			 elif type(value == unicode):
			 	value = str(value)
			 return value
		except:
			return None


	def createFuncMap(self):
		self.funcMap = {".mp3": self.loadMP3,
						".FLAC": self.loadFLAC,
						".flac": self.loadFLAC,
						".m4a": self.loadMP4,
						".mp4": self.loadMP4}

if __name__ == '__main__':
	ipodDir = None
	musicLib = None
	verbose = 2
	try:
		ipodDir = sys.argv[1]
		musicLib = sys.argv[2]
		if(len(sys.argv) > 3):
			verbose = int(sys.argv[3])
	except:
		ipodDir = raw_input("File Directory to Orgainze: ")
		musicLib = raw_input("Music Library: ")
		verbose = int(raw_input("Verbosity [0, 1, 2]: "))

	if not os.path.exists(ipodDir):
		print(ipodDir + " cannot be found.")
		sys.exit()
	if not os.path.exists(musicLib):
		print(musicLib + " cannot be found.")
		sys.exit()

	MO = MusicOrganizer(musicLib, verbose)
	MO.organize(ipodDir)