import sys
sys.argv[0] = 'bin/osh'

from osh import parse_lib
from core import reader
from core import alloc
import core.id_kind
import asdl.py_meta

pool = alloc.Pool()
arena = pool.NewArena()
arena.PushSource('<interactive>')

def cmd_to_ast(cmd = "${x/y/z}"):
    line_reader = reader.StringLineReader(cmd, arena = arena)
    w_parser, c_parser = parse_lib.MakeParser(line_reader, arena)

    node = c_parser.ParseWholeFile()
    return node

from collections import OrderedDict
def ast_dump(node):
    if isinstance(node, list) and not len(node): return None
    elif isinstance(node, (core.id_kind.Id, asdl.py_meta.SimpleObj)): return repr(node)
    elif not hasattr(node, 'FIELDS'): return node

    data = OrderedDict()
    for field_name in set(node.FIELDS) - set(['spids']):

        attr = getattr(node, field_name)
        if isinstance(attr, list) and len(attr): data[field_name] = [ast_dump(entry) for entry in attr]
        elif field_name in ['token', 'terminator']: data[field_name] = ast_dump(attr.val)
        else: data[field_name] = ast_dump(attr)
    return {'type': node.__class__.__name__, 'data': data}

#if __name__ == '__main__':
#    from flask import Flask, jsonify, request
#    app = Flask(__name__)
#
#    @app.route('/')
#    def index():
#        return 'yay'
#    
#    @app.route('/parse', methods = ["POST"])
#    def parse():
#        d = request.get_json()
#        return jsonify(ast_dump(cmd_to_ast(d['cmd'])))
#
#    app.run('0.0.0.0', port = '8080')
#
#
