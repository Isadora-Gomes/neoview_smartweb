part of '../pair.dart';

final class PairConnection extends ChangeNotifier with LimitedTimeUseClass {
  final Pair pair;

  static PairConnection? _current;

  static Future<Result<PairConnection, String>>_connect(Pair pair) async {
    throw UnimplementedError();
  }
  
  PairConnection._(this.pair) {
    init();
  }

  Future<Result<void, String>> use(GlassesFunctionality function) async {
    throw UnimplementedError();
  }

  @override
  void dispose() {
    _current = null;
    super.dispose();
  }
}

enum GlassesFunctionality<T> {
  tactileFloor("/floor", PythonServer._mapTactileFloor),
  readText("/text-read", PythonServer._readText),
  ambientDetection("/objects", PythonServer._readAmbient),
  ping("/ping", PythonServer._ping);

  final String endpoint;
  final Future<ServerResult> Function() call;

  const GlassesFunctionality(this.endpoint, this.call);
}