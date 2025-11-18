import 'dart:collection';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:neoview/core/constants/colors.dart';
import 'package:neoview/screens/home.dart';
import 'package:neoview/screens/instructions.dart';
import 'package:neoview/screens/login.dart';
import 'package:neoview/screens/pair.dart';
import 'package:neoview/screens/profile.dart';
import 'package:neoview/screens/register.dart';

typedef BrightnessStack = ({ Brightness statusBar, Brightness navigationBar });

const _fullDarkBrightness = (statusBar: Brightness.dark, navigationBar: Brightness.dark);
const _topLightBrightness = (statusBar: Brightness.light, navigationBar: Brightness.dark);

enum AppRoutes {
  login(_topLightBrightness, _login),
  register(_topLightBrightness, _register),
  home(_fullDarkBrightness, _home),
  profile(_topLightBrightness, _profile),
  pair(_fullDarkBrightness, _pair),
  instructions(_fullDarkBrightness, _instructions, true);

  final BrightnessStack brightness;
  final bool navigationBarContrast;
  final Widget Function(BuildContext) getRoute;

  const AppRoutes(this.brightness, this.getRoute, [ this.navigationBarContrast = false ]);

  bool stack(BuildContext context) {
    if (currentRoute == this) return false;
    _navigationStyle(statusBarBrightness: brightness.statusBar, navigationBarBrightness: brightness.navigationBar);
    _stack.add(this);
    _brightnessStack.add(brightness);
    currentRoute = this;
    currentBrightness = brightness;
    Navigator.of(context).pushNamed(name);
    notifier.value = this;
    return true;
  }

  bool resetTo(BuildContext context) {
    if (currentRoute == this) return false;
    _navigationStyle(statusBarBrightness: brightness.statusBar, navigationBarBrightness: brightness.navigationBar);
    _stack.clear();
    _stack.add(this);
    _brightnessStack.add(brightness);
    currentRoute = this;
    currentBrightness = brightness;
    Navigator.of(context).pushNamedAndRemoveUntil(name, (route) => false,);
    notifier.value = this;
    return true;
  }

  bool popAndStack(BuildContext context) {
    if (currentRoute == this) return false;
    final navigator = Navigator.of(context);
    if (!navigator.canPop()) return false;
    navigator.pop();
    stack(context);
    return true;
  }

  factory AppRoutes.byName(String name) => AppRoutes.values.firstWhere((e) => e.name == name);

  static void pop(BuildContext context) => Navigator.pop(context);

  static bool reset(BuildContext context) => initialRoute.resetTo(context);

  static final List<AppRoutes> _stack = [];
  static final List<BrightnessStack> _brightnessStack = [];
  static late AppRoutes initialRoute;
  static late AppRoutes currentRoute;

  static late BrightnessStack currentBrightness;

  static late SystemUiOverlayStyle systemUI;

  static final UnmodifiableListView<AppRoutes> stackView = UnmodifiableListView(_stack);

  static final Map<String, Widget Function(BuildContext)> routes = Map.unmodifiable({
    for (var route in AppRoutes.values) route.name: route.getRoute
  });

  static String initNavigation(AppRoutes route) {
    systemUiNotifier = ValueNotifier(const SystemUiOverlayStyle());
    _navigationStyle(navigationBarBrightness: route.brightness.navigationBar, statusBarBrightness: route.brightness.statusBar);
    if (_stack.isNotEmpty) return route.name;
    _stack.add(route);
    _brightnessStack.add(route.brightness);
    initialRoute = route;
    currentRoute = route;
    currentBrightness = route.brightness;
    notifier = ValueNotifier(route);
    return route.name;
  }

  static late ValueNotifier<AppRoutes> notifier;
  static late ValueNotifier<SystemUiOverlayStyle> systemUiNotifier;

  static Widget _login(BuildContext _) => const Login();
  static Widget _register(BuildContext _) => const Register();
  static Widget _home(BuildContext _) => const Home();
  static Widget _profile(BuildContext _) => const Profile();
  static Widget _pair(BuildContext _) => const Pair();
  static Widget _instructions(BuildContext _) => const Instructions();
}

void _navigationStyle({
  required Brightness statusBarBrightness,
  required Brightness navigationBarBrightness,
  bool navigationBarContrast = false,
}) {
  WidgetsBinding.instance.addPostFrameCallback((_) {
    AppRoutes.systemUI = SystemUiOverlayStyle(
      statusBarBrightness: statusBarBrightness == Brightness.light ?
        Brightness.dark : Brightness.light,
      statusBarIconBrightness: statusBarBrightness,
      statusBarColor: Colors.transparent,
      systemNavigationBarDividerColor: Colors.transparent,
      systemNavigationBarColor: navigationBarContrast ? AppColors.black.withAlpha(128) : Colors.transparent,
      systemNavigationBarIconBrightness: navigationBarBrightness,
      systemStatusBarContrastEnforced: false,
      systemNavigationBarContrastEnforced: navigationBarContrast,
    );

    AppRoutes.systemUiNotifier.value = AppRoutes.systemUI;

    SystemChrome.setSystemUIOverlayStyle(
      AppRoutes.systemUI
    );
  });
}

void navigationStyle({
  Brightness? statusBarBrightness,
  Brightness? navigationBarBrightness,
  bool navigationBarContrast = false,
}) {
  statusBarBrightness ??= AppRoutes.currentRoute.brightness.statusBar;
  navigationBarBrightness ??= AppRoutes.currentRoute.brightness.navigationBar;
  _navigationStyle(statusBarBrightness: statusBarBrightness, navigationBarBrightness: navigationBarBrightness);
  AppRoutes._brightnessStack.last = AppRoutes.currentBrightness = (statusBar: statusBarBrightness, navigationBar: navigationBarBrightness);
}

class PopObserver extends NavigatorObserver {
  @override
  void didPop(Route route, Route? previousRoute) {
    if (previousRoute != null && previousRoute.settings.name != null) {
      final prev = AppRoutes.byName(previousRoute.settings.name!);
      AppRoutes.currentRoute = prev;
      AppRoutes.notifier.value = prev;
      if (AppRoutes._stack.isNotEmpty) {
        AppRoutes._stack.removeLast();
        AppRoutes._brightnessStack.removeLast();
      }
      if (AppRoutes._stack.isNotEmpty) {
        AppRoutes.currentBrightness = AppRoutes._brightnessStack.last;
        _navigationStyle(
          statusBarBrightness: AppRoutes.currentBrightness.statusBar,
          navigationBarBrightness: AppRoutes.currentBrightness.navigationBar
        );
      }
    }
    super.didPop(route, previousRoute);
  }
}

void drawerNavigationStyler(bool isOpen) {
  print("Drawer changed $isOpen");
  navigationStyle(
    statusBarBrightness: isOpen ? Brightness.light : null,
    navigationBarBrightness: isOpen ? Brightness.light : null,
  );
}