import 'package:flutter/material.dart';
import 'package:neoview/core/constants/colors.dart';
import 'package:neoview/core/constants/sizes.dart';
import 'package:neoview/core/navigation.dart';
import 'package:neoview/widgets/drawer_button.dart';

class AppAppBar extends StatelessWidget implements PreferredSizeWidget {
  final Text? title;
  final bool drawerButton;
  final List<Widget> actions;
  
  const AppAppBar({ this.title, this.drawerButton = true, this.actions = const [], super.key});
  
  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder(
      valueListenable: AppRoutes.systemUiNotifier,
      builder: (context, value, child) {
        return AppBar(
          title: title,
          leading: drawerButton ? AppDrawerButton() : null,
          systemOverlayStyle: AppRoutes.systemUI,
          actions: actions.isEmpty ? null : actions.map(_actionsMap).toList()?..add(const SizedBox(width: kScreenPadding,)),
          backgroundColor: AppColors.white,
          surfaceTintColor: AppColors.white,
        );
      }
    );
  }
}

Widget _actionsMap(Widget action) => Padding(
  padding: AppPaddings.small,
  child: action,
);