from subprocess import call
import xml.etree.ElementTree as ET

# 'static' vars
files = [];
direc = "gittut";

def initGit():
    link = 'https://github.com/OpenExoplanetCatalogue/open_exoplanet_catalogue.git'
    call(["git", "--bare", "clone", link])
    link = link.split('/')[-1][0:-4]
    call(["git", "push", "--set-upstream", "origin", "master"], cwd=link)
    return link
    
def saveDirName(direc):
    file = open('dirname', 'w')
    file.write(direc)
    file.close()

def getDirName():
    try:
        file = open('dirname', 'r')
        return file.read()
    except IOError:
        return None

def UpdateRepo():
    # check for local github repo
    direc = getDirName()
    if(direc == None):
        direc = initGit()
        saveDirName(direc)

    # updating github repo
    call(["git", "fetch"], cwd=direc)
    call(["git", "pull"], cwd=direc)
    # commit process
    # require login info first
    #call(["git", "add", "."] + files, cwd=direc)
    #call(["git", "commit", "-m", "automated commit"], cwd=direc)
    #call(["git", "push"], cwd=direc)

# later just take proposedChange, and get sysname from that using another method
def modifyXML(sysName, proposedChange):
    oec = ET.parse("open_exoplanet_catalogue/systems/" + sysName + ".xml")
    for starXML in oec.findall(".//star"):
        for planetXML in starXML.findall(".//planet"):
            for child in planetXML.findall(".//mass"):
                child.text="21"
                oec.write("open_exoplanet_catalogue/systems/" + sysName + ".xml")
                print(child.text)

# def getSystemName(proposedChange):
# def commitAndPull():

# INSTALL THIS STUFF TO TO PULL REQUESTS:
# sudo apt-get install ruby-full
# sudo curl -O https://storage.googleapis.com/golang/go1.6.linux-amd64.tar.gz
# sudo tar -xvf go1.6.linux-amd64.tar.gz
# sudo mv go /usr/local
# vi ~/.profile
# add export PATH=$PATH:/usr/local/go/bin to end of file
# source ~/.profile
# cd back to hub checkedout and then: make
# git clone https://github.com/github/hub.git
# sudo ln -s /home/eric/Desktop/bob/hub/bin/hub /usr/local/bin/hub
# sudo apt-install linuxbrew-wrapper
# brew install hub
if __name__ == "__main__":
    # UpdateRepo()
    modifyXML("11 Com", ("20", "19.4"))
