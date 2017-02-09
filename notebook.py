from tkinter import *

# create the window
root = Tk()

topFrame = Frame(root)
topFrame.pack()

bottomFrame = Frame(root)
bottomFrame.pack(side=BOTTOM)

button1 = Button(topFrame, text='Click Me.', fg='red')
button2 = Button(topFrame, text='Click Me.', fg='blue')
button3 = Button(topFrame, text='Click Me.', fg='green')
button4 = Button(bottomFrame, text='Click Me.', fg='purple')
button1.pack(side=LEFT)
button2.pack(side=LEFT)
button3.pack(side=LEFT, fill=Y)
button4.pack(side=BOTTOM, fill=X)

root.mainloop()
