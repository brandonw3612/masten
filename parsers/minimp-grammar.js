module.exports = grammar({
  name: "minimp",

  rules: {
    source_file: $ => $._aexp,

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
    )
  }
});