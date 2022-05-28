import sys, os, re
from anki.storage import Collection
import sqlite3
from deep_translator import GoogleTranslator
from aqt import mw
from aqt.utils import showInfo, qconnect
import aqt.qt
import aqt

def main():
    translator = GoogleTranslator(source='french', target='german')

    PROFILE_HOME = os.path.expanduser("/Users/flo/Library/Application Support/Anki2/User 1") 
    cpath = os.path.join(PROFILE_HOME, "collection.anki2")
    col = Collection(cpath, log=True) # Entry point to the API

    model_basic = col.models.by_name('Idiom')
    col.decks.current()['mid'] = model_basic['id']

    deck = col.decks.by_name('french')
    with sqlite3.connect('vocab.db') as conn:
        cur = conn.cursor()
        cur.execute("Select * from LOOKUPS;")
        words_for_anki = []
        for lookup in cur.fetchall():
            book_id = lookup[2]
            cur.execute(f"select * from book_info where id == '{book_id}';")
            book_info = cur.fetchone()

            if book_info[4] == 'LE PETIT PRINCE (French Edition)' or book_info[4] == 'Le Petit Prince (Illustré) (Édition Originale) (French Edition)':
                word_id, beispiel = lookup[1], lookup[5],   
                cur.execute(f"Select * from words where id == '{word_id}';")
                words = cur.fetchone()
                words_for_anki.append((words[1], words[2], beispiel))

        for word in words_for_anki[:5]:
            note = col.new_note(model_basic)
            note.note_type()['did'] = deck['id']

            note.fields[0]= f'{word[0]}[{word[1]}]'
            note.fields[1]= f'{translator.translate(word[1])}'
            note.fields[2]= f'{word[2]}'
            print(note.fields)

            note.tags = col.tags.split("French")
            m = note.note_type()
            m['tags'] = note.tags
            col.models.save(m)
            col.addNote(note)

        cur.close()
        col.save()

action = aqt.qt.QAction("test", mw)
qconnect(action.triggered, main)
mw.form.menuTools.addAction(action)