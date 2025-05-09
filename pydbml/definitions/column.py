import pyparsing as pp

from .common import _, _c, c, n, note, pk, unique
from .generic import (
    boolean_literal,
    expression,
    expression_literal,
    name,
    number_literal,
    string_literal
)
from .reference import ref_inline
from pydbml.parser.blueprints import ColumnBlueprint


pp.ParserElement.set_default_whitespace_chars(' \t\r')

type_args = ("(" + pp.original_text_for(expression) + ")")

# column type is parsed as a single string, it will be split by blueprint
column_type = pp.Combine((name + pp.Literal('[]')) | (name + '.' + name) | ((name) + type_args[0, 1]))

default = pp.CaselessLiteral('default:').suppress() + _ - (
    string_literal
    | expression_literal
    | boolean_literal.set_parse_action(
        lambda s, loc, tok: {
            'true': True,
            'false': False,
            'NULL': None
        }[tok[0]]
    )
    | number_literal.set_parse_action(
        lambda s, loc, tok: float(''.join(tok[0])) if '.' in tok[0] else int(tok[0])
    )
)

prop = name + pp.Suppress(":") + string_literal

column_setting = _ + (
    pp.CaselessLiteral("not null").set_parse_action(
        lambda s, loc, tok: True
    )('notnull')
    | pp.CaselessLiteral("null").set_parse_action(
        lambda s, loc, tok: False
    )('notnull')
    | pp.CaselessLiteral("primary key")('pk')
    | pk('pk')
    | unique('unique')
    | pp.CaselessLiteral("increment")('increment')
    | note('note')
    | ref_inline('ref*')
    | default('default')
) + _

column_setting_with_property = column_setting | prop.set_results_name('property', list_all_matches=True)

column_settings = '[' - column_setting + ("," + column_setting)[...] + ']' + c

column_settings_with_properties = '[' - (_ + column_setting_with_property + _) + ("," + column_setting_with_property)[...] + ']' + c


def parse_column_settings(s, loc, tok):
    '''
    [ NOT NULL, increment, default: `now()`]
    '''
    result = {}
    if tok.get('notnull'):
        result['not_null'] = True
    if 'pk' in tok:
        result['pk'] = True
    if 'unique' in tok:
        result['unique'] = True
    if 'increment' in tok:
        result['autoinc'] = True
    if 'note' in tok:
        result['note'] = tok['note']
    if 'default' in tok:
        result['default'] = tok['default'][0]
    if 'ref' in tok:
        result['ref_blueprints'] = list(tok['ref'])
    if 'comment' in tok:
        result['comment'] = tok['comment'][0]
    if 'property' in tok:
        result['properties'] = {k: v for k, v in tok['property']}
    return result


column_settings.set_parse_action(parse_column_settings)
column_settings_with_properties.set_parse_action(parse_column_settings)


constraint = pp.CaselessLiteral("unique") | pp.CaselessLiteral("pk")

table_column = _c + (
    name('name')
    + column_type('type')
    + constraint[...]('constraints') + c
    + column_settings('settings')[0, 1]
) + n


table_column_with_properties = _c + (
    name('name')
    + column_type('type')
    + constraint[...]('constraints') + c
    + column_settings_with_properties('settings')[0, 1]
) + n


def parse_column(s, loc, tok):
    '''
    address varchar(255) [unique, not null, note: 'to include unit number']
    '''
    init_dict = {
        'name': tok['name'],
        'type': tok['type'],
    }
    # deprecated
    for constraint in tok.get('constraints', []):
        if constraint == 'pk':
            init_dict['pk'] = True
        elif constraint == 'unique':
            init_dict['unique'] = True

    if 'settings' in tok:
        init_dict.update(tok['settings'])

    # comments after column definition have priority
    if 'comment' in tok:
        init_dict['comment'] = tok['comment'][0]
    if 'comment' not in init_dict and 'comment_before' in tok:
        comment = '\n'.join(c[0] for c in tok['comment_before'])
        init_dict['comment'] = comment

    return ColumnBlueprint(**init_dict)


table_column.set_parse_action(parse_column)
table_column_with_properties.set_parse_action(parse_column)
