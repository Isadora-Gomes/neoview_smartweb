import 'package:dart_tools/rules.dart';

abstract final class AppRules {
  static bool _emptyRuleCallback(String v) => v.isNotEmpty;
  static const RuleCondition<String> _emptyRule = RuleCondition(function: _emptyRuleCallback, errorMessage: "Não pode estar vazio.");

  static final RegExp _emailRegExp = RegExp(
    r"^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+",
  );
  static bool _emailRegExpCallback(String v) => _emailRegExp.hasMatch(v);

  static bool _passwordSize(String v) => v.length >= 8 && v.length <= 64;

  static final RegExp _nameRegExp = RegExp(
    r"^[a-zA-Zà-úÀ-Ú ]+$",
  );
  static bool _nameRegExpCallback(String v) => _nameRegExp.hasMatch(v);
  static bool _nameSize(String v) => v.length >= 2 && v.length <= 256;

  static const email = Rule([
    _emptyRule,
    RuleCondition(function: _emailRegExpCallback, errorMessage: "Estrutura inválida.")
  ]);

  static const password = Rule([
    _emptyRule,
    RuleCondition(function: _passwordSize, errorMessage: "Precisa de 8 a 64 caracteres."),
  ]);

  static const name = Rule([
    _emptyRule,
    RuleCondition(function: _nameRegExpCallback, errorMessage: "Estrutura inválida."),
    RuleCondition(function: _nameSize, errorMessage: "Precisa de 2 a 256 caracteres.")
  ]);
}