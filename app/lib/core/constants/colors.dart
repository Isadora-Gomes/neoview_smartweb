import 'package:flutter/material.dart' show Color, MaterialColor;

abstract final class AppColors {
  static const blue = MaterialColor(0xFF1D34AD, {
    50: Color(0xFFE9ECFB),
    100: Color(0xFFCBD2F6),
    200: Color(0xFFA8B3F0),
    300: Color(0xFF7C8DE9),
    400: Color(0xFF5068E2),
    500: Color(0xFF1D35AF),
    600: Color(0xFF1D35AF),
    700: Color(0xFF162783),
    800: Color(0xFF0F1A57),
    900: Color(0xFF091034),
  });

  static const lightBlue = MaterialColor(0xFFC5D1FF, {
    50: Color(0xFFE5EBFF),
    100: Color(0xFFC2CEFF),
    200: Color(0xFF99AEFF),
    300: Color(0xFF6686FF),
    400: Color(0xFF335DFF),
    500: Color(0xFF002FE6),
    600: Color(0xFF002ACC),
    700: Color(0xFF002099),
    800: Color(0xFF001566),
    900: Color(0xFF000D3D),
  });

  static const grey = MaterialColor(0xFF808080, {
    50: Color(0xFFFFFFFF),
    100: Color(0xFFE0E0E0),
    200: Color(0xFFCCCCCC),
    300: Color(0xFFB3B3B3),
    400: Color(0xFF999999),
    500: Color(0xFF808080),
    600: Color(0xFF666666),
    700: Color(0xFF4D4D4D),
    800: Color(0xFF333333),
    900: Color(0xFF1F1F1F),
  });

  static const red = MaterialColor(0xFFAD341D, {
    50: Color(0xFFFBECE9),
    100: Color(0xFFF6D2CB),
    200: Color(0xFFF0B3A8),
    300: Color(0xFFE98D7C),
    400: Color(0xFFE26850),
    500: Color(0xFFAF351D),
    600: Color(0xFFAF351D),
    700: Color(0xFF832716),
    800: Color(0xFF571A0F),
    900: Color(0xFF341009),
  });

  static const white = Color(0xFFFFFFFF);
  static const black = Color(0xFF1F1F1F);
}