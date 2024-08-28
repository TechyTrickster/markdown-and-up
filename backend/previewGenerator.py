import os, sys, imp, json, base64
from functools import reduce
from markdown import Markdown
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



class MarkdownPreview():
    def __init__(self, featureFilePath: Path, prettyFilePath: Path, platformFilePath):
        self.pageData = ""
        self.htmlVersion = ""        
        self.isUpdated = False
        self.featuresOptionsList = MarkdownPreview.loadJson(featureFilePath)
        self.prettyOptionsList = MarkdownPreview.loadJson(prettyFilePath)
        self.platformList = MarkdownPreview.loadJson(platformFilePath)
        self.prettyConfig = MarkdownPreview.loadPretty(self.prettyOptionsList)
        self.featuresConfig = MarkdownPreview.loadFeatures(self.featuresOptionsList)
        self.platformConfig = MarkdownPreview.loadPlatform(self.platformList)


    @staticmethod
    def loadPretty(inputData: dict) -> list[dict]:
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
    def loadFeatures(inputData: dict) -> list[str]:
        selections = list(filter(lambda x : x['default state'], inputData))
        output = list(map(lambda x : x["internal name"], selections))
        return output


    @staticmethod
    def loadPlatform(inputData: dict) -> list[dict]:
        pass


    @staticmethod
    def loadJson(path: Path) -> dict:
        handle = open(path, "r")
        output = json.load(handle)
        handle.close()
        return output


    def setPrettyConfig(self, inputConfig: list[dict]):
        self.prettyConfig = inputConfig


    def setFeaturesConfig(self, inputConfig: list[str]):
        self.featuresConfig = inputConfig


    def showPrettyConfigList(self) -> list[dict]:
        return self.prettyOptionsList
    

    def showFeaturesConfigList(self) -> list[dict]:
        return self.featuresOptionsList
        

    def loadData(self, inputData: str):
        self.isUpdated = False
        self.pageData = inputData        


    def generatePreview(self) -> str:
        converter = Markdown(extensions = self.featuresConfig)
        buffer = converter.convert(self.pageData)
        self.htmlVersion = reduce(lambda data, element : element['function'](data, element['options']) if element['active'] else data, self.prettyConfig, buffer)
        self.isUpdated = True
        return self.htmlVersion



    def getPreview(self) -> str:
        if self.isUpdated:
            output = self.htmlVersion
        else:
            output = self.generatePreview()

        return output