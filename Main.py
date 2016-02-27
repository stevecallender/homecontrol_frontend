#!/usr/bin/python

from Tkinter import *
import zmq
from thread import *
from Queue import *
import time

#add in the zmq control



class HomeControl(Tk):

    def playPressed(self):
        print "play pressed"
        self.outboundMessageQueue.put("pause")

    def pausePressed(self):
        print "pause pressed"
        self.outboundMessageQueue.put("play")

    def nextPressed(self):
        print "next pressed"
        self.outboundMessageQueue.put("next")

    def previousPressed(self):
        print "prev pressed"
        self.outboundMessageQueue.put("prev")

    def lightsOnPressed(self):
        self.outboundMessageQueue.put("lightsOn")

    def lightsOffPressed(self):
        self.outboundMessageQueue.put("lightsOff")

    def monitorOutBound(self,context):

        socketOut = context.socket(zmq.REQ)
        socketOut.connect("tcp://192.168.1.1:5555")

        while True:
            outMessage = self.outboundMessageQueue.get()
            print "sending msg"
            socketOut.send(outMessage)
            print "pending call back"
            callback = socketOut.recv()
            print "received reply"
            print callback

    def monitorInBound(self,context):

        socketIn = context.socket(zmq.REP)
        socketIn.bind("tcp://*:5556")

        while True:
            inMessage = socketIn.recv()
            print "request received"
            print inMessage
            self.inboundMessageQueue.put(inMessage)
            print "sending callback"
            socketIn.send("1")



    def monitorBackend(self):
        if (not self.inboundMessageQueue.empty()):
            message = self.inboundMessageQueue.get_nowait()
            self.handleRequest(message)

        self.after(10,self.monitorBackend)

    def handleRequest(self, message):
        #in future this will expand to check on header date (maybe proto buffs)
        self.songText.set(message)

    def updateCurrentSong(self,song):
        self.songLabel = song

    def __init__(self,parent):
        Tk.__init__(self,parent)
        self.parent = parent


        self.outboundMessageQueue = Queue()
        self.inboundMessageQueue = Queue()

        self.pauseImage=PhotoImage(file="pause.gif").subsample(2,2)
        self.playImage=PhotoImage(file="play.gif").subsample(2,2)
        self.nextImage=PhotoImage(file="next.gif").subsample(2,2)
        self.previousImage=PhotoImage(file="previous.gif").subsample(2,2)
        self.lightOnImage=PhotoImage(file="lightson.gif").subsample(2,2)
        self.lightOffImage=PhotoImage(file="lightsoff.gif").subsample(2,2)

        self.grid()

        self.songText = StringVar()
        self.songLabel = Label(self, textvariable=self.songText)

        self.playButton = Button(self,command=self.playPressed)
        self.pauseButton = Button(self,command=self.pausePressed)
        self.nextButton = Button(self,command=self.nextPressed)
        self.previousButton = Button(self,command=self.previousPressed)
        self.lightsOnButton = Button(self,command=self.lightsOnPressed)
        self.lightsOffButton = Button(self,command=self.lightsOffPressed)

        self.playButton.config(image=self.pauseImage,width="270",height="270")
        self.pauseButton.config(image=self.playImage,width="270",height="270")
        self.nextButton.config(image=self.nextImage,width="270",height="270")
        self.previousButton.config(image=self.previousImage,width="270",height="270")
        self.lightsOnButton.config(image=self.lightOnImage,width="270",height="270")
        self.lightsOffButton.config(image=self.lightOffImage,width="270",height="270")


        self.songLabel.grid(column=1,row=0,sticky='EW')
        self.playButton.grid(column=1,row=1,sticky='EW')
        self.pauseButton.grid(column=2,row=1,sticky='EW')
        self.nextButton.grid(column=3,row=1,sticky='EW')
        self.previousButton.grid(column=0,row=1,sticky='EW')
        self.lightsOnButton.grid(column=0,row=2,sticky='EW')
        self.lightsOffButton.grid(column=3,row=2,sticky='EW')


        context = zmq.Context()

        start_new_thread(self.monitorOutBound, (context,))
        start_new_thread(self.monitorInBound, (context,))


if __name__ == "__main__":
    app = HomeControl(None)
    app.title('my application')
    app.after(0,app.monitorBackend)
    app.mainloop()


