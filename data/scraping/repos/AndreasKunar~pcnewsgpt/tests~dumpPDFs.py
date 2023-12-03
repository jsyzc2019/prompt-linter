"""
*** PCnewsGPT Hilfsprogramm: Inhaltsausgabe PDFs im Importverzeichnis ***

Änderungen:
    - folgt import.py Algorithmenänderungen
"""

"""
Initial banner Message
"""
print("\nPCnewsGPT dump PDFs aus importverzeichnis V0.2.1\n")

"""
Load Parameters, etc.
"""
from dotenv import load_dotenv
from os import environ as os_environ
from ast import literal_eval
load_dotenv()
source_directory = os_environ.get('SOURCE_DIRECTORY','source_documents')

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
from regex import sub as regex_sub, match as regex_match
def myPDFLoader (fname) -> Langchain_Document:
    return_docs = []                  # return value
    with PyMuPDF.open(fname) as doc:  # open document

        # simplified metadata for full document
        doc_metadata = {
            'source':       fname,
            'format':       doc.metadata.get('format'), 
            'author':       doc.metadata.get('author'), 
            'producer':     doc.metadata.get('producer'),  
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
                                    # PyMuPDF.TEXT_DEHYPHENATE | 
                                    PyMuPDF.TEXT_PRESERVE_SPANS | 
                                    PyMuPDF.TEXT_MEDIABOX_CLIP, 
                                    sort=False)
                
                # *** ignore pages with less than 80 characters
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
parse source_directory 
"""
from os import system as os_system, path as os_path
from glob import glob
file_paths = []
file_paths.extend(
    glob(os_path.join(source_directory, f"**/*.pdf"), recursive=True)
)

"""
Load + process all documents
"""
print(f"Dokumentdateien in {source_directory} werden eingelesen und verarbeitet...\n")

# process all documents
for idx,file_path in enumerate(file_paths):
    documents=myPDFLoader(file_path)                  # txt as 1 document, pdfs as 1 document per page
    for document in documents:
        print(document)