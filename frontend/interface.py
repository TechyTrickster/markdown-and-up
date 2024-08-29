import sys, os
import time
from pathlib import Path
from functools import reduce
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib #, WebKit # type: ignore

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

from backend.previewGenerator import MarkdownPreview


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, platforms, features, pretties,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variable = False        
        self.backend = MarkdownPreview(features, pretties, platforms)
        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)        
        self.notebookBlock = Gtk.Notebook()
        self.eventKeys = Gtk.EventControllerKey()
        self.add_controller(self.eventKeys)
        self.eventKeys.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.pages = []

        #self.webView = WebKit.WebView()        
        self.sideBar = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)

        self.set_child(self.notebookBlock)

        

        menuElements = [
            {
                'title': "Open File",
                'internal name': "fileOpen",
                'function': self.openFile
            },
            {
                'title': "Save File",
                'internal name': "fileSave",
                'function': self.saveFile
            },
            {
                'title': "Perferences",
                'internal name': "launchPerferences",
                'function': self.launchPerferencesWindow
            },
            {
                'title': "About",
                'internal name': "aboutDialog",
                'function': self.launchAboutWindow
            },
            {
                'title': "Exit",
                'internal name': "closeApp",
                'function': self.closeApp
            }
        ]

        MainWindow.createDropDownMenu(menuElements, self.header, self)
        self.insertNewPage("", "new")
        self.changePage(0, [])
        self.eventKeys.connect("key-released", self.updateOutput, )
        self.notebookBlock.connect("change_current-page", self.changePage)


    def changePage(self, pageNumber: int, data):        
        self.notebookBlock.set_current_page(pageNumber)
        self.updateOutput()

    
    def updateOutput(self, keyval = "", keycode = 0, state = [], userData = []):
        print("update")        
        print()
        print(self.pages[self.notebookBlock.get_current_page()])
        print()
        print()
        print()
        print()
        (editingBuffer, previewBuffer) = self.pages[self.notebookBlock.get_current_page()]        
        text = editingBuffer.get_text(editingBuffer.get_start_iter(), editingBuffer.get_end_iter(), True)        
        self.backend.loadData(text)
        newText = self.backend.getPreview()        
        previewBuffer.set_text(newText)                



    def launchAboutWindow(self, action, param):        
        self.about = Gtk.AboutDialog()
        self.about.set_transient_for(self)  # Makes the dialog always appear in from of the parent window
        self.about.set_modal(True)  # Makes the parent window unresponsive while dialog is showing

        self.about.set_authors(["Andrew Phifer"])
        self.about.set_copyright("Copyright 2024 Andrew Phifer")
        self.about.set_license_type(Gtk.License.GPL_3_0)
        self.about.set_website("https://github.com/TechyTrickster")
        self.about.set_website_label("The Trickster's Hub")
        self.about.set_version("0.0.1")
        self.about.set_program_name("Marking Up and Down")
        self.about.set_logo_icon_name("/home/autumn/Documents/Projects/personal_page/frontend/favicon.ico")  # The icon will need to be added to appropriate location
                                                 # E.g. /usr/share/icons/hicolor/scalable/apps/org.example.example.svg
        self.about.set_visible(True)


    def insertNewPage(self, contents: str, label: str, position: int = -1):
        editingWindow = Gtk.TextView()
        previewWindow = Gtk.TextView()
        leftScrollWrapper = Gtk.ScrolledWindow()
        rightScrollWrapper = Gtk.ScrolledWindow()
        leftPaneFrame = Gtk.Frame()
        rightPaneFrame = Gtk.Frame()
        labelBox = Gtk.Label()

        core = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, homogeneous = True)
        leftPane = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, homogeneous = True)
        rightPane = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, homogeneous = True)

        leftScrollWrapper.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        rightScrollWrapper.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        leftPaneFrame.set_margin_start(3)
        leftPaneFrame.set_margin_end(3)
        leftPaneFrame.set_margin_top(2)
        leftPaneFrame.set_margin_bottom(2)
        rightPaneFrame.set_margin_start(3)
        rightPaneFrame.set_margin_end(3)
        rightPaneFrame.set_margin_top(2)
        rightPaneFrame.set_margin_bottom(2)        
        core.append(leftPane)        
        core.append(rightPane)        
        leftPane.append(leftPaneFrame)
        rightPane.append(rightPaneFrame)
        leftPaneFrame.set_child(leftScrollWrapper)
        leftScrollWrapper.set_child(editingWindow)
        rightPaneFrame.set_child(rightScrollWrapper)
        rightScrollWrapper.set_child(previewWindow)

        textBuffer0 = Gtk.TextBuffer()
        textBuffer1 = Gtk.TextBuffer()
        pageBuffer = (textBuffer0, textBuffer1)
        
        if position == -1:
            self.pages.append(pageBuffer)
        else:
            self.pages.insert(position, pageBuffer)

        textBuffer0.set_text(contents, len(contents))
        editingWindow.set_buffer(textBuffer0)
        previewWindow.set_buffer(textBuffer1)
        labelBox.set_label(label)

        self.notebookBlock.insert_page(core, labelBox, position)


    def openFile(self, action, param):
        self.openFileDialog = Gtk.FileChooserNative.new(title = "Select a markdown document to load", parent = self, action = Gtk.FileChooserAction.OPEN)        
        self.openFileDialog.connect("response", self.open_response)
        self.openFileDialog.show()        
        print("file dialog")

    
    def open_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            fileName = file.get_path()
            path = Path(fileName)
            #load file
            handle = open(fileName, "r")
            data = handle.read()
            handle.close()            
            self.insertNewPage(data, path.stem, -1)
            newPageNumber = len(self.pages)
            self.changePage(newPageNumber, [])
            self.updateOutput()
            print(fileName)


    def createNewNotebookPage(self, contents, name):
        self.notebookBlock.create


    def saveFile(self, action, param):
        #extract current editor contents
        #save to a file
        print("another file dialog")


    def exportFile(self, action, param):
        #extract current preview window contents
        #save to a file
        pass


    def getPreferencesFromWindow(self, param):
        buffer = param.getConfig()        
        print("preferences window")
        print(buffer)


    def launchPerferencesWindow(self, action, param):
        instance = OptionsWindow()
        instance.set_transient_for(self)
        instance.set_modal(True)
        instance.connect("close-request", self.getPreferencesFromWindow)
        instance.show()        


    def closeApp(self, action, param):
        sys.exit()


    def print_something(self, action, param):
        print("Something!")
        print(self.variable)

    
    def another(self, action, param):
        self.variable = True
        print(self.variable)


    @staticmethod
    def createDropDownMenu(parts: dict, attachPoint, windowRef):
        menu = Gio.Menu.new()

        for element in parts:
            action = Gio.SimpleAction.new(element['internal name'], None)
            action.connect("activate", element['function'])
            windowRef.add_action(action)
            linkName = f"win.{element['internal name']}"
            menu.append(element["title"], linkName)

        popover = Gtk.PopoverMenu()
        popover.set_menu_model(menu)
        hamburger = Gtk.MenuButton()
        hamburger.set_popover(popover)
        hamburger.set_icon_name("open-menu-symbolic")
        attachPoint.pack_start(hamburger)



class EditingWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Things will go here



class PreviewWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Things will go here        



class OptionsWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.box1 = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.box2 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.platformBox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.featureSwitchBox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.prettySwitchBox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.featureSwitchBox.set_spacing(3)
        self.prettySwitchBox.set_spacing(3)


        radioNames = ["GitHub", "Discord", "CommonMark", "OpenStreetMap", "Reddit", "SourceForge", "Stack Exchange", "GitLab", "Discourse", "Swift", "Custom"]
        switchNames = ["Extras", "Admonition", "CodeHilite", "Meta-Data", "New Line to Break", "Sane Lists", "Table of Contents", "mark", "tasklist", "tilde", "progress bars"]
        prettyNames = ["tables", "lists", "fluid code blocks", "fluid images"]
        self.platformSelectors = self.generateRadioButtonList(radioNames, self.platformBox, self.optionSelected)
        self.featureSwitches = self.generateSwitchList(switchNames, self.featureSwitchBox, self.switch_switched)
        self.prettySwitches = self.generateSwitchList(prettyNames, self.prettySwitchBox, self.switch_switched)

        self.set_child(self.box1)
        self.box1.append(self.box2)
        self.box1.append(self.platformBox)        
        self.box1.append(self.featureSwitchBox)
        self.box1.append(self.prettySwitchBox)        


    def optionSelected(self, event , option: str):
        print(option)
        print(event)


    def switch_switched(self, switch, state):
        print(switch)
        
        print(state)


    @staticmethod
    def createRadioButton(name, attachPoint, functionToTrigger: callable):
        output = Gtk.CheckButton(label = name)
        output.connect('toggled', functionToTrigger, name)
        attachPoint.append(output)
        return output


    def generateRadioButtonList(self, names: list[str], attachPoint, functionToTrigger: callable) -> list:
        initialRadio = OptionsWindow.createRadioButton(names[0], attachPoint, functionToTrigger)
        output = [initialRadio]
        
        for element in names[1:]:
            newRadio = OptionsWindow.createRadioButton(element, attachPoint, functionToTrigger)
            newRadio.set_group(initialRadio)
            buffer = {
                'radio element': newRadio,
                'name': element,
                'description': '',
                'state': newRadio.get_active()
            }

            output.append(buffer)

        return output
    

    def generateSwitchList(self, names: list[str], attachPoint, functionToTrigger: callable) -> list[dict]:
        output = []
        
        for element in names:
            newBox = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
            newSwitch = Gtk.Switch()            
            newLable = Gtk.Label(label = element)            
            newBox.set_spacing(5)
            newSwitch.set_active(False)
            newSwitch.connect("state-set", functionToTrigger)
            newBox.append(newSwitch)
            newBox.append(newLable)
            attachPoint.append(newBox)

            buffer = {
                'switch element': newSwitch,
                'label element': newLable,
                'name': element,
                'description': '',
                'state': False
            }
            output.append(buffer)

        return output
    

    def getConfig(self) -> dict:        
        output = {
            'feature switches': self.featureSwitches,
            'pretty switches': self.prettySwitches,
            'platform selectors': self.platformSelectors
        }

        return output



class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)        
        self.connect('activate', self.on_activate)
        self.platformPath = rootDir / 'data' / 'platforms.json'        
        self.featuresPath = rootDir / 'data' /  'features.json'
        self.prettiesPath = rootDir / 'data' /  'pretties.json'

    def on_activate(self, app):
        self.win = MainWindow(platforms = self.platformPath, features = self.featuresPath, pretties = self.prettiesPath, application=app)
        self.win.present()




app = MyApp(application_id="com.techytrickster.markupanddown")
app.run(sys.argv)