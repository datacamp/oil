"""AST utils from protowhat for Python 2"""
from ast import AST
from collections import OrderedDict


class DumpConfig:
    def __init__(
        self,
        is_node=lambda node: isinstance(node, AST),
        node_type=lambda node: node.__class__.__name__,
        fields_iter=lambda node: node._fields,
        field_val=lambda node, field: getattr(node, field, None),
        is_list=lambda node: isinstance(node, list),
        list_iter=id,
        leaf_val=id,
    ):
        """
        Configuration to convert a node tree to the dump format

        The default configuration can be used to dump a tree of AstNodes
        """
        self.is_node = is_node
        self.node_type = node_type
        self.fields_iter = fields_iter
        self.field_val = field_val
        self.is_list = is_list
        self.list_iter = list_iter
        self.leaf_val = leaf_val


def dump(node, config):
    """
    Convert a node tree to a simple nested dict

    All steps in this conversion are configurable using DumpConfig

    dump dictionary node: {"type": str, "data": dict}
    """
    if config.is_node(node):
        fields = OrderedDict()
        for name in config.fields_iter(node):
            attr = config.field_val(node, name)
            if attr is not None:
                fields[name] = dump(attr, config)
        return {"type": config.node_type(node), "data": fields}
    elif config.is_list(node):
        return [dump(x, config) for x in config.list_iter(node)]
    else:
        return config.leaf_val(node)
