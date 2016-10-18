import os, PySide2, struct, socket, json, Queue
from PySide2 import QtGui
from PySide2.QtWidgets import QWidget
from PySide2.QtCore import QThread
from PySide2 import QtCore
from PySide2.QtWidgets import *

from qtnodes import (Header, Node, InputKnob,
                     OutputKnob, NodeGraphWidget, Slider)

facewareList = [ "01.mouth_rightMouth_stretch", "02.mouth_leftMouth_narrow", "03.mouth_up", "04.mouth_leftMouth_stretch", "05.mouth_rightMouth_narrow", "06.mouth_down", "07.mouth_upperLip_left_up", "08.mouth_upperLip_right_up", "09.mouth_lowerLip_left_down", "10.mouth_lowerLip_right_down", "11.mouth_leftMouth_frown", "12.mouth_rightMouth_frown", "13.mouth_leftMouth_smile", "14.mouth_rightMouth_smile", "19.eyes_leftEye_blink", "20.eyes_rightEye_blink", "21.eyes_leftEye_wide", "22.eyes_rightEye_wide", "23.brows_leftBrow_up", "24.brows_leftBrow_down", "25.brows_rightBrow_up", "26.brows_rightBrow_down", "27.brows_midBrows_up", "28.brows_midBrows_down", "29.jaw_open", "30.jaw_left", "31.jaw_right", "33.mouth_right", "34.mouth_left", "35.mouth_phoneme_mbp", "36.mouth_phoneme_ch", "37.mouth_phoneme_fv", "38.head_up", "39.head_down", "40.head_left", "41.head_right", "42.head_LeftTilt", "43.head_RightTilt" ]

                 
feRegularList = [ "01.Brows Raise Inner Left        ", "02.Brows Raise Inner Right", "03.Brows Raise Outer Left", "04.Brows Raise Outer Right", "05.Brows Drop Left", "06.Brows Drop Right", "07.Brow Raise Left", "08.Brow Raise Right", "09.Cheek Raise Left", "10.Cheek Raise Right", "11.Lips Drop", "12.Nose Scrunch", "13.Nose Flank Raise Left", "14.Nose Flank Raise Right", "15.Nose Flank Raise", "16.Lips Smirk", "17.Lips Smirk Left", "18.Lips Smirk Right", "19.Lips widen sides", "20.Lips Drop Sides", "21.Lips drop left side", "22.Lips drop right side", "23.Chin Raise", "24.Lips Puckered", "25.Lips widen", "26.Lips Puckered Open", "27.Eyelids Enlarge", "28.Lips Zipped Tight", "29.Mouth Open", "30.Lips Raise Top", "31.Lips Tuck", "32.Eye Squint", "33.Eye Blink", "34.Eye Blink Left", "35.Eye Blink Right", "36.Lips Open" ]

feCustomList = [ "01.", "02.", "03.", "04.", "05.", "06.", "07.", "08.", "09.", "10.", "11.", "12.", "13.", "14.", "15.", "16.", "17.", "18.", "19.", "20.", "21.", "22.", "23.", "24." ]

feEye = []

feHead = []

class Const(Node):
    def __init__(self, *args, **kwargs):
        super(Const, self).__init__(*args, **kwargs)
        self.className = "Const"
        self.addHeader(Header(node=self, text="0"))
        self.addKnob(OutputKnob(name="value"))
        self.value = 0
        
    def mouseDoubleClickEvent(self, event):
        self.setValueDialog = QDialog()
        #setValueDialog.setWindowTitle = "aaa"
        vBoxLayout = PySide2.QtWidgets.QVBoxLayout()
        self.setValueDialog.setLayout(vBoxLayout)
        self.spinbox = QSpinBox()
        self.spinbox.setMaximum(100)
        self.spinbox.setMinimum(-100)
        self.spinbox.setValue( self.value )
        vBoxLayout.addWidget( self.spinbox )
        self.applyButton = QPushButton("Apply")
        vBoxLayout.addWidget( self.applyButton )
        self.applyButton.clicked.connect( self.applyButtonPress )
        self.setValueDialog.show() 
        self.setValueDialog.exec_()
    
    def applyButtonPress(self):
        self.value = self.spinbox.value()
        print self.value
        self.knob("value").value = self.value
        self.setValueDialog.reject()
        #self.header.setHeader("Const: " + str(self.value))
        self.header.setHeader(str(self.value))
        
    def update(self):
        super(Const, self).update()
        #debugMsg(self.knob("a").value)
        #debugMsg(self.knob("b").value)
        self.value = self.knob("value").value
        #self.header.setHeader("Const: " + str(self.value))
        self.header.setHeader(str(self.value))
        #debugMsg(self.value)

class Weight(Node):
    def __init__(self, *args, **kwargs):
        super(Weight, self).__init__(*args, **kwargs)
        self.addHeader(Header(node=self, text=self.__class__.__name__))
        self.addSlider(Slider(node=self, text="result"))
        self.addKnob(OutputKnob(name="result"))
        #self.addKnob(OutputKnob(name="value1"))
        
class Multiply(Node):
    def __init__(self, *args, **kwargs):
        super(Multiply, self).__init__(*args, **kwargs)
        self.addHeader(Header(node=self, text=self.__class__.__name__))
        self.addKnob(InputKnob(name="a"))
        self.addKnob(InputKnob(name="b"))
        self.addKnob(OutputKnob(name="value"))
        
    def update(self):
        super(Multiply, self).update()
        self.knob("value").value = self.knob("a").value * self.knob("b").value
        self.value = self.knob("value").value
        print self.knob("value").value
       
class Add(Node):
    def __init__(self, *args, **kwargs):
        super(Add, self).__init__(*args, **kwargs)
        self.addHeader(Header(node=self, text=self.__class__.__name__))
        self.addKnob(InputKnob(name="a"))
        self.addKnob(InputKnob(name="b"))
        self.addKnob(OutputKnob(name="value"))
    
    def update(self):
        super(Add, self).update()
        self.knob("value").value = self.knob("a").value + self.knob("b").value
        self.value = self.knob("value").value
        #print self.knob("value").value

class CacheBuffer():
    def __init__(self):
        self.queue = Queue.Queue(maxsize = 10)
        self.lock = False
        
    def setData( self, dataX ):
        if self.queue.qsize() == 10:
            return
        while self.lock == True:
            pass
        self.lock = True
        #print 'setData'
        self.queue.put(dataX)
        #print self.queue.qsize()
        self.lock = False
        
    def getData(self):
        if self.queue.qsize() == 0:
            return None
        self.lock = True
        while self.queue.qsize() != 0:
            data = self.queue.get()
        self.lock = False
        return data
        
class DataThread(QThread):
    def __init__(self,subData,parent=None):
        QThread.__init__(self,parent)
        self.subData = subData
    
    def run(self):
        while True:
            if ( self.subData.sock != None ):
                self.subData.streamCacheBuffer.setData( self.subData.sock.recv(64*1024) )
                self.subData.loop()
        #self.sleep(0)
        
class Faceware(Node):

    def __init__(self, *args, **kwargs):
        global facewareList
        #QThread.__init__(self)
        super(Faceware, self).__init__(*args, **kwargs)
        self.sock = None
        self.addHeader(Header(node=self, text=self.__class__.__name__))
        #self.addWidget(PySide2.QtWidgets.QPushButton( "Start Record" ))
        for i in range(len(facewareList)):
            self.addKnob(OutputKnob(name=facewareList[i]))
        self.thread = None
        self.serverExiting = False
       
    def start(self):
        if self.sock == None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            facewareSock_server_address = ('localhost', 802)
            self.sock.settimeout(5)
            try:
                self.streamCacheBuffer = CacheBuffer()
                self.sock.connect(facewareSock_server_address)
                self.thread = DataThread(self)
                self.thread.start()
                self.loop()
                if self.serverExiting == False:
                    self.serverExiting = True
            except socket.timeout:
                self.serverExiting = False
        
        
    def stop(self):
        print "stop"
        if ( self.thread != None ):
            print "thread is" + str(self.thread.isRunning())
            self.thread.terminate()
            self.thread.wait()
            print "thread is " + str(self.thread.isRunning())
            self.thread = None
        if ( self.sock != None ):
            self.sock.close()
            self.sock = None
        self.serverExiting = False
        #icpy===================
        #scriptEvent.StopTimer()
        #=======================
    
    def loop(self):
        #while True:
        received = self.streamCacheBuffer.getData()
        if (received != None):
            #print received
            self.extractData(received)
    
    def extractData(self, received):
        reciv=received[0]+received[1]+received[2]+received[3]
        blockSize = struct.unpack('i', reciv)[0]
        print "blockSize: " + str(blockSize)
        if (len(received)) >= blockSize:
            dataType = "i"
            for i in range(len(received)-4, 0, -1):
                dataType = dataType+"c"
            dataStream = struct.unpack(dataType, received)
            data = ""
            for i in range(1, blockSize, 1):
                data = data + dataStream[i]
            data = data + "}"
            decodejson = json.loads(data)
            self.analystData(data)
        
    def analystData(self,_json):
        
        packer = struct.Struct('iifffffffffffffffffffffffffffffffffffffffffffffffff')
        bufferSize = struct.calcsize('iifffffffffffffffffffffffffffffffffffffffffffffffff')
        
        decodejson = json.loads(_json)
        data = decodejson["animationValues"]
        
        for name in facewareList:
            data_name = name.split(".")[1]
            try:
                self.knob(name).value = data[data_name]
            except:
                pass
            
        self.value = []
        for knob in self.knobs():
            self.value.append(knob.value)
        '''
        for value in data:
            print data[facewareList[]]
        '''
        '''
        filePath, _ = QFileDialog.getSaveFileName(
                None,
                "Save Scene to JSON",
                os.path.join(QtCore.QDir.currentPath(), "faceware.json"),
                "JSON File (*.json)"
            )
        
        if filePath:
            with open(filePath, "w") as f:
                f.write(str(_json) + "\n")
        '''
        #print self.value
        
    def update(self):
        super(Faceware, self).update()
    
class FacialExpression(Node):
    def __init__(self, *args, **kwargs):
        global feRegularList
        super(FacialExpression, self).__init__(*args, **kwargs)
        self.addHeader(Header(node=self, text=self.__class__.__name__))
        #print("a")
        #print self.scene
        #self.scene.addWidget(PySide2.QtWidgets.QPushButton( "Start Record" ))
        for i in range(len(feRegularList)):
            self.addKnob(InputKnob(name=feRegularList[i]))
            
    def update(self):
        super(FacialExpression, self).update()
        self.value = []
        
        for knob in self.knobs():
            #print "aa"
            self.value.append(knob.value)
        
        print self.value
        
        #script.SetFacePuppetKeyWithName( "Heidi",0,[0,0,0],[0,0],[0,0],[0,0,0,0,0,0,0,0,0,0,0,0],self.value,[0,0,0] )
        

app = PySide2.QtWidgets.QApplication([])

graph = NodeGraphWidget()
#graph.resize(500,500)
#graph.autoFillBackground = True
graph.registerNodeClass(Weight)
graph.registerNodeClass(Const)
graph.registerNodeClass(Add)
graph.registerNodeClass(Multiply)
graph.registerNodeClass(FacialExpression)
graph.registerNodeClass(Faceware)
'''
graph.addNode(FacialExpression())
graph.addNode(Faceware())
'''

mainWidget = PySide2.QtWidgets.QWidget()
mainWidget.resize(500,500)
vBoxLayout = PySide2.QtWidgets.QVBoxLayout()
startBtn = PySide2.QtWidgets.QPushButton( "Start" )
stopBtn = PySide2.QtWidgets.QPushButton( "Stop" )
vBoxLayout.addWidget(graph)
vBoxLayout.addWidget( startBtn )
vBoxLayout.addWidget( stopBtn )
mainWidget.setLayout( vBoxLayout )

def startButtonClick():
    print "start"
    nodes = graph.getNodes()
    #graph.execute()
    '''
    for node in nodes:
        for knob in node.knobs():
            for edge in knob.edges:
                print edge.target.value
    '''
    for node in nodes:
        node.isUpdate = False
        node.update()
        
    for node in nodes:
        node.isUpdate = False
        node.start()
    
def stopButtonClick():
    print ("stop")
    nodes = graph.getNodes()
    for node in nodes:
        #node.isUpdate = False
        node.stop()
    
    
    
    
startBtn.clicked.connect(startButtonClick)
stopBtn.clicked.connect(stopButtonClick)

mainWidget.show()

#graph.addNode(Weight())

#graph.show()
app.exec_()
