import sys
import json

from asdl import runtime
from core import alloc
from core import main_loop
from core import ui
from core import util
from frontend import parse_lib
from frontend import reader

from typing import Dict, Any

from osh.utils_ast import DumpConfig, dump as _dump


def parse(code):
    pool = alloc.Pool()
    arena = pool.NewArena()
    arena.PushSource("<stdin>")
    line_reader = reader.StringLineReader(code, arena)

    # Dummy value; not respecting aliases!
    aliases = {}  # type: Dict[str, Any]
    # parse `` and a[x+1]=bar differently
    parse_ctx = parse_lib.ParseContext(arena, aliases, one_pass_parse=True)
    c_parser = parse_ctx.MakeOshParser(line_reader)

    try:
        node = main_loop.ParseWholeFile(c_parser)
    except util.ParseError as e:
        ui.PrettyPrintError(e, arena)
        return 2
    assert node is not None

    return node.PrettyTree()


def dump(tree):
    dump_config = DumpConfig(
        is_node=lambda node: isinstance(node, runtime.PrettyNode),
        node_type=lambda node: node.node_type.split(".")[-1],
        fields_iter=lambda node: (name for name, value in node.fields),
        field_val=lambda node, field: next(
            iter([value for name, value in node.fields if name == field])
        ),
        is_list=lambda node: isinstance(node, runtime.PrettyArray),
        list_iter=lambda array: array.children,
        leaf_val=lambda leaf: leaf.s,
    )

    return _dump(tree, dump_config)


def main(args=None):
    if args is None:
        cmd = sys.argv[1]
    print(json.dumps(dump(parse(cmd))))


if __name__ == "__main__":
    main()
