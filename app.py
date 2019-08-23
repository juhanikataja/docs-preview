#!/usr/bin/env python3
import git, os, mkdocs, subprocess

from flask import Flask

# defaults

defaultWorkPath = "work"
defaultBuildRoot = "/tmp/preview-bot/builds"
defaultRemoteUrl = "https://github.com/CSCfi/csc-user-guide"
defaultSecret = "changeme" # we are using secret but we should be utilizing whitelists
defaultPort = 8081

try:
  workPath = os.environ["WORKPATH"]
except KeyError:
  workPath = defaultWorkPath

try:
  buildRoot = os.environ["BUILDROOT"]
except KeyError:
  buildRoot = defaultBuildRoot

try:
  buildSecret = os.environ["BUILDSECRET"]
except KeyError:
  buildSecret = defaultSecret

# Configuration 

config = {
    "workPath": workPath, #"work",
    "remoteUrl": "https://github.com/CSCfi/csc-user-guide",
    "buildRoot": buildRoot, # "/home/jkataja/workspace/csc-user-guide/preview-bot/builds",
    "debug": True, 
    "secret": buildSecret
    }

buildState = {}

##

def initRepo(workPath, remote_url):
  mkdirp(workPath)

  repo = git.Repo.init(workPath)

  origin = repo.remote('origin')
  if not origin.exists():
    origin = repo.create_remote('origin', remote_url)

  assert origin.exists()
  assert origin == repo.remotes.origin == repo.remotes['origin']
  

  for fetch_info in origin.fetch():
    print("Updated %s in %s" % (fetch_info.ref, fetch_info.commit))

  return repo, origin

def mkdirp(path):
  os.makedirs(path, exist_ok=True)

def buildRef(repo, ref, state):
  if not str(ref.commit) == state["built"]:
    print(str(ref.commit), state["built"])
    print("re-building %s in %s" % (ref, ref.commit))
    buildpath = config["buildRoot"]
    buildpath = os.path.join(buildpath, str(ref))
    print("buildpath = %s" % (buildpath))
    mkdirp(buildpath)
    cmd = "sh -c 'cd %s && mkdocs build --site-dir %s'" % (config["workPath"], buildpath)
    print("Executing: %s" % (cmd))
    cmdout = os.popen(cmd)
    print(cmdout.read())
    
    state["built"] = str(ref.commit)

app = Flask(__name__)

@app.route("/build/<string:secret>", methods=["GET"])
def listenBuild(secret):
  global buildState

  if not secret == config["secret"]:
    return "Access denied"

  repo, origin = initRepo(config["workPath"], config["remoteUrl"])
  output = ""

  # Clean buildState 
  for ref in origin.refs:
    sref = str(ref)
    output = output + "Found %s (%s)<br>" % (sref, str(ref.commit))
    
    if not sref in buildState:
      print(sref + " not found in " + str(buildState))
      buildState[sref] = {"sha": str(ref.commit), "status": "init", "built": None}

  # Refresh builds
  for ref in origin.refs:
    buildRef(repo, ref, buildState[str(ref)])

  return "listenBuilt:<br>" + output

if __name__=="__main__":
  print("workPath: " + workPath)
  print("buildRoot: " + buildRoot)
  print("buildSecret: " + "******")

  if buildSecret == defaultSecret:
    print("Don't use default secret since it's freely available in the internet")
    os.exit(1)

  app.run(debug=config["debug"], port=defaultPort, host='0.0.0.0')

def debug():
  repo, origin = initRepo(config["workPath"], config["remoteUrl"])

  for ref in origin.refs:

    print("ref %s (%s)" % (ref, ref.commit))
    sref = str(ref)
    if not sref in buildState:
      buildState[sref] = {"sha": str(ref.commit), "status": "init", "built": None}

  for ref in origin.refs:
    buildRef(repo, ref, buildState[str(ref)])
