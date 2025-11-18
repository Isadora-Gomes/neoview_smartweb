import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:neoview/core/constants/colors.dart';
import 'package:neoview/core/navigation.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);

  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
  ]);

  runApp(const MainApp());
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(
        fontFamily: "Poppins",
        colorScheme: ColorScheme(
          brightness: Brightness.light,
          primary: AppColors.blue,
          onPrimary: AppColors.white,
          secondary: AppColors.lightBlue,
          onSecondary: AppColors.black,
          error: AppColors.red,
          onError: AppColors.white,
          surface: AppColors.white,
          onSurface: AppColors.black
        ),
      ),
      routes: AppRoutes.routes,
      initialRoute: AppRoutes.initNavigation(AppRoutes.login),
      debugShowCheckedModeBanner: false,
      navigatorObservers: [PopObserver()],
    );
  }
}