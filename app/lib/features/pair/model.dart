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

  PairConnection connect() {
    if (_current != null) {
      throw Exception("A pair connection is already active.");
    }

    currentNotifier.value = _current = PairConnection(this);

    return _current = currentNotifier.value!;
  }
  
  static PairConnection? _current;
  static ValueNotifier<PairConnection?> get currentNotifier => ValueNotifier(_current);
}