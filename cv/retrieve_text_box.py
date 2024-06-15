import cv2
import pytesseract
import subprocess
import io
import pickle
from cv.text_match import check_closest_message
from parse import pokemon_parser

def process_image(cls, img):
    text = pytesseract.image_to_string(img) #, config=...)
    #print("Input :")
    #print(text)
    line1, line2 = check_closest_message(text, cls.config)
    #print("Parsed :")
    #print(line1)
    #print(line2)
    #print("================")
    

class TesseractQueue:
    def __init__(self):
        self.processes = []
        self.messages = []
        self.turns = []
        self.reset()
        self.config = pokemon_parser.PokemonParser("config/fake.yaml")

    def add_image_to_processing(self, img, turn):
        img_name = f"image_{len(self.processes)}.png"
        cv2.imwrite(img_name, img)
        self.processes.append(
                subprocess.Popen(
                [f"tesseract {img_name} stdout"], shell=True,
                stdout=subprocess.PIPE
           ))
        self.turns.append(turn)
        self.messages.append(()) # placeholder for stdout
        self.finished.append(False)
        self.receive_new_filter = False

    def check(self):
        results = []
        for i, proc in enumerate(self.processes):
            if proc.poll() is not None and not self.finished[i]:
                self.messages[i] = check_closest_message(proc.stdout.read().decode(), self.config.get_pokemon_names(), self.config)
                print(self.messages[i])
                self.finished[i]=True
                results.append((self.messages[i], self.turns[i]))

        # If everything is finished, reset
        if sum(self.finished) == len(self.finished):
            self.reset()
        return results
        

    def reset(self):
        for proc in self.processes:
            proc.wait()
        self.processes = []
        self.finished = []
        self.turns = []
        self.receive_new_filter = True
