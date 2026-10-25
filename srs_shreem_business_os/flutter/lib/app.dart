import 'package:flutter/material.dart';

import 'features/auth/login_screen.dart';

class SrsShreemBusinessOsApp extends StatelessWidget {
  const SrsShreemBusinessOsApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SRS & SHREEM BUSINESS OS',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1E3A8A),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          centerTitle: false,
        ),
      ),
      home: const LoginScreen(),
    );
  }
}
