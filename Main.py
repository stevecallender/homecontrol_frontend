#!/usr/bin/python

from Tkinter import *
import zmq
from thread import *
from Queue import *
import time


class HomeControl(Tk):

    def playTogglePressed(self):
        if (self.playing):
            self.outboundMessageQueue.put("pause")
        else:
            self.outboundMessageQueue.put("play")

    def pausePressed(self):
        self.outboundMessageQueue.put("play")

    def nextPressed(self):
        self.outboundMessageQueue.put("next")

    def previousPressed(self):
        self.outboundMessageQueue.put("prev")

    def lightTogglePressed(self):
        if self.lightsOn:
            self.outboundMessageQueue.put("lightsOff")
        else:
            self.outboundMessageQueue.put("lightsOn")


    def monitorOutBound(self,context):

        socketOut = context.socket(zmq.PUSH)
        socketOut.connect("tcp://192.168.1.1:5555")

        while True:
            outMessage = self.outboundMessageQueue.get()
            print "Pushing message " + outMessage
            socketOut.send(outMessage)

    def monitorInBound(self,context):

        socketIn = context.socket(zmq.PULL)
        socketIn.bind("tcp://*:5556")

        while True:
            inMessage = socketIn.recv()
            print "Message pulled: " +inMessage
            self.inboundMessageQueue.put(inMessage)



    def monitorBackend(self):
        if (not self.inboundMessageQueue.empty()):
            message = self.inboundMessageQueue.get_nowait()
            self.handleRequest(message)

        self.after(10,self.monitorBackend)

    def handleRequest(self, message):
        #in future this will expand to check on header date (maybe proto buffs)
        header = message[0]
        payload = message[1:]

        #current song info - 1
        if (header == "1"):
            trimmedPayload = payload[:-1]
            artist,song = trimmedPayload.split("-")
            self.songText.set(song[1:])#removing last char as it is new line
            self.artistText.set(artist)#removing last char as it is new line

        #lights state - 2
        elif (header == "2"):
            if (payload == "lightsOn"):
                self.lightsButton.config(image=self.lightOnImage,width="200",height="140")
                self.lightsOn = True
            elif (payload == "lightsOff"):
                self.lightsButton.config(image=self.lightOffImage,width="200",height="140")
                self.lightsOn = False
        #play state
        elif (header == "3"):
            if (payload == "play"):
                self.playPauseButton.config(image=self.pauseImage,width="266",height="180")
                self.playing = True
            elif (payload == "pause"):
                self.playPauseButton.config(image=self.playImage,width="266",height="180")
                self.playing = False

        #time
        elif (header == "4"):
            splitTime = payload.split(":")
            hours = splitTime[0]
            minutes = splitTime[1]
            if len(minutes) < 2:
                minutes = "0"+minutes
            if len(hours) < 2:
                hours = "0"+hours
            self.timeText.set(hours+":"+minutes)

    def updateCurrentSong(self,song):
        self.songLabel = song

    def __init__(self,parent):
        Tk.__init__(self,parent)
        self.parent = parent

        self.lightsOn = False
        self.playing = False

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
        self.songLabel = Label(self, textvariable=self.songText, font=("Helvetica", 24))

        self.artistText = StringVar()
        self.artistLabel = Label(self, textvariable=self.artistText, font=("Helvetica", 24))

        self.timeText = StringVar()
        self.timeLabel = Label(self, textvariable=self.timeText, font=("Helvetica", 24))


        self.playPauseButton = Button(self,command=self.playTogglePressed)
        self.nextButton = Button(self,command=self.nextPressed)
        self.previousButton = Button(self,command=self.previousPressed)
        self.lightsButton = Button(self,command=self.lightTogglePressed)

        self.playPauseButton.config(image=self.playImage,width="255",height="180")
        self.nextButton.config(image=self.nextImage,width="255",height="180")
        self.previousButton.config(image=self.previousImage,width="255",height="180")
        self.lightsButton.config(image=self.lightOffImage,width="350",height="170")


        self.songLabel.grid(column=0,row=0,sticky='WNS',columnspan = 2)
        self.artistLabel.grid(column=0,row=1,sticky='WNS',columnspan = 2)
        self.timeLabel.grid(column=2,row=0,sticky='E',rowspan = 2)

        self.previousButton.grid(column=0,row=2,sticky='EW')
        self.playPauseButton.grid(column=1,row=2,sticky='EW')
        self.nextButton.grid(column=2,row=2,sticky='EW')

        self.lightsButton.grid(column=0,row=3,sticky='EW',columnspan = 3)

        context = zmq.Context()

        start_new_thread(self.monitorOutBound, (context,))
        start_new_thread(self.monitorInBound, (context,))




if __name__ == "__main__":
    app = HomeControl(None)
    app.title('my application')

    app.after(0,app.monitorBackend)
    app.mainloop()


