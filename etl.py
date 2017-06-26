import argparse
from pattern.en import parsetree
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import model

description = """Extract using pattern, transform into character model, load to a
RDBM"""

################################
# parse command line arguments #
################################
parser = argparse.ArgumentParser(
    description=description)

parser.add_argument('--db_url',
                    default='sqlite:///characters.sqlite',
                    help='DB URL, default: sqlite:///characters.sqlite')

parser.add_argument('--text',
                    type=argparse.FileType('r'), required=True,
                    help='a plain text file')

args = parser.parse_args()


####################
# database connect #
####################
engine = create_engine(args.db_url)
Session = sessionmaker(bind=engine)
session = Session()

model.Base.metadata.create_all(engine)
model.session = session

tree = parsetree(args.text.read())

wid = 1
for n in range(len(tree.sentences)):
    s = tree[n]
    sentence = session.query(model.Sentence).get(s.id)
    if sentence is None:
        sentence = model.Sentence(id=s.id,
                                  sentence=s.string)
        session.add(sentence)

    for w in s.words:
        session.add(model.Word(id=wid,
                               word=w.string,
                               pos=w.pos,
                               sentence=sentence))
        wid += 1

session.commit()
