import copy
from StringIO import StringIO

from asdl import runtime
from core import alloc
from core import main_loop
from core import ui
from core import util
from frontend import parse_lib
from frontend import reader

from typing import Dict, Any

from osh.utils_ast import DumpConfig, dump as dump_util


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

    tree = node.PrettyTree()

    lines = StringIO(code).readlines()

    # add token text  # arena.GetLineSpan(int)
    tokens = copy.deepcopy(arena.spans)
    for token in tokens:
        token.text = lines[token.line_id][token.col : token.col + token.length]

    return tree, tokens


def enhance(tree, tokens):
    token_ids = []
    if not isinstance(tree, dict):
        return token_ids  # TODO

    data = tree["data"]
    if "spids" in data:
        token_ids.extend(map(int, data["spids"]))
        del data["spids"]
    if "span_id" in data:
        token_ids.append(int(data["span_id"]))
        del data["span_id"]
    if tree["type"] == "token":
        tree["type"] = data["id"]
        del data["id"]

    for field, value in data.items():
        if not isinstance(value, str):
            if not isinstance(value, list):
                value = [value]
            for item in value:
                token_ids.extend(enhance(item, tokens))

    first_token_id = min(token_ids)
    last_token_id = max(token_ids)
    tree["text"] = reduce(
        lambda text, token_id: text + tokens[int(token_id)].text,
        range(first_token_id, last_token_id + 1),
        "",
    )
    first_token = tokens[first_token_id]
    last_token = tokens[last_token_id]
    tree["position"] = {
        "line_start": first_token.line_id,
        "column_start": first_token.col,
        "line_end": last_token.line_id,
        "column_end": last_token.col + last_token.length,
    }

    return first_token_id, last_token_id


def dump(tree, tokens):
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

    tree = dump_util(tree, dump_config)

    enhance(tree, tokens)

    return tree
