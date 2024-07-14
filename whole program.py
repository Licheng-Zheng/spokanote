import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import assemblyai as aai 
from summarizer import Summarizer
from threading import *
from notion_client import Client 

aai.settings.api_key = "8a770d6d130e458986e3621866cd5bc3"
transcriber = aai.Transcriber()
notion_token = 'secret_H4ZRY3gIlioDMaqpT4oB59YTOcaSK8pbC62PCUREhPG'
notion_page_id = '70d2507afeb8411bacd5042309b07b7e'


class file_getter(QWidget):
    def __init__(self, parent = None):
      super(file_getter, self).__init__(parent)
		
      layout = QVBoxLayout()
      self.btn = QPushButton("Open your audio file here")
      self.btn.clicked.connect(self.getfile)
      layout.addWidget(self.btn)
      self.setLayout(layout)
      self.setWindowTitle("Spokanote")

      self.file = ""

    def getfile(self):
      fname = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\')
      self.file = fname[0]
      self.thread()
    
    def thread(self): 
       t1 = Thread(target=self.pusher)
       t1.start()
    
    def pusher(self):
      client = Client(auth=notion_token)

      write_text(client, notion_page_id, 'Transcript', 'heading_2')
      
      transcript = transcriber.transcribe(self.file)

      for times in range(1900, len(transcript.text)+1, 1900):
        write_text(client, notion_page_id, transcript.text[times-1900:times], 'paragraph')

      write_text(client, notion_page_id, 'Summary', 'heading_2')
      model = Summarizer()
      result = model(transcript.text, ratio=0.2)
      full_text = "".join(result)
      write_text(client, notion_page_id, full_text, 'paragraph')

def write_text(client, page_id, text, type):
    client.blocks.children.append(
    block_id=page_id,
    children=[{
        "object": "block",
        "type": type,
        type: {
            "rich_text": [{ "type": "text", "text": { "content": text } }]
        }
    }]
)
    
def main():
   app = QApplication(sys.argv)
   ex = file_getter()
   ex.show()
   sys.exit(app.exec_())
	
if __name__ == '__main__':
   main()