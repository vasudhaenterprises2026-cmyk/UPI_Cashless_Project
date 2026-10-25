import 'package:flutter/material.dart';

class AppTheme {
  static const Color primary = Color(0xFF1E3A8A);
  static const Color accent = Color(0xFF14B8A6);
  static const Color warning = Color(0xFFF59E0B);
  static const Color danger = Color(0xFFEF4444);
  static const Color background = Color(0xFFF8FAFC);
  static const Color card = Color(0xFFFFFFFF);

  static ThemeData lightTheme() {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary,
        brightness: Brightness.light,
      ),
      scaffoldBackgroundColor: background,
      cardTheme: const CardTheme(
        elevation: 0,
        margin: EdgeInsets.zero,
      ),
    );
  }
}
