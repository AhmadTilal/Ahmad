
import socket
import sys
import hashlib
from thread import start_new_thread
import math

argg =  sys.argv
port = int(argg[-1])
ip = '127.0.0.1'

ID = port - 1000
pred = 10000
succ = 10000

keys = list()
fingertable = list()

for x in range(0,4):
  ob = [ID + pow(2,x), ID]
  fingertable.append(ob)

#it is for the new node requesting to join dht
def join():
    global pred
    connport = raw_input('Port to connect to: ')
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip,int(connport)))
    s.send('join')
    s.recv(1024)
    s.send(str(ID))

def req_sock(ms):
    #c is the socket, addr is the address
    global succ
    global pred
    print 'waiting...'
    c,addr = ms.accept()
    stat=c.recv(1024)
    print "Accepted to", addr
    print stat
    c.send('FUCK U')
    if stat=='join':
      hash_recv=int(c.recv(1024))
      s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((ip,hash_recv+1000))
      #UPDATE HERE
      if (succ==10000 and pred==10000):
        print 'Updating P and S to', hash_recv
        succ=hash_recv
        pred=hash_recv
        s.send('UpdatePredAndSucc')
        s.recv(1024)
        s.send(str(ID))
        s.recv(1024)
        s.send(str(ID))

      elif (succ > hash_recv or (succ < ID and hash_recv > ID)):

          print 'Updating P to ', hash_recv
          s.send('UpdatePredAndSucc')
          s.recv(1024)
          s.send(str(ID))
          s.recv(1024)
          s.send(str(succ))
          succ=hash_recv

      else:
          s1=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          s1.connect((ip,succ+1000))
          print 'Forwarding reqst to ', succ
          s1.send('join')
          s1.recv(1024)
          s1.send(str(hash_recv))

      #UPDATE FINGER TABLE
      updateft(hash_recv)
      s1=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s1.connect((ip,hash_recv+1000))
      s1.send('UpdateFt')
      s1.recv(1024)
      for x in fingertable:
        s1.send(str(x[1]))
        s1.recv(1024)

    elif stat=='leave':
      succ=int(c.recv(1024))
      s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((ip,succ+1000))
      print 'Updating Pred to ', succ
      s.send('UpdatePred')
      s.recv(1024)
      s.send(str(ID))

    elif stat=='UpdatePredAndSucc':
      pred=int(c.recv(1024))
      c.send('Recvd')
      succ=int(c.recv(1024))
      s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((ip,succ+1000))
      s.send('UpdatePred')
      s.recv(1024)
      s.send(str(ID))
    elif stat=='UpdatePred':
      pred=int(c.recv(1024))
    elif stat=='KeyUpload':
      keynum = int(c.recv(1024))
      uploadkey(keynum)
    elif stat=='UpdateFt':
      while 1:
        nrec = int(c.recv(1024))
        if not nrec:
          break
        updateft(nrec)
        c.send('done')

    if succ==ID:
      succ=10000
    if pred==ID:
      pred=10000

    start_new_thread(req_sock,(ms,))

def updateft(node):
  global fingertable
  print 'UPDATING FT'
  for x in fingertable:
    if (node > x[0] and node < x[1]):
      x[1] = node
    if (x[1]==ID and succ!=10000):
      x[1] = succ
  print 'UPDATING DONE'
def leave():
  global succ
  global pred
  s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((ip,pred+1000))
  s.send('leave')
  s.recv(1024)
  s.send(str(succ))
  #we have yet to transfer keys to our succ, keys we will do later
  succ=10000
  pred=10000
  

def uploadkey(keynumber):
  global keys
  #DOESNT WORK when 20 uploads 5 and succ is 0
  #print(keynumber,"::",ID,"::",succ)
  if ((keynumber < ID and keynumber > pred) or (pred > ID and keynumber > pred)):
    print('Key uploaded on your device')
    keys.append(keynumber)
  else:
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip,succ+1000))
    s.send('KeyUpload')
    s.recv(1024)
    s.send(str(keynumber))

def ui():
    choice = raw_input("Press 1 to join a network, 2 to show succ  and pred,3 to leave network,4 to upload key,5 to show own keys: ")
    if choice=='1':
        join()
    elif choice=='2':
        print "succ: ", succ
        print "pred: ", pred
    elif choice=='3':
        leave()
    elif choice=='4':
        keynum=raw_input("Input yer key hashed number: ")
        uploadkey(keynum)
    elif choice=='5':
        for x in keys:
          print(x)
    elif choice=='6':
      for x in fingertable:
        print x

def main():

    ms = socket.socket()
    ms.bind((ip,port))
    ms.listen(2)
    listening = 0
    start_new_thread(req_sock,(ms,))
    while 1:
        ui()




if __name__ == "__main__":
    main()
  


