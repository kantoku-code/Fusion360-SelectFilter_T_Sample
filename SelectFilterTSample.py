#Fusion360API Python script
#Author-kantoku
#Description-Selection Filter SketchConstraints like

import adsk.core, adsk.fusion, traceback

_commandId = 'SelectFilterTSample'
_SelIptInfo = ['SktConstraints','Select SketchConstraint','Select SketchConstraint']

_handlers = []
_app = None
_ui = None

class CommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            adsk.terminate()
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class PreSelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.SelectionEventArgs.cast(args)

            selSktCon :adsk.core.SelectionCommandInput = eventArgs.firingEvent.activeInput
            try:
                preType :str = eventArgs.selection.entity.objectType.split('::')[-1]
                if not preType in selSktCon.getFilterT():
                    eventArgs.isSelectable = False
                    return
                eventArgs.isSelectable = True
            except:
                eventArgs.isSelectable = False
                
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmd = args.command

            onDestroy = CommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            onPreSelect = PreSelectHandler()
            cmd.preSelect.add(onPreSelect)
            _handlers.append(onPreSelect)

            inputs = cmd.commandInputs
            selSktCon = inputs.addSelectionInput(_SelIptInfo[0], _SelIptInfo[1], _SelIptInfo[2])
            selSktCon.setSelectionLimits(0)

            # Extension Method
            register_SelectionCommandInput_ExtensionMethod()

            # Addition by FilterT list
            selSktCon.addFilterT([
                'SketchAngularDimension',
                'SketchConcentricCircleDimension',
                'SketchDiameterDimension',
                'SketchLinearDimension',
                'SketchEllipseMajorRadiusDimension',
                'SketchEllipseMinorRadiusDimension'])

            # FilterT string addition
            selSktCon.addFilterT(
                'SketchOffsetDimension,SketchRadialDimension,hoge')
            
            # Partial deletion of FilterT
            selSktCon.removeFilterT('hoge')

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        cmdDefs = _ui.commandDefinitions
        cmdDef = cmdDefs.itemById(_commandId)
        if cmdDef:
            cmdDef.deleteMe()

        cmdDef = cmdDefs.addButtonDefinition(_commandId, _commandId, _commandId)

        onCmdCreated = CommandCreatedHandler()
        cmdDef.commandCreated.add(onCmdCreated)
        _handlers.append(onCmdCreated)
        cmdDef.execute()

        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# -- SelectionCommandInput Extension Method --
_filterT = {}

def register_SelectionCommandInput_ExtensionMethod():
    selCmdIput = adsk.core.SelectionCommandInput

    selCmdIput.addFilterT = addFilterT
    selCmdIput.getFilterT = getFilterT
    selCmdIput.clearFilterT = clearFilterT
    selCmdIput.removeFilterT = removeFilterT

def addFilterT(self, filters):
    fType = type(filters)
    fs = []
    if fType is str:
        fs =  list(filters.split(','))
    elif fType is list:
        fs = filters
    else:
        print('filters type errer')
        return fs

    global _filterT
    if self.id in _filterT:
        tmp = _filterT[self.id]
        tmp.extend(fs)
        _filterT[self.id] = list(set(tmp))
    else:

        _filterT[self.id] = fs

def getFilterT(self):
    global _filterT
    if not self.id in _filterT:
        return []
    
    return _filterT[self.id]

def clearFilterT(self):
    global _filterT
    if self.id in _filterT:
        _filterT[self.id] = []

def removeFilterT(self, filter):
    global _filterT
    if not self.id in _filterT:
        return

    _filterT[self.id].remove(filter)