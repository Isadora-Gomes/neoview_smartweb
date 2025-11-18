part of '../pair.dart';

final class PairConnection extends ChangeNotifier with LimitedTimeUseClass {
  final Pair pair;
  GlassesFunctionality? _currentFunction;
  final Set<GlassesFunctionality> _secondaryFunctions = {};

  GlassesFunctionality? get currentFunction => _currentFunction;
  late final UnmodifiableSetView<GlassesFunctionality> secondaryFunctions;
  
  PairConnection(this.pair) {
    init();
    secondaryFunctions = UnmodifiableSetView(_secondaryFunctions);
  }

  void use(GlassesFunctionality function) {
    if (_currentFunction == null) {
      _currentFunction = function;
      notifyListeners();
    } else {
      if (_currentFunction == function) return;
      if (_currentFunction!.canUseWith.contains(function)) {
        _secondaryFunctions.add(function);
      } else {
        throw Exception("Cannot use ${function.name} with ${_currentFunction!.name}");
      }
    }
  }

  void stop([GlassesFunctionality? function]) {
    if (function == null) {
      _currentFunction = null;
      _secondaryFunctions.clear();
    } else {
      if (function == _currentFunction) {
        _currentFunction = null;
        _secondaryFunctions.clear();
        return;
      }
      if (_secondaryFunctions.remove(function)) {
        return;
      }
    }
  }

  @override
  void dispose() {
    Pair._current = null;
    Pair.currentNotifier.value = null;
    super.dispose();
  }
}

enum GlassesFunctionality {
  tactileFloor(),
  readText(),
  gpsGuide(),
  ambientDetection();

  static const Map<GlassesFunctionality, Set<GlassesFunctionality>> _canUseWithGroups = {
    tactileFloor: { gpsGuide, ambientDetection },
    readText: { },
    gpsGuide: { tactileFloor, ambientDetection },
    ambientDetection: { }
  };

  Set<GlassesFunctionality> get canUseWith => _canUseWithGroups[this]!;
}