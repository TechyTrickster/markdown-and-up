import os, sys, imp, json, base64
from functools import reduce
from pathlib import Path


projectName = "markdown_and_up"
originalDir = os.getcwd()
scriptPath = Path(__file__)
scriptDir = scriptPath.parent
moveUpDegrees = lambda originalPath, amount : reduce(lambda x, y : x.parent, range(0, amount), originalPath)
potentials = list(map(lambda x : moveUpDegrees(scriptPath, x), range(0, len(scriptPath.parts))))
rootDir: Path = list(filter(lambda x : x.name == projectName, potentials))[-1] #should always grab the shortest possible, and therefore most likely to be actual root path, even if the root directory name was reused.
sys.path.append(str(rootDir))
sys.path = sorted(list(set(sys.path)))
print(sys.path)



class AppConfig():
    def __init__(self, platformPath: Path, featuresPath: Path, prettiesPath: Path, savedConfigPath: Path = None):
        self.platformPath = platformPath
        self.featuresPath = featuresPath
        self.prettiesPath = prettiesPath
        self.savedConfigPath = savedConfigPath
        self.platformsData = AppConfig.loadJson(self.platformPath)
        self.featuresData = AppConfig.loadJson(self.featuresPath)
        self.prettiesData = AppConfig.loadJson(self.prettiesPath)

        if self.savedConfigPath == None: #create new config object            
            self.platformSelected = AppConfig.configDefaultPlatform(self.platformPath)
            self.featuresConfig = AppConfig.configDefaultFeatures(self.featuresPath)
            self.prettiesConfig = AppConfig.configDefaultPretties(self.prettiesPath)  
        else: #load config data from file            
            buffer = AppConfig.loadJson(savedConfigPath)
            self.platformSelected = buffer['platform selected']
            self.featuresConfig = buffer['features config']
            self.prettiesConfig = buffer['pretties config']              


    @staticmethod
    def configDefaultPretties(inputData: dict) -> list[dict]:
        output = []
        for element in inputData:
            sourceCode = base64.b64decode(element['code'])
            newModule = imp.new_module(element['name'])
            exec(sourceCode, newModule.__dict__)
            code = lambda data, options : newModule.main(data, options)

            buffer = {
                'function': code,
                'options': element['options'],
                'active': element['default state']
            }
            output.append(buffer)

        return output


    @staticmethod
    def configDefaultFeatures(inputData: dict) -> list[str]:
        selections = list(filter(lambda x : x['default state'], inputData))
        output = list(map(lambda x : x["internal name"], selections))
        return output


    @staticmethod
    def configDefaultPlatform(inputData: dict) -> list[dict]:
        print(f"platform data: {inputData}")
        
        output = {}


    @staticmethod
    def loadJson(path: Path) -> dict:
        handle = open(path, "r")
        output = json.load(handle)
        handle.close()
        return output