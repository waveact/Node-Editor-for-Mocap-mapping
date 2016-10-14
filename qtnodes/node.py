"""Node classes."""

import uuid

import PySide2

from PySide2 import QtGui
from PySide2 import QtCore

from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtWidgets import QGraphicsProxyWidget

from .helpers import getTextSize
from .knob import Knob, InputKnob, OutputKnob
from .slider import Slider
from .exceptions import DuplicateKnobNameError


class Node(QGraphicsItem):
    """A Node is a container for a header and 0-n Knobs.

    It can be created, removed and modified by the user in the UI.
    """
    def __init__(self, **kwargs):
        super(Node, self).__init__(**kwargs)

        # This unique id is useful for serialization/reconstruction.
        self.uuid = str(uuid.uuid4())

        #self.proxyWidget = QGraphicsProxyWidget
        scene = self.scene()
        '''
        if ( scene != None ):
            scene.addWidget(PySide2.QtWidgets.QPushButton( "Start Record" ))
        '''
        self.header = None
        #self.slider = None
        
        self.isUpdate = False
        
        self.x = 0
        self.y = 0
        self.w = 10
        self.h = 10

        self.margin = 6
        self.roundness = 0

        self.fillColor = QtGui.QColor(220, 220, 220)

        # General configuration.
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self.setCursor(QtCore.Qt.SizeAllCursor)

        self.setAcceptHoverEvents(True)
        self.setAcceptTouchEvents(True)
        self.setAcceptDrops(True)
        
        self.value = None
    
    def start(self):
        return
        
    def stop(self):
        return
    
    def update(self):
        if (~self.isUpdate):
            #print str(self.uuid) + " is updated."
            
        #else:
            ####
            #if (self.slider(knob.name) != None):

            
            ####
            #print str(self.uuid) + " is not updated."
            self.isUpdate = True
            #print str(self.uuid) + " is updated."
            #print len(self.outputKnobs())
            
            for knob in self.inputKnobs():
                
                if len(knob.edges) != 0:
                
                    for edge in knob.edges:
                        if (edge.source != None):
                            edge.source.node().update()

                    knob.value = edge.source.value
                
                
            
            for knob in self.knobs():
                targetSlider = self.slider(knob.name)
                if (targetSlider != None):
                    #print str(hasSlider.sliderValue) + " ppp"
                    knob.value = targetSlider.sliderValue
        '''
        for knob in self.knobs():
            print knob.name
            print knob.value
        '''
        #print self.uuid
    
    def inputKnobs(self, cls=None):
        inputKnobs = []
        for child in self.childItems():
            if isinstance(child, InputKnob):
                inputKnobs.append(child)

        if cls:
            inputKnobs = filter(inputKnobs, lambda k: k.__class__ is cls)

        return inputKnobs
    
    def outputKnobs(self, cls=None):
        outputKnobs = []
        for child in self.childItems():
            if isinstance(child, OutputKnob):
                outputKnobs.append(child)

        if cls:
            outputKnobs = filter(outputKnobs, lambda k: k.__class__ is cls)

        return outputKnobs
    
    def knobs(self, cls=None):
        """Return a list of childItems that are Knob objects.

        If the optional `cls` is specified, return only Knobs of that class.
        This is useful e.g. to get all InputKnobs or OutputKnobs.
        """
        knobs = []
        for child in self.childItems():
            if isinstance(child, Knob):
                knobs.append(child)

        if cls:
            knobs = filter(knobs, lambda k: k.__class__ is cls)

        return knobs
        
    def knob(self, name):
        """Return matching Knob by its name, None otherwise."""
        for knob in self.knobs():
            if knob.name == name:
                return knob
        return None

    def sliders(self, cls=None):
        """Return a list of childItems that are Knob objects.

        If the optional `cls` is specified, return only Knobs of that class.
        This is useful e.g. to get all InputKnobs or OutputKnobs.
        """
        sliders = []
        for child in self.childItems():
            if isinstance(child, Slider):
                sliders.append(child)

        if cls:
            sliders = filter(sliders, lambda k: k.__class__ is cls)

        return sliders
        
    def slider(self, name):
        """Return matching Knob by its name, None otherwise."""
        for slider in self.sliders():
            if slider.name == name:
                return slider
        return None
        
        
    def boundingRect(self):
        """Return the bounding box of the Node, limited in height to its Header.

        This is so that the drag & drop sensitive area for the Node is only
        active when hovering its Header, as otherwise there would be conflicts
        with the hover events for the Node's Knobs.
        """
        rect = QtCore.QRect(self.x,
                            self.y,
                            self.w,
                            self.header.h)
        return rect

    def updateSizeForChildren(self):
        """Adjust width and height as needed for header and knobs."""

        def adjustHeight():
            """Adjust height to fit header and all knobs."""
            knobs = [c for c in self.childItems() if isinstance(c, Knob)]
            knobsHeight = sum([k.h + self.margin for k in knobs])
            heightNeeded = self.header.h + knobsHeight + self.margin
            self.h = heightNeeded
            
            sliders = [c for c in self.childItems() if isinstance(c, Slider)]
            slidersHeight = sum([k.h + self.margin for k in sliders])
            self.h = self.h + slidersHeight

        def adjustWidth():
            """Adjust width as needed for the widest child item."""
            headerWidth = (self.margin + getTextSize(self.header.text).width())

            knobs = [c for c in self.childItems() if isinstance(c, Knob)]
            knobWidths = [k.w + self.margin + getTextSize(k.displayName).width()
                          for k in knobs]
            maxWidth = max([headerWidth] + knobWidths)
            self.w = maxWidth + self.margin

        adjustWidth()
        adjustHeight()

    def addSlider(self, slider):
        #self.slider = slider
        children = [c for c in self.childItems()]
        yOffset = sum([c.h + self.margin for c in children])
        #print yOffset
        slider.setPos(0,yOffset)
        
        slider.setParentItem(self)
        self.updateSizeForChildren()
        
        
    def addHeader(self, header):
        """Assign the given header and adjust the Node's size for it."""
        self.header = header
        header.setPos(self.pos())
        header.setParentItem(self)
        self.updateSizeForChildren()

    def addKnob(self, knob):
        """Add the given Knob to this Node.

        A Knob must have a unique name, meaning there can be no duplicates within 
        a Node (the displayNames are not constrained though).

        Assign ourselves as the Knob's parent item (which also will put it onto
        the current scene, if not yet done) and adjust or size for it.

        The position of the Knob is set relative to this Node and depends on it
        either being an Input- or OutputKnob.
        """
        
        knobNames = [k.name for k in self.knobs()]
        if knob.name in knobNames:
            raise DuplicateKnobNameError(
                "Knob names must be unique, but {0} already exists."
                .format(knob.name))
        
        #print self.childItems()
        
        children = [c for c in self.childItems()]
        yOffset = sum([c.h + self.margin for c in children])
        
        #print yOffset
        
        xOffset = self.margin / 2

        knob.setParentItem(self)
        knob.margin = self.margin
        self.updateSizeForChildren()
        
        bbox = self.boundingRect()
        if isinstance(knob, OutputKnob):
            knob.setPos(bbox.right() - knob.w + xOffset, yOffset)
        elif isinstance(knob, InputKnob):
            knob.setPos(bbox.left() - xOffset, yOffset)
            

    def removeKnob(self, knob):
        """Remove the Knob reference to this node and resize."""
        knob.setParentItem(None)
        self.updateSizeForChildren()

    def paint(self, painter, option, widget):
        """Draw the Node's container rectangle."""
        painter.setBrush(QtGui.QBrush(self.fillColor))
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))

        # The bounding box is only as high as the header (we do this
        # to limit the area that is drag-enabled). Accommodate for that.
        bbox = self.boundingRect()
        painter.drawRoundedRect(self.x,
                                self.y,
                                bbox.width(),
                                self.h,
                                self.roundness,
                                self.roundness)

    def mouseMoveEvent(self, event):
        """Update selected item's (and children's) positions as needed.

        We assume here that only Nodes can be selected.

        We cannot just update our own childItems, since we are using
        RubberBandDrag, and that would lead to otherwise e.g. Edges
        visually lose their connection until an attached Node is moved
        individually.
        """
        nodes = self.scene().selectedItems()
        for node in nodes:
            for knob in node.knobs():
                for edge in knob.edges:
                    edge.updatePath()
        super(Node, self).mouseMoveEvent(event)
        
    def destroy(self):
        """Remove this Node, its Header, Knobs and connected Edges."""
        print("destroy node:", self)
        self.header.destroy()
        for knob in self.knobs():
            knob.destroy()

        scene = self.scene()
        scene.removeItem(self)
        del self
