part of '../pair.dart';

final class Pair extends Model<Pair> {
  String _name;
  String get name => _name;
  
  Pair(super.$id, {
    required String name,
  }): _name = name;

  void update({ String? name }) {
    if (name != null) {
      _name = name;
    }
  }

  Future<Result<PairConnection, String>> connect() async => PairConnection._current == null
    ? await PairConnection._connect(this)
    : Failure("Conexão já existente");

  static List<Pair> statics = [
    Pair(PartId(["neoview", "aa547cb0"]), name: "Óculos 1"),
    Pair(PartId(["neoview", "a8b9c02d"]), name: "Óculos 2"),
    Pair(PartId(["neoview", "ef650b12"]), name: "Óculos 3"),
    Pair(PartId(["neoview", "d9812bce"]), name: "Óculos 4"),
  ];

  static Pair? connected;
}