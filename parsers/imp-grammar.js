module.exports = grammar({
    name: "imp",

    rules: {
        source_file: $ => $._stmt,

        int: $ => /\d+/,
        id: $ => /[a-zA-Z_][a-zA-Z0-9_]*/,
        div_exp: $ => prec.left(2, seq($._aexp, '/', $._aexp)),
        add_exp: $ => prec.left(1, seq($._aexp, '+', $._aexp)),
        brc_a_exp: $ => seq('(', $._aexp, ')'),
        _aexp: $ => choice(
            $.int,
            $.id,
            $.div_exp,
            $.add_exp,
            $.brc_a_exp
        ),

        bool: $ => /true|false/,
        leq_exp: $ => prec.left(2, seq($._aexp, '<=', $._aexp)),
        not_exp: $ => seq('!', $._bexp),
        land_exp: $ => prec.left(1, seq($._bexp, '&&', $._bexp)),
        brc_b_exp: $ => seq('(', $._bexp, ')'),
        _bexp: $ => choice(
            $.bool,
            $.leq_exp,
            $.not_exp,
            $.land_exp,
            $.brc_b_exp
        ),

        block: $ => seq('{', optional(repeat($._stmt)), '}'),
        asn_stmt: $ => prec.left(2, seq($.id, '=', $._aexp, ';')),
        if_stmt: $ => prec.left(1, seq('if', '(', $._bexp, ')', $.block, 'else', $.block)),
        while_stmt: $ => seq('while', '(', $._bexp, ')', $.block),
        _stmt: $ => choice(
            $.block,
            $.asn_stmt,
            $.if_stmt,
            $.while_stmt
        )
    }
});