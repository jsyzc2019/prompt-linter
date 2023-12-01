"""
*** PCnewsGPT Wissensimporter - import.py ***

    Änderungen: 
    V0.1.5.x - PyMuPDF direkt eingebunden (kein ".txt" mehr), neues chunking, PDF-Ersetzungen via Tabellen
    V0.1.4.x - PyMuPDFLoader ersetzt pdfMiner.six
    V0.1.3.x - append als funktion, besser lesbare, verständliche chunk-texte
    V0.1.2.x - Ersetzungen (Ligaturen,...)
    V0.1.1.x - mehr Parameter (text_splitter,... deutsch)
    V0.1.x - pure langchain basierte Adaption von privateGPT
"""

"""
Initial Banner Message
"""
print("\nPCnewsGPT Wissensimporter V0.1.5.5\n")

"""
Load Parameters, etc.
"""
from dotenv import load_dotenv
from os import environ as os_environ
from ast import literal_eval
load_dotenv()
persist_directory = os_environ.get('PERSIST_DIRECTORY','db')
embeddings_model_name = os_environ.get('EMBEDDINGS_MODEL_NAME','paraphrase-multilingual-mpnet-base-v2')
source_directory = os_environ.get('SOURCE_DIRECTORY','source_documents')
append_directory = os_environ.get('APPEND_DIRECTORY','append_documents')
text_splitter_name = os_environ.get('TEXT_SPLITTER','RecursiveCharacterTextSplitter')
text_splitter_parameters = literal_eval(os_environ.get('TEXT_SPLITTER_PARAMETERS','{"chunk_size": 500, "chunk_overlap": 50}'))

"""
Define Substitutions for PDF-Import
"""
SUBST_PDF = {           # *** general substitutions ***
    '\t':' ',           # tabs with a space
    '\r':'',            # delete carriage returns
    '\v':'',            # delete vertical tabs
    '„':'"',            # Anführungszeichen-Anfang
    '—':'-',            # m-dash
    '–':'-',            # n-dash
    '\'':'"',           # single with double quotes
    '€':'Euro',
    '®':'(R)',
    '(cid:297)':'fb',   # ligatures
    '(cid:322)':'fj',
    '(cid:325)':'fk',
    '(cid:332)':'ft',
    '(cid:414)':'tf',
    '(cid:415)':'ti',
    '(cid:425)':'tt',
    '(cid:426)':'ttf',
    '(cid:427)':'tti',
    '•':'*',            # bullets
    '\u202f':' ',       # strange spacer
    '\uf02e':'.',
    '\uf031':'1',
    '\uf032':'2',
    '\uf033':'3',
    '\uf034':'4',
    '\uf035':'5',
    '\uf036':'6',
    '\uf037':'7',
    '\uf038':'8',
    '\uf039':'9',
    '\uf081':'1.',
    '\uf082':'2.',
    '\uf083':'3.',
    '\uf084':'4.',
    '\uf085':'5.',
    '\uf086':'6.',
    '\uf087':'7.',
    '\uf088':'8.',
    '\uf089':'9.',
    '\uf0b7':'*',
    '\uf0b0':'-',
    '\uf02f':'.Print.', # icons
    '\uf0c9':'.Menu.',
    '\uf0c1':'.Link.',
    '\uf05a':'.Info.',
    '\uf3c1':'.Unlock.',
    '\uf023':'.Lock.',
    '\uf57c':'.World.',
    '\uf4c4':'.Partner.',
    '\uf0c0':'.People.',
    '\uf007':'.Person.',
    '\uf0a4':'.Point.',
    '\uf06c':'o',
    '\uf09a':'x',
    '\uf0d7':'*',
    '\uf0d8':'.nicht.', # mathematical symbols
    '\uf0d9':'.und.',
    '\uf0da':'.oder.',
    '→':'.impl. (Mathem.)',
    '\uf0de':'.impl.',
    '↔':'.äquiv. (Mathem.)',
    '\uf0db':'.äquiv.',
    '≈':'.approx.',
    '\uf061':'Alpha',
    'β':'Beta',
    '\uf067':'Gamma',
    '\xa0':'',
    'i.\nR.': 'i.R.',
}
SUBST_PDF_PTP = {       # *** substitutions for PDFs generated by "Print To PDF" ***
    'h�p':'http',           # tt
    'e�ung':'ettung',
    'u�on':'utton',
    'le�er':'letter',
    'lä�ern':'lättern',
    'hä�e':'hätte',
    'en�ä':'enttä',
    'di�e':'ditie',         # Ausnahme für nächstes subst
    'i�e':'itte',
    'i�le':'ittle',
    'ückschri�':'ückschritt',
    'Scha�en':'Schatten',
    'ma�sch':'matisch',     # ti
    'ma�k':'matik',
    'ma�on':'mation',
    'k�on':'ktion',
    'ddi�on':'ddition',
    'ul�plika�o':'ultiplikatio',
    'r�kel':'rtikel',
    'a�onal':'ational',
    'li�sche':'litische',
    'u�on':'ution',
    'ompa�bl':'ompatibl',
    's�mm':'stimm',
    's�ge':'stige',
    'a�on':'ation',
    'er�kal':'ertikal',
    'ich�g':'ichtig',
    'äl�g':'ältig',
    's�eg':'stieg',
    'ela�v':'elativ',
    'a�v':'ativ',
    'ak�v':'aktiv',
    'p�on':'ption',
    'hris�an':'hristian',
    'ar�n':'artin',
    'Bra�slava':'Bratislava',
    'sen�er':'sentier',
    'kri�':'kriti',
    'ul�m':'ultim',
    'fik�v':'fiktiv',
    'den�':'denti',
    'scha�':'schaft',       #ft
    'ä�ig':'äftig',
    'u�ei':'uftei',
    'o�ware':'oftware',
    'icroso�':'icrosoft ',
    'o�all':'otfall',       #tf
    # TODO - erweitern!!
    '�':'??',              # catchall
} 

"""
PDF-Import via PyMuPDF with some more processing, 
    ignore any pages with full-page-sized images (covers, ads, etc.)
"""
from langchain.docstore.document import Document as Langchain_Document
import fitz as PyMuPDF
from regex import sub as regex_sub
def myPDFLoader (fname) -> Langchain_Document:
    return_docs = []                  # return value
    with PyMuPDF.open(fname) as doc:  # open document

        # simplified metadata for full document
        doc_metadata = {
            'source':       fname,
            'format':       doc.metadata.get('format'),
            'author':       doc.metadata.get('author'),
            'producer':     doc.metadata.get('producer').replace('®',''),       # get rid of (R)
            'creationDate': doc.metadata.get('creationDate'),
        }

        # process all document pages (page.number+1 for "real" numbering) 
        for page in doc:

            # *** check if full-page image

            # calculate the page's width and height in cm
            page_w = round((page.mediabox.x1 - page.mediabox.x0)/72*2.54,2)     # 72 dpi, 2,54 cm / inch
            page_h = round((page.mediabox.y1 - page.mediabox.y0)/72*2.54,2)

            # get all images and calculate concatenated img width x height
            image_infos = page.get_image_info()
            i=None
            for image_info in image_infos:
                x = image_info.get('bbox')[0]/72*2.54                           # 72 dpi, 2,54 cm / inch
                y = image_info.get('bbox')[1]/72*2.54
                w = (image_info.get('bbox')[2]-image_info.get('bbox')[0])/72*2.54
                h = (image_info.get('bbox')[3]-image_info.get('bbox')[1])/72*2.54
                # 1st or next image
                if i is None:
                    imgs=[{'x':x, 'y':y, 'w': w,'h':h }]
                    i=0
                else:
                    prev_img = imgs[i]
                    # try concatenate images vertically (same x and w)
                    if (x == prev_img.get('x')) and (w == prev_img.get('w')) and (abs(y - prev_img.get('y') - prev_img.get('h')) < 0.1):
                        # extend image height
                        imgs[i]['h'] += h
                    # try concatenate horizontally (same y and h)              
                    elif (y == prev_img.get('y')) and (h == prev_img.get('h')) and (abs(x - prev_img.get('x') - prev_img.get('w')) < 0.1):
                        # extend image width
                        imgs[i]['w'] += w
                    else:
                        imgs.append({'x':x, 'y':y, 'w': w,'h':h })
                        i=i+1
            
            # check if a concetenated image spans 95% of page
            fullpage_img = False
            for img in imgs:
                if (img.get('w') > page_w*0.95) and (img.get('h') > page_h*0.95):   # 95% of page width and height is enough
                    fullpage_img = True
                    print(f"{fname} Seite:{page.number+1} ignoriert, da Ganzseitenbild {round(img['w'],2)}x{round(img['h'],2)}cm")
                    break

            # *** only generate text-doc for non-full-image pages 
            if not fullpage_img:

                # *** get the text
                text = page.get_text(flags= PyMuPDF.TEXT_PRESERVE_WHITESPACE | 
                                    PyMuPDF.TEXT_INHIBIT_SPACES | 
                                    PyMuPDF.TEXT_DEHYPHENATE | 
                                    PyMuPDF.TEXT_PRESERVE_SPANS | 
                                    PyMuPDF.TEXT_MEDIABOX_CLIP, 
                                    sort=False)
                
                # *** ignore pages with less than 100 characters
                if len(text) < 80:
                    print(f"{fname} Seite:{page.number+1} ignoriert, da kein brauchbarer Text ({len(text)} Zeichen)")
                else:
                     # *** tidy-up the text

                    # ** some Substutions are independent of PDF-Generators
                    # remove line-break hyphenations
                    text = regex_sub(r'\-\n+\s*', '',text)
                    # remove training spaces in lines
                    text =text.replace(' +\n', '\n')
                    # change single \n in content to " ", but not multiple \n
                    text = regex_sub(r'(?<!\n)\n(?!\n)', ' ',text)
                    # change multiple consecutive \n in content to just one \n
                    text = regex_sub(r'\n{2,}', '\n',text)
                    # remove strange single-characters with optional leading and trailing spaces in lines
                    text = regex_sub(r'\n *(\w|\*) *\n', '\n',text)
                    # remove strange single-character sequences with spaces inbetween texts
                    text = regex_sub(r'((\w|/|:) +){3,}(\w|/|:)', '',text)
                    # replace multiple blanks with just one
                    text = regex_sub(r'  +', ' ',text)
                    # substitute strange characters & known ligatures
                    for k,v in SUBST_PDF.items():
                        text = text.replace(k, v)

                    # ** some substutions are dependent on "producer" (e.g. ligatures)
                    producer = doc.metadata.get('producer')
                    if producer.find('Print To PDF') >= 0:
                        text = regex_sub(r'\s\�\s','�',text) # remove white-space around ligatures
                        for k,v in SUBST_PDF_PTP.items():
                            text = text.replace(k, v)

                    # catchall-substutute for remaining unknown unicode characters
                    for t in text:
                        if not t.isprintable() and not t.isspace():
                            text = text.replace(t, '?')

                    # *** return a Langchain_Document for each non-empty page
                    if len(text) > 0:
                        return_docs.append(Langchain_Document(
                                metadata = {**doc_metadata, **{'page':page.number+1}},
                                page_content = text,
                            ))

    return return_docs

"""
Initialize Text Splitter
"""
# dynamically import the langchain text splitter class and instantiate it
from importlib import import_module
text_splitter_module = import_module("langchain.text_splitter")
TextSplitter = getattr(text_splitter_module, text_splitter_name)
text_splitter = TextSplitter(**text_splitter_parameters)

"""
Initialize Embeddings
"""
from langchain.embeddings import HuggingFaceEmbeddings
print(f"Embeddings {embeddings_model_name} werden eingelesen...\n")
embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

"""
Initialize ChromaDB
"""
from langchain.vectorstores import Chroma
from chromadb.config import Settings as Chroma_Settings
# Define the Chroma settings
chroma_settings = Chroma_Settings(
        chroma_db_impl='duckdb+parquet',
        persist_directory=persist_directory,
        anonymized_telemetry=False
)

"""
Checks if ChromaDB exists
"""
from os import system as os_system, path as os_path
from glob import glob
def does_db_exist() -> bool:
    if os_path.exists(os_path.join(persist_directory, 'index')):
        if os_path.exists(os_path.join(persist_directory, 'chroma-collections.parquet')) and os_path.exists(os_path.join(persist_directory, 'chroma-embeddings.parquet')):
            list_index_files = glob(os_path.join(persist_directory, 'index/*.bin'))
            list_index_files += glob(os_path.join(persist_directory, 'index/*.pkl'))
            return True
    return False

"""
parse source_directory (for full import) + append_directory for all filenames to load
"""
full_import_paths = []
full_import_paths.extend(
    glob(os_path.join(source_directory, f"**/*.pdf"), recursive=True)
)
append_paths = []
append_paths.extend(
    glob(os_path.join(append_directory, f"**/*.pdf"), recursive=True)
)

"""
Load + process all documents
"""
# decide if we append to existing db or create a new one
if does_db_exist():
    if len(append_paths) > 0:
        print(f"Dokumentdateien in {append_directory} werden eingelesen und verarbeitet...\n")
        create_db = False
        file_paths = append_paths
        move_from_append = True
    else:
        print(f"Es existiert bereits eine Wissensdatenbank in {persist_directory}.\n")
        print(f"Um Dokumente hinzuzufügen, lege diese im Ordner {append_directory} ab und starte den Import erneut.\n")
        print(f"Um eine neue Wissensdatenbank anzulegen, lösche den Ordner {persist_directory} und starte den Import erneut.\n")
        exit()
else:
    print(f"{persist_directory} wird gelöscht und neu erzeugt.\n")
    os_system(f'rm -rf {persist_directory}')
    print(f"Dokumentdateien in {source_directory} werden eingelesen und verarbeitet...\n")
    create_db = True
    file_paths = full_import_paths
    move_from_append = False

# process all documents
db = None
total_pages=0
total_chunks=0
for file_num,file_path in enumerate(file_paths):
    # import one document's pages
    print(f"Datei {file_path} ({file_num+1}/{len(file_paths)})...")
    pages=myPDFLoader(file_path)    # as langchain documents
    num_pages=len(pages)
    total_pages += num_pages
    docs = []                       # langchain documents for DB
    print(f"... wurde eingelesen und in {num_pages} Seite(n) umgewandelt ...")

    # for each page in the document
    num_chunks_in_doc=0
    for page in pages:
        # split this pages into chunks of text, and process each chunk
        chunks = text_splitter.split_documents([page])
        num_chunks_in_doc += len(chunks)
        for chunk_num, chunk in enumerate(chunks):
            # add metadata for each chunk
            chunk_metadata={**chunk.metadata,**{"chunk": chunk_num+1}}
            # final tidying-up of chunk text - needed because of SpaCy weirdnesses
            txt = chunk.page_content
            # change single \n in content to " ", but not multiple \n
            txt = regex_sub(r'(?<!\n)\n(?!\n)', ' ',txt)
            # change multiple consecutive \n in content to just one \n
            txt = regex_sub(r'\n{2,}', '\n',txt)
            # if we have a remaining text in the chunk -> add to docs
            if len(txt) > 0:
                docs.append(Langchain_Document(
                    metadata = chunk_metadata,
                    page_content = txt,
                ))
    # statistics per document
    print(f"... zerteilt auf {num_chunks_in_doc} Textteil(e) ...")
    total_chunks += num_chunks_in_doc
    # create embeddings and persist
    if db is None:
        # create or append-to db
        if create_db:
            db = Chroma.from_documents(docs, embeddings, persist_directory=persist_directory, client_settings=chroma_settings)
        else:
            db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=chroma_settings)
            db.add_documents(docs)
    else:
        # add to existing db
        db.add_documents(docs)
    db.persist()
    print("... und in der Wissensdatenbank gespeichert.\n")

# move files from append_directory to source_directory after finishing import
if move_from_append:
    print(f"Verschiebe alle Dateien aus {append_directory} nach {source_directory}...\n")
    os_system(f'mv {append_directory}/* {source_directory}/')

# Statistics
print(f"Insgesamt {len(file_paths)} Dokument(e) mit {total_pages} Seite(n) und {total_chunks} Textteil(en) wurden eingelesen.\n")
db = None
