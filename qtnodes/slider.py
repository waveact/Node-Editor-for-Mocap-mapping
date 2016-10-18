"""Node header."""
import uuid

from PySide2 import QtGui
from PySide2 import QtCore

from PySide2.QtWidgets import QGraphicsItem

from .helpers import getTextSize


class Slider(QGraphicsItem):
    """A Header is a child of a Node and gives it a title.

    Its width resizes automatically to match the Node's width.
    """
    def __init__(self, node, text, **kwargs):
        super(Slider, self).__init__(**kwargs)
        
        self.name = text
        
        self.node = node
        self.sliderValue = 0
        self.text = str(self.sliderValue)
        
        self.uuid = str(uuid.uuid4())
        
        self.x = 0
        self.y = 0
        self.h = 10
        self.w = 0
        #self.parent = 
        
        self.textColor = QtGui.QColor(0, 0, 0)
        self.fillColor = QtGui.QColor(255, 255, 255)
        self.setAcceptTouchEvents(True)
    
    def boundingRect(self):
        nodebox = self.node.boundingRect()
        rect = QtCore.QRect(self.x,
                            self.y,
                            self.w,
                            self.h)
        return rect

    def paint(self, painter, option, widget):
        # Draw background rectangle.
        self.w = self.parentItem().w
        bbox = self.boundingRect()

        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        painter.setBrush(self.fillColor)
        
        painter.drawRoundRect(0, 0, self.parentItem().w*self.sliderValue, 10, 0, 0)
        '''
        painter.drawRoundedRect(bbox,
                                self.node.roundness,
                                self.node.roundness)
        '''
        
        # Draw header label.
        if self.node.isSelected():
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0)))
        else:
            painter.setPen(QtGui.QPen(self.textColor))

        # # centered text
        # textSize = getTextSize(painter, self.text)
        # painter.drawText(self.x() + (self.node.w - textSize.width()) / 2,
        #                  self.y() + (self.h + textSize.height() / 2) / 2,
        #                  self.text)

        # left aligned text
        #textSize = getTextSize(self.text, painter=painter)

        painter.drawText(0, self.h, str(self.text))
        
        '''
        painter.drawText(self.x() + self.node.margin,
                         self.y() + (self.h + textSize.height() / 2) / 2,
                         self.text)
        '''
    def calculateValue(self, event):
        limit_w = self.mapFromScene(event.scenePos())
        temp = round(limit_w.x()/self.parentItem().w,2)
        if (temp < 0):
            temp = 0
        elif (temp > 1) :
            temp = 1
        else:
            temp = temp
        self.sliderValue = temp
        self.text = str(self.sliderValue)
    
    def mousePressEvent(self, event):
        """Handle Edge creation."""

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.calculateValue(event)
            self.update()
            return

    def mouseMoveEvent(self, event):
        """Update Edge position when currently creating one."""
        #self.setPos(event.scenePos().x, )
        #print event.scenePos().x()
        #print ("enter")
        #limit_w = self.mapFromScene(event.scenePos())
        #print limit_w.x()/self.parentItem().w*2
        #self.sliderValue = limit_w.x()/self.parentItem().w
        #self.text = str(self.sliderValue)
        self.calculateValue(event)
        self.update()
        #print (limit_w.x())
        #limit_w = self.mapFromParent(self.x, self.y).x()*-1
        
        #if ( limit_w.x() < self.parentItem().w ):
            #print limit_w.x()
        #self.setX(self.mapFromScene(event.scenePos()).x())
        #self.setX(10)
        
        #print self.parentItem().w
        #print self.mapFromParent(self.x, self.y).x()

    def mouseReleaseEvent(self, event):
        """Finish Edge creation (if validations are passed).

        TODO: This currently implements some constraints regarding the Knob
          connection logic, for which we should probably have a more
          flexible approach.
        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.calculateValue(event)
            self.update()
            return
            
    
    def destroy(self):
        """Remove this object from the scene and delete it."""
        print("destroy header:", self)
        scene = self.node.scene()
        scene.removeItem(self)
        del self
