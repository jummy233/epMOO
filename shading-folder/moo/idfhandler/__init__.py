from moo.idfhandler.ep_output_reader import EPOutputReader
from moo.idfhandler.ep_input_model import EPInputModel, IdfModel, JdfModel
from moo.idfhandler.idf_iostream import IdfIOStream
from moo.idfhandler.Preamble import Preamble
from moo.idfhandler.anchors import SearchAnchor, SubAnchor


def override(f):
    # dummy override wrapper
    return f


