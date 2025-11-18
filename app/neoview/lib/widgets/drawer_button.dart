import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:neoview/core/constants/colors.dart';
import 'package:neoview/core/constants/sizes.dart';

class AppDrawerButton extends StatelessWidget {
  const AppDrawerButton({super.key});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: "Abrir menu de navegação",
      child: GestureDetector(
        behavior: HitTestBehavior.translucent,
        onTap: () {
          Scaffold.of(context).openDrawer();
        },
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: kScreenPadding,
            ),
            Center(child: FaIcon(FontAwesomeIcons.bars, color: AppColors.blue, size: 36,)),
          ],
        ),
      ),
    );
  }
}