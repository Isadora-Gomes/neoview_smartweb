import 'package:flutter/material.dart' show BorderRadius, EdgeInsets, Radius;

abstract final class AppPaddings {
  static const tiny = EdgeInsets.all(4.0);
  static const small = EdgeInsets.all(8.0);
  static const medium = EdgeInsets.all(12.0);
  static const big = EdgeInsets.all(16.0);
  static const bigger = EdgeInsets.all(24.0);

  static const screen = EdgeInsets.symmetric(vertical: 8, horizontal: kScreenPadding);
}

abstract final class AppBorderRadius {
  static const tiny = BorderRadius.all(Radius.circular(2.0));
  static const small = BorderRadius.all(Radius.circular(4.0));
  static const medium = BorderRadius.all(Radius.circular(8.0));
  static const big = BorderRadius.all(Radius.circular(16.0));
  static const bigger = BorderRadius.all(Radius.circular(24.0));
}

const kScreenPadding = 24.0;
const kDoubleScreenPadding = kScreenPadding * 2;