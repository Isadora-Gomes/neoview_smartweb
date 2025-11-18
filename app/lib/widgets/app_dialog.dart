import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:neoview/core/constants/colors.dart';
import 'package:neoview/core/constants/sizes.dart';
import 'package:neoview/core/constants/styles.dart';

class AppDialog extends Dialog {
  final String? title;
  final Widget body;
  final IconData? icon;
  final List<Widget> actions;

  const AppDialog({
    required this.body,
    this.title,
    this.icon,
    this.actions = const [],
    super.key
  });

  @override
  Widget build(BuildContext context) {
    return Dialog(
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * .6,
        maxWidth: MediaQuery.of(context).size.width - kDoubleScreenPadding,
      ),
      child: Container(
        width: double.infinity,
        padding: AppPaddings.big,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          spacing: 8,
          children: [
            if (icon != null) Container(
              decoration: const BoxDecoration(
                color: AppColors.blue,
                shape: BoxShape.circle
              ),
              height: 96,
              child: Center(child: FaIcon(icon, color: AppColors.white, size: 48,)),
            ),
            if (title != null) Text(title!, style: AppTextStyles.title,),
            body,
            if (actions.isNotEmpty) Row(
              mainAxisAlignment: MainAxisAlignment.center,
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.center,
              spacing: 8,
              children: actions,
            )
          ],
        ),
      ),
    );
  }
}